# Control de flota y costos de mantenimiento — caso de estudio

Modelo de datos, limpieza en Python/pandas y carga a PostgreSQL de tres años (2024-2026) de
control de gastos, mantenimiento y proveedores de una flota de maquinaria y vehículos de una
empresa constructora en Mérida, Yucatán, México.

Este repositorio es la versión **pública y anonimizada** de un control operativo real que sigue
en uso diario dentro de la empresa. Sirve como caso de estudio de portafolio: modelado de datos,
limpieza con reglas de negocio explícitas, y una capa SQL lista para análisis.

## Por qué existe este proyecto

El control original vivía en tres archivos de Excel con estructura distinta cada año (una hoja
por equipo en 2024/2025, una tabla única en 2026), sin un modelo de datos consistente y sin forma
de responder preguntas simples como "¿cuánto cuesta operar cada equipo?" o "¿qué proveedores
concentran el gasto?". Este proyecto reconstruye los tres años bajo un solo modelo relacional.

## Qué contiene

```
sql/        script de creación de tablas + carga completa (PostgreSQL)
data/       catálogos ya limpios y anonimizados (CSV): equipos, categorías, proveedores, movimientos
scripts/    pipeline de limpieza en Python (extracción, normalización de catálogos, anonimización)
docs/       notas de metodología
```

## Modelo de datos

Modelo tipo estrella: una tabla de hechos (`movimientos`) con tres catálogos alrededor.

| Tabla | Contenido |
|---|---|
| `equipos` | 36 equipos y centros de costo (compresor, grúa, retroexcavadoras, camionetas...) |
| `categorias` | 26 categorías de gasto/ingreso, con su grupo (`operativo`, `no_operativo`, etc.) |
| `proveedores` | 174 proveedores, marcando cuáles son personas físicas |
| `movimientos` | 1,689 movimientos de gasto/ingreso, cada uno ligado a un equipo, una categoría y un proveedor, en una fecha |

Tres años de archivos con formato distinto rara vez comparten un nombre de equipo, categoría o
proveedor escrito igual — la parte más laboriosa del pipeline (`scripts/01`–`05`) es construir esa
correspondencia de forma explícita y verificable, no un `GROUP BY` directo por nombre de texto.

## Cómo se limpió

1. **Catálogo de equipos** (`01_equipos.py`): unifica 36 equipos/centros de costo a través de los
   tres años, decidiendo de forma explícita qué hacer con equipos dados de baja, renombrados o
   fusionados por error de captura.
2. **Extracción de movimientos crudos** (`02_extraer_movimientos.py`): lee las tres estructuras de
   archivo distintas (hoja por equipo en 2024/2025, tabla única en 2026) a un formato común.
3. **Catálogo de proveedores** (`03_proveedores.py`): fusiona 280 nombres crudos de proveedor en
   174 proveedores únicos, resolviendo típos y variantes de escritura entre años.
4. **Catálogo de categorías** (`04_categorias.py`): normaliza ~50 valores de texto libre a 26
   categorías consistentes, separando ingreso/egreso y marcando las categorías no operativas
   (préstamos internos, venta de activos) para no inflar el costo real de operar la flota.
5. **Carga de movimientos** (`05_movimientos.py`): aplica los tres catálogos y reglas de negocio
   específicas (ej. cuándo el IVA ya viene incluido en el precio unitario, cómo tratar préstamos
   internos sin proveedor real) para producir la tabla de hechos final.

## Confidencialidad

La empresa autorizó este caso de estudio con la condición de no exponer información interna de la
empresa. Los **proveedores externos** (talleres, mecánicos, refaccionarias) conservan su nombre
real: trabajan bajo su propio nombre como parte de su oficio (recomendación de boca en boca), así
que no hay ahí ningún dato sensible de la empresa. Lo que sí se protege es información interna.
`scripts/06_anonimizar_para_publicacion.py` documenta exactamente qué se transformó:

- **Nómina eliminada por completo**: todo movimiento de categoría `SUELDOS`/`BONOS` se excluyó del
  dataset publicado (no solo se ocultó una columna).
- **Personal interno de la empresa** (empleados, y los beneficiarios de préstamos/anticipos
  internos) sustituido por un marcador genérico (`[EMPLEADO INTERNO]`, `[BENEFICIARIO INTERNO]`),
  tanto en las columnas dedicadas como en el texto libre de `concepto`/`medio_pago` donde
  aparecían mencionados — sin tocar los nombres de proveedores externos que aparecen en ese mismo
  texto.
- **Folios fiscales reales** sustituidos por una bandera booleana `tiene_factura` — se conserva la
  señal analítica (qué proporción del gasto tiene comprobante) sin exponer el folio real.
- Los archivos Excel originales y el control 2026 vivo nunca se suben a este repositorio
  (ver `.gitignore`); el pipeline los espera en una carpeta local `privado/` que no se versiona.

## Próximos pasos de este caso de estudio

- Capa financiera: costo total de propiedad por equipo, análisis reparar-vs-reemplazar.
- Dashboard en Tableau sobre este mismo modelo.
- Bitácora de mantenimiento (`servicios`) reconstruida desde WhatsApp y ligada a los movimientos
  de costo reales — en desarrollo, se publica en una siguiente entrega.
