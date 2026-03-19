import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sistema.economia import SistemaEconomico


def test_filtrar_productos_por_nombre_categoria_y_tipo():
    economia = SistemaEconomico(SimpleNamespace(tick=1))
    economia.registrar_producto("fruta", categoria="alimento", tipo_alimento="frutas")
    economia.registrar_producto("carne", categoria="alimento", tipo_alimento="carnes")
    economia.registrar_producto("hacha", categoria="herramienta", tipo_alimento=None)

    productos = economia.filtrar_productos(
        nombre_articulo="fru",
        categoria="alimento",
        tipo_alimento="frutas",
    )

    assert productos == ["fruta"]


def test_listar_ofertas_filtradas_respeta_orden_y_filtros():
    economia = SistemaEconomico(SimpleNamespace(tick=3))
    economia.registrar_producto("fruta", categoria="alimento", tipo_alimento="frutas")
    economia.registrar_producto("madera", categoria="material", tipo_alimento=None)

    economia.publicar_oferta_venta(agente_id=1, producto="fruta", cantidad=2, precio_unitario=8, calidad=0.8)
    economia.publicar_oferta_venta(agente_id=2, producto="fruta", cantidad=2, precio_unitario=5, calidad=0.9)
    economia.publicar_oferta_venta(agente_id=3, producto="madera", cantidad=2, precio_unitario=2, calidad=1.0)

    economia.publicar_oferta_compra(agente_id=4, producto="fruta", cantidad=3, precio_maximo=6)
    economia.publicar_oferta_compra(agente_id=5, producto="fruta", cantidad=3, precio_maximo=10)

    ventas = economia.listar_ofertas_venta_filtradas(
        nombre_articulo="fruta",
        categoria="alimento",
        tipo_alimento="frutas",
        calidad_min=0.85,
    )
    compras = economia.listar_ofertas_compra_filtradas(
        nombre_articulo="fruta",
        categoria="alimento",
        tipo_alimento="frutas",
    )

    assert [venta["precio_unitario"] for venta in ventas] == [5]
    assert [compra["precio_maximo"] for compra in compras] == [10, 6]
<<<<<<< codex/add-mercado-and-menumercado-components


def test_publicar_oferta_autocompleta_categoria_si_no_se_registro_producto():
    economia = SistemaEconomico(SimpleNamespace(tick=2))
    economia.publicar_oferta_venta(agente_id=9, producto="carne", cantidad=1, precio_unitario=7, calidad=1.0)

    metadata = economia.obtener_metadata_producto("carne")

    assert metadata["categoria"] == "alimento"
    assert metadata["tipo_alimento"] == "carnes"
=======
>>>>>>> main
