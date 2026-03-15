from agentes.agente import Agente
from agentes.ai_agentes import AIAgentes
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
from render.world_renderer import WorldRenderer
from utils.hex_math import pixel_to_axial, axial_round, axial_to_pixel, get_hex_corners, hex_distance
from sistema.economia import SistemaEconomico
from sistema.acciones import Acciones
import config
import math
import numpy as np
import os
import pygame
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Simulador:

    def __init__(self):
        pygame.init()
        self.ancho, self.alto = 1200, 700
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Simulador Socio-Económico Multiagente")

        # Variable de control principal
        self.ejecutando = True  # <-- AÑADIR ESTO

        # Sistemas
        self.mapa = MapaHexagonal(radio=16)
        self.economia = SistemaEconomico(self)
        self.acciones = Acciones(self)
        self.menu_mercado = MenuMercado(self)
        self.ai_agentes = AIAgentes(self)
        self.interfaz = InterfazSimulador(self)

        # Capas por responsabilidad
        self.tick_system = TickSystem(self)
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
        self.ejecutando = True
        self.VELOCIDAD_MOVIMIENTO = 1

        # Sistema hexagonal
        self.hex_size = config.HEX_SIZE
        self.hex_flat = config.HEX_FLAT

        # Sistema de menú
        self.menu = MenuContextual(self)
        self.menu_inventario = MenuInventario(self)

        # UI
        self.font = pygame.font.SysFont(None, 24)

        self._inicializar_agentes()

    def _inicializar_agentes(self):
        """Crear agentes iniciales"""
        # Crear agente del jugador
        self.agente_jugador = Agente("Jugador", "M", dia_nacimiento=np.random.randint(1, config.DIAS_POR_AÑO + 1), edad=18)
        self.agente_jugador.controlado_por_jugador = True
        self.agente_jugador.ubicacion = (0, 0)  # Centro del mapa
        self.agentes.append(self.agente_jugador)
        self.agentes_controlables.append(self.agente_jugador)

        # Crear 20 agentes IA iniciales
        nombres_m = ["Carlos", "Juan", "Pedro", "Luis", "Miguel"]
        nombres_f = ["Ana", "Maria", "Laura", "Sofia", "Elena"]

        for i in range(20):
            sexo = np.random.choice(["M", "F"])
            if sexo == "M":
                nombre = np.random.choice(nombres_m) + str(i)
            else:
                nombre = np.random.choice(nombres_f) + str(i)

            agente = Agente(nombre, sexo, dia_nacimiento=np.random.randint(1, config.DIAS_POR_AÑO + 1), edad=18)
            agente.ubicacion = (0, 0)
            self.agentes.append(agente)
        self._inicializar_mercado_inicial()

    def _inicializar_mercado_inicial(self):
        """Crea ofertas iniciales simples para probar la interfaz"""
        print("\n=== INICIALIZANDO MERCADO DE PRUEBA ===")

        # Productos de ejemplo
        productos = ["manzana", "pan", "madera", "carne", "piedra"]

        # Crear 5 ofertas aleatorias
        for i in range(5):
            # Seleccionar agente aleatorio (que no sea el jugador)
            agentes_npc = [a for a in self.agentes if a != self.agente_jugador]
            if not agentes_npc:
                break

            agente = np.random.choice(agentes_npc)
            producto = np.random.choice(productos)
            cantidad = np.random.randint(1, 6)
            precio = np.random.randint(5, 30)

            # Publicar oferta directamente en el sistema económico
            oferta_id = self.economia.publicar_oferta_venta(
                agente.id, producto, cantidad, precio, 1.0
            )

            print(f"  Oferta {i+1}: {agente.nombre} vende {cantidad} {producto} a {precio} monedas")

        print("=== MERCADO INICIALIZADO ===\n")

    def ejecutar_tick(self):
        """Ejecutar tick delegando al sistema de tiempo/simulación."""
        return self.tick_system.ejecutar_tick()

    def _decision_ia(self, agente):
        """Delega la IA de NPCs al módulo de IA de agentes."""
        return self.ai_agentes.decidir(agente)

