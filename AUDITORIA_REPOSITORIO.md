# Auditoría técnica del repositorio

## Alcance revisado
- Código fuente Python de `main.py`, módulos de `agentes/`, `sistema/`, `mundo/`, `ui/`, utilidades y configuración.
- Se validó compilación sintáctica de todo el proyecto con `python -m compileall -q .`.

## Hallazgos prioritarios (bloqueantes)

### 1) Inconsistencias de referencias internas (`self.sim` vs `self.simulador`)
En `Acciones` se define `self.simulador`, pero en varios métodos de mercado se usa `self.sim`, lo que provocará errores de atributo al ejecutar compras/ventas.

**Impacto:** alto (funciones de mercado pueden fallar en runtime).

**Sugerencia:** estandarizar a `self.simulador` en toda la clase y añadir pruebas unitarias de compraventa.

---

### 2) API económica incompleta respecto a su consumo
`Acciones` invoca métodos `get_oferta_venta` y `get_oferta_compra`, pero `SistemaEconomico` no los implementa.

**Impacto:** alto (flujo de compra/venta incompleto).

**Sugerencia:** implementar getters por ID, o reemplazar esas llamadas por búsquedas internas validadas.

---

### 3) Modo de `MenuMercado` llama métodos no implementados
`MenuMercado.dibujar()` delega a `_dibujar_vender`, `_dibujar_ofertar_venta`, `_dibujar_ofertar_compra`, pero solo están implementados `_dibujar_principal`, `_dibujar_producto`, `_dibujar_comprar`.

**Impacto:** alto (riesgo de `AttributeError` al cambiar de modo).

**Sugerencia:** implementar los métodos faltantes o deshabilitar temporalmente esos modos.

---

### 4) Distancia hexagonal mal calculada en `Simulador`
`Simulador._distancia` usa distancia Manhattan axial simplificada, distinta de la distancia hexagonal correcta (ya existe `hex_distance` en `utils/hex_math.py`).

**Impacto:** medio-alto (afecta IA, interacción social, tiempos de desplazamiento y validaciones espaciales).

**Sugerencia:** reemplazar `_distancia` por `utils.hex_math.hex_distance` para consistencia global.

---

## Hallazgos de calidad y mantenibilidad

### 5) `main.py` concentra demasiadas responsabilidades
`main.py` (916 líneas) mezcla bucle principal, renderizado, input, simulación, mercado y lógica de movimiento.

**Impacto:** alto en mantenibilidad y pruebas.

**Sugerencia:** dividir por capas:
- `engine/tick_system.py` (tiempo + actualización)
- `engine/movement.py`
- `render/world_renderer.py`
- `controllers/input_controller.py`

---

### 6) Salida masiva por `print` en lógica de juego
Hay una cantidad muy alta de `print` en runtime (ticks, acciones, menús, economía, IA), lo que degrada rendimiento y dificulta depuración real.

**Impacto:** medio (ruido y costo de IO).

**Sugerencia:** migrar a `logging` con niveles (`DEBUG/INFO/WARNING`) y activar verbosidad por configuración.

---

### 7) Código y artefactos temporales en repositorio
Hay archivos y comentarios de prueba/provisionales (`prueba.py`, comentarios “AÑADIR ESTO”, etc.), y también archivos compilados `__pycache__` versionados.

**Impacto:** medio (higiene de repositorio y deuda técnica).

**Sugerencia:**
- Eliminar archivos de prueba no usados.
- Añadir `.gitignore` para `__pycache__/` y `*.pyc`.
- Limpiar comentarios temporales.

---

### 8) Desalineación entre documentación y estado real
README define IA como “próxima fase”, pero hay implementación activa (`agentes/ai_agentes.py`). También se anuncian sistemas parcialmente implementados.

**Impacto:** medio (expectativas incorrectas del proyecto).

**Sugerencia:** actualizar README con matriz de estado: `implementado / parcial / pendiente` por subsistema.

---

## Oportunidades de optimización

### 9) Determinismo para simulación
Se usa `numpy.random` en múltiples lugares sin semilla configurable.

**Sugerencia:** agregar `config.SEED` opcional y registrar semilla en el arranque para reproducibilidad.

### 10) Tipado estático y contratos
No hay type hints en la mayor parte del dominio.

**Sugerencia:** introducir tipado gradual en módulos base (`agente`, `economia`, `acciones`) + `mypy` opcional.

### 11) Pruebas automatizadas inexistentes
No hay suite de pruebas.

**Sugerencia inicial (rápida):**
- pruebas de distancia hexagonal
- pruebas de creación/consumo de ofertas
- pruebas de transición de actividad de agentes
- prueba de invariantes de inventario (nunca negativo)

### 12) Centralización de constantes de balance
Duraciones y tasas están repartidas entre `config.py`, atributos de clase y literales.

**Sugerencia:** consolidar en `config.py` o archivo de balance separado (`balance.py`) para tunear mecánicas sin tocar lógica.

---

## Backlog recomendado (ordenado)

### Sprint 1 (estabilidad)
1. Corregir `self.sim`/`self.simulador` en `sistema/acciones.py`.
2. Implementar `get_oferta_venta/get_oferta_compra` en `sistema/economia.py`.
3. Completar o desactivar modos incompletos de `ui/menu_mercado.py`.
4. Sustituir `Simulador._distancia` por distancia hexagonal correcta.

### Sprint 2 (mantenibilidad)
5. Introducir `logging` y reducir `print`.
6. Limpiar artefactos (`__pycache__`, `prueba.py`) y añadir `.gitignore`.
7. Refactor de `main.py` en módulos.

### Sprint 3 (calidad)
8. Base de pruebas (`pytest`) para economía, distancias y actividades.
9. Tipado gradual + validaciones de inventario.
10. Actualizar README con estado real de implementación.

---

## Validaciones ejecutadas
- `python -m compileall -q .` → OK, sin errores de sintaxis.
