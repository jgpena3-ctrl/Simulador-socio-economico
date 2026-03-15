import logging

logger = logging.getLogger(__name__)
# menu_inventario.py (nuevo archivo)
import pygame

class MenuInventario:
    def __init__(self, simulador):
        self.sim = simulador
        self.visible = False
        self.posicion = (300, 200)  # Posición fija en pantalla
        self.ancho = 600
        self.alto = 400
        self.font_titulo = pygame.font.SysFont(None, 32)
        self.font_texto = pygame.font.SysFont(None, 24)
        self.font_pequeno = pygame.font.SysFont(None, 18)

    def mostrar(self):
        """Abre el menú de inventario"""
        self.visible = True
        logger.debug("\n=== INVENTARIO ABIERTO ===")

    def ocultar(self):
        """Cierra el menú de inventario"""
        self.visible = False
        logger.debug("Inventario cerrado")

    def dibujar(self, pantalla):
        """Dibuja el menú de inventario"""
        if not self.visible:
            return

        x, y = self.posicion

        # Fondo semitransparente
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        s.fill((40, 40, 60, 240))  # RGBA con transparencia
        pantalla.blit(s, (x, y))

        # Borde
        pygame.draw.rect(pantalla, (100, 100, 150), (x, y, self.ancho, self.alto), 2)

        # Título
        titulo = self.font_titulo.render("INVENTARIO", True, (255, 255, 200))
        pantalla.blit(titulo, (x + 20, y + 15))

        # Línea separadora
        pygame.draw.line(pantalla, (100, 100, 150),
                        (x + 20, y + 50), (x + self.ancho - 20, y + 50), 2)

        # Obtener inventario del agente
        agente = self.sim.agente_jugador
        if not agente:
            return

        inventario = agente.inventario

        # Mostrar items (organizados por categorías)
        y_actual = y + 70

        # 1. RECURSOS BÁSICOS
        self._dibujar_seccion(pantalla, "RECURSOS", x + 30, y_actual)
        y_actual += 30

        recursos = ["comida", "agua", "madera", "piedra", "monedas"]
        for recurso in recursos:
            cantidad = inventario.get(recurso, 0)
            if cantidad > 0 or recurso == "monedas":  # Siempre mostrar monedas
                texto = f"  {recurso.capitalize()}: {cantidad}"
                if recurso == "monedas":
                    texto += " 🪙"
                superficie = self.font_texto.render(texto, True, (220, 220, 220))
                pantalla.blit(superficie, (x + 50, y_actual))
                y_actual += 25

        # 2. ALIMENTOS
        if y_actual > y + 200:  # Saltar a siguiente columna
            x_col2 = x + 300
            y_actual = y + 70
        else:
            x_col2 = x + 30
            y_actual += 20

        self._dibujar_seccion(pantalla, "ALIMENTOS", x_col2, y_actual)
        y_actual += 30

        alimentos = ["fruta", "carne", "pescado", "pan", "vegetal", "cereal"]
        for alimento in alimentos:
            cantidad = inventario.get(alimento, 0)
            if cantidad > 0:
                texto = f"  {alimento.capitalize()}: {cantidad}"
                superficie = self.font_texto.render(texto, True, (220, 220, 220))
                pantalla.blit(superficie, (x_col2 + 20, y_actual))
                y_actual += 25

        # 3. HERRAMIENTAS Y OTROS
        if y_actual > y + 200:
            x_col3 = x + 300
            y_actual = y + 70
        else:
            x_col3 = x_col2
            y_actual += 20

        self._dibujar_seccion(pantalla, "HERRAMIENTAS", x_col3, y_actual)
        y_actual += 30

        otros = ["herramientas", "piel", "hueso", "semillas"]
        for otro in otros:
            cantidad = inventario.get(otro, 0)
            if cantidad > 0:
                texto = f"  {otro.capitalize()}: {cantidad}"
                superficie = self.font_texto.render(texto, True, (220, 220, 220))
                pantalla.blit(superficie, (x_col3 + 20, y_actual))
                y_actual += 25

        # Información adicional
        y_bottom = y + self.alto - 50

        # Total de items
        total_items = sum(inventario.values())
        texto_total = f"Total items: {total_items}"
        superficie_total = self.font_pequeno.render(texto_total, True, (180, 180, 180))
        pantalla.blit(superficie_total, (x + 20, y_bottom))

        # Instrucción para cerrar
        texto_cerrar = "Presiona ESPACIO o ESC para cerrar"
        superficie_cerrar = self.font_pequeno.render(texto_cerrar, True, (200, 200, 100))
        ancho_texto = superficie_cerrar.get_width()
        pantalla.blit(superficie_cerrar, (x + self.ancho - ancho_texto - 20, y_bottom))

    def _dibujar_seccion(self, pantalla, titulo, x, y):
        """Dibuja título de sección"""
        superficie = self.font_pequeno.render(titulo, True, (255, 255, 100))
        pantalla.blit(superficie, (x, y))
        pygame.draw.line(pantalla, (150, 150, 100),
                        (x, y + 18), (x + 150, y + 18), 1)

    def procesar_tecla(self, tecla):
        """Procesa teclas cuando el menú está abierto"""
        if tecla == pygame.K_SPACE or tecla == pygame.K_ESCAPE:
            self.ocultar()
            return True
        return False
