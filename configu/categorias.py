# config/categorias.py (nuevo archivo)

# Definición de colores para categorías
COLORES_CATEGORIAS = {
    "centro": (100, 100, 255),      # Azul
    "vivienda": (150, 150, 255),    # Azul claro

     # Zona económica principal
    "mercado": (255, 215, 0),             # Dorado
    "cocina": (255, 140, 0),              # Naranja
    "talleres": (169, 169, 169),          # Gris
    "granja": (154, 205, 50),             # Verde amarillento

    # Nuevas categorías
    "servicios_civicos": (100, 149, 237), # Azul cielo
    "centro_comunitario": (255, 218, 185), # Melocotón

    "bosque_denso": (34, 139, 34),  # Verde oscuro
    "bosque_claro": (50, 150, 50),  # Verde claro
    "rio": (64, 164, 223),          # Azul agua
    "montaña": (139, 137, 137),     # Gris
    "desierto": (238, 203, 173),    # Beige
    "playa": (255, 228, 181),       # Arena
}

# Categorías especiales por coordenadas (ejemplo)
CATEGORIAS_POR_COORDENADA = {
    # Centro
    (0, 0): "centro",

    # Zona económica (6 casillas)
    (1, 0): "mercado",           # Comercio, compra/venta
    (0, 1): "cocina",            # Preparar alimentos
    (-1, 0): "talleres",         # Artesanías, carpintería, herrería
    (0, -1): "granja",           # Agricultura, cultivos
    (1, -1): "servicios_civicos", # Gobierno, banco, lotería, guardería
    (-1, 1): "centro_comunitario", # Eventos, escuela, sanidad, gym, altares

    # Ejemplo de río (coordenadas ficticias)
    (-16, 8): "rio",(-15, 7): "rio",(-14, 6): "rio",(-13, 5): "rio",(-12, 4): "rio",(-11, 3): "rio",(-10, 2): "rio",(-9, 1): "rio",
    (-8, 0): "rio",(-7, -1): "rio",(-6, -2): "rio",(-5, -3): "rio",(-4, -4): "rio",(-3, -5): "rio",(-2, -6): "rio",(-1, -7): "rio",
    (0, -8): "rio",(1, -9): "rio",(2, -10): "rio",(3, -11): "rio",(4, -12): "rio",(5, -13): "rio",(6, -14): "rio",(7, -15): "rio",
    (8, -16): "rio",(8, -15): "rio",(8, -14): "rio",(8, -13): "rio",(8, -12): "rio",(8, -11): "rio",(8, -10): "rio",
    (8, -9): "rio",(8, -8): "rio",(8, -7): "rio",(8, -6): "rio",(8, -5): "rio",(8, -4): "rio",(8, -3): "rio",(8, -2): "rio",
    (8, -1): "rio",(8, 0): "rio",(8, 1): "rio",(8, 2): "rio",(8, 3): "rio",(8, 4): "rio",(8, 5): "rio",(8, 6): "rio",(8, 7): "rio",
    (8, 8): "rio",(7, 8): "rio",(6, 8): "rio",(5, 8): "rio",(4, 8): "rio",(3, 8): "rio",(2, 8): "rio",(1, 8): "rio",(0, 8): "rio",
    (-1, 8): "rio",(-2, 8): "rio",(-3, 8): "rio",(-4, 8): "rio",(-5, 8): "rio",(-6, 8): "rio",(-7, 8): "rio",(-8, 8): "rio",
    (-9, 8): "rio",(-10, 8): "rio",(-11, 8): "rio",(-12, 8): "rio",(-13, 8): "rio",(-14, 8): "rio",(-15, 8): "rio",(7, 1): "rio",
    (6, 2): "rio",(5, 3): "rio",(4, 4): "rio",(3, 5): "rio",(2, 6): "rio",(1, 7): "rio",(7, -8): "rio",(6, -8): "rio",
    (5, -8): "rio",(4, -8): "rio",(3, -8): "rio",(2, -8): "rio",(1, -8): "rio",(-8, 1): "rio",(-8, 2): "rio",(-8, 3): "rio",
    (-8, 4): "rio",(-8, 5): "rio",(-8, 6): "rio",(-8, 7): "rio",
}

# Función para asignar categorías por región
"""def asignar_categoria_por_distancia(hexagono, radio_mapa):
    #Asigna categoría basada en distancia al centro
    q, r = hexagono.q, hexagono.r
    distancia = abs(q) + abs(r) + abs(-q - r)

    if distancia == 0:
        return "centro"
    elif distancia <= 2:
        return "zona_economica"
    elif distancia <= 5:
        return "bosque_claro"
    elif distancia <= 8:
        return "bosque_denso"
    else:
        return "montaña"
"""
