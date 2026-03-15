import logging
import numpy as np
from agentes.agente import Personalidad

logger = logging.getLogger(__name__)


class AIAgentes:
    """Motor de decisiones para agentes no controlados por el jugador."""

    def __init__(self, simulador):
        self.sim = simulador

    def decidir(self, agente):
        """Toma de decisión por prioridades fisiológicas y personalidad."""
        if agente.fisiologia.necesita_dormir():
            self.sim.acciones._accion_dormir(agente)
            logger.debug(f"{agente.nombre} duerme (IA)")
            return

        if agente.fisiologia.necesita_comer():
            if agente.inventario.get("comida", 0) > 0:
                self.sim.acciones._accion_comer(agente)
                logger.debug(f"{agente.nombre} come (IA)")
            else:
                self.sim.acciones._accion_recolectar(agente)
                logger.debug(f"{agente.nombre} busca comida (IA)")
            return

        if agente.personalidad in [Personalidad.ESTJ, Personalidad.ENTJ]:
            self.sim.acciones._accion_trabajar(agente)
            logger.debug(f"{agente.nombre} trabaja (IA)")
            return

        if agente.personalidad in [Personalidad.ENFP, Personalidad.ESFP]:
            self.sim.acciones._accion_socializar(agente)
            logger.debug(f"{agente.nombre} socializa (IA)")
            return

        acciones = [
            self.sim.acciones._accion_recolectar,
            self.sim.acciones._accion_socializar,
            self.sim.acciones._accion_descansar,
        ]
        accion_elegida = np.random.choice(acciones)
        accion_elegida(agente)
        logger.debug(f"{agente.nombre} {accion_elegida.__name__} (IA aleatoria)")
