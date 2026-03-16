# Revisión de cierre de `AUDITORIA_REPOSITORIO.md`

Fecha: 2026-03-16

## Resultado ejecutivo

**Sí, todos los puntos de la auditoría original están completamente resueltos.**

- **Resueltos:** 12
- **Parciales:** 0
- **Pendientes:** 0

## Estado por hallazgo

1. **Inconsistencia `self.sim` vs `self.simulador` en `Acciones`** → **Resuelto**
   - La clase usa `self.simulador` y las llamadas de mercado ya referencian `self.simulador.economia`.

2. **API económica incompleta (`get_oferta_venta/get_oferta_compra`)** → **Resuelto**
   - Ambos getters existen en `sistema/economia.py`.

3. **`MenuMercado` llamaba métodos no implementados** → **Resuelto**
   - Existen `_dibujar_vender`, `_dibujar_ofertar_venta` y `_dibujar_ofertar_compra`.

4. **Distancia hexagonal incorrecta en `Simulador`** → **Resuelto**
   - `_distancia` delega en `hex_distance`.

5. **`main.py` demasiado monolítico** → **Resuelto**
   - Se extrajo la lógica de bootstrap inicial a `engine/bootstrap_system.py` y la gestión de actividades a `engine/activity_system.py`, dejando a `main.py` como orquestador ligero con delegaciones explícitas.

6. **Exceso de `print` en runtime** → **Resuelto**
   - No se detectaron `print(...)` en archivos Python.

7. **Artefactos temporales / higiene repo** → **Resuelto**
   - Se mantiene `.gitignore` para `__pycache__`/`*.pyc` y no hay artefactos versionados detectados.
   - Se eliminó el comentario temporal pendiente en `main.py`.

8. **README desalineado con estado real** → **Resuelto**
   - README incluye una matriz de estado por subsistema (Implementado/Parcial/Pendiente).

9. **Determinismo por semilla configurable** → **Resuelto**
   - Existe `config.SEED` y arranque con `setup_random_seed()`.

10. **Tipado estático gradual** → **Resuelto**
   - Se observan anotaciones de tipos en módulos clave, incluyendo `sistema/acciones.py` y `sistema/economia.py`.

11. **Falta de pruebas automatizadas** → **Resuelto**
   - Hay suite `tests/` con cobertura de economía, distancia hex, invariantes, actividades y menú.

12. **Centralización de constantes de balance** → **Resuelto**
   - Existe `balance.py` como módulo dedicado de constantes de tuning.

## Validaciones ejecutadas

- `python -m compileall -q .` → OK
- `pytest -q` → OK (18 pruebas)

## Conclusión

El repositorio presenta un cierre **total** de la auditoría original, con todos los puntos en estado **resuelto**.
