import logging

logger = logging.getLogger(__name__)
# sistema/economia.py

class SistemaEconomico:
    def __init__(self, simulador):
        # Registro de ofertas activas
        self.ofertas_venta = []  # Lista de ofertas de venta
        self.ofertas_compra = []  # Lista de ofertas de compra

        # Historial de transacciones completadas
        self.historial_transacciones = []

        # Estadísticas por producto
        self.estadisticas = {}

        self.simulador = simulador

    def publicar_oferta_venta(self, agente_id, producto, cantidad, precio_unitario, calidad=1.0):
        """Un agente ofrece vender un producto"""
        oferta = {
            "id": len(self.ofertas_venta) + len(self.historial_transacciones),
            "agente_id": agente_id,
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "calidad": calidad,  # Factor de calidad (1.0 = normal)
            "fecha_tick": self.simulador.tick,
            "activa": True
        }
        self.ofertas_venta.append(oferta)
        logger.debug(f"📢 Agente {agente_id} ofrece {cantidad} {producto} a {precio_unitario} monedas")
        return oferta["id"]

    def publicar_oferta_compra(self, agente_id, producto, cantidad, precio_maximo):
        """Un agente busca comprar un producto"""
        oferta = {
            "id": len(self.ofertas_compra) + len(self.historial_transacciones),
            "agente_id": agente_id,
            "producto": producto,
            "cantidad": cantidad,
            "precio_maximo": precio_maximo,
            "fecha_tick": self.simulador.tick,
            "activa": True
        }
        self.ofertas_compra.append(oferta)
        logger.debug(f"📢 Agente {agente_id} busca comprar {cantidad} {producto} (max {precio_maximo})")
        return oferta["id"]

    def buscar_ofertas_venta(self, producto=None, precio_max=None, calidad_min=None):
        """Busca ofertas de venta activas"""
        resultados = []
        for oferta in self.ofertas_venta:
            if not oferta["activa"]:
                continue

            if producto and oferta["producto"] != producto:
                continue

            if precio_max and oferta["precio_unitario"] > precio_max:
                continue

            if calidad_min and oferta["calidad"] < calidad_min:
                continue

            resultados.append(oferta)

        # Ordenar por precio (menor primero)
        return sorted(resultados, key=lambda x: x["precio_unitario"])

    def get_oferta_venta(self, oferta_id):
        """Obtiene una oferta de venta por ID."""
        return next((oferta for oferta in self.ofertas_venta if oferta["id"] == oferta_id), None)

    def buscar_ofertas_compra(self, producto=None, precio_min=None):
        """Busca ofertas de compra activas"""
        resultados = []
        for oferta in self.ofertas_compra:
            if not oferta["activa"]:
                continue

            if producto and oferta["producto"] != producto:
                continue

            if precio_min and oferta["precio_maximo"] < precio_min:
                continue

            resultados.append(oferta)

        # Ordenar por precio (mayor primero)
        return sorted(resultados, key=lambda x: x["precio_maximo"], reverse=True)

    def get_oferta_compra(self, oferta_id):
        """Obtiene una oferta de compra por ID."""
        return next((oferta for oferta in self.ofertas_compra if oferta["id"] == oferta_id), None)

    def realizar_transaccion(self, oferta_venta_id, oferta_compra_id, cantidad):
        """Realiza una transacción entre dos agentes"""
        # Buscar ofertas
        oferta_venta = next((o for o in self.ofertas_venta if o["id"] == oferta_venta_id), None)
        oferta_compra = next((o for o in self.ofertas_compra if o["id"] == oferta_compra_id), None)

        if not oferta_venta or not oferta_compra:
            return False

        if not oferta_venta["activa"] or not oferta_compra["activa"]:
            return False

        # Verificar cantidad
        cantidad_real = min(cantidad, oferta_venta["cantidad"], oferta_compra["cantidad"])
        if cantidad_real <= 0:
            return False

        # Precio de la transacción (punto medio o precio de oferta)
        precio_unitario = oferta_venta["precio_unitario"]

        # Registrar transacción
        transaccion = {
            "fecha_tick": self.simulador.tick,
            "vendedor_id": oferta_venta["agente_id"],
            "comprador_id": oferta_compra["agente_id"],
            "producto": oferta_venta["producto"],
            "cantidad": cantidad_real,
            "precio_unitario": precio_unitario,
            "calidad": oferta_venta["calidad"],
            "total": precio_unitario * cantidad_real
        }
        self.historial_transacciones.append(transaccion)

        # Actualizar ofertas
        oferta_venta["cantidad"] -= cantidad_real
        oferta_compra["cantidad"] -= cantidad_real

        if oferta_venta["cantidad"] <= 0:
            oferta_venta["activa"] = False

        if oferta_compra["cantidad"] <= 0:
            oferta_compra["activa"] = False

        # Actualizar estadísticas
        self._actualizar_estadisticas(transaccion)

        return transaccion

    def _actualizar_estadisticas(self, transaccion):
        """Actualiza estadísticas de precios por producto"""
        producto = transaccion["producto"]

        if producto not in self.estadisticas:
            self.estadisticas[producto] = {
                "precios": [],
                "ultimo_precio": 0,
                "precio_promedio": 0,
                "precio_minimo": float('inf'),
                "precio_maximo": 0,
                "volumen_total": 0,
                "tendencia": "estable"
            }

        stats = self.estadisticas[producto]
        stats["precios"].append(transaccion["precio_unitario"])
        stats["ultimo_precio"] = transaccion["precio_unitario"]
        stats["volumen_total"] += transaccion["cantidad"]

        # Calcular promedios (últimos 50)
        ultimos = stats["precios"][-50:]
        stats["precio_promedio"] = sum(ultimos) / len(ultimos)
        stats["precio_minimo"] = min(ultimos)
        stats["precio_maximo"] = max(ultimos)

        # Calcular tendencia
        if len(ultimos) >= 10:
            primeros = sum(ultimos[:5]) / 5
            ultimos_5 = sum(ultimos[-5:]) / 5
            if ultimos_5 > primeros * 1.1:
                stats["tendencia"] = "subiendo"
            elif ultimos_5 < primeros * 0.9:
                stats["tendencia"] = "bajando"
            else:
                stats["tendencia"] = "estable"

    def obtener_info_producto(self, producto):
        """Retorna información de mercado para un producto"""
        stats = self.estadisticas.get(producto, {
            "precio_promedio": 0,
            "precio_minimo": 0,
            "precio_maximo": 0,
            "ultimo_precio": 0,
            "tendencia": "sin datos",
            "volumen_total": 0
        })

        # Ofertas activas
        ofertas_venta = [o for o in self.ofertas_venta if o["producto"] == producto and o["activa"]]
        ofertas_compra = [o for o in self.ofertas_compra if o["producto"] == producto and o["activa"]]

        return {
            "nombre": producto,
            "estadisticas": stats,
            "ofertas_venta_activas": len(ofertas_venta),
            "ofertas_compra_activas": len(ofertas_compra),
            "precio_venta_minimo": min([o["precio_unitario"] for o in ofertas_venta]) if ofertas_venta else 0,
            "precio_compra_maximo": max([o["precio_maximo"] for o in ofertas_compra]) if ofertas_compra else 0
        }
