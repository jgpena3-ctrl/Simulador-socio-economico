import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from types import SimpleNamespace

import types

if "numpy" not in sys.modules:
    numpy_stub = types.ModuleType("numpy")
    numpy_stub.random = types.SimpleNamespace(random=lambda: 0.0, randint=lambda *args, **kwargs: 0, choice=lambda seq: seq[0])
    sys.modules["numpy"] = numpy_stub

from sistema.acciones import Acciones


class EconomiaStub:
    def __init__(self):
        self.ofertas_venta = {
            1: {
                "activa": True,
                "cantidad": 5,
                "precio_unitario": 3,
                "producto": "fruta",
                "agente_id": 200,
            }
        }
        self.ofertas_compra = {
            2: {
                "activa": True,
                "cantidad": 5,
                "precio_maximo": 4,
                "producto": "madera",
                "agente_id": 201,
            }
        }

    def publicar_oferta_venta(self, agente_id, producto, cantidad, precio_unitario, calidad=1.0):
        return 99

    def publicar_oferta_compra(self, agente_id, producto, cantidad, precio_maximo):
        return 88

    def get_oferta_venta(self, oferta_id):
        return self.ofertas_venta.get(oferta_id)

    def get_oferta_compra(self, oferta_id):
        return self.ofertas_compra.get(oferta_id)

    def realizar_transaccion(self, oferta_venta_id, oferta_compra_id, cantidad):
        return {"total": 12, "cantidad": cantidad}


def _agente(agente_id, nombre, inventario):
    return SimpleNamespace(
        id=agente_id,
        nombre=nombre,
        inventario=dict(inventario),
        experiencia={},
        fisiologia=SimpleNamespace(cansancio=0, hambre=0),
        actualizar_afinidad=lambda *_args, **_kwargs: None,
    )


def test_accion_comprar_usa_simulador_y_transfiere_producto():
    simulador = SimpleNamespace(economia=EconomiaStub())
    acciones = Acciones(simulador)
    acciones._get_agente_by_id = lambda _agente_id: None

    comprador = _agente(100, "Comprador", {"monedas": 50})

    transaccion = acciones.accion_comprar(comprador, oferta_venta_id=1, cantidad=2)

    assert transaccion
    assert comprador.inventario["fruta"] == 2


def test_accion_vender_usa_simulador_y_descuenta_inventario():
    simulador = SimpleNamespace(economia=EconomiaStub())
    acciones = Acciones(simulador)

    vendedor = _agente(101, "Vendedor", {"madera": 7})

    transaccion = acciones.accion_vender(vendedor, oferta_compra_id=2, cantidad=3)

    assert transaccion
    assert vendedor.inventario["madera"] == 4
