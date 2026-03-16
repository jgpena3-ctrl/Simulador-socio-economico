import logging
from agentes.ai_agentes import AIAgentes

logger = logging.getLogger(__name__)
#from agentes.agente_jugador import AgenteJugador
from menuContestual import MenuContextual
from menu_inventario import MenuInventario
from mundo.camara import Camara
from mundo.mapa_hexagonal import MapaHexagonal
from ui.menu_mercado import MenuMercado
from ui.interfaz import InterfazSimulador
from controllers.input_controller import InputController
from engine.movement import MovementSystem
from engine.tick_system import TickSystem
from engine.activity_system import ActivitySystem
from engine.bootstrap_system import BootstrapSystem
from render.world_renderer import WorldRenderer
from utils.hex_math import hex_distance
from utils.logging_config import setup_logging
from utils.random_config import setup_random_seed
from sistema.economia import SistemaEconomico
from sistema.acciones import Acciones
import config
import os
import pygame
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Simulador:

    def __init__(self):
        setup_logging()
        setup_random_seed()
        pygame.init()
        self.ancho, self.alto = 1200, 700
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Simulador Socio-Económico Multiagente")

        # Variable de control principal
        self.ejecutando = True

        # Sistemas
        self.mapa = MapaHexagonal(radio=16)
        self.economia = SistemaEconomico(self)
        self.acciones = Acciones(self)
        self.menu_mercado = MenuMercado(self)
        self.ai_agentes = AIAgentes(self)
        self.interfaz = InterfazSimulador(self)

        # Capas por responsabilidad
        self.tick_system = TickSystem(self)
        self.activity_system = ActivitySystem(self)
        self.bootstrap_system = BootstrapSystem(self)
        self.movement = MovementSystem(self)
        self.renderer = WorldRenderer(self)
        self.input_controller = InputController(self)

        # Agentes
        self.agentes = []
        self.agente_jugador = None
        self.agentes_controlables = []

        # Tiempo
        self.tick = 0
        self.tiempo_transcurrido = 0
        self.pausado = False
        self.minutos = 0
        self.hora = 0
        self.dia = 1
        self.anno = 0

        # Sistema de cámara
        self.camara = Camara(self.ancho, self.alto)
        self.seguir_jugador = False  # Seguir al jugador automáticamente (false momentaneo)

        # Estados de teclas para movimiento continuo
        self.teclas_presionadas = {
            pygame.K_w: False, pygame.K_s: False,
            pygame.K_a: False, pygame.K_d: False,
            pygame.K_UP: False, pygame.K_DOWN: False,
            pygame.K_LEFT: False, pygame.K_RIGHT: False
        }

        self.seguir_agente = True
        self.ruta_actual = []
        self.moviendo_agente = False

        # Configuración simple (REEMPLAZAR Configuracion())
        self.VELOCIDAD_MOVIMIENTO = 1

        # Sistema hexagonal
        self.hex_size = config.HEX_SIZE
        self.hex_flat = config.HEX_FLAT

        # Sistema de menú
        self.menu = MenuContextual(self)
        self.menu_inventario = MenuInventario(self)

        # UI
        self.font = pygame.font.SysFont(None, 24)

        self.bootstrap_system.inicializar_agentes()

    def _inicializar_agentes(self):
        """Compatibilidad: delega bootstrap de agentes."""
        return self.bootstrap_system.inicializar_agentes()

    def _inicializar_mercado_inicial(self):
        """Compatibilidad: delega bootstrap de mercado."""
        return self.bootstrap_system.inicializar_mercado_inicial()

    def ejecutar_tick(self):
        """Ejecutar tick delegando al sistema de tiempo/simulación."""
        return self.tick_system.ejecutar_tick()

    def _decision_ia(self, agente):
        """Delega la IA de NPCs al módulo de IA de agentes."""
        return self.ai_agentes.decidir(agente)

    def _distancia(self, pos1, pos2):
        """Distancia entre dos posiciones hexagonales."""
        return hex_distance(pos1, pos2)

    def dibujar(self):
        """Dibujar todo delegando en el renderizador del mundo."""
        return self.renderer.dibujar()

    def _color_para_hex(self, hexagono):
        """Delega colores de render al módulo de interfaz."""
        return self.interfaz.color_para_hex(hexagono)

    def _esta_en_pantalla(self, x, y, margen=100):
        """Verificar si una posición está visible"""
        return (-margen <= x <= self.ancho + margen and
                -margen <= y <= self.alto + margen)

    def _dibujar_ui(self):
        """Delega la UI al módulo de interfaz."""
        return self.interfaz.dibujar_ui()

    def _dibujar_ruta(self):
        """Compatibilidad: delega al sistema de movimiento."""
        return self.movement.dibujar_ruta()

    def tiempo(self, tick):
        return self.tick_system.tiempo(tick)

    def ejecutar(self):
        """Bucle principal con movimiento de cámara"""
        reloj = pygame.time.Clock()

        while self.ejecutando:
            # Manejar eventos
            for evento in pygame.event.get():
                self.input_controller.procesar_evento(evento)

            # Actualizar movimiento de cámara
            self.movement.actualizar_movimiento_camara()

            # Seguir al jugador si está activado
            if self.seguir_jugador and self.agente_jugador:
                self.camara.seguir_agente(self.agente_jugador)

            # Ejecutar lógica del juego
            if self._hay_accion_en_progreso():
                self.ejecutar_tick()

            # Dibujar
            self.dibujar()
            reloj.tick(60)  # 60 FPS para movimiento suave

    def _hay_accion_en_progreso(self):
        """Verificar si hay alguna acción que consuma tiempo."""
        return self.tick_system.hay_accion_en_progreso()

    def _manejar_teclas(self, tecla, presionada=True):
        """Compatibilidad: delega al controlador de entrada."""
        return self.input_controller.manejar_teclas(tecla, presionada)

    def _manejar_clic_mouse(self, evento):
        """Compatibilidad: delega al controlador de entrada."""
        return self.input_controller.manejar_clic_mouse(evento)

    def _mostrar_info_casilla(self, casilla):
        """Mostrar información de la casilla seleccionada"""
        hex_info = self.mapa.hexagonos.get(casilla)
        if not hex_info:
            return

        agente = self.agente_jugador
        en_casilla = (casilla == agente.ubicacion)

        logger.debug(f"=== INFORMACIÓN DE CASILLA {casilla} ===")

        # Información general
        if casilla == (0, 0):
            logger.debug("  ÁREA CENTRAL - Viviendas")
        elif abs(casilla[0]) + abs(casilla[1]) + abs(-casilla[0] - casilla[1]) <= 2:
            logger.debug("  ZONA ECONÓMICA - Actividades")
        else:
            logger.debug("  ZONA SILVESTRE - Recursos naturales")

        # Recursos
        if hex_info.arboles > 0:
            logger.debug(f"  Árboles: {hex_info.arboles}")
        if hex_info.arbustos > 0:
            logger.debug(f"  Arbustos: {hex_info.arbustos}")
        if hex_info.animales:
            for animal, cantidad in hex_info.animales.items():
                if cantidad > 0:
                    logger.debug(f"  {animal.capitalize()}: {cantidad}")

        # Estado
        if en_casilla:
            logger.debug("  (Tu agente está aquí)")
        elif self.agente_jugador:
            distancia = self._distancia_hex(self.agente_jugador.ubicacion, casilla)
            logger.debug(f"  Distancia: {distancia} pasos")
            logger.debug(f"  Tiempo estimado: {distancia * 30} minutos")

    def _calcular_ruta(self, inicio, destino):
        """Compatibilidad: delega el cálculo de ruta al sistema de movimiento."""
        return self.movement.calcular_ruta(inicio, destino)

    def _distancia_hex(self, hex1, hex2):
        """Distancia hexagonal entre dos casillas."""
        return self.movement.distancia_hex(hex1, hex2)

    def _actualizar_movimiento_camara(self):
        """Compatibilidad: delega al sistema de movimiento."""
        return self.movement.actualizar_movimiento_camara()

    def _axial_round(self, q, r):
        """Compatibilidad: delega redondeo axial al sistema de movimiento."""
        return self.movement.axial_round(q, r)

    def mover_agente_a(self, agente, destino):
        """Iniciar movimiento a una casilla destino."""
        return self.movement.mover_agente_a(agente, destino)

    def _avanzar_paso_movimiento(self):
        """Compatibilidad: delega avance de paso al sistema de movimiento."""
        return self.movement.avanzar_paso_movimiento()

    def _finalizar_movimiento(self):
        """Compatibilidad: delega finalización al sistema de movimiento."""
        return self.movement.finalizar_movimiento()

    def _procesar_actividad_agente(self, agente):
        """Compatibilidad: delega procesamiento de actividad."""
        return self.activity_system.procesar_actividad_agente(agente)

    def iniciar_actividad(self, agente, actividad, duracion_ticks=1, **kwargs):
        """Compatibilidad: delega inicio de actividad."""
        return self.activity_system.iniciar_actividad(agente, actividad, duracion_ticks, **kwargs)

    def _finalizar_actividad(self, agente):
        """Compatibilidad: delega finalización de actividad."""
        return self.activity_system.finalizar_actividad(agente)


if __name__ == "__main__":
    simulador = Simulador()
    simulador.ejecutar()
