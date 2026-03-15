import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import balance
from agentes.agente import Agente
from sistema.acciones import Acciones


def test_acciones_usa_constantes_centralizadas_de_balance():
    assert Acciones.TICKS_BUSCAR == balance.TICKS_BUSCAR
    assert Acciones.TICKS_DORMIR == balance.TICKS_DORMIR
    assert Acciones.TICKS_COMER == balance.TICKS_COMER


def test_fisiologia_usa_tasas_desde_balance():
    agente = Agente(nombre="Test", sexo="M", edad=20)

    assert agente.fisiologia.agua_necesaria == balance.AGUA_NECESARIA_BASE
    assert agente.fisiologia.factor_deca_por_año == balance.FACTOR_DECAIMIENTO_ANUAL
