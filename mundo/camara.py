# mundo/camara.py
import pygame
import math

class Camara:
    def __init__(self, ancho_pantalla, alto_pantalla):
        self.ancho = ancho_pantalla
        self.alto = alto_pantalla

        # Posición del mundo (en unidades de hexágonos)
        self.x = 0.0  # Centro horizontal
        self.y = 0.0  # Centro vertical

        # Zoom
        self.escala = 1.0
        self.escala_min = 0.5
        self.escala_max = 2.0
        self.zoom_paso = 0.1

        # Velocidad de movimiento
        self.velocidad = 0.5  # hexágonos por tick de movimiento

        # Límites del mapa (ajustar según tu mapa)
        self.limite_x_min = -20
        self.limite_x_max = 20
        self.limite_y_min = -20
        self.limite_y_max = 20

    def mundo_a_pantalla(self, x_mundo, y_mundo):
        """Convertir coordenadas del mundo a pantalla"""
        # Ajustar por posición de cámara y zoom
        x_pant = (x_mundo - self.x) * self.escala + self.ancho // 2
        y_pant = (y_mundo - self.y) * self.escala + self.alto // 2
        return x_pant, y_pant

    def pantalla_a_mundo(self, x_pantalla, y_pantalla):
        """Convertir coordenadas de pantalla a mundo"""
        # Inverso de la transformación anterior
        x_mundo = (x_pantalla - self.ancho // 2) / self.escala + self.x
        y_mundo = (y_pantalla - self.alto // 2) / self.escala + self.y
        return x_mundo, y_mundo

    def mover(self, dx, dy):
        """Mover la cámara en unidades del mundo"""
        nuevo_x = self.x + dx * self.velocidad / self.escala
        nuevo_y = self.y + dy * self.velocidad / self.escala

        # Aplicar límites
        self.x = max(self.limite_x_min, min(self.limite_x_max, nuevo_x))
        self.y = max(self.limite_y_min, min(self.limite_y_max, nuevo_y))

    def zoom_in(self):
        """Acercar la cámara"""
        self.escala = min(self.escala_max, self.escala + self.zoom_paso)

    def zoom_out(self):
        """Alejar la cámara"""
        self.escala = max(self.escala_min, self.escala - self.zoom_paso)

    def centrar_en(self, x, y):
        """Centrar la cámara en una posición del mundo"""
        self.x = x
        self.y = y

    def seguir_agente(self, agente, factor_suavizado=0.1):
        """Suavemente seguir a un agente"""
        if agente and hasattr(agente, 'ubicacion'):
            # Convertir ubicación hexagonal a coordenadas mundo
            q, r = agente.ubicacion
            # Convertir axial a pixel (aproximado)
            target_x = q * 1.5  # Ajustar según tu sistema
            target_y = r * math.sqrt(3) + q * math.sqrt(3) / 2

            # Movimiento suavizado
            self.x += (target_x - self.x) * factor_suavizado
            self.y += (target_y - self.y) * factor_suavizado

    def get_estado(self):
        """Obtener estado actual de la cámara"""
        return {
            "posicion": (self.x, self.y),
            "escala": self.escala,
            "zoom_percent": (self.escala - self.escala_min) / (self.escala_max - self.escala_min) * 100
        }
