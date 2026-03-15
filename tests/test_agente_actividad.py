import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agentes.agente import Agente


def test_iniciar_actividad_bloquea_segunda_actividad_hasta_terminar():
    agente = Agente(nombre="Ana", sexo="F", edad=25)

    assert agente.iniciar_actividad("comiendo", duracion_ticks=2) is True
    assert agente.iniciar_actividad("durmiendo", duracion_ticks=3) is False

    completada = agente.tick_actividad()
    assert completada is False
    assert agente.actividad_actual == "comiendo"

    completada = agente.tick_actividad()
    assert completada is True
    assert agente.actividad_actual is None
    assert agente.actividad_restante == 0
    assert agente.actividad_datos == {}


def test_actividad_se_puede_reiniciar_despues_de_finalizar():
    agente = Agente(nombre="Luis", sexo="M", edad=30)

    assert agente.iniciar_actividad("trabajando", duracion_ticks=1) is True
    assert agente.tick_actividad() is True
    assert agente.iniciar_actividad("durmiendo", duracion_ticks=1) is True
