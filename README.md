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

## 1.1 Estado de implementación por subsistema

> Convención: **Implementado** = funcional en código principal; **Parcial** = existe base funcional pero faltan casos/capas; **Pendiente** = planificado sin implementación integral.

| Subsistema | Estado | Evidencia rápida |
| --- | --- | --- |
| Mundo hexagonal (`mundo/`) | Implementado | Generación de mapa, categorías y cámara funcional. |
| Agentes y fisiología (`agentes/`) | Implementado | Modelo de agente con atributos, inventario y fisiología activa. |
| Acciones y tiempo (`sistema/`, `engine/`) | Implementado | Acciones por ticks y ciclo temporal centralizado. |
| Economía / mercado (`sistema/economia.py`, `ui/menu_mercado.py`) | Implementado | Ofertas de compra/venta y menú de mercado disponibles. |
| IA de agentes (`agentes/ai_agentes.py`) | Implementado | Toma de decisiones por necesidades + personalidad ya operativa. |
| Uso autónomo de mercado por IA | Parcial | La IA decide acciones base; el comercio autónomo aún no está integrado en su rutina. |
| Interacciones sociales complejas | Parcial | Existe acción de socializar, pero sin sistema profundo de relaciones persistentes. |
| Reproducción y ciclo de vida avanzado | Parcial | Hay bases y pendientes, pero no un sistema completo de crecimiento/reproducción. |
| Enfermedades y salud avanzada | Pendiente | No hay módulo integral dedicado. |
| Construcciones, trabajos/contratos y eventos amplios | Pendiente | Declarados como próximos features. |

---

## 2. Componentes Principales

### 2.1 Mundo (`MapaHexagonal`)

- **Forma:** hexágonos en coordenadas axiales `(q, r)`.
- **Tamaño:** radio `16` → `817` casillas.

#### Recursos por casilla

- `arboles`: cantidad de árboles (separar entre arboles frutales y no frutales, ademas de especies de arboles).
- `arbustos`: cantidad de arbustos(separar entre especies de arbustos).
- `pasto`: de diferencia entre corto y largo, los largos permite alimentar a los herbiboros.
- `animales`: diccionario con especies y cantidades.
- `frutos`: frutos disponibles para recolectar(diferenciar entre cada tipo que depende de la especie de arbol o arbusto).

#### Categorías de casillas

- `(0,0)`: **Centro** (vivienda/descanso).

- **Zona económica** (6 casillas adyacentes):
  - `(1,0)`: Mercado
  - `(0,1)`: Cocina
  - `(-1,0)`: Talleres
  - `(0,-1)`: Granja
  - `(1,-1)`: Servicios Cívicos
  - `(-1,1)`: Centro Comunitario

- **Resto del mapa:** ecosistema autonomo 
### 2.2 Agentes

#### Atributos fijos (genética)

- `nombre`, `sexo`, `edad`
- `altura`, `peso`, `color_ojos`, `color_piel`, `color_cabello`
- `belleza` (heredada)
- `personalidad`: 16 tipos MBTI

#### Fisiología (`Fisiologia`)

**Estados (0-100):**

- `saciedad`: el inverso de habre actualmente nombrado `combustible`(pendiente por cambiar el nombre de la variable) disminulle con cada tick durando del 100% a 0% 12 tick, si se lleva al 100% aumenta el limite de saciedad y si llega a 0% disminulle simulando la capacidad estomacal pero independiente de limite de saciedad siempre se vacia en 12 ticks, así simulamos el apetito de los agentes ,
- `sed`: funcionalidad sin especificar,
- `cansancio`: se acumula dependiendo de la actividad que realice actiividades de exigencia minima como andar, pescar, cocinar generarán 1 de cansancio, de exigencia media como cazar, recolectar, lavar ropa, generan 2 de cansancio y exigencias maximas como talar, minar, herreria, carpintería generan 3 de cansancio (mecanica sin implementar)
- `energia`: regula la fase de sueño de los agentes funcionando como un reloj circadiano, recuperando en 8 horas de sueño nocturno la totalidad de la energia que proporciona 16 horas de vigilia con energia, dormir en las horas diurnas recupera la energia al mismo ritmo de se gasta en vigilia.


**Capacidades base (heredadas):**

- `fuerza_base`, `agilidad_base`, `resistencia_base`
- `inteligencia`, `carisma`

**Esperiencias:**

cada actividad o habilidad tiene facultad de acumular experiencia, cada tick gastado en una tarea genera experiencia en dicha tarea, siguiendo la creencia popular se requieren 10 mil horas o 20 mil ticks para volverse experto en una habilidad o maxearlo al 100% esto para la configuracion "normal" de tiempo en el juego (remitace al punto 3. Sistema de Tiempo)

**Capacidades actuales (afectadas por fatiga):**

- Cada capacidad fisica actual se calcula de la siquiente manera: (capacidad_base+capacidad_entrenada)*capacidad fisiologica (que es una distribucion normal normalizada por la edad)
- `fuerza_actual`, `agilidad_actual`, `resistencia_actual`
- Las capacidades actuales se ven afectadas por el imc siendo la agilidad y resistencia afectadas negativamente y la fuerza positivamente
-Las capacidades tambien se ven afectadas negativamente por el alto cansancio y la baja energia

