import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from types import SimpleNamespace

from sistema.economia import SistemaEconomico


def test_get_oferta_venta_retorna_oferta_por_id():
    economia = SistemaEconomico(SimpleNamespace(tick=1))
    oferta_id = economia.publicar_oferta_venta(agente_id=10, producto="fruta", cantidad=3, precio_unitario=7)

    oferta = economia.get_oferta_venta(oferta_id)

    assert oferta is not None
    assert oferta["id"] == oferta_id
    assert oferta["producto"] == "fruta"


def test_get_oferta_compra_retorna_none_si_no_existe():
    economia = SistemaEconomico(SimpleNamespace(tick=1))

    oferta = economia.get_oferta_compra(999)

    assert oferta is None
