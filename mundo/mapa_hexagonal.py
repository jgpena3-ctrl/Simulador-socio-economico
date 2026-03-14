#mundo\mapa_hexagonal.py
import numpy as np
from configu.categorias import CATEGORIAS_POR_COORDENADA
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Hex:
    """Representa una casilla hexagonal"""
    q: int  # Coordenada q (columna)
    r: int  # Coordenada r (fila)

    # Recursos
    arboles: int = 0
    arboles_jovenes: int = 0
    arbustos: int = 0
    animales: Dict[str, int] = None  # {"vaca": 2, "conejo": 5}

    # Construcciones
    construccion: str = None  # "casa", "granja", "herreria", etc.
    propietario: int = None  # ID del agente dueño

    # NUEVO: Categoría para colores personalizados
    categoria: str = None  # "centro", "vivienda", "bosque", "rio", "desierto", etc.

    # OPCIONAL: Color directo (si quieres máximo control)
    color_personalizado: tuple = None  # (R, G, B)

    def __post_init__(self):
        if self.animales is None:
            self.animales = {}

    def distancia_a(self, otro_hex):
        """Distancia hexagonal"""
        return (abs(self.q - otro_hex.q) +
                abs(self.q + self.r - otro_hex.q - otro_hex.r) +
                abs(self.r - otro_hex.r)) / 2

    def coordenadas_pixel(self, tamaño):
        """Convertir a coordenadas de píxel"""
        x = tamaño * (3/2 * self.q)
        y = tamaño * (np.sqrt(3)/2 * self.q + np.sqrt(3) * self.r)
        return (x, y)

class MapaHexagonal:
    def __init__(self, radio):
        self.radio = radio
        cara = radio+1
        self.area = 3*cara*cara-3*cara-1
        self.hexagonos = {}
        self._inicializar_mapa()
        self._inicializar_recursos()
        self.frutos = 33
        self.asignar_categorias()

    def _inicializar_mapa(self):
        """Crear todas las casillas hexagonales"""
        for q in range(-self.radio, self.radio + 1):
            for r in range(-self.radio, self.radio + 1):
                s = -q - r
                if abs(s) <= self.radio:
                    self.hexagonos[(q, r)] = Hex(q, r)

    def _inicializar_recursos(self):
        """Inicializar recursos naturales"""
        tipos_animales = ["conejo", "ciervo", "jabalí", "pájaro", "rata"]

        for hexagono in self.hexagonos.values():
            # Más recursos en los bordes
            distancia_centro = abs(hexagono.q) + abs(hexagono.r) + abs(-hexagono.q - hexagono.r)

            if distancia_centro > self.radio * 0.7:  # Bordes
                hexagono.arboles = np.random.randint(20, 50)
                hexagono.arboles_jovenes = np.random.randint(5, 15)
                hexagono.frutos = 33

                # Animales en bordes
                for animal in tipos_animales:
                    if np.random.random() < 0.3:
                        hexagono.animales[animal] = np.random.randint(1, 10)
            else:  # Centro - menos recursos naturales
                hexagono.arboles = np.random.randint(0, 10)
                hexagono.arbustos = np.random.randint(0, 5)
                hexagono.frutos = 33

    def get_vecinos(self, q, r, distancia=1):
        """Obtener vecinos en un radio"""
        vecinos = []
        for dq in range(-distancia, distancia + 1):
            for dr in range(-distancia, distancia + 1):
                ds = -dq - dr
                if abs(ds) <= distancia:
                    vecino = (q + dq, r + dr)
                    if vecino in self.hexagonos:
                        vecinos.append(self.hexagonos[vecino])
        return vecinos

    def actualizar_ecosistema(self):
        """Actualizar crecimiento y reproducción"""
        for hexagono in self.hexagonos.values():
            # Crecimiento de árboles
            if hexagono.arboles < 50:
                tasa_crecimiento = 0.01
                vecinos = self.get_vecinos(hexagono.q, hexagono.r)
                arboles_vecinos = sum(h.arboles for h in vecinos) / len(vecinos)

                prob_crecimiento = tasa_crecimiento * (1 + arboles_vecinos / 100)
                if np.random.random() < prob_crecimiento:
                    hexagono.arboles += 1

            # Reproducción de animales
            for especie, cantidad in list(hexagono.animales.items()):
                if cantidad >= 2:  # Mínimo para reproducción
                    tasa_reproduccion = 0.05  # 5% por tick
                    if np.random.random() < tasa_reproduccion:
                        hexagono.animales[especie] += 1

            hexagono.frutos += hexagono.arboles*0.33

    def asignar_categorias(self, categorias_por_coordenada=None):
        """
        Asigna categorías a los hexágonos
        categorias_por_coordenada: dict con {(q,r): "categoria"}
        """

        if categorias_por_coordenada is None:
            categorias_por_coordenada = CATEGORIAS_POR_COORDENADA

        for (q, r), hexagono in self.hexagonos.items():
            # 1. Prioridad: categoría por coordenada específica
            if (q, r) in categorias_por_coordenada:
                hexagono.categoria = categorias_por_coordenada[(q, r)]

    def set_categoria(self, q, r, categoria):
        """Asignar categoría a un hexágono específico"""
        if (q, r) in self.hexagonos:
            self.hexagonos[(q, r)].categoria = categoria
            return True
        return False

    def set_color_personalizado(self, q, r, color):
        """Asignar color directo a un hexágono (opcional)"""
        if (q, r) in self.hexagonos:
            self.hexagonos[(q, r)].color_personalizado = color
            return True
        return False
