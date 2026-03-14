# menu_mercado.py - Interfaz de usuario
import pygame

class MenuMercado:
    def __init__(self, simulador):
        self.sim = simulador
        self.visible = False
        self.modo = "principal"  # principal, ver_producto, comprar, vender, ofertar
        self.producto_seleccionado = None
        self.oferta_seleccionada = None

    def mostrar(self):
        self.visible = True
        self.modo = "ver_producto"

    def ocultar(self):
        self.visible = False

    def procesar_eventos(self, evento):
        """Procesa clics/teclas en el menú"""
        if not self.visible:
            return False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if self.modo == "principal":
                    self.ocultar()
                else:
                    self.modo = "principal"
                return True

        return False

    def dibujar(self, pantalla):
        """Dibuja la interfaz del mercado"""
        if not self.visible:
            return

        # Fondo
        s = pygame.Surface((800, 600), pygame.SRCALPHA)
        s.fill((40, 40, 60, 240))
        pantalla.blit(s, (200, 100))


        if self.modo == "principal":
            self._dibujar_principal(pantalla)
        elif self.modo == "ver_producto":
            self._dibujar_producto(pantalla)
        elif self.modo == "comprar":
            self._dibujar_comprar(pantalla)
        elif self.modo == "vender":
            self._dibujar_vender(pantalla)
        elif self.modo == "ofertar_venta":
            self._dibujar_ofertar_venta(pantalla)
        elif self.modo == "ofertar_compra":
            self._dibujar_ofertar_compra(pantalla)

    def _dibujar_principal(self, pantalla):
        """Pantalla principal del mercado"""
        x, y = 220, 120
        font_titulo = pygame.font.SysFont(None, 36)
        font_texto = pygame.font.SysFont(None, 24)

        # Título
        titulo = font_titulo.render("MERCADO", True, (255, 255, 200))
        pantalla.blit(titulo, (x, y))

        # Lista de productos
        productos = list(self.sim.economia.estadisticas.keys())
        y_actual = y + 50

        for i, producto in enumerate(productos[:15]):
            stats = self.sim.economia.estadisticas.get(producto, {})
            info = self.sim.economia.obtener_info_producto(producto)

            texto = f"{i+1}. {producto.capitalize()}: {stats.get('precio_promedio', 0):.1f} ({info['ofertas_venta_activas']} ventas / {info['ofertas_compra_activas']} compras)"
            superficie = font_texto.render(texto, True, (220, 220, 220))
            pantalla.blit(superficie, (x, y_actual))
            y_actual += 25

        # Instrucciones
        y_actual = 650
        instrucciones = font_texto.render("Click en producto para ver detalles | ESC: Salir", True, (150, 150, 150))
        pantalla.blit(instrucciones, (x, y_actual))

    def _dibujar_producto(self, pantalla):
        """Detalle de un producto específico"""
        if not self.producto_seleccionado:
            self.modo = "principal"
            return

        x, y = 220, 120
        font_titulo = pygame.font.SysFont(None, 36)
        font_texto = pygame.font.SysFont(None, 24)

        producto = self.producto_seleccionado
        info = self.sim.economia.obtener_info_producto(producto)
        stats = info["estadisticas"]

        # Título
        titulo = font_titulo.render(f"{producto.capitalize()}", True, (255, 255, 200))
        pantalla.blit(titulo, (x, y))

        # Estadísticas
        y_actual = y + 50
        textos = [
            f"Precio promedio: {stats.get('precio_promedio', 0):.1f}",
            f"Precio mínimo: {stats.get('precio_minimo', 0)}",
            f"Precio máximo: {stats.get('precio_maximo', 0)}",
            f"Tendencia: {stats.get('tendencia', 'sin datos')}",
            f"Volumen total: {stats.get('volumen_total', 0)}",
            f"Ofertas de venta: {info['ofertas_venta_activas']}",
            f"Ofertas de compra: {info['ofertas_compra_activas']}"
        ]

        for texto in textos:
            superficie = font_texto.render(texto, True, (220, 220, 220))
            pantalla.blit(superficie, (x, y_actual))
            y_actual += 25

        # Opciones
        y_actual += 20
        opciones = [
            "1. Comprar (ver ofertas de venta)",
            "2. Vender (ver ofertas de compra)",
            "3. Ofertar venta (publicar para vender)",
            "4. Ofertar compra (publicar para comprar)",
            "5. Volver"
        ]

        for texto in opciones:
            superficie = font_texto.render(texto, True, (200, 200, 100))
            pantalla.blit(superficie, (x, y_actual))
            y_actual += 25

    def _dibujar_comprar(self, pantalla):
        """Interfaz para comprar (ver ofertas de venta)"""
        if not self.producto_seleccionado:
            self.modo = "principal"
            return

        x, y = 220, 120
        font_titulo = pygame.font.SysFont(None, 36)
        font_texto = pygame.font.SysFont(None, 24)

        producto = self.producto_seleccionado
        ofertas = self.sim.economia.buscar_ofertas_venta(producto=producto)

        titulo = font_titulo.render(f"Comprar {producto.capitalize()}", True, (255, 255, 200))
        pantalla.blit(titulo, (x, y))

        y_actual = y + 50
        if not ofertas:
            texto = font_texto.render("No hay ofertas de venta disponibles", True, (200, 200, 200))
            pantalla.blit(texto, (x, y_actual))
        else:
            for i, oferta in enumerate(ofertas[:10]):
                vendedor = self._get_agente_by_id(oferta["agente_id"])
                nombre = vendedor.nombre if vendedor else "Desconocido"

                texto = f"{i+1}. {nombre}: {oferta['cantidad']} x {oferta['precio_unitario']} (calidad {oferta['calidad']:.1f})"
                superficie = font_texto.render(texto, True, (220, 220, 220))
                pantalla.blit(superficie, (x, y_actual))
                y_actual += 20

    def _get_agente_by_id(self, agente_id):
        """Busca un agente por ID"""
        for agente in self.sim.agentes:
            if agente.id == agente_id:
                return agente
        return None
