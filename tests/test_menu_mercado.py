import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))


class _FakeFont:
    def render(self, text, _aa, _color):
        return text


class _FakeSurface:
    def __init__(self, *_args, **_kwargs):
        pass

    def fill(self, *_args, **_kwargs):
        return None


class _FakePantalla:
    def __init__(self):
        self.blits = []

    def blit(self, superficie, pos):
        self.blits.append((superficie, pos))


def _cargar_menu_mercado_con_pygame_stub():
    pygame_stub = SimpleNamespace(
        SRCALPHA=0,
        KEYDOWN=1,
        K_ESCAPE=27,
        Surface=lambda *args, **kwargs: _FakeSurface(),
        font=SimpleNamespace(SysFont=lambda *_args, **_kwargs: _FakeFont()),
    )
    sys.modules["pygame"] = pygame_stub

    module = importlib.import_module("ui.menu_mercado")
    return importlib.reload(module)


class _EconomiaStub:
    estadisticas = {"fruta": {"precio_promedio": 2.5}}

    def filtrar_productos(self, nombre_articulo=None, categoria=None, tipo_alimento=None):
        _ = (nombre_articulo, categoria, tipo_alimento)
        return ["fruta"]

    def obtener_info_producto(self, _producto):
        return {
            "estadisticas": {
                "precio_promedio": 2.5,
                "precio_minimo": 1,
                "precio_maximo": 5,
                "tendencia": "estable",
                "volumen_total": 10,
            },
            "ofertas_venta_activas": 1,
            "ofertas_compra_activas": 1,
        }

    def listar_ofertas_venta_filtradas(self, nombre_articulo=None, categoria=None, tipo_alimento=None, calidad_min=None, precio_max=None):
        _ = (categoria, tipo_alimento, calidad_min, precio_max)
        producto = nombre_articulo
        return [{"agente_id": 1, "cantidad": 3, "precio_unitario": 4, "calidad": 1.0, "producto": producto}]

    def listar_ofertas_compra_filtradas(self, nombre_articulo=None, categoria=None, tipo_alimento=None, precio_min=None):
        _ = (categoria, tipo_alimento, precio_min)
        producto = nombre_articulo
        return [{"agente_id": 2, "cantidad": 2, "precio_maximo": 5, "producto": producto}]


def test_dibujar_soporta_todos_los_modos_de_menu_mercado():
    menu_module = _cargar_menu_mercado_con_pygame_stub()

    sim = SimpleNamespace(
        economia=_EconomiaStub(),
        agentes=[SimpleNamespace(id=1, nombre="Vendedor"), SimpleNamespace(id=2, nombre="Comprador")],
    )

    menu = menu_module.MenuMercado(sim)
    menu.visible = True
    menu.producto_seleccionado = "fruta"
    pantalla = _FakePantalla()

    for modo in ["principal", "ver_producto", "comprar", "vender", "ofertar_venta", "ofertar_compra"]:
        menu.modo = modo
        menu.dibujar(pantalla)

    assert pantalla.blits
