# Auditoría comparativa basada en README actualizado

**Fecha:** 2026-03-18  
**Objetivo:** comparar lo documentado en `README.md` con el estado actual del código para clasificar en:
- Lo que ya se hizo.
- Lo que se puede mejorar.
- Lo que falta por trabajar.

---

## 1) Lo que ya se hizo (coincide README ↔ código)

1. **Arquitectura base modular en funcionamiento**
   - El simulador principal delega en sistemas especializados (`tick`, `actividad`, `movimiento`, `bootstrap`, `render`, `input`).
   - Esto confirma la descomposición respecto al enfoque monolítico anterior.

2. **Economía con ofertas operativa a nivel de dominio**
   - Existen publicación y búsqueda de ofertas de venta/compra.
   - Existen getters por ID (`get_oferta_venta`, `get_oferta_compra`).
   - Existe ejecución de transacciones y actualización de estadísticas por producto.

3. **Distancia hexagonal consistente**
   - El simulador usa `hex_distance` para cálculo de distancia entre casillas.

4. **Semilla configurable para reproducibilidad**
   - Existe `config.SEED` y rutina de inicialización de semilla (`setup_random_seed`).

5. **Logging en lugar de prints**
   - No se detectaron `print(...)` en `.py`; la salida usa `logging`.

6. **Suite mínima de pruebas automatizadas vigente**
   - `pytest -q` pasa (18 tests).
   - `compileall` también pasa sin errores sintácticos.

---

## 2) Lo que hay por mejorar (parcial / desalineado)

1. **Flujo de mercado en UI aún incompleto respecto al README**
   - README describe flujo completo para comprar/vender/ofertar con filtros e interacción.
   - En código, `MenuMercado` solo procesa `ESC`; no hay captura interactiva de entradas ni manejo de clics/acciones de compra/venta.
   - Las vistas `ofertar_venta` y `ofertar_compra` son informativas y declaran explícitamente que falta captura de datos.

2. **IA implementada pero sin integración de comercio autónomo**
   - README ya lo marca como parcial y el código lo confirma.
   - La IA decide dormir/comer/recolectar/trabajar/socializar, pero no publica ni toma ofertas de mercado como parte de su rutina.

3. **README mezcla estado actual con diseño aspiracional sin separación fuerte**
   - En varias secciones de fisiología/acciones hay texto de diseño futuro junto con comportamiento actual.
   - Esto dificulta usar README como documento de verdad técnica para onboarding y planificación.

4. **Cobertura de pruebas todavía básica en superficie de UI e integración**
   - Hay prueba de dibujo por modos del menú de mercado, pero no hay flujo end-to-end de compra/venta desde UI.

---

## 3) Lo que falta por trabajar (pendiente real)

1. **Mercado interactivo completo en UI**
   - Entrada de cantidades/precios.
   - Selección de ofertas por usuario.
   - Validaciones de inventario/monedas y retroalimentación en pantalla.
   - Soporte real para filtros descritos en README.

2. **Comercio autónomo de IA**
   - Políticas para decidir cuándo comprar, vender o publicar ofertas.
   - Integración con necesidades fisiológicas y personalidad.

3. **Sistemas declarados como pendientes en README**
   - Enfermedades/salud avanzada.
   - Construcciones.
   - Trabajos/contratos.
   - Eventos amplios.
   - Reproducción/ciclo de vida avanzado completo.

4. **Alineación fina README ↔ implementación de mundo/recursos**
   - El README menciona un modelo de recursos más granular (por ejemplo, categorías detalladas de vegetación/alimentos) que no está plenamente materializado de forma equivalente en estructuras y flujo de juego.

---

## 4) Priorización recomendada (siguiente auditoría)

### Prioridad alta (impacto jugable inmediato)
1. Cerrar flujo interactivo de `MenuMercado` (comprar/vender/ofertar) con validaciones.
2. Agregar pruebas de integración de mercado (acción de usuario → transacción → inventarios/monedas).

### Prioridad media
3. Integrar ciclo económico en IA (al menos compra de comida/agua y venta de excedentes).
4. Separar en README bloques de **"implementado"** vs **"diseño objetivo"** para evitar ambigüedad.

### Prioridad baja
5. Expandir dominios pendientes (salud, contratos, construcciones, eventos) de forma incremental con pruebas por feature.

---

## 5) Validaciones ejecutadas en esta auditoría

- `python -m compileall -q .` ✅
- `pytest -q` ✅ (18 tests)
- `rg -n "\bprint\(" --glob '*.py'` ✅ (sin coincidencias)

