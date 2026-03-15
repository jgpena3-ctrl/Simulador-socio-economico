import logging
import config

logger = logging.getLogger(__name__)


class TickSystem:
    """Coordina el avance del tiempo y la actualización de simulación por tick."""

    def __init__(self, simulador):
        self.simulador = simulador

    def ejecutar_tick(self):
        sim = self.simulador
        if sim.pausado:
            return

        sim.tick += 1
        sim.tiempo_transcurrido += 30
        nuevo_dia = self.tiempo(config.TIEMPO_TICK)

        logger.debug(f"\n=== TICK {sim.tick} ({sim.hora:02d}:{sim.minutos:02d}) ===")

        if sim.moviendo_agente:
            sim.movement.avanzar_paso_movimiento()

        if sim.tick % 48 == 0:
            sim.mapa.actualizar_ecosistema()
            logger.debug("  Ecosistema actualizado")

        for agente in sim.agentes[:]:
            if not agente.vivo:
                sim.agentes.remove(agente)
                if agente in sim.agentes_controlables:
                    sim.agentes_controlables.remove(agente)
                continue

            nuevo_anno = agente.dia_nacimiento == sim.dia if nuevo_dia else False

            agente.fisiologia.hora = sim.hora
            agente.fisiologia.actualizar_tick_30min(nuevo_dia, nuevo_anno)

            sim._procesar_actividad_agente(agente)

            if not agente.controlado_por_jugador:
                sim._decision_ia(agente)

        logger.debug("  Tick completado")

    def tiempo(self, tick):
        sim = self.simulador
        nuevo_dia = False
        sim.minutos += tick
        if sim.minutos >= 60:
            sim.hora += 1
            sim.minutos -= 60
            if sim.hora == 24:
                sim.dia += 1
                sim.hora = 0
                nuevo_dia = True
                if sim.dia > config.DIAS_POR_AÑO:
                    sim.anno += 1
                    sim.dia = 1
        return nuevo_dia

    def hay_accion_en_progreso(self):
        sim = self.simulador
        return sim.moviendo_agente or sim.agente_jugador.actividad_actual not in [None, "descansando"]
