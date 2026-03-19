import logging
import math
import pygame
from utils.hex_math import pixel_to_axial, axial_round

logger = logging.getLogger(__name__)


class InputController:
    """Maneja eventos de teclado/ratón y atajos de interacción."""

    def __init__(self, simulador):
        self.simulador = simulador

    def procesar_evento(self, evento):
        sim = self.simulador
        if evento.type == pygame.QUIT:
            sim.ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            self.manejar_teclas(evento.key, True, getattr(evento, "unicode", ""))
        elif evento.type == pygame.KEYUP:
            self.manejar_teclas(evento.key, False)
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            self.manejar_clic_mouse(evento)
        elif evento.type == pygame.MOUSEWHEEL:
            if evento.y > 0:
                sim.camara.zoom_in()
            elif evento.y < 0:
                sim.camara.zoom_out()

    def manejar_teclas(self, tecla, presionada=True, texto=""):
        sim = self.simulador

        if tecla in sim.teclas_presionadas:
            sim.teclas_presionadas[tecla] = presionada

        if sim.menu_mercado.visible and sim.menu_mercado.procesar_eventos_teclado(tecla, texto):
            return

        if sim.menu_inventario.visible:
            sim.menu_inventario.procesar_tecla(tecla)
            return

        if not presionada:
            return

        if tecla == pygame.K_p:
            sim.pausado = not sim.pausado
            logger.debug(f"Juego {'pausado' if sim.pausado else 'reanudado'}")
        elif tecla == pygame.K_SPACE and sim.pausado:
            sim.ejecutar_tick()
            logger.debug("Tick manual ejecutado")
        elif tecla == pygame.K_c and sim.agente_jugador:
            sim.agente_jugador.consumir()
            logger.debug(f"{sim.agente_jugador.nombre} comió")
        elif tecla == pygame.K_f:
            sim.seguir_jugador = not sim.seguir_jugador
            logger.debug(f"Seguir jugador: {'ON' if sim.seguir_jugador else 'OFF'}")
        elif tecla == pygame.K_z:
            sim.camara.zoom_in()
            logger.debug(f"Zoom: {sim.camara.escala:.1f}x")
        elif tecla == pygame.K_x:
            sim.camara.zoom_out()
            logger.debug(f"Zoom: {sim.camara.escala:.1f}x")
        elif tecla == pygame.K_r:
            sim.camara.escala = 1.0
            logger.debug("Zoom reseteado")
        elif tecla == pygame.K_HOME and sim.agente_jugador:
            q, r = sim.agente_jugador.ubicacion
            sim.camara.centrar_en(q * 1.5, r * math.sqrt(3))
            logger.debug("Centrado en jugador")
        elif tecla == pygame.K_ESCAPE:
            if sim.menu.visible:
                sim.menu.ocultar()
            logger.debug("ESC: cerrar menús contextuales (no cierra el juego)")

    def manejar_clic_mouse(self, evento):
        sim = self.simulador
        if evento.button == 1:
            if sim.menu_mercado.visible and sim.menu_mercado.procesar_clic(evento.pos):
                return

            if sim.menu_inventario.visible and sim.menu_inventario.procesar_clic(evento.pos):
                return

            if sim.menu.procesar_clic(evento.pos):
                return

            x_mundo, y_mundo = sim.camara.pantalla_a_mundo(*evento.pos)
            q_float, r_float = pixel_to_axial(x_mundo, y_mundo, sim.hex_size, sim.hex_flat)
            q_round, r_round = axial_round(q_float, r_float)
            casilla = (q_round, r_round)

            if casilla in sim.mapa.hexagonos:
                logger.debug(f"\nCasilla seleccionada: {casilla}")
                sim.menu.mostrar(evento.pos, casilla)
                sim._mostrar_info_casilla(casilla)
            else:
                logger.debug(f"Casilla {casilla} fuera del mapa")
                sim.menu.ocultar()

        elif evento.button == 3:
            logger.debug("Clic derecho: Cancelar")
            sim.menu.ocultar()

            if sim.moviendo_agente:
                logger.debug("Movimiento cancelado")
                sim.moviendo_agente = False
                sim.ruta_actual = []
                if sim.agente_jugador:
                    sim.agente_jugador.actividad_actual = None
