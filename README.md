# Simulador Socioeconómico

Simulador en tiempo discreto donde el jugador controla un agente en un mundo hexagonal poblado por agentes autónomos (IA). El juego combina simulación fisiológica, económica y social con herencia genética y personalidades.

## 1. Visión General

El proyecto modela:

- **Mundo hexagonal** con recursos distribuidos por casilla.
- **Agentes** con genética, fisiología, inventario y experiencia.
- **Economía emergente** basada en ofertas de compra/venta.
- **Sistema de tiempo por ticks** para unificar todas las mecánicas.
- **Interacción del jugador** mediante menús contextuales y control de cámara.

---

## 2. Componentes Principales

### 2.1 Mundo (`MapaHexagonal`)

- **Forma:** hexágonos en coordenadas axiales `(q, r)`.
- **Tamaño:** radio `16` → `817` casillas.

#### Recursos por casilla

- `arboles`: cantidad de árboles.
- `arbustos`: cantidad de arbustos.
- `animales`: diccionario con especies y cantidades.
- `frutos`: frutos disponibles para recolectar.

#### Categorías de casillas

- `(0,0)`: **Centro** (vivienda/descanso).

- **Zona económica** (6 casillas adyacentes):
  - `(1,0)`: Mercado
  - `(0,1)`: Cocina
  - `(-1,0)`: Talleres
  - `(0,-1)`: Granja
  - `(1,-1)`: Servicios Cívicos
  - `(-1,1)`: Centro Comunitario

- **Resto del mapa:** clasificadas por distancia (bosque, montaña, etc.).

### 2.2 Agentes

#### Atributos fijos (genética)

- `nombre`, `sexo`, `edad`
- `altura`, `peso`, `color_ojos`, `color_piel`, `color_cabello`
- `belleza` (heredada)
- `personalidad`: 16 tipos MBTI

#### Fisiología (`Fisiologia`)

**Estados (0-100):**

- `hambre`, `sed`, `cansancio`, `energía`

**Capacidades base (heredadas):**

- `fuerza_base`, `agilidad_base`, `resistencia_base`
- `inteligencia`, `carisma`

**Capacidades actuales (afectadas por fatiga):**

- `fuerza_actual`, `agilidad_actual`, `resistencia_actual`

**Metabolismo:**

- `peso`, `imc`, `tmb` (Tasa Metabólica Basal)
- `calorias_consumidas_hoy`, `calorias_gastadas_hoy`

#### Inventario

```python
{
    "comida": int, "agua": int, "madera": int, "piedra": int,
    "monedas": int, "fruta": int, "carne": int, "herramientas": int,
    # ... otros items
}
```

#### Experiencia

```python
{
    "recolectar": float, "cazar": float, "talar": float,
    "cocinar": float, "comerciar": float, "construir": float
}
```

#### Sistema de actividades

- `actividad_actual: str` (`"recolectando"`, `"cazando"`, `"durmiendo"`, etc.)
- `actividad_restante: int` (ticks restantes)
- `actividad_datos: dict` (información contextual)

---

## 3. Sistema de Tiempo

- **Tick base:** 30 minutos.

### Conversiones

- `1 día = 48 ticks`
- `1 año = 365 días = 17,520 ticks`

### Banderas temporales

- `nuevo_dia`
- `nuevo_ano`

> Se calculan centralizadamente para sincronizar sistemas (fisiología, economía y eventos).

---

## 4. Acciones Disponibles

### 4.1 Movimiento

`mover_agente_a(destino)`:

- Calcula ruta en línea recta hexagonal.
- Consume `1 tick` por casilla.
- Afecta:
  - `cansancio += 2`
  - `hambre += 1`

### 4.2 Recolectar (duración: 3 ticks)

- Probabilidad de encontrar: basada en densidad de vegetación.
- Cantidad obtenida: aleatoria con bonus por experiencia.
- Reduce `frutos` de la casilla.
- Afecta:
  - `cansancio += 5`
  - `hambre += 3`

### 4.3 Cazar (duración: 4 ticks)

- Probabilidad de encontrar: basada en densidad de animales.
- Probabilidad de éxito: `50%` + bonus por experiencia/fuerza/agilidad.
- Reduce población del animal objetivo.
- Afecta:
  - `cansancio += 15`
  - `hambre += 8`
  - `energía -= 10`

### 4.4 Talar (duración: 4 ticks)

- Probabilidad de éxito: `70%` + bonus por experiencia/fuerza.
- Madera obtenida: base `5` + bonus.
- Reduce `arboles` de la casilla en `1`.
- Afecta:
  - `cansancio += 15`
  - `hambre += 8`

### 4.5 Descansar (duración: 3 ticks)

- Solo en casillas habitables (centro o viviendas).
- Reduce cansancio y aumenta energía.
- Afecta:
  - `cansancio -= 24%`
  - `energía += 15%`

### 4.6 Mercado

- **Comprar:** ver ofertas de venta activas.
- **Vender:** ver ofertas de compra activas.
- **Ofertar venta:** publicar producto a precio deseado.
- **Ofertar compra:** publicar búsqueda con precio máximo.

---

## 5. Sistema Económico (`Economia`)

### 5.1 Ofertas

```python
# Oferta de venta
{
    "id": int, "agente_id": int, "producto": str,
    "cantidad": int, "precio_unitario": int,
    "calidad": float, "fecha_tick": int, "activa": bool
}

# Oferta de compra
{
    "id": int, "agente_id": int, "producto": str,
    "cantidad": int, "precio_maximo": int,
    "fecha_tick": int, "activa": bool
}
```

### 5.2 Estadísticas por producto

- `precio_promedio`, `precio_minimo`, `precio_maximo`
- `volumen_total`, `tendencia` (`"subiendo"` / `"bajando"` / `"estable"`)
- `ofertas_venta_activas`, `ofertas_compra_activas`

---

## 6. Interfaz de Usuario

### 6.1 Menú Contextual

- Aparece al hacer clic en casilla.
- Opciones dinámicas según:
  - si el agente está en esa casilla,
  - categoría de la casilla,
  - recursos disponibles.

### 6.2 Menú de Inventario

- Muestra todos los ítems del jugador.
- Organizado por categorías.
- Tecla rápida: `I`.

### 6.3 Menú de Mercado

Flujo:

1. Acción
2. Producto
3. Detalle

Incluye estadísticas de precios, consulta de ofertas y publicación de nuevas ofertas.

### 6.4 Controles de Cámara

- `WASD` / Flechas: mover vista
- Rueda del mouse: zoom
- `F`: alternar seguimiento del jugador
- `HOME`: centrar en jugador

---

## 7. IA de Agentes (Próxima Fase)

- Sistema de prioridades basado en necesidades fisiológicas.
- Decisiones influenciadas por personalidad.
- Capacidad de usar el mercado (comprar/vender).
- Interacciones sociales y formación de relaciones.

---

## 8. Pendientes / Próximos Features

- Sistema de reproducción completo
- Crecimiento infantil
- Enfermedades y salud
- Construcciones (casas, talleres)
- Sistema de trabajos/contratos
- Árbol genealógico
- Eventos aleatorios
- Multi-jugador (?)
