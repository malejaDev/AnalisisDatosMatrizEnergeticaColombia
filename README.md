<div align="center">

# ⚡📊 Análisis de Datos: Matriz Energética de Colombia

**Proyecto final – Talento Tech | Curso: Análisis de Datos**

![SQL](https://img.shields.io/badge/SQL-MySQL%2FMariaDB-4479A1?logo=mysql&logoColor=white)
![Estado](https://img.shields.io/badge/estado-en%20progreso-yellow)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)
![Periodo](https://img.shields.io/badge/periodo-2020%E2%80%932025-blue)

</div>

---

## 🧭 Índice

- [✨ Resumen visual](#resumen)
- [👥 Integrantes](#integrantes)
- [🎯 Objetivo del proyecto](#objetivo)
- [🗂️ Contenido del repositorio](#contenido)
- [✅ Requisitos](#requisitos)
- [🚀 Cómo ejecutar (base de datos + consultas)](#ejecucion)
- [🧩 Modelo de datos (alto nivel)](#modelo)
- [🔎 Preguntas de análisis incluidas (ejemplos)](#preguntas)
- [📌 Resultados y conclusiones (por completar)](#resultados)
- [🧾 Fuentes de datos (por completar)](#fuentes)
- [🛣️ Próximos pasos (roadmap)](#roadmap)
- [📄 Licencia](#licencia)

<a id="resumen"></a>
## ✨ Resumen visual

| 🧩 Módulo | 📦 ¿Qué hay? | ✅ Estado |
|---|---|---|
| 🗄️ Base de datos | Esquema + datos de ejemplo (2020–2025) | ✅ Listo |
| 🧠 Consultas SQL | Consultas analíticas (Q01–Q28) | ✅ Listo |
| 📓 Notebooks | EDA / limpieza / visualizaciones | ⏳ Pendiente |
| 📁 Datos | Dataset(s) (o instrucciones de descarga) | ⏳ Pendiente |
| 📈 Resultados | Hallazgos + gráficas + conclusiones | ⏳ Pendiente |
| 🧾 Fuentes | Fuentes oficiales + supuestos + licencia | ⏳ Pendiente |

### 🧰 Stack (actual)

- 🐬 **MySQL/MariaDB** (scripts en `database/`)
- 📄 **SQL** (modelo + consultas)

### 🧭 Navegación rápida

- 🧱 **Crear/cargar datos**: `database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`
- 🔍 **Ejecutar análisis**: `database/Consultas_Analisis_Matriz_Energetica_Colombia.sql`

<a id="integrantes"></a>
## 👥 Integrantes

- Claudia Arroyave
- Michely Muñoz
- Jesus Garcia
- Maria Alejandra Colorado Ríos

<a id="objetivo"></a>
## 🎯 Objetivo del proyecto

Analizar la **diversificación de la matriz energética en Colombia** usando un modelo de datos en SQL y consultas analíticas (inicialmente con información de ejemplo para el período **2020–2025**).

> Este README está diseñado para **irse completando** a medida que se agreguen más entregables (notebooks, visualizaciones, fuentes oficiales, conclusiones, etc.).

<a id="contenido"></a>
## 🗂️ Contenido del repositorio

- `database/`
  - `Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`: crea el esquema, tablas e inserta datos.
  - `Consultas_Analisis_Matriz_Energetica_Colombia.sql`: consultas para análisis (requiere el script anterior).
- `LICENSE`: licencia del repositorio.

<a id="requisitos"></a>
## ✅ Requisitos

- Un motor SQL compatible con `CREATE DATABASE IF NOT EXISTS` y `AUTO_INCREMENT` (por ejemplo, **MySQL** o **MariaDB**).

<a id="ejecucion"></a>
## 🚀 Cómo ejecutar (base de datos + consultas)

1. Ejecuta el script de creación/carga:
   - `database/Matriz_Energetica_Colombia_Schema_y_Datos_2020_2025.sql`
2. Ejecuta las consultas:
   - `database/Consultas_Analisis_Matriz_Energetica_Colombia.sql`

El esquema utiliza la base de datos `MatrizEnergeticaCol`.

<a id="modelo"></a>
## 🧩 Modelo de datos (alto nivel)

- **Dimensiones**
  - `Dim_TipoEnergia`: catálogo de fuentes (convencional / no convencional).
  - `Dim_Regulacion`: leyes/incentivos.
  - `Dim_Proyecto`: proyectos, ubicación y capacidad (MW).
- **Hechos**
  - `Fact_Generacion`: generación (GWh) y factor de planta por fecha.
  - `Fact_Costos`: costos (LCOE, CAPEX, OPEX) por año.
  - `Fact_ImpactoAmbiental`: CO₂ evitado y ahorro de agua.
  - `Fact_Cobertura`: usuarios atendidos, disponibilidad y regulación aplicada.

<a id="preguntas"></a>
## 🔎 Preguntas de análisis incluidas (ejemplos)

En `database/Consultas_Analisis_Matriz_Energetica_Colombia.sql` hay consultas para:

- generación total por proyecto y por fuente
- promedio de factor de planta
- agregaciones mensuales
- rankings (top días / ranking por fuente)
- costos (LCOE/CAPEX) versus promedios
- impacto ambiental y cobertura (usuarios)
- chequeos de consistencia (anti-joins / NOT EXISTS)

<a id="resultados"></a>
## 📌 Resultados y conclusiones (por completar)

- **Hallazgos clave**: TBD
- **Visualizaciones**: TBD
- **Recomendaciones**: TBD

<a id="fuentes"></a>
## 🧾 Fuentes de datos (por completar)

- **Fuentes oficiales**: TBD (URL, fecha de consulta, licencia)
- **Supuestos**: TBD

<a id="roadmap"></a>
## 🛣️ Próximos pasos (roadmap)

- [ ] Agregar notebooks (`.ipynb`) con EDA y visualizaciones.
- [ ] Agregar dataset(s) en `data/` (o instrucciones de descarga si es muy grande).
- [ ] Documentar el diccionario de datos y definición de métricas.
- [ ] Publicar conclusiones finales del proyecto.

<a id="licencia"></a>
## 📄 Licencia

Ver `LICENSE`.
