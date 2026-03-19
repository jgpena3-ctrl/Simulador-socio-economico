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
        self._cantidad_venta = 1
        self._cantidad_oferta = 1
        self._precio_oferta = 5.0
        self._calidad_oferta = 1.0
        self._producto_oferta_idx = 0
        self._producto_objetivo_idx = 0
        self._mensaje_estado = ""
        self._busqueda_texto = ""

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

    def procesar_eventos_teclado(self, tecla, texto=""):
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

        if self.modo == "comprar":
            if tecla == pygame.K_BACKSPACE:
                self._busqueda_texto = self._busqueda_texto[:-1]
                return True
            if texto and texto.isprintable():
                self._busqueda_texto += texto.lower()
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
        self._cantidad_venta = 1
        self._mensaje_estado = ""
        self._busqueda_texto = ""

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
        texto_busqueda = f"Búsqueda: {self._busqueda_texto or '(escribe para filtrar)'}"
        pantalla.blit(font.render(texto_busqueda, True, (215, 215, 215)), (self.x + 30, self.y + 132))

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
            if self._busqueda_texto and not self._coincide_busqueda(oferta, nombre):
                continue
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
        pantalla.blit(font.render("Vender (selecciona artículo propio + comprador)", True, (230, 230, 210)), (self.x + 30, self.y + 70))

        productos_jugador = self._productos_vendibles_jugador()
        if not productos_jugador:
            pantalla.blit(font.render("No tienes artículos vendibles en inventario.", True, (200, 200, 200)), (self.x + 30, self.y + 110))
            return

        if self._producto_oferta_idx >= len(productos_jugador):
            self._producto_oferta_idx = 0
        producto = productos_jugador[self._producto_oferta_idx]

        self._dibujar_boton_filtro(
            pantalla,
            texto=f"Producto inventario: {producto}",
            x=self.x + 30,
            y=self.y + 102,
            accion=lambda _payload: self._ciclar_producto_inventario(productos_jugador),
        )

        ofertas = self.sim.economia.listar_ofertas_compra_filtradas(
            nombre_articulo=producto,
            categoria=None,
            tipo_alimento=None,
            precio_min=self.filtros["precio_min"],
        )

        if not ofertas:
            pantalla.blit(font.render("No hay compradores para ese artículo.", True, (200, 200, 200)), (self.x + 30, self.y + 140))
            return

        y = self.y + 140
        for oferta in ofertas[:12]:
            comprador = self._get_agente_by_id(oferta["agente_id"])
            nombre = comprador.nombre if comprador else "Desconocido"
            texto = f"#{oferta['id']} {oferta['producto']} | {nombre} | cant:{oferta['cantidad']} | precio máx:{oferta['precio_maximo']:.2f}"
            rect = pygame.Rect(self.x + 30, y, self.ancho - 60, 28)
            color = (88, 68, 62) if self.oferta_seleccionada and self.oferta_seleccionada["id"] == oferta["id"] else (62, 62, 88)
            pygame.draw.rect(pantalla, color, rect, border_radius=4)
            pantalla.blit(font.render(texto, True, (225, 225, 225)), (rect.x + 8, rect.y + 5))
            self._items_clickables.append({"rect": rect, "accion": self._seleccionar_oferta_venta, "payload": oferta})
            y += 32

        if self.oferta_seleccionada:
            self._dibujar_panel_venta(pantalla, self.oferta_seleccionada, producto)

        if self._mensaje_estado:
            pantalla.blit(font.render(self._mensaje_estado, True, (200, 255, 200)), (self.x + 30, self.y + self.alto - 35))

    def _dibujar_ofertar_venta(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        pantalla.blit(font.render("Ofertar venta", True, (230, 230, 210)), (self.x + 30, self.y + 70))
        productos = self._productos_vendibles_jugador()
        if not productos:
            pantalla.blit(font.render("No tienes artículos en inventario para ofertar.", True, (210, 200, 200)), (self.x + 30, self.y + 110))
            return
        if self._producto_oferta_idx >= len(productos):
            self._producto_oferta_idx = 0
        producto = productos[self._producto_oferta_idx]

        self._dibujar_boton_filtro(
            pantalla, f"Producto: {producto}", self.x + 30, self.y + 105,
            lambda _payload: self._ciclar_producto_inventario(productos)
        )
        self._dibujar_controles_valor(
            pantalla,
            etiqueta=f"Cantidad: {self._cantidad_oferta}",
            y=self.y + 145,
            decrementar=lambda: self._ajustar_cantidad_oferta(-1),
            incrementar=lambda: self._ajustar_cantidad_oferta(+1),
        )
        self._dibujar_controles_valor(
            pantalla,
            etiqueta=f"Precio unitario: {self._precio_oferta:.2f}",
            y=self.y + 185,
            decrementar=lambda: self._ajustar_precio_oferta(-1),
            incrementar=lambda: self._ajustar_precio_oferta(+1),
        )
        self._dibujar_controles_valor(
            pantalla,
            etiqueta=f"Calidad: {self._calidad_oferta:.1f}",
            y=self.y + 225,
            decrementar=lambda: self._ajustar_calidad_oferta(-0.1),
            incrementar=lambda: self._ajustar_calidad_oferta(+0.1),
        )
        publicar = pygame.Rect(self.x + 30, self.y + 270, 180, 32)
        pygame.draw.rect(pantalla, (70, 120, 80), publicar, border_radius=4)
        pantalla.blit(font.render("Publicar venta", True, (245, 255, 245)), (publicar.x + 20, publicar.y + 7))
        self._items_clickables.append({"rect": publicar, "accion": lambda _payload: self._publicar_oferta_venta(producto)})
        if self._mensaje_estado:
            pantalla.blit(font.render(self._mensaje_estado, True, (200, 255, 200)), (self.x + 30, self.y + 320))

    def _dibujar_ofertar_compra(self, pantalla):
        font = pygame.font.SysFont(None, 24)
        pantalla.blit(font.render("Ofertar compra", True, (230, 230, 210)), (self.x + 30, self.y + 70))
        productos = self.sim.economia.filtrar_productos()
        if not productos:
            productos = ["madera", "carne", "pan"]
        if self._producto_objetivo_idx >= len(productos):
            self._producto_objetivo_idx = 0
        producto = productos[self._producto_objetivo_idx]

        self._dibujar_boton_filtro(
            pantalla, f"Producto objetivo: {producto}", self.x + 30, self.y + 105,
            lambda _payload: self._ciclar_producto_objetivo(productos)
        )
        self._dibujar_controles_valor(
            pantalla,
            etiqueta=f"Cantidad: {self._cantidad_oferta}",
            y=self.y + 145,
            decrementar=lambda: self._ajustar_cantidad_oferta(-1),
            incrementar=lambda: self._ajustar_cantidad_oferta(+1),
        )
        self._dibujar_controles_valor(
            pantalla,
            etiqueta=f"Precio máximo: {self._precio_oferta:.2f}",
            y=self.y + 185,
            decrementar=lambda: self._ajustar_precio_oferta(-1),
            incrementar=lambda: self._ajustar_precio_oferta(+1),
        )
        publicar = pygame.Rect(self.x + 30, self.y + 230, 190, 32)
        pygame.draw.rect(pantalla, (70, 105, 130), publicar, border_radius=4)
        pantalla.blit(font.render("Publicar compra", True, (235, 245, 255)), (publicar.x + 20, publicar.y + 7))
        self._items_clickables.append({"rect": publicar, "accion": lambda _payload: self._publicar_oferta_compra(producto)})
        if self._mensaje_estado:
            pantalla.blit(font.render(self._mensaje_estado, True, (200, 255, 200)), (self.x + 30, self.y + 280))

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

    def _ciclar_producto_inventario(self, productos):
        if not productos:
            return
        self._producto_oferta_idx = (self._producto_oferta_idx + 1) % len(productos)
        self.oferta_seleccionada = None

    def _ciclar_producto_objetivo(self, productos):
        if not productos:
            return
        self._producto_objetivo_idx = (self._producto_objetivo_idx + 1) % len(productos)

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

    def _coincide_busqueda(self, oferta, nombre_vendedor):
        termino = self._busqueda_texto.strip().lower()
        if not termino:
            return True
        metadata = self.sim.economia.obtener_metadata_producto(oferta["producto"])
        categoria = (metadata.get("categoria") or "").lower()
        tipo = (metadata.get("tipo_alimento") or "").lower()
        producto = oferta["producto"].lower()
        vendedor = nombre_vendedor.lower()
        return (
            termino in producto
            or termino in categoria
            or termino in tipo
            or termino in vendedor
        )

    def _seleccionar_oferta_compra(self, oferta):
        if oferta:
            self.oferta_seleccionada = oferta
            self._cantidad_compra = 1

    def _seleccionar_oferta_venta(self, oferta):
        if oferta:
            self.oferta_seleccionada = oferta
            self._cantidad_venta = 1

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

    def _ajustar_cantidad_venta(self, delta):
        self._cantidad_venta = max(1, self._cantidad_venta + delta)

    def _ajustar_cantidad_oferta(self, delta):
        self._cantidad_oferta = max(1, self._cantidad_oferta + delta)

    def _ajustar_precio_oferta(self, delta):
        self._precio_oferta = max(1.0, self._precio_oferta + delta)

    def _ajustar_calidad_oferta(self, delta):
        self._calidad_oferta = max(0.1, min(1.0, self._calidad_oferta + delta))

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

    def _dibujar_panel_venta(self, pantalla, oferta, producto):
        font = pygame.font.SysFont(None, 22)
        panel = pygame.Rect(self.x + 30, self.y + self.alto - 130, self.ancho - 60, 90)
        pygame.draw.rect(pantalla, (65, 48, 42), panel, border_radius=6)
        inventario_disp = self.sim.agente_jugador.inventario.get(producto, 0) if self.sim.agente_jugador else 0
        max_cantidad = max(1, min(oferta["cantidad"], inventario_disp))
        self._cantidad_venta = min(max(1, self._cantidad_venta), max_cantidad)
        total = self._cantidad_venta * oferta["precio_maximo"]
        texto = f"Selección #{oferta['id']} | cantidad: {self._cantidad_venta} / {max_cantidad} | total esperado: {total:.2f}"
        pantalla.blit(font.render(texto, True, (255, 232, 220)), (panel.x + 10, panel.y + 10))

        menos = pygame.Rect(panel.x + 10, panel.y + 40, 30, 30)
        mas = pygame.Rect(panel.x + 50, panel.y + 40, 30, 30)
        vender = pygame.Rect(panel.x + 100, panel.y + 40, 140, 30)
        pygame.draw.rect(pantalla, (120, 90, 90), menos, border_radius=4)
        pygame.draw.rect(pantalla, (120, 90, 90), mas, border_radius=4)
        pygame.draw.rect(pantalla, (140, 85, 70), vender, border_radius=4)
        pantalla.blit(font.render("-", True, (255, 245, 245)), (menos.x + 10, menos.y + 5))
        pantalla.blit(font.render("+", True, (255, 245, 245)), (mas.x + 8, mas.y + 5))
        pantalla.blit(font.render("Vender", True, (255, 245, 235)), (vender.x + 32, vender.y + 5))
        self._items_clickables.append({"rect": menos, "accion": lambda _payload: self._ajustar_cantidad_venta(-1)})
        self._items_clickables.append({"rect": mas, "accion": lambda _payload: self._ajustar_cantidad_venta(+1)})
        self._items_clickables.append({"rect": vender, "accion": lambda _payload: self._ejecutar_venta(oferta)})

    def _ejecutar_venta(self, oferta):
        agente = self.sim.agente_jugador
        if not agente:
            self._mensaje_estado = "No hay agente jugador."
            return
        resultado = self.sim.acciones.accion_vender(agente, oferta["id"], self._cantidad_venta)
        self._mensaje_estado = "Venta realizada." if resultado else "No se pudo completar la venta."
        if resultado:
            self.oferta_seleccionada = None

    def _productos_vendibles_jugador(self):
        if not self.sim.agente_jugador:
            return []
        ignorar = {"monedas", "agua", "comida"}
        return sorted([k for k, v in self.sim.agente_jugador.inventario.items() if v > 0 and k not in ignorar])

    def _dibujar_controles_valor(self, pantalla, etiqueta, y, decrementar, incrementar):
        font = pygame.font.SysFont(None, 22)
        etiqueta_rect = pygame.Rect(self.x + 30, y, 260, 30)
        pygame.draw.rect(pantalla, (62, 62, 88), etiqueta_rect, border_radius=4)
        pantalla.blit(font.render(etiqueta, True, (230, 230, 230)), (etiqueta_rect.x + 8, etiqueta_rect.y + 5))

        menos = pygame.Rect(self.x + 300, y, 30, 30)
        mas = pygame.Rect(self.x + 335, y, 30, 30)
        pygame.draw.rect(pantalla, (90, 90, 120), menos, border_radius=4)
        pygame.draw.rect(pantalla, (90, 90, 120), mas, border_radius=4)
        pantalla.blit(font.render("-", True, (245, 245, 255)), (menos.x + 10, menos.y + 5))
        pantalla.blit(font.render("+", True, (245, 245, 255)), (mas.x + 8, mas.y + 5))
        self._items_clickables.append({"rect": menos, "accion": lambda _payload: decrementar()})
        self._items_clickables.append({"rect": mas, "accion": lambda _payload: incrementar()})

    def _publicar_oferta_venta(self, producto):
        agente = self.sim.agente_jugador
        if not agente:
            self._mensaje_estado = "No hay agente jugador."
            return
        resultado = self.sim.acciones.accion_publicar_oferta_venta(
            agente,
            producto,
            self._cantidad_oferta,
            self._precio_oferta,
            self._calidad_oferta,
        )
        self._mensaje_estado = "Oferta de venta publicada." if resultado else "No se pudo publicar oferta de venta."

    def _publicar_oferta_compra(self, producto):
        agente = self.sim.agente_jugador
        if not agente:
            self._mensaje_estado = "No hay agente jugador."
            return
        resultado = self.sim.acciones.accion_publicar_oferta_compra(
            agente,
            producto,
            self._cantidad_oferta,
            self._precio_oferta,
        )
        self._mensaje_estado = "Oferta de compra publicada." if resultado else "No se pudo publicar oferta de compra."

    def _get_agente_by_id(self, agente_id):
        for agente in self.sim.agentes:
            if agente.id == agente_id:
                return agente
        return None
