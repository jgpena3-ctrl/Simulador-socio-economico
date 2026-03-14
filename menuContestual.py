import pygame
import math
import numpy as np
import config

def combinacion(n, r):
    return math.comb(n, r)

class MenuContextual:
    def __init__(self, simulador):
        self.simulador = simulador
        self.visible = False
        self.posicion = (0, 0)  # Posición en pantalla
        self.casilla = None  # Casilla a la que se refiere el menú
        self.opciones = []
        self.ancho_menu = 200
        self.alto_opcion = 30

    def mostrar(self, pos_pantalla, casilla):
        """Mostrar menú en una posición con opciones para la casilla"""
        self.posicion = pos_pantalla
        self.casilla = casilla
        self.visible = True

        # Generar opciones según la casilla
        self._generar_opciones(casilla)

    def ocultar(self):
        """Ocultar el menú"""
        self.visible = False
        self.casilla = None
        self.opciones = []

    def _generar_opciones(self, casilla):
        """Generar opciones del menú según la casilla"""
        self.opciones = []
        agente = self.simulador.agente_jugador

        if not agente:
            return

        # ¿Estamos en esta casilla?
        en_casilla = (casilla == agente.ubicacion)

        if not en_casilla:
            # Opciones para casillas ajenas
            self.opciones.append(("Ir a esta casilla", self._accion_ir_a))

        else:
            # Opciones para casilla actual
            hex_info = self.simulador.mapa.hexagonos.get(casilla)
            if hex_info:
                # Acciones basadas en recursos de la casilla
                if hex_info.arboles > 0:
                    self.opciones.append(("Talar árbol", self.simulador.acciones._accion_talar))
                if hex_info.arbustos > 0:
                    self.opciones.append(("Recolectar frutos", self.simulador.acciones._accion_recolectar))
                self.opciones.append(("Cazar animal", self.simulador.acciones._accion_cazar))

                # Acciones especiales por ubicación
                if casilla == (0, 0):
                    self.opciones.append(("Descansar/Dormir", self.simulador.acciones._accion_descansar))

                # Construcciones específicas (si las hay)
                if hasattr(hex_info, 'construccion') and hex_info.construccion:
                    self.opciones.append((f"Usar {hex_info.construccion}",
                                        self._accion_usar_construccion))
                if hex_info and hasattr(hex_info, 'categoria'):
                    if hex_info.categoria == "mercado" and en_casilla:
                        self.opciones.append(("💰 Abrir mercado", self._accion_abrir_mercado))
                        #self.opciones.append(("💰 Comprar", self.simulador.acciones._accion_comprar))
                        #self.opciones.append(("💰 Vender", self.simulador.acciones._accion_vender))

                    elif hex_info.categoria == "cocina" and en_casilla:
                        self.opciones.append(("🍳 Cocinar", self.simulador.acciones._accion_cocinar))

                    elif hex_info.categoria == "granja" and en_casilla:
                        self.opciones.append(("🌱 Cultivar", self.simulador.acciones._accion_cultivar))
                        self.opciones.append(("Animales", self.simulador.acciones._accion_animales))

                    elif hex_info.categoria == "talleres" and en_casilla:
                        self.opciones.append(("Carpinteria", self.simulador.acciones._accion_carpinteria))
                        self.opciones.append(("Herreria", self.simulador.acciones._accion_herreria))
                        self.opciones.append(("Cantera", self.simulador.acciones._accion_cantera))
                        self.opciones.append(("Telar", self.simulador.acciones._accion_tejer))

                    elif hex_info.categoria == "servicios_civicos" and en_casilla:
                        self.opciones.append(("🏛️ Ayuntamiento", self.simulador.acciones._accion_ayuntamiento))
                        self.opciones.append(("🏦 Banco", self.simulador.acciones._accion_banco))
                        self.opciones.append(("🎰 Lotería", self.simulador.acciones._accion_loteria))
                        self.opciones.append(("👶 Guardería", self.simulador.acciones._accion_guarderia))

                    elif hex_info.categoria == "centro_comunitario" and en_casilla:
                        self.opciones.append(("🎪 Plaza de eventos", self.simulador.acciones._accion_plaza))
                        self.opciones.append(("📚 Escuela", self.simulador.acciones._accion_escuela))
                        self.opciones.append(("🏥 Sanidad", self.simulador.acciones._accion_sanidad))
                        self.opciones.append(("💪 Gimnasio", self.simulador.acciones._accion_gym))
                        self.opciones.append(("🕯️ Altares", self.simulador.acciones._accion_altares))

        # Acciones generales (siempre disponibles)
        self.opciones.append(("Comer algo", self._accion_comer))
        self.opciones.append(("Beber agua", self._accion_beber))
        self.opciones.append(("Ver inventario", self._accion_inventario))
        self.opciones.append(("Cancelar", self._accion_cancelar))

    def dibujar(self, pantalla):
        """Dibujar el menú en pantalla"""
        if not self.visible:
            return

        x, y = self.posicion
        num_opciones = len(self.opciones)
        alto_total = num_opciones * self.alto_opcion

        # Ajustar posición si el menú se sale de la pantalla
        if x + self.ancho_menu > self.simulador.ancho:
            x = self.simulador.ancho - self.ancho_menu
        if y + alto_total > self.simulador.alto:
            y = self.simulador.alto - alto_total

        # Fondo del menú
        pygame.draw.rect(pantalla, (40, 40, 60),
                        (x, y, self.ancho_menu, alto_total))
        pygame.draw.rect(pantalla, (80, 80, 120),
                        (x, y, self.ancho_menu, alto_total), 2)

        # Opciones
        mouse_x, mouse_y = pygame.mouse.get_pos()
        font = pygame.font.SysFont(None, 24)

        for i, (texto, accion) in enumerate(self.opciones):
            rect_opcion = pygame.Rect(x, y + i * self.alto_opcion,
                                    self.ancho_menu, self.alto_opcion)

            # Resaltar opción bajo el mouse
            if rect_opcion.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(pantalla, (60, 60, 90), rect_opcion)
                color_texto = (255, 255, 200)
            else:
                color_texto = (220, 220, 220)

            # Texto
            superficie = font.render(texto, True, color_texto)
            pantalla.blit(superficie, (x + 10, y + i * self.alto_opcion + 8))

    def procesar_clic(self, pos_mouse):
        """Procesar clic en el menú"""
        if not self.visible:
            return False

        x, y = self.posicion
        mouse_x, mouse_y = pos_mouse

        # Verificar si el clic está dentro del menú
        if (x <= mouse_x <= x + self.ancho_menu and
            y <= mouse_y <= y + len(self.opciones) * self.alto_opcion):

            # Calcular qué opción fue seleccionada
            indice = (mouse_y - y) // self.alto_opcion

            if 0 <= indice < len(self.opciones):
                texto, accion = self.opciones[indice]
                print(f"Menú: {texto}")
                accion()
                self.ocultar()
                return True

        # Si se hizo clic fuera del menú, cerrarlo
        self.ocultar()
        return False

    # Métodos de acción
    def _accion_ir_a(self):
        if self.casilla:
            agente = self.simulador.agente_jugador
            if agente and not self.simulador.moviendo_agente:
                self.simulador.mover_agente_a(agente, self.casilla)
        return config.TIEMPO_TICK

    def _accion_comer(self):
        agente = self.simulador.agente_jugador
        if agente:
            agente.consumir()
        return config.TIEMPO_TICK

    def _accion_beber(self):
        print("Acción: Beber agua")
        return config.TIEMPO_TICK
        # Implementar después

    def _accion_inventario(self):
        print("Acción: Ver inventario")
        self.simulador.menu_inventario.mostrar()
        self.visible = False
        return 0
        # Mostrar inventario después

    def _accion_cancelar(self):
        print("Menú cancelado")
        return config.TIEMPO_TICK

    def _accion_abrir_mercado(self):
        """Abre la interfaz del mercado"""
        self.simulador.menu_mercado.mostrar()
        self.visible = False
