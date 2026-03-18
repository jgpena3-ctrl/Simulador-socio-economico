import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))


def _cargar_input_controller_con_pygame_stub():
    pygame_stub = SimpleNamespace(
        QUIT=0,
        KEYDOWN=1,
        KEYUP=2,
        MOUSEBUTTONDOWN=3,
        MOUSEWHEEL=4,
        K_ESCAPE=27,
        K_p=112,
        K_SPACE=32,
        K_c=99,
        K_f=102,
        K_z=122,
        K_x=120,
        K_r=114,
        K_HOME=278,
    )
    sys.modules["pygame"] = pygame_stub
    module = importlib.import_module("controllers.input_controller")
    return importlib.reload(module), pygame_stub


def test_escape_no_cierra_juego_si_hay_menu_abierto():
    module, pygame_stub = _cargar_input_controller_con_pygame_stub()

    sim = SimpleNamespace(
        teclas_presionadas={},
        menu_mercado=SimpleNamespace(visible=False, procesar_eventos_teclado=lambda _tecla: False),
        menu_inventario=SimpleNamespace(visible=False, procesar_tecla=lambda _tecla: False),
        menu=SimpleNamespace(visible=True, ocultar=lambda: setattr(sim.menu, "visible", False)),
        ejecutando=True,
        pausado=False,
        agente_jugador=None,
        camara=SimpleNamespace(zoom_in=lambda: None, zoom_out=lambda: None, escala=1.0, centrar_en=lambda *_args: None),
    )

    controller = module.InputController(sim)
    controller.manejar_teclas(pygame_stub.K_ESCAPE, True)

    assert sim.ejecutando is True
    assert sim.menu.visible is False


def test_clic_inventario_visible_se_consume_y_no_llega_al_mapa():
    module, _pygame_stub = _cargar_input_controller_con_pygame_stub()

    registro = {"menu_procesado": False, "mapa_mostrado": False}

    sim = SimpleNamespace(
        menu_mercado=SimpleNamespace(visible=False, procesar_clic=lambda _pos: False),
        menu_inventario=SimpleNamespace(visible=True, procesar_clic=lambda _pos: True, procesar_tecla=lambda _tecla: False),
        menu=SimpleNamespace(
            procesar_clic=lambda _pos: registro.__setitem__("menu_procesado", True),
            mostrar=lambda *_args, **_kwargs: registro.__setitem__("mapa_mostrado", True),
            ocultar=lambda: None,
        ),
        camara=SimpleNamespace(
            pantalla_a_mundo=lambda x, y: (x, y),
        ),
        mapa=SimpleNamespace(hexagonos={(0, 0): object()}),
        hex_size=1,
        hex_flat=True,
        _mostrar_info_casilla=lambda *_args: None,
        moviendo_agente=False,
        ruta_actual=[],
        agente_jugador=None,
    )

    controller = module.InputController(sim)
    evento = SimpleNamespace(button=1, pos=(10, 10))
    controller.manejar_clic_mouse(evento)

    assert registro["menu_procesado"] is False
    assert registro["mapa_mostrado"] is False