<<<<<<< HEAD
=======
    def _accion_dormir(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_dormir(agente)

    def _accion_comer(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_comer(agente)

    def _accion_trabajar(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_trabajar(agente)

    def _accion_recolectar(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_recolectar(agente)

    def _accion_socializar(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_socializar(agente)

    def _accion_descansar(self, agente):
        """Delega acción al sistema de acciones."""
        return self.acciones._accion_descansar(agente)

>>>>>>> 0ff225f (Refactoriza IA, acciones e interfaz fuera de main)
    def _procesar_reproduccion(self):
        """Procesar reproducción entre agentes"""
        # Buscar parejas potenciales
        for agente1 in self.agentes:
            if agente1.pareja is not None:
                continue

            for agente2 in self.agentes:
                if agente2 == agente1 or agente2.pareja is not None:
                    continue

                # Verificar compatibilidad y proximidad
                if (agente1.puede_procrear(agente2) and
                    self._distancia(agente1.ubicacion, agente2.ubicacion) < 2):

                    # Probabilidad basada en afinidad
                    afinidad = agente1.afinidades.get(agente2.id, 50)
                    prob = min(0.1, afinidad / 1000)  # Baja probabilidad

                    if np.random.random() < prob:
                        hijo = agente1.procrear(agente2)
                        if hijo:
                            self.agentes.append(hijo)
                            print(f"Nacimiento: {hijo.nombre}")

                            # Si es hijo del jugador, añadir a controlables a los 18
                            if (agente1.controlado_por_jugador or
                                agente2.controlado_por_jugador):
                                # Se podrá controlar cuando cumpla 18
                                pass

    def _distancia(self, pos1, pos2):
        """Distancia entre dos posiciones hexagonales"""
        return hex_distance(pos1, pos2)

    def dibujar(self):
        """Dibujar todo delegando en el renderizador del mundo."""
        return self.renderer.dibujar()

    def _color_para_hex(self, hexagono):
        """Delega colores de render al módulo de interfaz."""
        return self.interfaz.color_para_hex(hexagono)

    def _dibujar_debug_clics(self):
        """Dibujar información de debug de clics"""
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convertir a coordenadas del mundo
        world_x = mouse_x - self.ancho // 2
        world_y = mouse_y - self.alto // 2

        # Obtener hexágono bajo el mouse
        q_float, r_float = pixel_to_axial(world_x, world_y,
                                        self.hex_size, self.hex_flat)
        q_round, r_round = axial_round(q_float, r_float)

        # Información de debug
        font = pygame.font.SysFont(None, 20)

        textos = [
            f"Mouse: ({mouse_x}, {mouse_y})",
            f"Mundo: ({world_x:.0f}, {world_y:.0f})",
            f"Hex float: ({q_float:.2f}, {r_float:.2f})",
            f"Hex redondeado: ({q_round}, {r_round})"
        ]

        y = 30
        for texto in textos:
            superficie = font.render(texto, True, (255, 255, 0))
            self.pantalla.blit(superficie, (self.ancho - 350, y))
            y += 25

        # Cruz en el mouse
        pygame.draw.line(self.pantalla, (255, 255, 0),
                        (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 2)
        pygame.draw.line(self.pantalla, (255, 255, 0),
                        (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 2)

        # Dibujar hexágono bajo el mouse
        if (q_round, r_round) in self.mapa.hexagonos:
            x_hex, y_hex = axial_to_pixel(q_round, r_round, self.hex_size, self.hex_flat)
            x_pantalla = self.ancho // 2 + x_hex
            y_pantalla = self.alto // 2 + y_hex

            vertices = get_hex_corners(x_pantalla, y_pantalla,
                                     self.hex_size, self.hex_flat)
            pygame.draw.polygon(self.pantalla, (255, 255, 0), vertices, 3)

    def _esta_en_pantalla(self, x, y, margen=100):
        """Verificar si una posición está visible"""
        return (-margen <= x <= self.ancho + margen and
                -margen <= y <= self.alto + margen)

    def _hex_a_pixel(self, q, r, tamaño):
        """Convertir coordenadas hexagonales a píxeles"""
        x = tamaño * (3/2 * q)
        y = tamaño * (3**0.5/2 * q + 3**0.5 * r)
        return x, y

    def _calcular_vertices_hex(self, centro_x, centro_y, tamaño):
        """Calcular los 6 vértices de un hexágono"""
        vertices = []
        for i in range(6):
            angulo = 2 * math.pi / 6 * i
            x = centro_x + tamaño * math.cos(angulo)
            y = centro_y + tamaño * math.sin(angulo)
            vertices.append((x, y))
        return vertices

    def _hex_en_pantalla(self, x, y, tamaño):
        """Verificar si un hexágono está visible en pantalla"""
        margen = tamaño * 2
        return (-margen <= x <= self.ancho + margen and
                -margen <= y <= self.alto + margen)

    def _color_por_tipo_hex(self, hexagono):
        """Determinar color del hexágono"""
        # Área central (0,0)
        if hexagono.q == 0 and hexagono.r == 0:
            return (100, 100, 200)  # Azul para centro

        # Casillas adyacentes al centro
        distancia = abs(hexagono.q) + abs(hexagono.r) + abs(-hexagono.q - hexagono.r)
        if distancia <= 2:
            return (150, 10, 10)  # Amarillo verdoso para zona económica

        # Áreas con recursos
        if hexagono.arboles > 5:
            verde = min(200, 50 + hexagono.arboles * 10)
            return (50, verde, 50)

        # Tierra normal
        return (100, 80, 60)

    def _dibujar_debug(self):
        """Dibujar información de debug"""
        # Mostrar posición del mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hex_mouse = self._pixel_a_hex_preciso(mouse_x, mouse_y)

        font = pygame.font.SysFont(None, 20)

        # Información del mouse
        texto_mouse = f"Mouse: ({mouse_x}, {mouse_y}) -> Hex: {hex_mouse}"
        superficie = font.render(texto_mouse, True, (255, 255, 0))
        self.pantalla.blit(superficie, (self.ancho - 350, 30))

        # Cruz en el mouse para referencia
        pygame.draw.line(self.pantalla, (255, 255, 0),
                        (mouse_x - 10, mouse_y), (mouse_x + 10, mouse_y), 1)
        pygame.draw.line(self.pantalla, (255, 255, 0),
                        (mouse_x, mouse_y - 10), (mouse_x, mouse_y + 10), 1)

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

        print(f"=== INFORMACIÓN DE CASILLA {casilla} ===")

        # Información general
        if casilla == (0, 0):
            print("  ÁREA CENTRAL - Viviendas")
        elif abs(casilla[0]) + abs(casilla[1]) + abs(-casilla[0] - casilla[1]) <= 2:
            print("  ZONA ECONÓMICA - Actividades")
        else:
            print("  ZONA SILVESTRE - Recursos naturales")

        # Recursos
        if hex_info.arboles > 0:
            print(f"  Árboles: {hex_info.arboles}")
        if hex_info.arbustos > 0:
            print(f"  Arbustos: {hex_info.arbustos}")
        if hex_info.animales:
            for animal, cantidad in hex_info.animales.items():
                if cantidad > 0:
                    print(f"  {animal.capitalize()}: {cantidad}")

        # Estado
        if en_casilla:
            print("  (Tu agente está aquí)")
        elif self.agente_jugador:
            distancia = self._distancia_hex(self.agente_jugador.ubicacion, casilla)
            print(f"  Distancia: {distancia} pasos")
            print(f"  Tiempo estimado: {distancia * 30} minutos")

    def _pixel_a_hex_preciso(self, x_pixel, y_pixel):
        """
        Convertir coordenadas de píxel a coordenadas hexagonales precisas.
        Usa el sistema de coordenadas axiales.
        """
        tamaño = self.TAMANO_HEX
        centro_x, centro_y = self.ancho // 2, self.alto // 2

        # 1. Convertir a coordenadas relativas al centro del mapa
        x_rel = x_pixel - centro_x
        y_rel = y_pixel - centro_y

        # 2. Para una cámara estática (sin scroll/zoom por ahora)
        # Si tienes cámara, necesitarías ajustar con: x_rel -= self.camara.x * tamaño, etc.

        # 3. Convertir a coordenadas hexagonales usando coordenadas axiales
        # Fórmulas para hexágonos punto-arriba
        q = (x_rel * (3/2)) / tamaño
        r = ((-x_rel / 2) + (y_rel * (3**0.5) / 2)) / tamaño

        # 4. Convertir a coordenadas cúbicas y redondear
        return self._axial_a_hex_redondeado(q, r)

    def _axial_a_hex_redondeado(self, q, r):
        """
        Convertir coordenadas axiales (q, r) a hexágono redondeado
        usando coordenadas cúbicas.
        """
        # Convertir a coordenadas cúbicas
        x = q
        z = r
        y = -x - z

        # Redondear a hexágono más cercano
        rx = round(x)
        ry = round(y)
        rz = round(z)

        # Corrección de redondeo para coordenadas cúbicas
        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        # Retornar coordenadas axiales (q, r)
        return (int(rx), int(rz))

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
        """Procesar la actividad actual del agente"""
        if agente.actividad_actual and agente.actividad_restante > 0:
            agente.actividad_restante -= 1

            # Si la actividad terminó
            if agente.actividad_restante <= 0:
                self._finalizar_actividad(agente)

    def iniciar_actividad(self, agente, actividad, duracion_ticks=1, **kwargs):
        """Iniciar una actividad que consume tiempo"""
        if self.moviendo_agente:
            print(f"{agente.nombre} no puede iniciar '{actividad}' mientras se mueve")
            return False

        agente.actividad_actual = actividad
        agente.actividad_restante = duracion_ticks
        agente.actividad_destino = kwargs.get('destino', None)

        print(f"{agente.nombre} inicia '{actividad}' ({duracion_ticks} ticks)")
        return True

    def _finalizar_actividad(self, agente):
        """Finalizar la actividad actual"""
        actividad = agente.actividad_actual
        print(f"{agente.nombre} termina '{actividad}'")

        # Efectos según actividad
        if actividad == "comiendo":
            agente.fisiologia.hambre = max(0, agente.fisiologia.hambre - 30)
        elif actividad == "durmiendo":
            agente.fisiologia.cansancio = max(0, agente.fisiologia.cansancio - 50)

        # Resetear actividad
        agente.actividad_actual = None
        agente.actividad_restante = 0
        agente.actividad_destino = None

    def calibrar_clics(self):
        """Función rápida de calibración"""
        print("\n=== CALIBRACIÓN RÁPIDA ===")
        print("Haz clic en el CENTRO de varios hexágonos")
        print("Las coordenadas detectadas deberían coincidir")
        print("Presiona 'C' para terminar\n")

        calibrando = True
        while calibrando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                    calibrando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_c:
                        calibrando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        self._manejar_clic_mouse(evento)

            # Dibujar pantalla normal
            self.dibujar()

        print("=== FIN CALIBRACIÓN ===")

if __name__ == "__main__":
    simulador = Simulador()
    simulador.ejecutar()