**Metabolismo:**

- `peso`, `imc`, `tmb` (Tasa Metabólica Basal)

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
- `1 semana = 7 día`
- `1 mes = (ajustable entre 1 y 4 semanas)`
- `1 año = (ajustable en 4, 8, 12 meses + 1 día)`: se ajusta un día mas para que roten los dias para cada semana a lo largo de los años, con esa configuracion el año tendría max 337 dias y min 29 dias, las experiencias por ticks al igual que las variables que cambian con la edad como fisiologia se ajustarán  segun el numero de días que tenga un año para que sean equivalentes en el transcurso de un año así si tengo configurado 2 semanas pos mes en vez de 4 la experiencia de un tick al cazar será del doble respecto al que se tendría en un año "normal" (4 semanas y 12 meses).

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

### 4.2 Recolectar (duración: 1 ticks)

- Probabilidad de encontrar: basada en densidad de vegetación.
- Cantidad obtenida: aleatoria con bonus por experiencia.
- Reduce `frutos` de la casilla.

### 4.3 Cazar (duración: 1 ticks)

- Probabilidad de encontrar: basada en densidad de animales.
- Probabilidad de éxito: `50%`*experiencia requerida (puntería con arco, puntería con lanza, sagacidad con las mano(tal vez)) + `50%`*capacidades fisicas requerídas (dependiendo de la herramienta de caza)*dificultad_animal.
- Reduce población del animal objetivo.

### 4.4 Talar (duración: 4 ticks)
- se requiere hacha para realizarlo
- Probabilidad de éxito: `100%` pero la experiencia de tala otorga la probabilidad de reducir 1 tick de tala y las capacidades fisicas tambien otorgan la probabilidad de reducir otro tick de tala.
- Madera obtenida: depende del tipo de arbol y su edad.
- Reduce `arboles` de la casilla en `1`.

### 4.5 Descansar (duración: 3 ticks)

- Solo en casillas habitables (centro o viviendas).
- Reduce cansancio y aumenta energía.
- Afecta:
  - `cansancio -= x%` valor no especificado por el momento.
  - `energía += 6.25%`:por cada tick dormido por la noche, `3.125%` por cada tick dormido por el día.

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
    "cantidad": int, "precio_unitario": float, "precio_minimo": float,
    "calidad": float, "fecha_tick": int, "activa": bool
}

# Oferta de compra
{
    "id": int, "agente_id": int, "producto": str,
    "cantidad": int, "precio_unitario": float, "precio_maximo": float,
    "calidad": float, "fecha_tick": int, "activa": bool
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

- `comprar`, `vender`, `ofertar_compra`, `ofertar_venta`, `cancelar_oferta`
- **comprar**
- aplicar filtros, (nombre del articulo, categoria(alimento, herramienta, material), tipos de alimento(carnes, carbohidratos, lipidos, frutas, verduras))y calidad.
- se despliega una lista de menor a mayor con los productos ofertados segun el filtro, junto con el vendedor y la cantidad.
- se selecciona el producto que se deseas, proporciona la cantidad y se realiza la compra.
- el vendedor al que le compraste gana puntos de afinidad por ti.
- **vender**
- seleciionas el producto que quieres vender
- se despliega oferta de compradores de ese producto de mayor a menor precio, junto con el numbre de comprador y la cantidad.
- selecciona una oferta de la lista, proporciona la cantidad y se realiza la venta.
- el comprador al que le compraste gana puntos de afinidad por ti.
- **ofertar_compra**
- busca el producto a ofertas mediente los filtros.
- proporciona los valores necesarios para la oferta especificados en el punto 5.1 Ofertas y publica.
- **ofertar_venta**
- seleciona el producto de tu inventario
- proporciona los valores necesarios para la oferta especificados en el punto 5.1 Ofertas y publica.
- la cantidad de ese producto ofertado saldra de tu inventario.


Incluye estadísticas de precios, consulta de ofertas y publicación de nuevas ofertas.

### 6.4 Controles de Cámara

- `WASD` / Flechas: mover vista
- Rueda del mouse: zoom
- `F`: alternar seguimiento del jugador
- `HOME`: centrar en jugador

---

## 7. IA de Agentes (Estado actual: Implementado)
- marcaremos una rutina para los agentes que le servirá de guía para su día a día.
- esta rutina busca que el agente genere los ingresos minimos vitales que se calcula obteniendo el precio de cada tick de trabajo.
- el agente guardará un registro de los ingresos por tick que obtiene de cada actividad econimica a la que se ha dedicado.
- segun la personalidad de cada agente su rutina se amoldará para seguir su proposito.
- entre los propositos: maximizar ingresos, construir relaciones, buscar el osio, generar ingresos para establecer una familia, entre otros.
- guardara sus propias rutinas a las que será propenso a seguir.

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

---

## 7. Tipado estático gradual (opcional)

Se incorporó tipado base en módulos de dominio (`agentes/agente.py`, `sistema/economia.py`, `sistema/acciones.py`) para mejorar contratos internos sin romper compatibilidad.

Para validarlo localmente de forma opcional:

```bash
pip install mypy
mypy agentes/agente.py sistema/economia.py sistema/acciones.py
```

También se incluye configuración base en `mypy.ini` para adoptar el chequeo de forma incremental.
