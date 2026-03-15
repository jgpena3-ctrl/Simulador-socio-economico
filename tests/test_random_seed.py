import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.random_config import setup_random_seed


def test_setup_random_seed_hace_determinista_numpy_random():
    setup_random_seed(123)
    primera = np.random.randint(0, 1000, size=5)

    setup_random_seed(123)
    segunda = np.random.randint(0, 1000, size=5)

    assert np.array_equal(primera, segunda)


def test_setup_random_seed_none_retorna_none():
    resultado = setup_random_seed(None)

    assert resultado is None
