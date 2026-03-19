import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.bootstrap_system import BootstrapSystem


class _EconomiaRegistro:
    def __init__(self):
        self.ventas = []
        self.compras = []

    def publicar_oferta_venta(self, agente_id, producto, cantidad, precio, calidad):
        self.ventas.append((agente_id, producto, cantidad, precio, calidad))

    def publicar_oferta_compra(self, agente_id, producto, cantidad, precio_maximo):
        self.compras.append((agente_id, producto, cantidad, precio_maximo))


def test_bootstrap_crea_ofertas_compra_y_prepara_inventario_para_vender():
    jugador = SimpleNamespace(id=1, nombre="Jugador", inventario={"madera": 0, "monedas": 100})
    npc = SimpleNamespace(id=2, nombre="NPC", inventario={})
    sim = SimpleNamespace(
        agente_jugador=jugador,
        agentes=[jugador, npc],
        economia=_EconomiaRegistro(),
    )
    bootstrap = BootstrapSystem(sim)

    bootstrap.inicializar_mercado_inicial()

    assert sim.economia.ventas
    assert sim.economia.compras
    assert jugador.inventario["madera"] >= 6
