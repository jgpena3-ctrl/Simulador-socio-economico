import tkinter as tk
from tkinter import ttk, messagebox
from statistics import mean


class MercadoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Menú de Mercado")
        self.root.geometry("900x620")

        self.ofertas_venta = [
            {"producto": "trigo", "cantidad": 100, "precio": 10.5, "dueno": "Ana"},
            {"producto": "trigo", "cantidad": 70, "precio": 9.8, "dueno": "Luis"},
            {"producto": "maiz", "cantidad": 40, "precio": 8.2, "dueno": "Sofía"},
            {"producto": "cafe", "cantidad": 25, "precio": 15.0, "dueno": "Pedro"},
        ]
        self.ofertas_compra = [
            {"producto": "trigo", "cantidad": 50, "precio": 10.0, "dueno": "Mercado Norte"},
            {"producto": "maiz", "cantidad": 60, "precio": 8.7, "dueno": "Coop Sur"},
            {"producto": "cafe", "cantidad": 10, "precio": 14.5, "dueno": "Cafetería Sol"},
        ]
        self.historial = [
            {"producto": "trigo", "cantidad": 20, "precio": 10.1, "tipo": "venta", "dueno": "Ana"},
            {"producto": "trigo", "cantidad": 35, "precio": 9.9, "tipo": "compra", "dueno": "Luis"},
            {"producto": "maiz", "cantidad": 15, "precio": 8.4, "tipo": "venta", "dueno": "Sofía"},
        ]

        self.producto_var = tk.StringVar()

        self._build_layout()

    def _build_layout(self) -> None:
        selector = ttk.LabelFrame(self.root, text="1) Elegir producto a negociar")
        selector.pack(fill="x", padx=12, pady=(12, 8))

        ttk.Label(selector, text="Producto:").grid(row=0, column=0, padx=8, pady=10, sticky="w")
        self.entry_producto = ttk.Entry(selector, textvariable=self.producto_var, width=30)
        self.entry_producto.grid(row=0, column=1, padx=8, pady=10, sticky="w")

        self.btn_activar = ttk.Button(selector, text="Confirmar producto", command=self.activar_menu)
        self.btn_activar.grid(row=0, column=2, padx=8, pady=10)

        self.lbl_estado = ttk.Label(selector, text="Primero selecciona un producto.")
        self.lbl_estado.grid(row=1, column=0, columnspan=3, padx=8, pady=(0, 10), sticky="w")

        self.frame_botones = ttk.LabelFrame(self.root, text="2) Acciones de mercado")
        self.frame_botones.pack(fill="x", padx=12, pady=8)

        self.btn_comprar = ttk.Button(self.frame_botones, text="Comprar", command=self.mostrar_ofertas_venta, state="disabled")
        self.btn_vender = ttk.Button(self.frame_botones, text="Vender", command=self.mostrar_ofertas_compra, state="disabled")
        self.btn_ofertar_compra = ttk.Button(
            self.frame_botones,
            text="Ofertar compra",
            command=lambda: self.mostrar_panel_oferta("compra"),
            state="disabled",
        )
        self.btn_ofertar_venta = ttk.Button(
            self.frame_botones,
            text="Ofertar venta",
            command=lambda: self.mostrar_panel_oferta("venta"),
            state="disabled",
        )

        self.btn_comprar.grid(row=0, column=0, padx=8, pady=10)
        self.btn_vender.grid(row=0, column=1, padx=8, pady=10)
        self.btn_ofertar_compra.grid(row=0, column=2, padx=8, pady=10)
        self.btn_ofertar_venta.grid(row=0, column=3, padx=8, pady=10)

        self.panel_resultados = ttk.LabelFrame(self.root, text="Información")
        self.panel_resultados.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        self.txt_resultado = tk.Text(self.panel_resultados, height=20, wrap="word")
        self.txt_resultado.pack(fill="both", expand=True, padx=10, pady=10)

    def activar_menu(self) -> None:
        producto = self.producto_var.get().strip().lower()
        if not producto:
            messagebox.showwarning("Producto requerido", "Debes indicar el producto a negociar.")
            return

        for boton in (self.btn_comprar, self.btn_vender, self.btn_ofertar_compra, self.btn_ofertar_venta):
            boton.config(state="normal")

        self.lbl_estado.config(text=f"Producto seleccionado: {producto}. Ya puedes elegir una acción.")
        self._escribir_texto(
            f"Producto activo: {producto}\n"
            "- Comprar: muestra ofertas de venta.\n"
            "- Vender: muestra ofertas de compra.\n"
            "- Ofertar compra/venta: muestra historial y resumen de precios para crear tu oferta."
        )

    def mostrar_ofertas_venta(self) -> None:
        producto = self.producto_var.get().strip().lower()
        ofertas = [o for o in self.ofertas_venta if o["producto"] == producto]

        if not ofertas:
            self._escribir_texto(f"No hay ofertas de venta activas para '{producto}'.")
            return

        lineas = [f"Ofertas de VENTA para comprar '{producto}':"]
        for i, oferta in enumerate(ofertas, start=1):
            lineas.append(
                f"{i}. Dueño: {oferta['dueno']} | Cantidad: {oferta['cantidad']} | Precio: {oferta['precio']:.2f}"
            )
        self._escribir_texto("\n".join(lineas))

    def mostrar_ofertas_compra(self) -> None:
        producto = self.producto_var.get().strip().lower()
        ofertas = [o for o in self.ofertas_compra if o["producto"] == producto]

        if not ofertas:
            self._escribir_texto(f"No hay ofertas de compra activas para '{producto}'.")
            return

        lineas = [f"Ofertas de COMPRA para vender '{producto}':"]
        for i, oferta in enumerate(ofertas, start=1):
            lineas.append(
                f"{i}. Comprador: {oferta['dueno']} | Cantidad: {oferta['cantidad']} | Precio: {oferta['precio']:.2f}"
            )
        self._escribir_texto("\n".join(lineas))

    def mostrar_panel_oferta(self, tipo: str) -> None:
        producto = self.producto_var.get().strip().lower()
        historial_producto = [h for h in self.historial if h["producto"] == producto]
        resumen = self._resumen_precios(producto)

        lineas = [
            f"Preparando OFERTA de {tipo.upper()} para '{producto}'.",
            "",
            "Historial del mercado:",
        ]
        if historial_producto:
            for item in historial_producto:
                lineas.append(
                    f"- {item['tipo'].capitalize()} | Cantidad: {item['cantidad']} | Precio: {item['precio']:.2f} | Dueño: {item['dueno']}"
                )
        else:
            lineas.append("- Sin movimientos previos para este producto.")

        lineas.extend(
            [
                "",
                "Resumen de precios actuales:",
                f"- Máximo: {resumen['max']:.2f}",
                f"- Mínimo: {resumen['min']:.2f}",
                f"- Promedio: {resumen['promedio']:.2f}",
                "",
                "Completa tu oferta con: cantidad, precio, producto y dueño.",
            ]
        )
        self._escribir_texto("\n".join(lineas))
        self._abrir_formulario_oferta(tipo, producto)

    def _resumen_precios(self, producto: str) -> dict[str, float]:
        precios = [o["precio"] for o in self.ofertas_venta + self.ofertas_compra if o["producto"] == producto]
        if not precios:
            return {"max": 0.0, "min": 0.0, "promedio": 0.0}
        return {"max": max(precios), "min": min(precios), "promedio": mean(precios)}

    def _abrir_formulario_oferta(self, tipo: str, producto: str) -> None:
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Nueva oferta de {tipo}")
        ventana.geometry("390x250")

        cantidad_var = tk.StringVar()
        precio_var = tk.StringVar()
        dueno_var = tk.StringVar()

        ttk.Label(ventana, text=f"Producto: {producto}").grid(row=0, column=0, columnspan=2, padx=12, pady=(14, 10), sticky="w")

        ttk.Label(ventana, text="Cantidad:").grid(row=1, column=0, padx=12, pady=6, sticky="e")
        ttk.Entry(ventana, textvariable=cantidad_var).grid(row=1, column=1, padx=12, pady=6, sticky="w")

        ttk.Label(ventana, text="Precio:").grid(row=2, column=0, padx=12, pady=6, sticky="e")
        ttk.Entry(ventana, textvariable=precio_var).grid(row=2, column=1, padx=12, pady=6, sticky="w")

        ttk.Label(ventana, text="Dueño:").grid(row=3, column=0, padx=12, pady=6, sticky="e")
        ttk.Entry(ventana, textvariable=dueno_var).grid(row=3, column=1, padx=12, pady=6, sticky="w")

        def guardar_oferta() -> None:
            try:
                cantidad = int(cantidad_var.get())
                precio = float(precio_var.get())
            except ValueError:
                messagebox.showerror("Datos inválidos", "Cantidad y precio deben ser numéricos.")
                return

            dueno = dueno_var.get().strip()
            if not dueno:
                messagebox.showwarning("Dato faltante", "Debes indicar el dueño de la oferta.")
                return

            oferta = {"producto": producto, "cantidad": cantidad, "precio": precio, "dueno": dueno}
            if tipo == "compra":
                self.ofertas_compra.append(oferta)
            else:
                self.ofertas_venta.append(oferta)

            self.historial.append(
                {"producto": producto, "cantidad": cantidad, "precio": precio, "tipo": tipo, "dueno": dueno}
            )

            self._escribir_texto(
                f"Oferta de {tipo} registrada: Producto={producto}, Cantidad={cantidad}, Precio={precio:.2f}, Dueño={dueno}."
            )
            ventana.destroy()

        ttk.Button(ventana, text="Guardar oferta", command=guardar_oferta).grid(
            row=4, column=0, columnspan=2, padx=12, pady=16
        )

    def _escribir_texto(self, texto: str) -> None:
        self.txt_resultado.delete("1.0", tk.END)
        self.txt_resultado.insert(tk.END, texto)


def principal() -> None:
    root = tk.Tk()
    MercadoApp(root)
    root.mainloop()


if __name__ == "__main__":
    principal()
