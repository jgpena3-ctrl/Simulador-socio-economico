import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sistema.acciones import Acciones


class EconomiaMinimaStub:
    def publicar_oferta_venta(self, *_args, **_kwargs):
        return 1

    def publicar_oferta_compra(self, *_args, **_kwargs):
        return 2


def _crear_agente_stub(**inventario):
    return SimpleNamespace(
        id=11,
        nombre="Agente",
        inventario=dict(inventario),
        experiencia={},
        fisiologia=SimpleNamespace(cansancio=0, hambre=0),
    )


def test_publicar_oferta_venta_no_deja_inventario_negativo_si_no_hay_stock():
    simulador = SimpleNamespace(economia=EconomiaMinimaStub())
    acciones = Acciones(simulador)
    agente = _crear_agente_stub(madera=1)

    resultado = acciones.accion_publicar_oferta_venta(agente, "madera", cantidad=2, precio_unitario=4)

    assert resultado is False
    assert agente.inventario["madera"] == 1
    assert agente.inventario["madera"] >= 0


def test_accion_comer_no_deja_comida_negativa_si_no_hay_comida():
    simulador = SimpleNamespace(
        agente_jugador=None,
        iniciar_actividad=lambda *_args, **_kwargs: True,
    )
    acciones = Acciones(simulador)
    agente = _crear_agente_stub(comida=0)

    resultado = acciones._accion_comer(agente)

    assert resultado is False
    assert agente.inventario["comida"] == 0
    assert agente.inventario["comida"] >= 0
