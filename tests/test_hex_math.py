import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.hex_math import hex_distance


def test_hex_distance_es_cero_en_mismo_hexagono():
    assert hex_distance((0, 0), (0, 0)) == 0


def test_hex_distance_es_simetrica_y_consistente():
    origen = (0, 0)
    destino = (2, -1)

    assert hex_distance(origen, destino) == 2
    assert hex_distance(destino, origen) == 2


def test_hex_distance_cumple_ejemplo_largo():
    assert hex_distance((3, -5), (-2, 1)) == 6
