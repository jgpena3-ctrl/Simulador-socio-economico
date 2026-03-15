import math

# Parámetros del mundo
TIEMPO_TICK = 30  # minutos
DIAS_POR_AÑO = 365
HORAS_POR_DIA = 24
TICK_POR_DIA = 60*HORAS_POR_DIA/TIEMPO_TICK

CALORIAS_BASE_HOMBRE = 2500  # kcal/día
CALORIAS_BASE_MUJER = 2000   # kcal/día
AGUA_NECESARIA_BASE = 2500   # ml/día

# Tasas realistas
TASA_CRECIMIENTO_NIÑO = 0.06  # 6 cm/año promedio
TASA_DECREPITUD = 0.003  # 0.3% anual después de 25
PERDIDA_ENTRENAMIENTO_DIARIA = 0.01  # 1% por día sin practicar

# Mundo hexagonal
RADIO_MAPA = 16  # 32 casillas de diámetro
CENTRO_MAPA = (RADIO_MAPA, RADIO_MAPA)

# Configuración agentes
EDAD_ADULTO = 18
MAX_AGENTES_CONTROL = 3
EXP_MAX_ACTIVIDAD = 100

# Sistema hexagonal
HEX_SIZE = 15  # Radio del hexágono (de centro a vértice)
HEX_FLAT = True  # True = hexágonos planos-arriba (lados horizontales)
HEX_WIDTH = HEX_SIZE * 2  # Ancho total
HEX_HEIGHT = HEX_SIZE * math.sqrt(3)  # Altura total

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Reproducibilidad (None = aleatorio, entero = ejecución determinista)
SEED = None
