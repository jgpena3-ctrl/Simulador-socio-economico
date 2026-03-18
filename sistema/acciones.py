from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
# acciones.py
import config
import balance
import math
import numpy as np
import inspect
from functools import wraps
from typing import Any, Callable

def combinacion(n: int, r: int) -> int:
    return math.comb(n, r)


def rastrear_llamadas(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Obtener información del llamante
        frame = inspect.currentframe()
        frame_llamada = inspect.getouterframes(frame, 2)[1]

        logger.debug(f"⚡ {func.__name__} fue llamado desde:")
        logger.debug(f"   📁 Archivo: {frame_llamada.filename}")
        logger.debug(f"   📍 Línea: {frame_llamada.lineno}")
        logger.debug(f"   🔧 Función: {frame_llamada.function}")
        logger.debug(f"   📝 Código: {frame_llamada.code_context[0].strip() if frame_llamada.code_context else 'N/A'}")

        return func(*args, **kwargs)
    return wrapper


class Acciones:
    TICKS_BUSCAR = balance.TICKS_BUSCAR
    TICKS_RECOLECTAR = balance.TICKS_RECOLECTAR
    TICKS_CAZAR = balance.TICKS_CAZAR
    TICKS_TALAR = balance.TICKS_TALAR
    TICKS_DORMIR = balance.TICKS_DORMIR
    TICKS_DESCANSAR = balance.TICKS_DESCANSAR
    TICKS_COMER = balance.TICKS_COMER
    TICKS_BEBER = balance.TICKS_BEBER

    def __init__(self, simulador: Any) -> None:
        self.simulador = simulador  # Referencia al simulador
        self.TICKS_BUSQUEDA = balance.TICKS_BUSQUEDA_INTERNA
        self.TICKS_ACCION = balance.TICKS_ACCION_INTERNA
        self.TICKS_COMPLETO = balance.TICKS_COMPLETO


    def _accion_dormir(self, agente: Any = None) -> bool:
        """Inicia actividad de dormir."""
        if agente is None:
            agente = self.simulador.agente_jugador
        if not agente:
            return False

        if self.simulador.iniciar_actividad(agente, "durmiendo", duracion_ticks=self.TICKS_DORMIR):
            logger.debug(f"{agente.nombre} se acuesta a dormir")
            return True
        return False

    def _accion_comer(self, agente: Any = None) -> bool:
        """Consume comida e inicia actividad de comer."""
        if agente is None:
            agente = self.simulador.agente_jugador
        if not agente:
            return False

        if agente.inventario.get("comida", 0) <= 0:
            logger.debug(f"{agente.nombre} no tiene comida")
            return False

        if self.simulador.iniciar_actividad(agente, "comiendo", duracion_ticks=self.TICKS_COMER):
            agente.inventario["comida"] -= 1
            return True
        return False

    def _accion_trabajar(self, agente: Any = None) -> bool:
        """Acción de trabajo simple basada en experiencia."""
        if agente is None:
            agente = self.simulador.agente_jugador
        if not agente:
            return False

        duracion = np.random.randint(balance.TRABAJO_DURACION_MIN, balance.TRABAJO_DURACION_MAX)
        if self.simulador.iniciar_actividad(agente, "trabajando", duracion_ticks=duracion):
            if agente.experiencia.get("agricultura", 0) > 30:
                produccion = np.random.randint(1, 4)
                agente.inventario["comida"] = agente.inventario.get("comida", 0) + produccion
                agente.experiencia["agricultura"] = agente.experiencia.get("agricultura", 0) + 0.5
                logger.debug(f"{agente.nombre} trabaja en la granja: +{produccion} comida")
            else:
                ingresos = np.random.randint(3, 8)
                agente.inventario["monedas"] = agente.inventario.get("monedas", 0) + ingresos
                logger.debug(f"{agente.nombre} hace trabajos básicos: +{ingresos} monedas")
            return True
        return False

    def _accion_socializar(self, agente: Any = None) -> bool:
        """Interacción social básica con agentes cercanos."""
        if agente is None:
            agente = self.simulador.agente_jugador
        if not agente:
            return False

        if not self.simulador.iniciar_actividad(agente, "socializando", duracion_ticks=balance.SOCIALIZAR_DURACION):
            return False

        vecinos = [
            otro for otro in self.simulador.agentes
            if otro is not agente and otro.vivo and self.simulador._distancia(agente.ubicacion, otro.ubicacion) <= 2
        ]

        if not vecinos:
            logger.debug(f"{agente.nombre} intenta socializar pero no hay nadie cerca")
            return True

        otro_agente = np.random.choice(vecinos)
        agente.actualizar_afinidad(otro_agente, "charla_amistosa")
        otro_agente.actualizar_afinidad(agente, "charla_amistosa")
        logger.debug(f"{agente.nombre} socializa con {otro_agente.nombre}")
        return True

    def _accion_recolectar(self, agente: Any = None) -> None:
        """
        Acción de recolectar - COMPLETAMENTE PROBABILÍSTICA
        """
        total_casillas = 817
        vision = 9
        ticks = 0

        while ticks < config.TIEMPO_TICK:

            if agente is None:
                agente = self.simulador.agente_jugador

            if not agente:
                return

            # Obtener información de la macro-casilla actual
            hex_info = self.simulador.mapa.hexagonos.get(agente.ubicacion)
            if not hex_info:
                logger.debug("Error: Casilla no encontrada")
                return

            logger.debug(f"\n=== RECOLECTANDO en macro-casilla {agente.ubicacion} ===")

            # 1. PROBABILIDAD DE ENCONTRAR algo para recolectar
            # Basado en recursos TOTALES de la macro-casilla

            # Calcular recursos totales disponibles
            total_arbustos = hex_info.arbustos
            total_arboles = hex_info.arboles
            total_frutos = hex_info.frutos
            total_vegetacion = int(total_arbustos + total_arboles * 0.3)
            if total_vegetacion == 0:
                ticks += self.TICKS_BUSQUEDA
                continue

            prom_frutos = total_frutos / total_vegetacion

            if (total_arbustos == 0 and total_arboles == 0) or total_frutos == 0:
                logger.debug("Esta macro-casilla no tiene recursos para recolectar")
                ticks += self.TICKS_BUSQUEDA
                continue

            logger.debug(f"Recursos en esta macro-casilla:")
            logger.debug(f"  - Arbustos: {total_arbustos}")
            logger.debug(f"  - Árboles: {total_arboles}")
            logger.debug(f"  - Frutos: {total_frutos}")

            # Probabilidad de encontrar algo = densidad de recursos
            ''' A mayor densidad, más probable encontrar,
                Un tercio de los arboles son frutales?'''

            favorables = combinacion(total_casillas-total_vegetacion, vision)
            totales = combinacion(total_casillas, vision)

            prob_ninguno = favorables / totales
            prob_encontrar = 1 - prob_ninguno

            logger.debug(f"Probabilidad de encontrar algo: {prob_encontrar*100:.1f}%")

            # Tirar dados para ver si encuentra
            if np.random.random() > prob_encontrar:
                logger.debug("❌ No encontraste nada para recolectar después de buscar")
                # Pequeña ganancia de experiencia
                agente.experiencia["recolectar"] = min(100,
                    agente.experiencia.get("recolectar", 0) + 0.2)
                ticks += self.TICKS_BUSQUEDA
                continue

            logger.debug("✅ ¡Encontraste algo para recolectar!")

            # 2. DETERMINAR QUÉ ENCONTRÓ
            # Aleatorio basado en proporción de recursos
            opciones = []
            if total_arbustos > 0:
                opciones.extend(["arbusto"] * total_arbustos)
            if total_arboles > 0:
                opciones.extend(["arbol"] * total_arboles)

            tipo_encontrado = np.random.choice(opciones)

            logger.debug(f"Encontraste: {tipo_encontrado}")

            # 3. CALIDAD DE LA RECOLECCIÓN (éxito)
            # Basado en experiencia del agente
            exp_recoleccion = agente.experiencia.get("recolectar", 0) # por usar
            cantidad = np.random.randint(0, prom_frutos*2)
            hex_info.frutos = max(0, hex_info.frutos-cantidad)

            # 4. CANTIDAD RECOLECTADA
            if tipo_encontrado == "arbusto":
                agente.inventario["fruta"] = agente.inventario.get("fruta", 0) + cantidad
                logger.debug(f"✅ Recolectaste {cantidad} frutas de arbustos!")

            else:  # árbol
                agente.inventario["fruta"] = agente.inventario.get("fruta", 0) + cantidad
                logger.debug(f"✅ Encontraste {cantidad} frutas en los árboles!")

            # 5. GANANCIA DE EXPERIENCIA
            ganancia_exp = 0.01
            agente.experiencia["recolectar"] = min(100,
                agente.experiencia.get("recolectar", 0) + ganancia_exp)

            ticks += self.TICKS_ACCION
            continue

        agente.iniciar_actividad(
            actividad="recolectar",
            duracion_ticks = self.TICKS_RECOLECTAR
        )

    def _accion_cazar(self, agente: Any = None) -> int | None:
        logger.debug("Acción: Cazar animal")
        """
        Acción de cazar - COMPLETAMENTE PROBABILÍSTICA
        """
        vision = 9
        total_casillas = 817
        ticks = 0

        while ticks < config.TIEMPO_TICK:

            if agente is None:
                agente = self.simulador.agente_jugador

            if not agente:
                return

            # Obtener información de la macro-casilla actual
            hex_info = self.simulador.mapa.hexagonos.get(agente.ubicacion)
            if not hex_info:
                logger.debug("Error: Casilla no encontrada")
                return

            logger.debug(f"\n=== CAZANDO en macro-casilla {agente.ubicacion} ===")

            # 1. PROBABILIDAD DE ENCONTRAR animales
            # Calcular total de animales en la macro-casilla
            if not hex_info.animales or sum(hex_info.animales.values()) == 0:
                logger.debug("Esta macro-casilla no tiene animales")
                ticks += self.TICKS_BUSQUEDA
                continue

            total_animales = sum(hex_info.animales.values())

            logger.debug(f"Animales en esta macro-casilla: {total_animales}")
            for animal, cantidad in hex_info.animales.items():
                if cantidad > 0:
                    logger.debug(f"  - {animal}: {cantidad}")

            # Probabilidad de encontrar rastros/avistar
            favorables = combinacion(total_casillas-total_animales, vision)
            totales = combinacion(total_casillas, vision)

            prob_ninguno = favorables / totales
            prob_encontrar = 1 - prob_ninguno

            logger.debug(f"Probabilidad de encontrar rastros: {prob_encontrar*100:.1f}%")

            if np.random.random() > prob_encontrar:
                logger.debug("❌ No encontraste rastros de animales hoy")
                ticks += self.TICKS_BUSQUEDA
                continue

            logger.debug("✅ ¡Encontraste rastros frescos!")

            # 2. DETERMINAR QUÉ ANIMAL ENCONTRÓ
            # Selección aleatoria ponderada por cantidad
            animales_lista = []
            pesos = []
            for animal, cantidad in hex_info.animales.items():
                if cantidad > 0:
                    animales_lista.append(animal)
                    pesos.append(cantidad)

            animal_elegido = np.random.choice(animales_lista, p=np.array(pesos)/sum(pesos))

            logger.debug(f"Rastros de: {animal_elegido}")

            # 3. PROBABILIDAD DE ÉXITO EN LA CACERÍA
            exp_caza = agente.experiencia.get("cazar", 0)
            fuerza = agente.fisiologia.fuerza_actual
            agilidad = agente.fisiologia.agilidad_actual

            # Dificultad por animal
            dificultad = {
                "conejo": 0.3, "pájaro": 0.4, "rata": 0.2,
                "ciervo": 0.7, "jabalí": 0.8, "zorro": 0.6, "lobo": 0.9
            }.get(animal_elegido, 0.5)

            # Probabilidad base: 50% - dificultad + habilidades
            prob_exito = 0.5 - dificultad + (exp_caza / 200) + ((fuerza - 50) / 200) + ((agilidad - 50) / 200)
            prob_exito = max(0.1, min(0.9, prob_exito))

            logger.debug(f"Probabilidad de éxito: {prob_exito*100:.1f}%")
            logger.debug(f"  Dificultad del {animal_elegido}: {dificultad*100:.0f}%")
            logger.debug(f"  Bonus por experiencia: +{exp_caza/200*100:.1f}%")

            if np.random.random() > prob_exito:
                logger.debug(f"❌ El {animal_elegido} escapó")
                agente.experiencia["cazar"] = min(100,
                    agente.experiencia.get("cazar", 0) + 0.01)
                ticks += self.TICKS_BUSQUEDA
                continue

            # 4. ÉXITO - CALCULAR PRESA
            # Peso de carne por animal (kg)
            peso_carne = {
                "conejo": 1.0, "pájaro": 0.5, "rata": 0.3,
                "ciervo": 20.0, "jabalí": 15.0, "zorro": 5.0, "lobo": 10.0
            }

            carne_base = peso_carne.get(animal_elegido, 1.0)

            # Bonus por experiencia (mejor despiece)
            bonus_exp = exp_caza / 50  # +0.02 por punto de exp
            carne_total = carne_base * (1 + bonus_exp)
            carne_total = round(carne_total, 1)

            # Reducir población del animal
            hex_info.animales[animal_elegido] -= 1
            if hex_info.animales[animal_elegido] <= 0:
                del hex_info.animales[animal_elegido]

            # Añadir al inventario
            agente.inventario["carne"] = agente.inventario.get("carne", 0) + carne_total

            logger.debug(f"✅ ¡Caza exitosa!")
            logger.debug(f"   Obtuviste {carne_total} kg de carne de {animal_elegido}")

            # Posibilidad de obtener piel/cuero (para crafting futuro)
            """if np.random.random() < 0.4:  # 40% de obtener piel
                agente.inventario["piel"] = agente.inventario.get("piel", 0) + 1
                logger.debug(f"   También obtuviste 1 piel")"""

            # 5. GANANCIA DE EXPERIENCIA
            agente.experiencia["cazar"] = min(100,
                agente.experiencia.get("cazar", 0) + 0.02)

            return self.TICKS_ACCION

        agente.iniciar_actividad(
            actividad="cazar",
            duracion_ticks = self.TICKS_CAZAR
        )

    def _accion_descansar(self, agente: Any = None) -> int:
        """
        Inicia la acción de descansar
        Solo se puede descansar en casillas habitables
        """

        logger.debug('está _accion_descansar')
        if agente is None:
            agente = self.simulador.agente_jugador

        # Verificar si puede descansar aquí
        if not self._puede_descansar_aqui(agente.ubicacion):
            logger.debug(f"No puedes descansar en {agente.ubicacion}. Busca una vivienda o el centro.")
            return self.TICKS_COMPLETO

        # Verificar que no esté ya en otra actividad
        if agente.actividad_actual:
            logger.debug(f"{agente.nombre} ya está {agente.actividad_actual}")
            return self.TICKS_COMPLETO

        logger.debug(f"\n=== DESCANSANDO en {agente.ubicacion} ===")
        logger.debug(f"Duración: {self.TICKS_DESCANSAR} ticks ({self.TICKS_DESCANSAR * 30} minutos)")
        #logger.debug(f"Recuperación estimada: {self.REDUCCION_CANSANCIO_POR_TICK * self.TICKS_DESCANSAR}% cansancio")

        # Iniciar actividad
        agente.iniciar_actividad(
            actividad="durmiendo",
            duracion_ticks = self.TICKS_DORMIR
        )

        return self.TICKS_COMPLETO  # Consume 1 tick para iniciar

    def _puede_descansar_aqui(self, ubicacion: tuple[int, int]) -> bool:
        """Determina si una casilla es habitable"""
        hex_info = self.simulador.mapa.hexagonos.get(ubicacion)
        if not hex_info:
            return False

        # Casilla central (siempre habitable)
        if ubicacion == (0, 0):
            return True

        # Casillas con viviendas
        if hasattr(hex_info, 'construccion') and hex_info.construccion == "vivienda":
            return True

        # Casillas que son propiedad del agente (futuro)
        # if hex_info.propietario == agente.id:
        #     return True

        return False

    def _accion_talar(self, agente: Any = None) -> None:
        """
        Acción de talar
        """
        total_casillas = 817
        vision = 9

        if agente is None:
            agente = self.simulador.agente_jugador

        if not agente:
            return

        # Obtener información de la macro-casilla actual
        hex_info = self.simulador.mapa.hexagonos.get(agente.ubicacion)
        if not hex_info:
            logger.debug("Error: Casilla no encontrada")
            return

        logger.debug(f"\n=== TALANDO en macro-casilla {agente.ubicacion} ===")

        # 1. PROBABILIDAD DE ENCONTRAR algo para talar
        # Basado en recursos TOTALES de la macro-casilla

        # Calcular recursos totales disponibles
        total_arboles = hex_info.arboles
        if total_arboles == 0:
            logger.debug("Esta macro-casilla no tiene recursos para recolectar")
            return

        logger.debug(f"Recursos en esta macro-casilla:")
        logger.debug(f"  - Árboles: {total_arboles}")

        # Probabilidad de encontrar algo = densidad de recursos
        ''' A mayor densidad, más probable encontrar'''

        favorables = combinacion(total_casillas-total_arboles, vision)
        totales = combinacion(total_casillas, vision)

        prob_ninguno = favorables / totales
        prob_encontrar = 1 - prob_ninguno

        logger.debug(f"Probabilidad de encontrar algo: {prob_encontrar*100:.1f}%")

        # Tirar dados para ver si encuentra
        for _ in range(config.TIEMPO_TICK):
            if np.random.random() < prob_encontrar:
                logger.debug("✅ ¡Encontraste algo para talar!")
                break
        else:
            logger.debug("❌ No encontraste nada para talar después de buscar")
            return

        # 2. DETERMINAR QUÉ ENCONTRÓ
        # Aleatorio basado en proporción de recursos
        opciones = []
        if total_arboles > 0:
            opciones.extend(["arbol"] * total_arboles)

        tipo_encontrado = np.random.choice(opciones)

        logger.debug(f"Encontraste: {tipo_encontrado}")

        # 3. CALIDAD DE LA RECOLECCIÓN (éxito)
        # Basado en experiencia del agente
        exp_talar = agente.experiencia.get("talar", 0) # por usar
        cantidad = np.random.randint(1)
        hex_info.arboles -= 1
        #hex_info.recoger += 1

        # 4. GANANCIA DE EXPERIENCIA
        ganancia_exp = 0.01
        agente.experiencia["talar"] = min(100,
            agente.experiencia.get("talar", 0) + ganancia_exp)

        agente.iniciar_actividad(
            actividad="talar",
            duracion_ticks = self.TICKS_TALAR
        )

    # ===== ACCIONES DE MERCADO =====

    def accion_publicar_oferta_venta(self, agente: Any, producto: str, cantidad: int, precio_unitario: float, calidad: float = 1.0) -> int | bool:
        """
        Acción: Publicar una oferta de venta en el mercado
        - Consume tiempo (1 tick)
        - Requiere que el agente tenga los productos en inventario
        """
        # Verificar que tiene los productos
        if agente.inventario.get(producto, 0) < cantidad:
            logger.debug(f"❌ {agente.nombre} no tiene suficiente {producto}")
            return False

        # Quitar productos del inventario (pasan al mercado)
        agente.inventario[producto] -= cantidad

        # Publicar oferta
        oferta_id = self.simulador.economia.publicar_oferta_venta(
            agente.id, producto, cantidad, precio_unitario, calidad
        )

        logger.debug(f"📢 {agente.nombre} publicó venta: {cantidad} {producto} a {precio_unitario} monedas")

        # Registrar acción para experiencia
        agente.experiencia["comerciar"] = agente.experiencia.get("comerciar", 0) + 0.1

        # Consumir energía (burocracia también cansa)
        agente.fisiologia.cansancio += 2
        agente.fisiologia.hambre += 1

        return oferta_id

    def accion_publicar_oferta_compra(self, agente: Any, producto: str, cantidad: int, precio_maximo: float) -> int | bool:
        """
        Acción: Publicar una oferta de compra en el mercado
        - Consume tiempo (1 tick)
        - Requiere reservar las monedas (congeladas hasta que se compre)
        """
        # Calcular costo total máximo
        costo_maximo = precio_maximo * cantidad

        # Verificar que tiene las monedas
        if agente.inventario.get("monedas", 0) < costo_maximo:
            logger.debug(f"❌ {agente.nombre} no tiene suficientes monedas")
            return False

        # Congelar monedas (se descuentan temporalmente)
        # Podrías tener un sistema de "monedas_reservadas"
        agente.inventario["monedas"] -= costo_maximo
        agente.monedas_reservadas = agente.monedas_reservadas + costo_maximo if hasattr(agente, 'monedas_reservadas') else costo_maximo

        # Publicar oferta
        oferta_id = self.simulador.economia.publicar_oferta_compra(
            agente.id, producto, cantidad, precio_maximo
        )

        logger.debug(f"📢 {agente.nombre} publicó compra: busca {cantidad} {producto} (max {precio_maximo})")

        agente.experiencia["comerciar"] = agente.experiencia.get("comerciar", 0) + 0.1
        agente.fisiologia.cansancio += 2
        agente.fisiologia.hambre += 1

        return oferta_id

    def accion_comprar(self, comprador: Any, oferta_venta_id: int, cantidad: int) -> dict[str, Any] | bool:
        """
        Acción: Comprar de una oferta de venta existente
        - Consume tiempo (1 tick)
        - Transfiere productos y monedas
        """
        # Buscar oferta
        oferta = self.simulador.economia.get_oferta_venta(oferta_venta_id)
        if not oferta or not oferta["activa"]:
            logger.debug(f"❌ Oferta de venta no disponible")
            return False

        if oferta["cantidad"] < cantidad:
            logger.debug(f"❌ Cantidad insuficiente en oferta")
            return False

        # Verificar que tiene monedas
        costo_total = oferta["precio_unitario"] * cantidad
        if comprador.inventario.get("monedas", 0) < costo_total:
            logger.debug(f"❌ {comprador.nombre} no tiene suficientes monedas")
            return False

        # Buscar o crear oferta de compra automática
        oferta_compra_id = self.simulador.economia.publicar_oferta_compra(
            comprador.id, oferta["producto"], cantidad, oferta["precio_unitario"] + 1
        )

        # Realizar transacción
        transaccion = self.simulador.economia.realizar_transaccion(
            oferta_venta_id, oferta_compra_id, cantidad
        )

        if transaccion:
            # Transferir productos al comprador
            comprador.inventario[oferta["producto"]] = comprador.inventario.get(oferta["producto"], 0) + cantidad

            # El vendedor ya no tiene los productos (se quitaron al publicar)
            # Las monedas se manejan en la transacción

            logger.debug(f"✅ {comprador.nombre} compró {cantidad} {oferta['producto']} por {costo_total} monedas")

            # Registrar afinidad con el vendedor
            vendedor = self._get_agente_by_id(oferta["agente_id"])
            if vendedor:
                comprador.actualizar_afinidad(vendedor, "comercial_positiva")

            return transaccion

        return False

    def accion_vender(self, vendedor: Any, oferta_compra_id: int, cantidad: int) -> dict[str, Any] | bool:
        """
        Acción: Vender a una oferta de compra existente
        - Consume tiempo (1 tick)
        - Transfiere productos y monedas
        """
        # Buscar oferta de compra
        oferta = self.simulador.economia.get_oferta_compra(oferta_compra_id)
        if not oferta or not oferta["activa"]:
            logger.debug(f"❌ Oferta de compra no disponible")
            return False

        if oferta["cantidad"] < cantidad:
            logger.debug(f"❌ Cantidad solicitada insuficiente")
            return False

        # Verificar que tiene los productos
        if vendedor.inventario.get(oferta["producto"], 0) < cantidad:
            logger.debug(f"❌ {vendedor.nombre} no tiene suficiente {oferta['producto']}")
            return False

        # Crear oferta de venta automática
        oferta_venta_id = self.simulador.economia.publicar_oferta_venta(
            vendedor.id, oferta["producto"], cantidad, oferta["precio_maximo"], 1.0
        )

        # Realizar transacción
        transaccion = self.simulador.economia.realizar_transaccion(
            oferta_venta_id, oferta_compra_id, cantidad
        )

        if transaccion:
            # Quitar productos del inventario
            vendedor.inventario[oferta["producto"]] -= cantidad

            # Las monedas ya están en la transacción

            logger.debug(f"✅ {vendedor.nombre} vendió {cantidad} {oferta['producto']} por {transaccion['total']} monedas")

            return transaccion

        return False

    def accion_cancelar_oferta(self, agente: Any, oferta_id: int, tipo_oferta: str) -> bool:
        """
        Acción: Cancelar una oferta propia
        - Devuelve los productos/monedas al agente
        """
        if tipo_oferta == "venta":
            oferta = self.simulador.economia.get_oferta_venta(oferta_id)
            if oferta and oferta["agente_id"] == agente.id and oferta["activa"]:
                # Devolver productos
                agente.inventario[oferta["producto"]] = agente.inventario.get(oferta["producto"], 0) + oferta["cantidad"]
                oferta["activa"] = False
                logger.debug(f"✅ Oferta de venta cancelada, {oferta['cantidad']} {oferta['producto']} devueltos")
                return True

        elif tipo_oferta == "compra":
            oferta = self.simulador.economia.get_oferta_compra(oferta_id)
            if oferta and oferta["agente_id"] == agente.id and oferta["activa"]:
                # Devolver monedas congeladas
                costo = oferta["precio_maximo"] * oferta["cantidad"]
                agente.inventario["monedas"] = agente.inventario.get("monedas", 0) + costo
                if hasattr(agente, 'monedas_reservadas'):
                    agente.monedas_reservadas -= costo
                oferta["activa"] = False
                logger.debug(f"✅ Oferta de compra cancelada, {costo} monedas devueltas")
                return True

        return False
