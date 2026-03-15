import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sistema.economia import SistemaEconomico


def test_publicar_ofertas_y_realizar_transaccion_actualiza_cantidades_y_estado():
    simulador = SimpleNamespace(tick=7)
    economia = SistemaEconomico(simulador)

    oferta_venta_id = economia.publicar_oferta_venta(
        agente_id=1,
        producto="fruta",
        cantidad=5,
        precio_unitario=3.0,
        calidad=0.9,
    )
    oferta_compra_id = economia.publicar_oferta_compra(
        agente_id=2,
        producto="fruta",
        cantidad=4,
        precio_maximo=4.0,
    )

    transaccion = economia.realizar_transaccion(oferta_venta_id, oferta_compra_id, cantidad=3)

    assert transaccion
    assert transaccion["cantidad"] == 3
    assert economia.get_oferta_venta(oferta_venta_id)["cantidad"] == 2
    assert economia.get_oferta_venta(oferta_venta_id)["activa"] is True
    assert economia.get_oferta_compra(oferta_compra_id)["cantidad"] == 1
    assert economia.get_oferta_compra(oferta_compra_id)["activa"] is True


def test_realizar_transaccion_desactiva_oferta_al_consumirse_completa():
    simulador = SimpleNamespace(tick=9)
    economia = SistemaEconomico(simulador)

    oferta_venta_id = economia.publicar_oferta_venta(agente_id=3, producto="madera", cantidad=2, precio_unitario=5.0)
    oferta_compra_id = economia.publicar_oferta_compra(agente_id=4, producto="madera", cantidad=10, precio_maximo=6.0)

    transaccion = economia.realizar_transaccion(oferta_venta_id, oferta_compra_id, cantidad=10)

    assert transaccion
    assert transaccion["cantidad"] == 2
    assert economia.get_oferta_venta(oferta_venta_id)["cantidad"] == 0
    assert economia.get_oferta_venta(oferta_venta_id)["activa"] is False
