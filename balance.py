"""Constantes de balance del juego.

Este módulo centraliza duraciones y tasas de mecánicas para facilitar
el tuning sin tocar la lógica principal.
"""

import config

# Duraciones de acciones (en ticks)
TICKS_BUSCAR = 1
TICKS_RECOLECTAR = 1
TICKS_CAZAR = 1
TICKS_TALAR = 2
TICKS_DORMIR = 3
TICKS_DESCANSAR = 1
TICKS_COMER = 1
TICKS_BEBER = 1
TICKS_BUSQUEDA_INTERNA = 1
TICKS_ACCION_INTERNA = 5
TICKS_COMPLETO = 30

# Acciones con duración variable
TRABAJO_DURACION_MIN = 4
TRABAJO_DURACION_MAX = 8
SOCIALIZAR_DURACION = 1

# Balance fisiológico
AGUA_NECESARIA_BASE = config.AGUA_NECESARIA_BASE
FACTOR_DECAIMIENTO_ANUAL = config.TASA_DECREPITUD
PERDIDA_ENTRENAMIENTO_DIARIA = config.PERDIDA_ENTRENAMIENTO_DIARIA

