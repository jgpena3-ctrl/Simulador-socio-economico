from agentes.agente import Agente
from agentes.ai_agentes import AIAgentes
#from agentes.agente_jugador import AgenteJugador
from menuContestual import MenuContextual
from menu_inventario import MenuInventario
from mundo.camara import Camara
from mundo.mapa_hexagonal import MapaHexagonal
from ui.menu_mercado import MenuMercado
from ui.interfaz import InterfazSimulador
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
        """Ejecutar un tick de 30 minutos cuando hay actividad - LIMPIO"""
        if self.pausado:
            return

        self.tick += 1
        self.tiempo_transcurrido += 30
        nuevo_dia = self.tiempo(config.TIEMPO_TICK)

        print(f"\n=== TICK {self.tick} ({self.hora:02d}:{self.minutos:02d}) ===")

        # 1. Procesar movimiento del jugador (si hay)
        if self.moviendo_agente:
            self._avanzar_paso_movimiento()

        # 2. Actualizar mundo (solo cada día completo)
        if self.tick % 48 == 0:
            self.mapa.actualizar_ecosistema()
            print("  Ecosistema actualizado")

        # 3. Actualizar cada agente
        for agente in self.agentes[:]:
            if not agente.vivo:
                self.agentes.remove(agente)
                if agente in self.agentes_controlables:
                    self.agentes_controlables.remove(agente)
                continue

            # Actualizar fisiología
            if nuevo_dia:
                nuevo_anno = agente.dia_nacimiento == self.dia
            else:
                nuevo_anno = False

            agente.fisiologia.hora = self.hora
            agente.fisiologia.actualizar_tick_30min(nuevo_dia, nuevo_anno)

            # Procesar actividades del agente
            self._procesar_actividad_agente(agente)

            # Tomar decisiones de IA (solo para NPCs)
            if not agente.controlado_por_jugador:
                self._decision_ia(agente)

        print(f"  Tick completado")

    def _decision_ia(self, agente):
        """Delega la IA de NPCs al módulo de IA de agentes."""
        return self.ai_agentes.decidir(agente)

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
        """Dibujar todo usando la cámara"""
        self.pantalla.fill((25, 25, 35))

        # Dibujar hexágonos visibles
        for (q, r), hexagono in self.mapa.hexagonos.items():
            # Convertir coordenadas hexagonales a pixel del mundo
            x_mundo, y_mundo = axial_to_pixel(q, r, self.hex_size, self.hex_flat)

            # Convertir a pantalla usando la cámara
            x_pant, y_pant = self.camara.mundo_a_pantalla(x_mundo, y_mundo)

            # Solo dibujar si está visible (optimización)
            if self._esta_en_pantalla(x_pant, y_pant):
                vertices = get_hex_corners(x_pant, y_pant,
                                         self.hex_size * self.camara.escala,
                                         self.hex_flat)
                color = self._color_para_hex(hexagono)
                pygame.draw.polygon(self.pantalla, color, vertices, 0)
                pygame.draw.polygon(self.pantalla, (0,0,0), vertices, 1)

        # Dibujar ruta
        if self.moviendo_agente and self.ruta_actual:
            self._dibujar_ruta()

        # Dibujar agentes
        for agente in self.agentes:
            if agente.ubicacion in self.mapa.hexagonos:
                q, r = agente.ubicacion
                x_mundo, y_mundo = axial_to_pixel(q, r, self.hex_size, self.hex_flat)
                x_pant, y_pant = self.camara.mundo_a_pantalla(x_mundo, y_mundo)

                color = (0, 200, 255) if agente.controlado_por_jugador else (255, 100, 100)
                radio = max(3, (self.hex_size * self.camara.escala) // 3)
                pygame.draw.circle(self.pantalla, color, (int(x_pant), int(y_pant)), radio)

                # Nombre en zoom cercano
                if self.camara.escala > 0.8 and agente.controlado_por_jugador:
                    font = pygame.font.SysFont(None, int(20 * self.camara.escala))
                    nombre_surf = font.render(agente.nombre, True, (255, 255, 255))
                    self.pantalla.blit(nombre_surf, (x_pant - 40, y_pant - radio - 20))

        # Dibujar UI
        self._dibujar_ui()

        # Dibujar menú (siempre encima)
        self.menu.dibujar(self.pantalla)
        if self.menu_inventario.visible:
            self.menu_inventario.dibujar(self.pantalla)

        if self.menu_mercado.visible:
            self.menu_mercado.dibujar(self.pantalla)

        pygame.display.flip()

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
        """Dibujar ruta usando la cámara"""
        if not self.ruta_actual or not self.agente_jugador:
            return

        puntos = []

        # Empezar desde la posición actual
        q_actual, r_actual = self.agente_jugador.ubicacion
        x_mundo, y_mundo = axial_to_pixel(q_actual, r_actual, self.hex_size, self.hex_flat)
        x_pant, y_pant = self.camara.mundo_a_pantalla(x_mundo, y_mundo)
        puntos.append((x_pant, y_pant))

        # Añadir todos los puntos de la ruta
        for paso in self.ruta_actual:
            q, r = paso
            x_mundo, y_mundo = axial_to_pixel(q, r, self.hex_size, self.hex_flat)
            x_pant, y_pant = self.camara.mundo_a_pantalla(x_mundo, y_mundo)
            puntos.append((x_pant, y_pant))

        # Dibujar línea
        if len(puntos) >= 2:
            pygame.draw.lines(self.pantalla, (255, 255, 0), False, puntos,
                             max(2, int(3 * self.camara.escala)))

        # Dibujar puntos en cada paso (excepto el primero)
        for punto in puntos[1:]:
            radio = max(3, int(6 * self.camara.escala))
            pygame.draw.circle(self.pantalla, (255, 200, 0),
                             (int(punto[0]), int(punto[1])), radio)

    def tiempo(self, tick):
        nuevo_dia = False
        self.minutos += tick
        if self.minutos >= 60:
            self.hora += 1
            self.minutos -= 60
            if self.hora == 24:
                self.dia += 1
                self.hora = 0
                nuevo_dia = True
                if self.dia > config.DIAS_POR_AÑO:
                    self.anno += 1
                    self.dia = 1
        return nuevo_dia

    def ejecutar(self):
        """Bucle principal con movimiento de cámara"""
        reloj = pygame.time.Clock()

        while self.ejecutando:
            # Manejar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                elif evento.type == pygame.KEYDOWN:
                    self._manejar_teclas(evento.key, True)
                elif evento.type == pygame.KEYUP:
                    self._manejar_teclas(evento.key, False)
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    self._manejar_clic_mouse(evento)
                elif evento.type == pygame.MOUSEWHEEL:  # Rueda del mouse
                    if evento.y > 0:
                        self.camara.zoom_in()
                    elif evento.y < 0:
                        self.camara.zoom_out()

            # Actualizar movimiento de cámara
            self._actualizar_movimiento_camara()

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
        """Verificar si hay alguna acción que consuma tiempo"""
        return (self.moviendo_agente or
                self.agente_jugador.actividad_actual not in [None, "descansando"])

    def _manejar_teclas(self, tecla, presionada=True):
            """Manejar teclas presionadas o liberadas"""
            if tecla in self.teclas_presionadas:
                self.teclas_presionadas[tecla] = presionada

            # Si el menú de inventario está abierto, solo él recibe teclas
            if self.menu_inventario.visible:
                self.menu_inventario.procesar_tecla(tecla)
                return

            # Teclas de acción (solo cuando se presionan)
            if presionada:
                if tecla == pygame.K_p:
                    self.pausado = not self.pausado
                    print(f"Juego {'pausado' if self.pausado else 'reanudado'}")

                elif tecla == pygame.K_SPACE and self.pausado:
                    self.ejecutar_tick()
                    print("Tick manual ejecutado")

                elif tecla == pygame.K_c and self.agente_jugador:
                    self.agente_jugador.consumir()
                    print(f"{self.agente_jugador.nombre} comió")

                elif tecla == pygame.K_f:  # Alternar seguir jugador
                    self.seguir_jugador = not self.seguir_jugador
                    print(f"Seguir jugador: {'ON' if self.seguir_jugador else 'OFF'}")

                elif tecla == pygame.K_z:  # Zoom in
                    self.camara.zoom_in()
                    print(f"Zoom: {self.camara.escala:.1f}x")

                elif tecla == pygame.K_x:  # Zoom out
                    self.camara.zoom_out()
                    print(f"Zoom: {self.camara.escala:.1f}x")

                elif tecla == pygame.K_r:  # Reset zoom
                    self.camara.escala = 1.0
                    print("Zoom reseteado")

                elif tecla == pygame.K_HOME:  # Centrar en jugador
                    if self.agente_jugador:
                        q, r = self.agente_jugador.ubicacion
                        self.camara.centrar_en(q * 1.5, r * math.sqrt(3))
                        print("Centrado en jugador")

                elif tecla == pygame.K_ESCAPE:
                    self.ejecutando = False

    def _manejar_clic_mouse(self, evento):
        """Manejo de clics con cámara"""
        if evento.button == 1:  # Cli5c izquierdo
            # Primero verificar si se hizo clic en el menú
            if self.menu.procesar_clic(evento.pos):
                return

            # Convertir coordenadas de pantalla a mundo
            x_mundo, y_mundo = self.camara.pantalla_a_mundo(*evento.pos)

            # Obtener hexágono clicado
            q_float, r_float = pixel_to_axial(x_mundo, y_mundo,
                                            self.hex_size, self.hex_flat)
            q_round, r_round = axial_round(q_float, r_float)

            casilla = (q_round, r_round)

            # Verificar si es una casilla válida
            if casilla in self.mapa.hexagonos:
                print(f"\nCasilla seleccionada: {casilla}")

                # Mostrar menú contextual
                self.menu.mostrar(evento.pos, casilla)

                # Mostrar información
                self._mostrar_info_casilla(casilla)
            else:
                print(f"Casilla {casilla} fuera del mapa")
                self.menu.ocultar()

        elif evento.button == 3:  # Clic derecho
            print("Clic derecho: Cancelar")
            self.menu.ocultar()

            if self.moviendo_agente:
                print("Movimiento cancelado")
                self.moviendo_agente = False
                self.ruta_actual = []
                if self.agente_jugador:
                    self.agente_jugador.actividad_actual = None

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
        """
        Calcular ruta en línea recta usando algoritmo de Bresenham para hexágonos.
        Retorna lista de hexágonos desde inicio (exclusivo) hasta destino (inclusivo).
        """
        if inicio == destino:
            return []

        # Algoritmo de línea recta axial (hexagonal)
        q1, r1 = inicio
        q2, r2 = destino

        # Calcular distancia
        distancia = self._distancia_hex(inicio, destino)

        # Si la distancia es 1, ruta directa
        if distancia == 1:
            return [destino]

        # Interpolación lineal en coordenadas axiales
        ruta = []

        # Para cada paso intermedio
        for i in range(1, distancia + 1):
            t = i / distancia

            # Interpolar en float
            q_float = q1 * (1 - t) + q2 * t
            r_float = r1 * (1 - t) + r2 * t

            # Redondear al hexágono más cercano
            hex_redondeado = self._axial_round(q_float, r_float)

            # No añadir si es el mismo que el anterior
            if not ruta or hex_redondeado != ruta[-1]:
                ruta.append(hex_redondeado)

        return ruta

    def _distancia_hex(self, hex1, hex2):
        """Distancia hexagonal entre dos casillas"""
        return hex_distance(hex1, hex2)

    def _actualizar_movimiento_camara(self):
        """Actualizar movimiento de cámara basado en teclas presionadas"""
        if not any(self.teclas_presionadas.values()):
            return

        # Movimiento con WASD
        dx, dy = 0, 0

        if self.teclas_presionadas[pygame.K_w] or self.teclas_presionadas[pygame.K_UP]:
            dy -= 1
        if self.teclas_presionadas[pygame.K_s] or self.teclas_presionadas[pygame.K_DOWN]:
            dy += 1
        if self.teclas_presionadas[pygame.K_a] or self.teclas_presionadas[pygame.K_LEFT]:
            dx -= 1
        if self.teclas_presionadas[pygame.K_d] or self.teclas_presionadas[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 or dy != 0:
            self.camara.mover(dx, dy)
            self.seguir_jugador = False

    def _axial_round(self, q, r):
        """Redondear coordenadas axiales flotantes a hexágono más cercano"""
        # Convertir a cúbicas
        x = q
        z = r
        y = -x - z

        # Redondear
        rx = round(x)
        ry = round(y)
        rz = round(z)

        # Corrección de redondeo
        x_diff = abs(rx - x)
        y_diff = abs(ry - y)
        z_diff = abs(rz - z)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return (int(rx), int(rz))

    def mover_agente_a(self, agente, destino):
        """Iniciar movimiento a una casilla destino"""
        print('por mover_agente_a')
        inicio = agente.ubicacion

        if inicio == destino:
            print(f"{agente.nombre} ya está en {destino}")
            return False

        # Verificar que el destino está en el mapa
        if destino not in self.mapa.hexagonos:
            print(f"Destino {destino} no está en el mapa")
            return False

        # Calcular ruta (usa la versión que prefieras)
        self.ruta_actual = self._calcular_ruta(inicio, destino)  # Bresenham
        # self.ruta_actual = self._calcular_ruta_simple(inicio, destino)  # Simple

        if not self.ruta_actual:
            print(f"No se pudo calcular ruta de {inicio} a {destino}")
            return False

        print(f"{agente.nombre} se mueve a {destino} ({len(self.ruta_actual)} pasos)")

        # Configurar movimiento
        self.moviendo_agente = True
        agente.actividad_actual = "moviendose"

        # NO mover inmediatamente - esperar al primer tick
        print(f"Movimiento iniciado. Primer paso en el próximo tick.")

        return True

    def _avanzar_paso_movimiento(self):
        """Mover UN paso por tick"""
        if not self.ruta_actual or not self.moviendo_agente:
            return False

        agente = self.agente_jugador
        if not agente:
            return False

        # Tomar el primer paso de la ruta
        siguiente = self.ruta_actual.pop(0)

        # Verificar validez
        if siguiente not in self.mapa.hexagonos:
            print(f"Error: Paso inválido {siguiente}")
            self._finalizar_movimiento()
            return False

        # Actualizar ubicación
        ubicacion_anterior = agente.ubicacion
        agente.ubicacion = siguiente

        # Consumir recursos (por paso)
        agente.fisiologia.cansancio += 2
        #agente.fisiologia.combustible = max(0, agente.fisiologia.combustible-0.017)
        agente.fisiologia.energia = max(0, agente.fisiologia.energia - 1)

        print(f"  {agente.nombre}: {ubicacion_anterior} → {siguiente}")

        # Verificar si llegó
        if not self.ruta_actual:
            self._finalizar_movimiento()
            return True  # Movimiento completado

        return False  # Todavía en movimiento

    def _finalizar_movimiento(self):
        """Finalizar movimiento correctamente"""
        agente = self.agente_jugador
        if agente:
            destino = agente.ubicacion
            print(f"{agente.nombre} llegó a {destino}")

            # Verificar si llegó a un lugar especial
            hex_destino = self.mapa.hexagonos.get(destino)
            if hex_destino:
                if destino == (0, 0):
                    print("  (Estás en el área central)")
                elif hex_destino.arboles > 0:
                    print("  (Hay árboles aquí para talar)")
                elif any(count > 0 for count in hex_destino.animales.values()):
                    print("  (Hay animales aquí para cazar)")

        # Resetear estado de movimiento
        self.moviendo_agente = False
        self.ruta_actual = []

        if agente:
            agente.actividad_actual = None

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
