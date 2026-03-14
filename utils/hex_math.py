# utils/hex_math.py
import math
import numpy as np

def pixel_to_axial(x, y, size, flat_top=True):
    """
    Convertir coordenadas de píxel a coordenadas axiales (q, r) de hexágono.

    Args:
        x, y: Coordenadas de píxel
        size: Tamaño del hexágono (radio desde centro a vértice)
        flat_top: True si los hexágonos son planos-arriba (como los tuyos)

    Returns:
        (q, r): Coordenadas axiales flotantes
    """
    if flat_top:
        # Para hexágonos planos-arriba (lados horizontales)
        q = (x * 2/3) / size
        r = (-x/3 + math.sqrt(3)/3 * y) / size
    else:
        # Para hexágonos punto-arriba
        q = (math.sqrt(3)/3 * x - y/3) / size
        r = (2/3 * y) / size

    return q, r

def axial_to_pixel(q, r, size, flat_top=True):
    """
    Convertir coordenadas axiales a píxel.

    Args:
        q, r: Coordenadas axiales
        size: Tamaño del hexágono
        flat_top: True para hexágonos planos-arriba

    Returns:
        (x, y): Coordenadas de píxel del centro del hexágono
    """
    if flat_top:
        x = size * (3/2 * q)
        y = size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    else:
        x = size * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
        y = size * (3/2 * r)

    return x, y

def axial_round(q, r):
    """
    Redondear coordenadas axiales flotantes a hexágono más cercano.

    Args:
        q, r: Coordenadas axiales flotantes

    Returns:
        (q_round, r_round): Coordenadas axiales enteras
    """
    # Convertir a coordenadas cúbicas
    x = q
    z = r
    y = -x - z

    # Redondear
    rx = round(x)
    ry = round(y)
    rz = round(z)

    # Corrección de redondeo cúbico
    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    # Volver a axial
    return (int(rx), int(rz))

def hex_distance(hex1, hex2):
    """Distancia entre dos hexágonos (en pasos)"""
    q1, r1 = hex1
    q2, r2 = hex2
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def get_hex_corners(center_x, center_y, size, flat_top=True):
    """
    Obtener los 6 vértices de un hexágono.

    Args:
        center_x, center_y: Centro del hexágono
        size: Tamaño
        flat_top: True para hexágonos planos-arriba

    Returns:
        Lista de 6 (x, y) tuplas
    """
    corners = []

    for i in range(6):
        if flat_top:
            # Ángulos para hexágonos planos-arriba
            angle_deg = 60 * i
        else:
            # Ángulos para hexágonos punto-arriba
            angle_deg = 60 * i - 30

        angle_rad = math.pi / 180 * angle_deg
        x = center_x + size * math.cos(angle_rad)
        y = center_y + size * math.sin(angle_rad)
        corners.append((x, y))

    return corners
