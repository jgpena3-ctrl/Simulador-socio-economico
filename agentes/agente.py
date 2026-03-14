import numpy as np
from enum import Enum
from .fisiologia import Fisiologia
import config

class Personalidad(Enum):
    INTJ = "Arquitecto"
    INTP = "Lógico"
    ENTJ = "Comandante"
    ENTP = "Innovador"
    INFJ = "Abogado"
    INFP = "Mediador"
    ENFJ = "Protagonista"
    ENFP = "Activista"
    ISTJ = "Logístico"
    ISFJ = "Defensor"
    ESTJ = "Ejecutivo"
    ESFJ = "Cónsul"
    ISTP = "Virtuoso"
    ISFP = "Aventurero"
    ESTP = "Emprendedor"
    ESFP = "Animador"

class Agente:
    id_counter = 0

    def __init__(self, nombre, sexo, padre=None, madre=None, dia_nacimiento=None, edad=0):
        self.id = Agente.id_counter
        Agente.id_counter += 1

        self.nombre = nombre
        self.sexo = sexo
        self.edad = edad  # años
        self.dia_nacimiento = dia_nacimiento
        self.vivo = True

        # Genética heredada
        self.padre = padre
        self.madre = madre
        self.altura = self._heredar_altura()
        self.peso = self._calcular_peso_inicial()
        self.color_ojos = self._heredar_color()
        self.color_piel = self._heredar_color()
        self.color_cabello = self._heredar_color()
        self.belleza = self._calcular_belleza()

        # Sistema fisiológico
        self.fisiologia = Fisiologia(self)

        self.fisiologia.peso = self.peso
        self.fisiologia.altura = self.altura

        # Personalidad (16 tipos)
        self.personalidad = np.random.choice(list(Personalidad))

        # Sistema de actividades
        self.actividad_restante = 0   # ticks que faltan para terminar
        self.actividad_datos = {}      # datos adicionales (qué está recolectando, etc.)
        self.actividad_actual = None  # None, "moviendose", "comiendo", "trabajando", etc.
        self.actividad_destino = None  # Para actividades con objetivo

        # Experiencia en actividades
        self.experiencia = {
            "cazar": 0, "pescar": 0, "recolectar": 0,
            "cocinar": 0, "construir": 0, "comerciar": 0,
            "agricultura": 0, "herreria": 0, "carpinteria": 0
        }

        # Inventario
        self.inventario = {
            "comida": 10,
            "agua": 10,
            "madera": 0,
            "piedra": 0,
            "herramientas": 0,
            "monedas": 100
        }

        # Estado social
        self.pareja = None
        self.hijos = []
        self.afinidades = {}  # {agente_id: puntuacion}
        self.ubicacion = (0, 0)

        # Control del jugador
        self.controlado_por_jugador = False
        self.edad_control = 0  # Edad cuando comenzó a ser controlado



    def _heredar_altura(self):
        """Herencia de altura con variación genética"""
        if self.padre and self.madre:
            base = (self.padre.altura + self.madre.altura) / 2
        else:
            base = np.random.normal(1.7, 0.15)  # Altura promedio

        # Variación genética
        variacion = np.random.normal(0, 0.05)
        return max(1.4, min(2.1, base + variacion))

    def _calcular_peso_inicial(self):
        """Peso basado en altura y sexo"""
        imc_base = 22 if self.sexo == "M" else 21
        return imc_base * (self.altura ** 2)

    def _heredar_color(self):
        """Herencia de colores (simplificado)"""
        if self.padre and self.madre:
            return np.random.choice([self.padre.color_piel, self.madre.color_piel])
        return f"#{np.random.randint(50, 200):02x}{np.random.randint(50, 200):02x}{np.random.randint(50, 200):02x}"

    def _calcular_belleza(self):
        """Belleza basada en simetría y características"""
        base = np.random.normal(50, 15)
        if self.padre and self.madre:
            base = (base + self.padre.belleza + self.madre.belleza) / 3
        return max(0, min(100, base))

    def envejecer(self):
        """Envejecer el agente"""
        self.edad += 1 / config.DIAS_POR_AÑO

        # Morir por vejez (probabilístico)
        if self.edad > 70:
            prob_muerte = (self.edad - 70) * 0.01
            if np.random.random() < prob_muerte:
                self.vivo = False

    def puede_procrear(self, otro_agente):
        """Verificar si puede tener hijos con otro agente"""
        if not self.vivo or not otro_agente.vivo:
            return False
        if self.sexo == otro_agente.sexo:
            return False
        if self.edad < 18 or otro_agente.edad < 18:
            return False
        if self.edad > 50 or otro_agente.edad > 50:
            return False
        return True

    def procrear(self, pareja):
        """Crear un nuevo agente"""
        if not self.puede_procrear(pareja):
            return None

        # Determinar quién es padre y madre
        if self.sexo == "M":
            padre, madre = self, pareja
        else:
            padre, madre = pareja, self

        # Crear hijo
        sexos = ["M", "F"]
        hijo = Agente(
            nombre=f"Hijo_{self.id}_{pareja.id}",
            sexo=np.random.choice(sexos),
            padre=padre,
            madre=madre
        )

        # Añadir a listas de hijos
        self.hijos.append(hijo)
        pareja.hijos.append(hijo)

        return hijo

    def actualizar_afinidad(self, otro_agente, interaccion):
        """Actualizar afinidad con otro agente"""
        if otro_agente.id not in self.afinidades:
            self.afinidades[otro_agente.id] = 50

        # Factores de afinidad
        factor_personalidad = self._compatibilidad_personalidad(otro_agente)
        factor_belleza = (self.belleza + otro_agente.belleza) / 200
        factor_carisma = (self.fisiologia.carisma + otro_agente.fisiologia.carisma) / 200

        cambio = 0
        if interaccion == "positiva":
            cambio = 5 * factor_personalidad * factor_belleza
        elif interaccion == "negativa":
            cambio = -10

        self.afinidades[otro_agente.id] = max(0, min(100,
            self.afinidades[otro_agente.id] + cambio))

    def _compatibilidad_personalidad(self, otro_agente):
        """Compatibilidad basada en personalidad"""
        # Simplificado - algunas personalidades son más compatibles
        compatibilidades = {
            ("INTJ", "ENFP"): 1.5,
            ("INTP", "ENTJ"): 1.3,
            ("INFJ", "ENFP"): 1.6,
            ("ENFJ", "INFP"): 1.4,
        }

        key = (self.personalidad.name, otro_agente.personalidad.name)
        reverse_key = (otro_agente.personalidad.name, self.personalidad.name)

        if key in compatibilidades:
            return compatibilidades[key]
        elif reverse_key in compatibilidades:
            return compatibilidades[reverse_key]

        return 1.0  # Compatibilidad neutral

    def actualizar_tick(self):
        """Actualizar agente cada 30 minutos"""
        if not self.vivo:
            return

        # Envejecer (cada tick = 30 minutos)
        self.edad_dias += 30 / (24 * 60)  # Convertir minutos a días
        if self.edad_dias >= 365:
            self.edad += 1
            self.edad_dias -= 365
            self._cumpleannos()

        # Actualizar fisiología
        self.fisiologia.actualizar_tick_30min()

    def _cumpleannos(self):
        """Acciones en cumpleaños"""
        print(f"{self.nombre} cumple {self.edad} años!")

    def consumir(self):
        """Consumir alimento"""
        # Calorías aproximadas por tipo de alimento
        calorias_por_unidad = {
            "fruta": 50,
            "verdura": 30,
            "carne": 150,
            "pescado": 120,
            "cereal": 80,
            "agua": 0
        }
        alimento = self.inventario['comida']
        agua_ml = 250

        if alimento != 0:
            self.fisiologia.consumir_comida(150, agua_ml)
            self.inventario['comida'] = alimento-1

    def realizar_actividad(self, actividad, intensidad=1):
        """Realizar una actividad"""
        # Registrar actividad actual
        self.actividad_actual = actividad

        # Efectos específicos por actividad
        if actividad == "entrenar_fuerza":
            self.fisiologia.entrenar("fuerza", intensidad)
        elif actividad == "entrenar_agilidad":
            self.fisiologia.entrenar("agilidad", intensidad)
        elif actividad == "entrenar_resistencia":
            self.fisiologia.entrenar("resistencia", intensidad)
        elif actividad == "trabajar":
            self.fisiologia.calorias_gastadas_hoy += 200 * intensidad
            self.fisiologia.cansancio += 10 * intensidad
        elif actividad == "descansar":
            self.fisiologia.cansancio -= 5 * intensidad

        # Actualizar hambre/sed por actividad
        self.fisiologia.hambre += 2 * intensidad
        self.fisiologia.sed += 3 * intensidad

    def iniciar_actividad(self, actividad, duracion_ticks, **datos):
        """Inicia una actividad que durará múltiples ticks"""
        if self.actividad_actual:
            print(f"{self.nombre} ya está {self.actividad_actual}")
            return False

        self.actividad_actual = actividad
        self.actividad_restante = duracion_ticks
        self.actividad_datos = datos
        print(f"{self.nombre} comienza {actividad} ({duracion_ticks} ticks)")
        return True

    def tick_actividad(self):
        """Procesa un tick de la actividad actual"""
        if not self.actividad_actual:
            return False

        self.actividad_restante -= 1
        print(f"  {self.nombre}: {self.actividad_actual} - {self.actividad_restante} ticks restantes")

        if self.actividad_restante <= 0:
            self._finalizar_actividad()
            return True  # Actividad completada este tick

        return False  # Actividad aún en progreso

    def _finalizar_actividad(self):
        """Limpia la actividad actual"""
        print(f"{self.nombre} terminó {self.actividad_actual}")
        self.actividad_actual = None
        self.actividad_restante = 0
        self.actividad_datos = {}
