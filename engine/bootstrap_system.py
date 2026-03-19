import logging

import numpy as np

import config
from agentes.agente import Agente

logger = logging.getLogger(__name__)


class BootstrapSystem:
    """Inicializa población y estado económico inicial de la simulación."""

    def __init__(self, simulador):
        self.simulador = simulador

    def inicializar_agentes(self):
        """Crear agentes iniciales (jugador + NPCs)."""
        sim = self.simulador

        sim.agente_jugador = Agente(
            "Jugador",
            "M",
            dia_nacimiento=np.random.randint(1, config.DIAS_POR_AÑO + 1),
            edad=18,
        )
        sim.agente_jugador.controlado_por_jugador = True
        sim.agente_jugador.ubicacion = (0, 0)
        sim.agentes.append(sim.agente_jugador)
        sim.agentes_controlables.append(sim.agente_jugador)

        nombres_m = ["Carlos", "Juan", "Pedro", "Luis", "Miguel"]
        nombres_f = ["Ana", "Maria", "Laura", "Sofia", "Elena"]

        for i in range(20):
            sexo = np.random.choice(["M", "F"])
            nombre_base = np.random.choice(nombres_m if sexo == "M" else nombres_f)

            agente = Agente(
                f"{nombre_base}{i}",
                sexo,
                dia_nacimiento=np.random.randint(1, config.DIAS_POR_AÑO + 1),
                edad=18,
            )
            agente.ubicacion = (0, 0)
            sim.agentes.append(agente)

        self.inicializar_mercado_inicial()

    def inicializar_mercado_inicial(self):
        """Crear ofertas iniciales simples para probar la interfaz."""
        sim = self.simulador
        logger.debug("\n=== INICIALIZANDO MERCADO DE PRUEBA ===")

        productos = ["manzana", "pan", "madera", "carne", "piedra"]
        # Inventario base del jugador para poder probar venta desde el primer arranque.
        sim.agente_jugador.inventario["madera"] = max(sim.agente_jugador.inventario.get("madera", 0), 6)
        sim.agente_jugador.inventario["carne"] = sim.agente_jugador.inventario.get("carne", 0) + 3
        sim.agente_jugador.inventario["fruta"] = sim.agente_jugador.inventario.get("fruta", 0) + 4

        for i in range(5):
            agentes_npc = [a for a in sim.agentes if a != sim.agente_jugador]
            if not agentes_npc:
                break

            agente = np.random.choice(agentes_npc)
            producto = np.random.choice(productos)
            cantidad = np.random.randint(1, 6)
            precio = np.random.randint(5, 30)

            sim.economia.publicar_oferta_venta(agente.id, producto, cantidad, precio, 1.0)

            logger.debug(
                f"  Oferta {i + 1}: {agente.nombre} vende {cantidad} {producto} a {precio} monedas"
            )

        # También generar demandas de compra para probar el flujo de venta.
        for i in range(5):
            agentes_npc = [a for a in sim.agentes if a != sim.agente_jugador]
            if not agentes_npc:
                break
            agente = np.random.choice(agentes_npc)
            producto = np.random.choice(productos)
            cantidad = np.random.randint(1, 6)
            precio_maximo = np.random.randint(6, 35)
            sim.economia.publicar_oferta_compra(agente.id, producto, cantidad, precio_maximo)
            logger.debug(
                f"  Demanda {i + 1}: {agente.nombre} compra {cantidad} {producto} hasta {precio_maximo} monedas"
            )

        logger.debug("=== MERCADO INICIALIZADO ===\n")
