import logging
import config
import balance
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Fisiologia:
    def __init__(self, agente):
        self.agente = agente

        # Estados que se actualizan cada 30 minutos
        self.combustible = 0.1  # 0-100
        self.saciedad = 0.2
        self.sed = 50.0     # 0-100
        self.cansancio = 0.0  # 0-100
        self.energia = 100.0  # 0-100
        self.felicidad = 0
        self.hora = 0

        # Estados diarios (se actualizan cada día)
        self._ultima_actualizacion_diaria = datetime.now()
        self._ultima_actualizacion_anual = datetime.now()

        # Peso y características físicas
        self.peso = agente.peso  # kg
        self.altura = agente.altura  # m
        self.imc = self.peso / (self.altura ** 2)

        # Características físicas (se actualizan anualmente)
        self.fuerza_base = np.random.normal(50, 15)  # 0-100
        self.agilidad_base = np.random.normal(50, 15)  # 0-100
        self.resistencia_base = np.random.normal(50, 15)  # 0-100

        # Características cognitivas (más estables)
        self.inteligencia = np.random.normal(50, 10)  # 0-100
        self.carisma = np.random.normal(50, 10)  # 0-100

        # Estado actual (afectado por entrenamiento, fatiga, etc.)
        self.fuerza_actual = self.fuerza_base
        self.agilidad_actual = self.agilidad_base
        self.resistencia_actual = self.resistencia_base

        # Entrenamiento acumulado (se pierde si no se mantiene)
        self.entrenamiento_fuerza = 0  # 0-100
        self.entrenamiento_agilidad = 0  # 0-100
        self.entrenamiento_resistencia = 0  # 0-100

        # Consumo energético
        self.tmb = self.calcular_tmb()  # kcal/día
        self.calorias_por_tick = self.tmb/(48*4)

        # Registro de consumo
        self.agua_consumida_hoy = 0  # ml

        # Requerimientos diarios (varían según actividad)
        self.agua_necesaria = balance.AGUA_NECESARIA_BASE  # ml/día base

        # Tasa de consumo por tick (30 min)
        self.agua_por_tick = self.agua_necesaria / 48

        # Decaimiento por edad (por año)
        self.factor_deca_por_año = balance.FACTOR_DECAIMIENTO_ANUAL  # 0.3% anual después de cierta edad

    def actualizar_tick_30min(self, nuevo_día, nuevo_año):
        """Actualiza fisiología cada 30 minutos"""
        # Consumo energético basal
        agua_consumida = self.agua_por_tick
        self.peso -= self.calorias_por_tick * self._factor_actividad() # Límites realistas

        # Aumentar necesidades fisiológicas
        vaciable = False
        if self.combustible != 0:
            vaciable = True
        
        self.sed += (agua_consumida / self.agua_necesaria) * 100 * 0.4
        self.cansancio += self._actualizar_cansancio()

        # Energía basada en cansancio y nutrición
        logger.debug('energia actualizada por actualizar_tick_30min')
        if self.agente.actividad_actual != "durmiendo":
            self.energia = self.energia-(150/config.TICK_POR_DIA) #2/3 del dia en peddida de energia
            self.energia = max(0, min(100, self.energia))
            self.combustible = max(0, self.combustible-(self.saciedad/12))
        else:
            if self.hora > 20 or self.hora < 6:
                self.energia = self.energia+(300/config.TICK_POR_DIA)
                self.energia = max(0, min(100, self.energia))
            else:
                self.energia = self.energia+(150/config.TICK_POR_DIA)
                self.energia = max(0, min(100, self.energia))

            self.combustible = max(0, self.combustible-(self.saciedad/48))

        # Límites
        if vaciable and self.combustible == 0:
            self.saciedad *= 0.99

        # Efectos de fatiga en capacidades actuales
        self._actualizar_capacidades_actuales()

        # actualización
        if nuevo_día:
            self.actualizar_diario()

        if nuevo_año:
            self.actualizar_anual()

    def actualizar_diario(self):
        """Actualiza valores que cambian diariamente"""
        # Recalcular TMB con nuevo peso
        peso_anterior = self.peso
        self.tmb = self.calcular_tmb()
        self.calorias_por_tick = self.tmb/(48*4)

        # Recalcular IMC
        self.imc = self.peso / (self.altura ** 2)

        # Pérdida de entrenamiento si no se practica
        self._perdida_entrenamiento_diaria()

        #Envejecer
        self.agente.envejecer()

        # Debug/log
        cambio_peso = self.peso - peso_anterior
        if abs(cambio_peso) > 0.1:
            logger.debug(f"{self.agente.nombre}: Peso cambiado {cambio_peso:.2f}kg, ahora {self.peso:.1f}kg")

    def actualizar_anual(self):
        """Actualiza valores que cambian anualmente (en cumpleaños)"""
        edad = self.agente.edad

        # Decaimiento natural por edad (después de los 25-30)
        if edad > 25:
            decaimiento = self.factor_deca_por_año * (edad - 25)

            # Decaimiento mayor para agilidad, menor para fuerza
            self.fuerza_base *= (1 - decaimiento * 0.8)
            self.agilidad_base *= (1 - decaimiento * 1.2)
            self.resistencia_base *= (1 - decaimiento)

        # Crecimiento hasta los 25
        elif edad < 25:
            crecimiento = min(1.0, edad / 25)  # 0 a 1

            # Ajustar características base según crecimiento
            factor_crecimiento = 0.5 + (crecimiento * 0.5)  # 50% a 100%
            self.fuerza_base = 30 * factor_crecimiento + 20
            self.agilidad_base = 40 * factor_crecimiento + 30

        # Recalcular características actuales
        self._recalcular_capacidades_totales()

        # Ajustar altura si es joven (crecimiento hasta ~21 años)
        if edad < 21:
            self._crecer_altura()

    def _factor_actividad(self):
        """Factor multiplicador según nivel de actividad"""
        if self.cansancio > 80:
            return 0.8  # Muy cansado, menor gasto
        elif self.cansancio > 60:
            return 0.9
        elif self.energia > 80:
            return 1.2  # Energético, mayor gasto
        elif self.energia > 50:
            return 1.0  # Normal
        else:
            return 0.95  # Baja energía

    def _actualizar_cansancio(self):
        """Calcula incremento de cansancio basado en actividad"""
        base = 0.3

        # Modificadores
        if self.combustible > 0.70:
            base += 0.2  # Más cansancio si hay hambre
        if self.sed > 70:
            base += 0.2  # Más cansancio si hay sed

        # Actividad física incrementa cansancio
        if hasattr(self.agente, 'actividad_actual'):
            if self.agente.actividad_actual in ['trabajar', 'cazar', 'construir']:
                base += 0.5
            elif self.agente.actividad_actual in ['correr', 'pelear']:
                base += 1.0

        # Dormir reduce cansancio
        if hasattr(self.agente, 'durmiendo') and self.agente.durmiendo:
            base = -2.0  # Recuperación rápida

        return base

    def _actualizar_capacidades_actuales(self):
        """Ajusta capacidades actuales basado en estado"""
        # Fatiga afecta capacidades actuales
        factor_fatiga = 1.0 - (self.cansancio / 200)  # Hasta 50% de reducción

        # Hambre afecta fuerza y resistencia
        factor_hambre = 1.0

        # Sed afecta agilidad y cognición
        factor_sed = 1.0
        if self.sed > 70:
            factor_sed = 0.9 - ((self.sed - 70) / 300)

        # Calcular capacidades actuales
        self.fuerza_actual = self._calcular_fuerza_total() * factor_fatiga * factor_hambre
        self.agilidad_actual = self._calcular_agilidad_total() * factor_fatiga * factor_sed
        self.resistencia_actual = self._calcular_resistencia_total() * factor_fatiga * factor_hambre

    def _calcular_fuerza_total(self):
        """Calcula fuerza total incluyendo entrenamiento y características"""
        base = self.fuerza_base

        # Contribución del entrenamiento (hasta +50%)
        entrenamiento_bonus = (self.entrenamiento_fuerza / 100) * 50

        # Contribución del peso (más peso = potencial para más fuerza)
        peso_bonus = min(20, (self.peso - 70) * 0.5) if self.peso > 70 else 0

        # Contribución de la altura (personas más altas pueden tener palanca)
        altura_bonus = min(10, (self.altura - 1.7) * 10) if self.altura > 1.7 else 0

        total = base + entrenamiento_bonus + peso_bonus + altura_bonus
        return min(100, max(10, total))

    def _calcular_agilidad_total(self):
        """Calcula agilidad total"""
        base = self.agilidad_base

        # Entrenamiento bonus (hasta +40%)
        entrenamiento_bonus = (self.entrenamiento_agilidad / 100) * 40

        # IMC afecta agilidad (óptimo ~21-23)
        imc_optimo = 22
        imc_penalizacion = abs(self.imc - imc_optimo) * 2  # 2 puntos por unidad de IMC

        total = base + entrenamiento_bonus - imc_penalizacion
        return min(100, max(10, total))

    def _calcular_resistencia_total(self):
        """Calcula resistencia total (VO2 max aproximado)"""
        base = self.resistencia_base

        # Entrenamiento bonus (hasta +60%)
        entrenamiento_bonus = (self.entrenamiento_resistencia / 100) * 60

        # Edad afecta resistencia (pico a los 20-30)
        edad = self.agente.edad
        if edad > 30:
            edad_penalizacion = (edad - 30) * 0.5  # 0.5% por año después de 30
        else:
            edad_penalizacion = 0

        total = base + entrenamiento_bonus - edad_penalizacion
        return min(100, max(10, total))

    def _recalcular_capacidades_totales(self):
        """Recalcula todas las capacidades desde base"""
        self.fuerza_actual = self._calcular_fuerza_total()
        self.agilidad_actual = self._calcular_agilidad_total()
        self.resistencia_actual = self._calcular_resistencia_total()

    def _perdida_entrenamiento_diaria(self):
        """Pérdida diaria de entrenamiento si no se practica"""
        tasa_perdida = balance.PERDIDA_ENTRENAMIENTO_DIARIA  # 1% por día sin practicar

        # Verificar si hubo actividad relacionada
        if not self._ejercio_fuerza_hoy():
            self.entrenamiento_fuerza *= (1 - tasa_perdida)

        if not self._ejercio_agilidad_hoy():
            self.entrenamiento_agilidad *= (1 - tasa_perdida)

        if not self._ejercio_resistencia_hoy():
            self.entrenamiento_resistencia *= (1 - tasa_perdida)

    def _ejercio_fuerza_hoy(self):
        """Determina si hubo ejercicio de fuerza hoy"""
        # Esto se debería llenar con el registro de actividades del agente
        # Por ahora, retornamos aleatorio para testing
        return np.random.random() > 0.7

    def _ejercio_agilidad_hoy(self):
        return np.random.random() > 0.7

    def _ejercio_resistencia_hoy(self):
        return np.random.random() > 0.7

    def _crecer_altura(self):
        """Crecimiento de altura hasta los ~21 años"""
        edad = self.agente.edad

        # Curva de crecimiento aproximada
        if edad < 1:
            crecimiento = 0.25  # 25 cm primer año
        elif edad < 2:
            crecimiento = 0.12  # 12 cm segundo año
        elif edad < 12:
            crecimiento = 0.06  # 6 cm por año
        elif edad < 16:
            crecimiento = 0.08  # 8 cm por año (pubertad)
        elif edad < 18:
            crecimiento = 0.04  # 4 cm por año
        elif edad < 21:
            crecimiento = 0.01  # 1 cm por año (crecimiento residual)
        else:
            crecimiento = 0

        # Aplicar crecimiento
        self.altura += crecimiento / 100  # Convertir a metros
        self.agente.altura = self.altura  # Actualizar en agente

    def calcular_tmb(self):
        """Tasa Metabólica Basal (Harris-Benedict revisado)"""
        peso = self.peso
        altura_cm = self.altura * 100
        edad = self.agente.edad

        if self.agente.sexo == "M":
            tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161

        return tmb

    def consumir_comida(self, kg_comida, agua_ml=0):
        """Registrar consumo de comida y agua"""

        # Reducir hambre basado en calorías consumidas
        self.combustible = min(self.combustible + kg_comida, self.saciedad)
        self.peso += kg_comida
        if self.saciedad == self.combustible:
            self.saciedad *= 1.01

        # Reducir sed si se consumió agua
        if agua_ml > 0:
            reduccion_sed = (agua_ml / self.agua_necesaria) * 100 * 0.9
            self.sed = max(0, self.sed - reduccion_sed)

    def dormir(self, horas):
        """Efecto de dormir"""
        logger.debug('se ejecutó dormir')
        recuperacion = horas * 5  # 5% por hora
        self.cansancio = max(0, self.cansancio - recuperacion)

        # Recuperación más rápida si se duerme de noche
        ahora = datetime.now().hour
        if 22 <= ahora <= 6:  # Noche
            recuperacion *= 1.5

        # Mejor recuperación si no hay hambre/sed
        if self.combustible > 0.1 and self.sed < 30:
            recuperacion *= 1.2

    def entrenar(self, tipo, intensidad):
        """Entrenar una característica física"""
        ganancia = intensidad * 0.1  # 0.1% por punto de intensidad

        if tipo == "fuerza":
            self.entrenamiento_fuerza = min(100, self.entrenamiento_fuerza + ganancia)
            # Aumenta cansancio
            self.cansancio += intensidad * 0.5
            # Gasta más calorías
            self.peso -= self.calorias_por_tick * 2
        elif tipo == "agilidad":
            self.entrenamiento_agilidad = min(100, self.entrenamiento_agilidad + ganancia)
            self.cansancio += intensidad * 0.4
            self.peso -= self.calorias_por_tick * 2
        elif tipo == "resistencia":
            self.entrenamiento_resistencia = min(100, self.entrenamiento_resistencia + ganancia)
            self.cansancio += intensidad * 0.3
            self.peso -= self.calorias_por_tick * 2

        # Recalcular capacidades
        self._recalcular_capacidades_totales()

    def necesita_dormir(self):
        return self.cansancio > 70 or self.energia < 30

    def necesita_comer(self):
        return 1-(self.combustible / self.saciedad)

    def necesita_beber(self):
        return self.sed > 50 or self.agua_consumida_hoy < self.agua_necesaria * 0.6

    def get_estado_salud(self):
        """Retorna un string con el estado de salud"""
        if self.imc < 18.5:
            peso_estado = "Bajo peso"
        elif self.imc < 25:
            peso_estado = "Peso normal"
        elif self.imc < 30:
            peso_estado = "Sobrepeso"
        else:
            peso_estado = "Obesidad"

        return {
            "peso": f"{self.peso:.1f} kg",
            "imc": f"{self.imc:.1f} ({peso_estado})",
            "tmb": f"{self.tmb:.0f} kcal/día",
            "fuerza": f"{self.fuerza_actual:.1f}/100",
            "agilidad": f"{self.agilidad_actual:.1f}/100",
            "resistencia": f"{self.resistencia_actual:.1f}/100",
            "entrenamiento": {
                "fuerza": f"{self.entrenamiento_fuerza:.1f}%",
                "agilidad": f"{self.entrenamiento_agilidad:.1f}%",
                "resistencia": f"{self.entrenamiento_resistencia:.1f}%"
            }
        }
