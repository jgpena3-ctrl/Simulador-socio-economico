import logging

logger = logging.getLogger(__name__)


class ActivitySystem:
    """Gestiona ciclo de vida de actividades de agentes."""

    def __init__(self, simulador):
        self.simulador = simulador

    def procesar_actividad_agente(self, agente):
        """Procesar la actividad actual del agente."""
        if agente.actividad_actual and agente.actividad_restante > 0:
            agente.actividad_restante -= 1

            if agente.actividad_restante <= 0:
                self.finalizar_actividad(agente)

    def iniciar_actividad(self, agente, actividad, duracion_ticks=1, **kwargs):
        """Iniciar una actividad que consume tiempo."""
        sim = self.simulador
        if sim.moviendo_agente:
            logger.debug(f"{agente.nombre} no puede iniciar '{actividad}' mientras se mueve")
            return False

        agente.actividad_actual = actividad
        agente.actividad_restante = duracion_ticks
        agente.actividad_destino = kwargs.get("destino", None)

        logger.debug(f"{agente.nombre} inicia '{actividad}' ({duracion_ticks} ticks)")
        return True

    def finalizar_actividad(self, agente):
        """Finalizar la actividad actual."""
        actividad = agente.actividad_actual
        logger.debug(f"{agente.nombre} termina '{actividad}'")

        agente.actividad_actual = None
        agente.actividad_restante = 0
        agente.actividad_destino = None
