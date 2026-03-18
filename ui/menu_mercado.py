import pygame


class MenuMercado:
    def __init__(self, simulador):
        self.sim = simulador
        self.visible = False
        self.modo = "principal"  # principal, comprar, vender, ofertar_venta, ofertar_compra, cancelar_oferta
        self.producto_seleccionado = None
        self.oferta_seleccionada = None
        self.filtros = {
            "nombre_articulo": None,
            "categoria": None,
            "tipo_alimento": None,
            "calidad_min": None,
            "precio_max": None,
            "precio_min": None,
        }

        self.x, self.y = 180, 70
        self.ancho, self.alto = 860, 560
        self._boton_cerrar_rect = pygame.Rect(0, 0, 0, 0)
        self._boton_atras_rect = pygame.Rect(0, 0, 0, 0)
        self._items_clickables = []
        self._filtro_categoria_idx = 0
        self._filtro_tipo_idx = 0
        self._filtro_producto_idx = 0
        self._cantidad_compra = 1
        self._mensaje_estado = ""

    def actualizar_filtros(self, **filtros):
        for clave, valor in filtros.items():
            if clave in self.filtros:
                self.filtros[clave] = valor

    def limpiar_filtros(self):
        for clave in self.filtros:
            self.filtros[clave] = None

    def mostrar(self):
        self.visible = True
        self.modo = "principal"
        self.producto_seleccionado = None
        self.oferta_seleccionada = None

    def ocultar(self):
        self.visible = False
        self._items_clickables = []

    def procesar_eventos_teclado(self, tecla):
        """Solo consume ESC para volver atrás dentro del menú."""
        if not self.visible:
            return False

        if tecla == pygame.K_ESCAPE:
            if self.modo == "principal":
                self.ocultar()
            else:
                self.modo = "principal"
                self.oferta_seleccionada = None
            return True

        return False

    def procesar_eventos(self, evento):
        """Compatibilidad con llamadas antiguas basadas en eventos pygame."""
        if not self.visible:
            return False
        if evento.type == pygame.KEYDOWN:
            return self.procesar_eventos_teclado(evento.key)
        return False

    def procesar_clic(self, pos_mouse):
        """Consume clics dentro del mercado para evitar clics en el mapa."""
        if not self.visible:
            return False

        if self._boton_cerrar_rect.collidepoint(pos_mouse):
            self.ocultar()
            return True

        if self.modo != "principal" and self._boton_atras_rect.collidepoint(pos_mouse):
            self.modo = "principal"
            self.oferta_seleccionada = None
            return True

        for item in self._items_clickables:
            if item["rect"].collidepoint(pos_mouse):
                accion = item["accion"]
                accion(item.get("payload"))
                return True

        if pygame.Rect(self.x, self.y, self.ancho, self.alto).collidepoint(pos_mouse):
            return True

        return False

    def dibujar(self, pantalla):
        if not self.visible:
            return

        self._items_clickables = []
        font_titulo = pygame.font.SysFont(None, 36)
        font_texto = pygame.font.SysFont(None, 24)

        fondo = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        fondo.fill((40, 40, 60, 240))
        pantalla.blit(fondo, (self.x, self.y))

        pygame.draw.rect(pantalla, (100, 100, 150), (self.x, self.y, self.ancho, self.alto), 2)

        titulo = font_titulo.render("MERCADO", True, (255, 255, 200))
        pantalla.blit(titulo, (self.x + 20, self.y + 15))

        self._boton_cerrar_rect = pygame.Rect(self.x + self.ancho - 45, self.y + 12, 30, 30)
        pygame.draw.rect(pantalla, (120, 60, 60), self._boton_cerrar_rect, border_radius=4)
        pantalla.blit(font_texto.render("X", True, (255, 240, 240)), (self._boton_cerrar_rect.x + 8, self._boton_cerrar_rect.y + 6))

        self._boton_atras_rect = pygame.Rect(self.x + self.ancho - 90, self.y + 12, 35, 30)
        if self.modo != "principal":
            pygame.draw.rect(pantalla, (70, 90, 130), self._boton_atras_rect, border_radius=4)
            pantalla.blit(font_texto.render("<-", True, (235, 235, 255)), (self._boton_atras_rect.x + 7, self._boton_atras_rect.y + 6))

        if self.modo == "principal":
            self._dibujar_principal(pantalla)
        elif self.modo == "comprar":
            self._dibujar_comprar(pantalla)
        elif self.modo == "vender":
            self._dibujar_vender(pantalla)
        elif self.modo == "ofertar_venta":
            self._dibujar_ofertar_venta(pantalla)
        elif self.modo == "ofertar_compra":
            self._dibujar_ofertar_compra(pantalla)
        elif self.modo == "cancelar_oferta":
            self._dibujar_cancelar_oferta(pantalla)

    def _dibujar_boton_accion(self, pantalla, y, texto, accion):
        font = pygame.font.SysFont(None, 28)
        rect = pygame.Rect(self.x + 30, y, self.ancho - 60, 44)
        pygame.draw.rect(pantalla, (70, 70, 100), rect, border_radius=6)
        pygame.draw.rect(pantalla, (120, 120, 170), rect, 1, border_radius=6)
        pantalla.blit(font.render(texto, True, (240, 240, 230)), (rect.x + 15, rect.y + 11))
        self._items_clickables.append({"rect": rect, "accion": accion})

    def _dibujar_principal(self, pantalla):
        y = self.y + 70
        self._dibujar_boton_accion(pantalla, y, "Comprar", lambda _payload: self._cambiar_modo("comprar"))
        self._dibujar_boton_accion(pantalla, y + 54, "Vender", lambda _payload: self._cambiar_modo("vender"))
        self._dibujar_boton_accion(pantalla, y + 108, "Ofertar compra", lambda _payload: self._cambiar_modo("ofertar_compra"))
        self._dibujar_boton_accion(pantalla, y + 162, "Ofertar venta", lambda _payload: self._cambiar_modo("ofertar_venta"))
        self._dibujar_boton_accion(pantalla, y + 216, "Cancelar oferta", lambda _payload: self._cambiar_modo("cancelar_oferta"))

    def _cambiar_modo(self, modo):
        self.modo = modo
        self.oferta_seleccionada = None
        self._cantidad_compra = 1
        self._mensaje_estado = ""

    def _dibujar_comprar(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        pantalla.blit(font.render("Comprar (ofertas de venta, menor a mayor)", True, (230, 230, 210)), (self.x + 30, self.y + 70))

        categorias = ["todas"] + self._obtener_categorias_disponibles()
        tipos = ["todos"] + self._obtener_tipos_disponibles()

        if self._filtro_categoria_idx >= len(categorias):
            self._filtro_categoria_idx = 0
        if self._filtro_tipo_idx >= len(tipos):
            self._filtro_tipo_idx = 0

        categoria_valor = None if categorias[self._filtro_categoria_idx] == "todas" else categorias[self._filtro_categoria_idx]
        tipo_valor = None if tipos[self._filtro_tipo_idx] == "todos" else tipos[self._filtro_tipo_idx]

        productos = ["todos"] + self.sim.economia.filtrar_productos(categoria=categoria_valor, tipo_alimento=tipo_valor)
        if self._filtro_producto_idx >= len(productos):
            self._filtro_producto_idx = 0
        producto_valor = None if productos[self._filtro_producto_idx] == "todos" else productos[self._filtro_producto_idx]

        self._dibujar_boton_filtro(
            pantalla,
            texto=f"Categoría: {categorias[self._filtro_categoria_idx]}",
            x=self.x + 30,
            y=self.y + 102,
            accion=lambda _payload: self._ciclar_filtro("categoria"),
        )
        self._dibujar_boton_filtro(
            pantalla,
            texto=f"Tipo: {tipos[self._filtro_tipo_idx]}",
            x=self.x + 300,
            y=self.y + 102,
            accion=lambda _payload: self._ciclar_filtro("tipo"),
        )
        self._dibujar_boton_filtro(
            pantalla,
            texto=f"Producto: {productos[self._filtro_producto_idx]}",
            x=self.x + 530,
            y=self.y + 102,
            accion=lambda _payload: self._ciclar_filtro("producto", productos),
        )

        ofertas = self.sim.economia.listar_ofertas_venta_filtradas(
            nombre_articulo=producto_valor,
            categoria=categoria_valor,
            tipo_alimento=tipo_valor,
            calidad_min=self.filtros["calidad_min"],
            precio_max=self.filtros["precio_max"],
        )

        if not ofertas:
            pantalla.blit(font.render("No hay ofertas de venta con los filtros actuales.", True, (200, 200, 200)), (self.x + 30, self.y + 140))
            return

        y = self.y + 140
        for oferta in ofertas[:12]:
            vendedor = self._get_agente_by_id(oferta["agente_id"])
            nombre = vendedor.nombre if vendedor else "Desconocido"
            texto = (
                f"#{oferta['id']} {oferta['producto']} | {nombre} | cant:{oferta['cantidad']} "
                f"| precio:{oferta['precio_unitario']:.2f} | cal:{oferta['calidad']:.1f}"
            )
            rect = pygame.Rect(self.x + 30, y, self.ancho - 60, 28)
            color = (62, 88, 62) if self.oferta_seleccionada and self.oferta_seleccionada["id"] == oferta["id"] else (62, 62, 88)
            pygame.draw.rect(pantalla, color, rect, border_radius=4)
            pantalla.blit(font.render(texto, True, (225, 225, 225)), (rect.x + 8, rect.y + 5))
            self._items_clickables.append({"rect": rect, "accion": self._seleccionar_oferta_compra, "payload": oferta})
            y += 32

        if self.oferta_seleccionada:
            self._dibujar_panel_compra(pantalla, self.oferta_seleccionada)

        if self._mensaje_estado:
            pantalla.blit(font.render(self._mensaje_estado, True, (200, 255, 200)), (self.x + 30, self.y + self.alto - 35))

    def _dibujar_vender(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        pantalla.blit(font.render("Vender (ofertas de compra, mayor a menor)", True, (230, 230, 210)), (self.x + 30, self.y + 70))

        ofertas = self.sim.economia.listar_ofertas_compra_filtradas(
            nombre_articulo=self.filtros["nombre_articulo"],
            categoria=self.filtros["categoria"],
            tipo_alimento=self.filtros["tipo_alimento"],
            precio_min=self.filtros["precio_min"],
        )

        if not ofertas:
            pantalla.blit(font.render("No hay ofertas de compra con los filtros actuales.", True, (200, 200, 200)), (self.x + 30, self.y + 110))
            return

        y = self.y + 110
        for oferta in ofertas[:12]:
            comprador = self._get_agente_by_id(oferta["agente_id"])
            nombre = comprador.nombre if comprador else "Desconocido"
            texto = f"{oferta['producto']} | {nombre} | {oferta['cantidad']} x {oferta['precio_maximo']} (máx.)"
            rect = pygame.Rect(self.x + 30, y, self.ancho - 60, 28)
            pygame.draw.rect(pantalla, (62, 62, 88), rect, border_radius=4)
            pantalla.blit(font.render(texto, True, (225, 225, 225)), (rect.x + 8, rect.y + 5))
            y += 32

    def _dibujar_ofertar_venta(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        mensajes = [
            "Ofertar venta:",
            "1) Selecciona un producto de inventario.",
            "2) Define cantidad, precio unitario y calidad.",
            "3) Publica la oferta.",
            "(Pendiente: formulario interactivo dentro del menú)",
        ]
        y = self.y + 75
        for msg in mensajes:
            pantalla.blit(font.render(msg, True, (220, 220, 220)), (self.x + 30, y))
            y += 28

    def _dibujar_ofertar_compra(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        mensajes = [
            "Ofertar compra:",
            "1) Busca producto con filtros.",
            "2) Define cantidad y precio máximo.",
            "3) Publica la oferta.",
            "(Pendiente: formulario interactivo dentro del menú)",
        ]
        y = self.y + 75
        for msg in mensajes:
            pantalla.blit(font.render(msg, True, (220, 220, 220)), (self.x + 30, y))
            y += 28

    def _dibujar_cancelar_oferta(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        pantalla.blit(font.render("Cancelar oferta propia (clic para dar de baja)", True, (230, 230, 210)), (self.x + 30, self.y + 70))

        agente = self.sim.agente_jugador
        if not agente:
            pantalla.blit(font.render("No hay agente jugador activo.", True, (210, 180, 180)), (self.x + 30, self.y + 110))
            return

        ofertas_propias = []
        for oferta in self.sim.economia.ofertas_venta:
            if oferta["agente_id"] == agente.id and oferta["activa"]:
                ofertas_propias.append(("venta", oferta))
        for oferta in self.sim.economia.ofertas_compra:
            if oferta["agente_id"] == agente.id and oferta["activa"]:
                ofertas_propias.append(("compra", oferta))

        if not ofertas_propias:
            pantalla.blit(font.render("No tienes ofertas activas.", True, (200, 200, 200)), (self.x + 30, self.y + 110))
            return

        y = self.y + 110
        for tipo, oferta in ofertas_propias[:12]:
            if tipo == "venta":
                texto = f"[VENTA] #{oferta['id']} {oferta['producto']} - {oferta['cantidad']} x {oferta['precio_unitario']}"
            else:
                texto = f"[COMPRA] #{oferta['id']} {oferta['producto']} - {oferta['cantidad']} x {oferta['precio_maximo']} max"

            rect = pygame.Rect(self.x + 30, y, self.ancho - 60, 28)
            pygame.draw.rect(pantalla, (82, 66, 66), rect, border_radius=4)
            pantalla.blit(font.render(texto, True, (240, 230, 230)), (rect.x + 8, rect.y + 5))

            self._items_clickables.append(
                {
                    "rect": rect,
                    "accion": self._cancelar_oferta_desde_click,
                    "payload": {"tipo": tipo, "id": oferta["id"]},
                }
            )
            y += 32

    def _cancelar_oferta_desde_click(self, payload):
        if not payload:
            return
        agente = self.sim.agente_jugador
        if not agente:
            return
        self.sim.acciones.accion_cancelar_oferta(agente, payload["id"], payload["tipo"])

    def _dibujar_boton_filtro(self, pantalla, texto, x, y, accion):
        font = pygame.font.SysFont(None, 22)
        rect = pygame.Rect(x, y, 240, 28)
        pygame.draw.rect(pantalla, (58, 70, 95), rect, border_radius=4)
        pantalla.blit(font.render(texto, True, (230, 230, 235)), (rect.x + 8, rect.y + 5))
        self._items_clickables.append({"rect": rect, "accion": accion})

    def _ciclar_filtro(self, filtro, productos=None):
        if filtro == "categoria":
            self._filtro_categoria_idx += 1
            self._filtro_producto_idx = 0
        elif filtro == "tipo":
            self._filtro_tipo_idx += 1
            self._filtro_producto_idx = 0
        elif filtro == "producto":
            self._filtro_producto_idx += 1
            if productos is not None and self._filtro_producto_idx >= len(productos):
                self._filtro_producto_idx = 0

    def _obtener_categorias_disponibles(self):
        categorias = set()
        for metadata in self.sim.economia.catalogo_productos.values():
            categoria = metadata.get("categoria")
            if categoria:
                categorias.add(categoria)
        return sorted(categorias)

    def _obtener_tipos_disponibles(self):
        tipos = set()
        for metadata in self.sim.economia.catalogo_productos.values():
            tipo = metadata.get("tipo_alimento")
            if tipo:
                tipos.add(tipo)
        return sorted(tipos)

    def _seleccionar_oferta_compra(self, oferta):
        if oferta:
            self.oferta_seleccionada = oferta
            self._cantidad_compra = 1

    def _dibujar_panel_compra(self, pantalla, oferta):
        font = pygame.font.SysFont(None, 22)
        panel = pygame.Rect(self.x + 30, self.y + self.alto - 130, self.ancho - 60, 90)
        pygame.draw.rect(pantalla, (42, 65, 48), panel, border_radius=6)

        max_cantidad = max(1, oferta["cantidad"])
        self._cantidad_compra = min(max(1, self._cantidad_compra), max_cantidad)
        costo = self._cantidad_compra * oferta["precio_unitario"]
        texto = f"Selección #{oferta['id']} | cantidad: {self._cantidad_compra} / {max_cantidad} | total: {costo:.2f}"
        pantalla.blit(font.render(texto, True, (230, 250, 230)), (panel.x + 10, panel.y + 10))

        menos = pygame.Rect(panel.x + 10, panel.y + 40, 30, 30)
        mas = pygame.Rect(panel.x + 50, panel.y + 40, 30, 30)
        comprar = pygame.Rect(panel.x + 100, panel.y + 40, 140, 30)
        pygame.draw.rect(pantalla, (90, 90, 120), menos, border_radius=4)
        pygame.draw.rect(pantalla, (90, 90, 120), mas, border_radius=4)
        pygame.draw.rect(pantalla, (70, 120, 80), comprar, border_radius=4)
        pantalla.blit(font.render("-", True, (245, 245, 255)), (menos.x + 10, menos.y + 5))
        pantalla.blit(font.render("+", True, (245, 245, 255)), (mas.x + 8, mas.y + 5))
        pantalla.blit(font.render("Comprar", True, (245, 255, 245)), (comprar.x + 28, comprar.y + 5))

        self._items_clickables.append({"rect": menos, "accion": lambda _payload: self._ajustar_cantidad_compra(-1)})
        self._items_clickables.append({"rect": mas, "accion": lambda _payload: self._ajustar_cantidad_compra(+1)})
        self._items_clickables.append({"rect": comprar, "accion": lambda _payload: self._ejecutar_compra(oferta)})

    def _ajustar_cantidad_compra(self, delta):
        self._cantidad_compra = max(1, self._cantidad_compra + delta)

    def _ejecutar_compra(self, oferta):
        agente = self.sim.agente_jugador
        if not agente:
            self._mensaje_estado = "No hay agente jugador."
            return
        resultado = self.sim.acciones.accion_comprar(agente, oferta["id"], self._cantidad_compra)
        if resultado:
            self._mensaje_estado = "Compra realizada."
            self.oferta_seleccionada = None
        else:
            self._mensaje_estado = "No se pudo completar la compra."

    def _get_agente_by_id(self, agente_id):
        for agente in self.sim.agentes:
            if agente.id == agente_id:
                return agente
        return None
