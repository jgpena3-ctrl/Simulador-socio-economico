import logging
from typing import Any, TypedDict, Optional, Union

logger = logging.getLogger(__name__)


class OfertaVenta(TypedDict):
    id: int
    agente_id: int
    producto: str
    cantidad: int
    precio_unitario: float
    calidad: float
    fecha_tick: int
    activa: bool


class OfertaCompra(TypedDict):
    id: int
    agente_id: int
    producto: str
    cantidad: int
    precio_maximo: float
    fecha_tick: int
    activa: bool


class Transaccion(TypedDict):
    fecha_tick: int
    vendedor_id: int
    comprador_id: int
    producto: str
    cantidad: int
    precio_unitario: float
    calidad: float
    total: float


class EstadisticaProducto(TypedDict):
    precios: list[float]
    ultimo_precio: float
    precio_promedio: float
    precio_minimo: float
    precio_maximo: float
    volumen_total: int
    tendencia: str


class SistemaEconomico:
    def __init__(self, simulador: Any) -> None:
        self.ofertas_venta: list[OfertaVenta] = []
        self.ofertas_compra: list[OfertaCompra] = []
        self.historial_transacciones: list[Transaccion] = []
        self.estadisticas: dict[str, EstadisticaProducto] = {}
        self.catalogo_productos: dict[str, dict[str, Optional[str]]] = {}
        self.simulador = simulador

    def registrar_producto(
        self,
        nombre: str,
        categoria: Optional[str] = None,
        tipo_alimento: Optional[str] = None,
    ) -> None:
        """Registra metadatos para filtros del mercado."""
        self.catalogo_productos[nombre] = {
            "categoria": categoria,
            "tipo_alimento": tipo_alimento,
        }

    def obtener_metadata_producto(self, producto: str) -> dict[str, Optional[str]]:
        return self.catalogo_productos.get(
            producto,
            {
                "categoria": None,
                "tipo_alimento": None,
            },
        )

    def publicar_oferta_venta(
        self,
        agente_id: int,
        producto: str,
        cantidad: int,
        precio_unitario: float,
        calidad: float = 1.0,
    ) -> int:
        oferta: OfertaVenta = {
            "id": len(self.ofertas_venta) + len(self.historial_transacciones),
            "agente_id": agente_id,
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "calidad": calidad,
            "fecha_tick": self.simulador.tick,
            "activa": True,
        }
        self.ofertas_venta.append(oferta)
        self.catalogo_productos.setdefault(
            producto,
            {"categoria": None, "tipo_alimento": None},
        )
        logger.debug(f"📢 Agente {agente_id} ofrece {cantidad} {producto} a {precio_unitario} monedas")
        return oferta["id"]

    def publicar_oferta_compra(
        self,
        agente_id: int,
        producto: str,
        cantidad: int,
        precio_maximo: float,
    ) -> int:
        oferta: OfertaCompra = {
            "id": len(self.ofertas_compra) + len(self.historial_transacciones),
            "agente_id": agente_id,
            "producto": producto,
            "cantidad": cantidad,
            "precio_maximo": precio_maximo,
            "fecha_tick": self.simulador.tick,
            "activa": True,
        }
        self.ofertas_compra.append(oferta)
        self.catalogo_productos.setdefault(
            producto,
            {"categoria": None, "tipo_alimento": None},
        )
        logger.debug(f"📢 Agente {agente_id} busca comprar {cantidad} {producto} (max {precio_maximo})")
        return oferta["id"]

    def filtrar_productos(
        self,
        nombre_articulo: Optional[str] = None,
        categoria: Optional[str] = None,
        tipo_alimento: Optional[str] = None,
    ) -> list[str]:
        """
        Devuelve productos del mercado según filtros declarados en README.
        Incluye productos con actividad histórica y/o ofertas activas.
        """
        productos = set(self.catalogo_productos.keys()) | set(self.estadisticas.keys())
        productos |= {oferta["producto"] for oferta in self.ofertas_venta}
        productos |= {oferta["producto"] for oferta in self.ofertas_compra}

        resultados: list[str] = []
        nombre_normalizado = nombre_articulo.lower() if nombre_articulo else None

        for producto in sorted(productos):
            metadata = self.obtener_metadata_producto(producto)
            if nombre_normalizado and nombre_normalizado not in producto.lower():
                continue
            if categoria is not None and metadata["categoria"] != categoria:
                continue
            if tipo_alimento is not None and metadata["tipo_alimento"] != tipo_alimento:
                continue
            resultados.append(producto)

        return resultados

    def buscar_ofertas_venta(
        self,
        producto: Optional[str] = None,
        precio_max: Optional[float] = None,
        calidad_min: Optional[float] = None,
    ) -> list[OfertaVenta]:
        resultados: list[OfertaVenta] = []
        for oferta in self.ofertas_venta:
            if not oferta["activa"]:
                continue
            if producto is not None and oferta["producto"] != producto:
                continue
            if precio_max is not None and oferta["precio_unitario"] > precio_max:
                continue
            if calidad_min is not None and oferta["calidad"] < calidad_min:
                continue
            resultados.append(oferta)
        return sorted(resultados, key=lambda x: x["precio_unitario"])

    def listar_ofertas_venta_filtradas(
        self,
        nombre_articulo: Optional[str] = None,
        categoria: Optional[str] = None,
        tipo_alimento: Optional[str] = None,
        calidad_min: Optional[float] = None,
        precio_max: Optional[float] = None,
    ) -> list[OfertaVenta]:
        """Lista ofertas de venta ordenadas de menor a mayor precio con filtros de producto."""
        productos_filtrados = set(
            self.filtrar_productos(
                nombre_articulo=nombre_articulo,
                categoria=categoria,
                tipo_alimento=tipo_alimento,
            )
        )
        return [
            oferta
            for oferta in self.buscar_ofertas_venta(precio_max=precio_max, calidad_min=calidad_min)
            if oferta["producto"] in productos_filtrados
        ]

    def get_oferta_venta(self, oferta_id: int) -> Optional[OfertaVenta]:
        return next((oferta for oferta in self.ofertas_venta if oferta["id"] == oferta_id), None)

    def buscar_ofertas_compra(
        self,
        producto: Optional[str] = None,
        precio_min: Optional[float] = None,
    ) -> list[OfertaCompra]:
        resultados: list[OfertaCompra] = []
        for oferta in self.ofertas_compra:
            if not oferta["activa"]:
                continue
            if producto is not None and oferta["producto"] != producto:
                continue
            if precio_min is not None and oferta["precio_maximo"] < precio_min:
                continue
            resultados.append(oferta)
        return sorted(resultados, key=lambda x: x["precio_maximo"], reverse=True)

    def listar_ofertas_compra_filtradas(
        self,
        nombre_articulo: Optional[str] = None,
        categoria: Optional[str] = None,
        tipo_alimento: Optional[str] = None,
        precio_min: Optional[float] = None,
    ) -> list[OfertaCompra]:
        """Lista ofertas de compra ordenadas de mayor a menor precio con filtros de producto."""
        productos_filtrados = set(
            self.filtrar_productos(
                nombre_articulo=nombre_articulo,
                categoria=categoria,
                tipo_alimento=tipo_alimento,
            )
        )
        return [
            oferta
            for oferta in self.buscar_ofertas_compra(precio_min=precio_min)
            if oferta["producto"] in productos_filtrados
        ]

    def get_oferta_compra(self, oferta_id: int) -> Optional[OfertaCompra]:
        return next((oferta for oferta in self.ofertas_compra if oferta["id"] == oferta_id), None)

    def realizar_transaccion(
        self,
        oferta_venta_id: int,
        oferta_compra_id: int,
        cantidad: int,
    ) -> Union[Transaccion, bool]:
        oferta_venta = next((o for o in self.ofertas_venta if o["id"] == oferta_venta_id), None)
        oferta_compra = next((o for o in self.ofertas_compra if o["id"] == oferta_compra_id), None)

        if not oferta_venta or not oferta_compra:
            return False
        if not oferta_venta["activa"] or not oferta_compra["activa"]:
            return False

        cantidad_real = min(cantidad, oferta_venta["cantidad"], oferta_compra["cantidad"])
        if cantidad_real <= 0:
            return False

        precio_unitario = oferta_venta["precio_unitario"]
        transaccion: Transaccion = {
            "fecha_tick": self.simulador.tick,
            "vendedor_id": oferta_venta["agente_id"],
            "comprador_id": oferta_compra["agente_id"],
            "producto": oferta_venta["producto"],
            "cantidad": cantidad_real,
            "precio_unitario": precio_unitario,
            "calidad": oferta_venta["calidad"],
            "total": precio_unitario * cantidad_real,
        }
        self.historial_transacciones.append(transaccion)

        oferta_venta["cantidad"] -= cantidad_real
        oferta_compra["cantidad"] -= cantidad_real

        if oferta_venta["cantidad"] <= 0:
            oferta_venta["activa"] = False
        if oferta_compra["cantidad"] <= 0:
            oferta_compra["activa"] = False

        self._actualizar_estadisticas(transaccion)
        return transaccion

    def _actualizar_estadisticas(self, transaccion: Transaccion) -> None:
        producto = transaccion["producto"]

        if producto not in self.estadisticas:
            self.estadisticas[producto] = {
                "precios": [],
                "ultimo_precio": 0,
                "precio_promedio": 0,
                "precio_minimo": float("inf"),
                "precio_maximo": 0,
                "volumen_total": 0,
                "tendencia": "estable",
            }

        stats = self.estadisticas[producto]
        stats["precios"].append(transaccion["precio_unitario"])
        stats["ultimo_precio"] = transaccion["precio_unitario"]
        stats["volumen_total"] += transaccion["cantidad"]

        ultimos = stats["precios"][-50:]
        stats["precio_promedio"] = sum(ultimos) / len(ultimos)
        stats["precio_minimo"] = min(ultimos)
        stats["precio_maximo"] = max(ultimos)

        if len(ultimos) >= 10:
            primeros = sum(ultimos[:5]) / 5
            ultimos_5 = sum(ultimos[-5:]) / 5
            if ultimos_5 > primeros * 1.1:
                stats["tendencia"] = "subiendo"
            elif ultimos_5 < primeros * 0.9:
                stats["tendencia"] = "bajando"
            else:
                stats["tendencia"] = "estable"

    def obtener_info_producto(self, producto: str) -> dict[str, Any]:
        stats = self.estadisticas.get(
            producto,
            {
                "precio_promedio": 0,
                "precio_minimo": 0,
                "precio_maximo": 0,
                "ultimo_precio": 0,
                "tendencia": "sin datos",
                "volumen_total": 0,
            },
        )

        ofertas_venta = [o for o in self.ofertas_venta if o["producto"] == producto and o["activa"]]
        ofertas_compra = [o for o in self.ofertas_compra if o["producto"] == producto and o["activa"]]

        return {
            "nombre": producto,
            "estadisticas": stats,
            "ofertas_venta_activas": len(ofertas_venta),
            "ofertas_compra_activas": len(ofertas_compra),
            "precio_venta_minimo": min([o["precio_unitario"] for o in ofertas_venta]) if ofertas_venta else 0,
            "precio_compra_maximo": max([o["precio_maximo"] for o in ofertas_compra]) if ofertas_compra else 0,
        }
