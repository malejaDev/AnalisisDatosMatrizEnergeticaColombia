-- Consultas de análisis para MatrizEnergeticaCol
-- Requiere haber ejecutado: Matriz_Energetica_Colombia_Completo.sql (creación de esquema + carga de datos)

USE MatrizEnergeticaCol;

/* ============================================================================
   Q01) Listar los tipos de energía (dimensión) y si son convencionales.
   ============================================================================ */
SELECT
  id_tipo_energia,
  fuente,
  es_convencional,
  descripcion
FROM Dim_TipoEnergia
ORDER BY id_tipo_energia;

/* ============================================================================
   Q02) Listar proyectos con su fuente energética y capacidad instalada (MW).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  p.depto,
  t.fuente,
  p.capacidad_mw
FROM Dim_Proyecto p
JOIN Dim_TipoEnergia t ON t.id_tipo_energia = p.id_tipo
ORDER BY p.capacidad_mw DESC;

select * from Dim_Proyecto;

/* ============================================================================
   Q03) Proyectos de un departamento específico (filtro con WHERE).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre,
  p.depto,
  p.capacidad_mw
FROM Dim_Proyecto p
WHERE p.depto = 'La Guajira'
ORDER BY p.capacidad_mw DESC;

/* ============================================================================
   Q04) Generación diaria por proyecto en un rango de fechas (WHERE por fecha).
   ============================================================================ */
SELECT
  g.id_proyecto,
  p.nombre AS proyecto,
  g.fecha,
  g.generacion_gwh,
  g.factor_planta_pct
FROM Fact_Generacion g
JOIN Dim_Proyecto p ON p.id_proyecto = g.id_proyecto
WHERE g.fecha BETWEEN '2020-01-01' AND '2020-01-31'
ORDER BY g.id_proyecto, g.fecha;

/* ============================================================================
   Q05) Total de generación (GWh) por proyecto (GROUP BY).
   ============================================================================ */
SELECT
  g.id_proyecto,
  p.nombre AS proyecto,
  SUM(g.generacion_gwh) AS total_gwh
FROM Fact_Generacion g
JOIN Dim_Proyecto p
  ON p.id_proyecto = g.id_proyecto
GROUP BY g.id_proyecto, p.nombre
ORDER BY total_gwh DESC;

/* ============================================================================
   Q06) Total de generación (GWh) por fuente energética (JOIN + GROUP BY).
   ============================================================================ */
SELECT
  t.fuente,
  SUM(g.generacion_gwh) AS total_gwh
FROM Fact_Generacion g
JOIN Dim_Proyecto p ON p.id_proyecto = g.id_proyecto
JOIN Dim_TipoEnergia t ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
ORDER BY total_gwh DESC;

/* ============================================================================
   Q07) Promedio del factor de planta por proyecto (GROUP BY + AVG).
   ============================================================================ */
SELECT
  g.id_proyecto,
  p.nombre AS proyecto,
  AVG(g.factor_planta_pct) AS factor_planta_promedio_pct
FROM Fact_Generacion g
JOIN Dim_Proyecto p ON p.id_proyecto = g.id_proyecto
GROUP BY g.id_proyecto, p.nombre
ORDER BY factor_planta_promedio_pct DESC;

/* ============================================================================
   Q08) Días con factor de planta alto (WHERE) para un proyecto (ejemplo 101).
   ============================================================================ */
SELECT
  g.fecha,
  g.generacion_gwh,
  g.factor_planta_pct
FROM Fact_Generacion g
WHERE g.id_proyecto = 101
  AND g.factor_planta_pct >= 75
ORDER BY g.fecha;

/* ============================================================================
   Q09) Generación mensual (agregación por año-mes) por fuente.
   Nota: usa DATE_FORMAT (MySQL).
   ============================================================================ */
SELECT
  DATE_FORMAT(g.fecha, '%Y-%m') AS anio_mes,
  t.fuente,
  SUM(g.generacion_gwh) AS total_gwh
FROM Fact_Generacion g
JOIN Dim_Proyecto p
  ON p.id_proyecto = g.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY DATE_FORMAT(g.fecha, '%Y-%m'), t.fuente
ORDER BY anio_mes, total_gwh DESC;

/* ============================================================================
   Q10) Fuentes con más de N proyectos (HAVING COUNT).
   ============================================================================ */
SELECT
  t.fuente,
  COUNT(*) AS cantidad_proyectos
FROM Dim_Proyecto p
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
HAVING COUNT(*) >= 2
ORDER BY cantidad_proyectos DESC, t.fuente;

/* ============================================================================
   Q11) Departamentos con más de 1 proyecto (GROUP BY + HAVING COUNT).
   ============================================================================ */
SELECT
  p.depto,
  COUNT(*) AS cantidad_proyectos
FROM Dim_Proyecto p
GROUP BY p.depto
HAVING COUNT(*) > 1
ORDER BY cantidad_proyectos DESC, p.depto;

/* ============================================================================
   Q12) Top 5 días de mayor generación por proyecto (subconsulta con ORDER/LIMIT).
   ============================================================================ */
SELECT
  x.id_proyecto,
  p.nombre AS proyecto,
  x.fecha,
  x.generacion_gwh
FROM (
  SELECT id_proyecto, fecha, generacion_gwh
  FROM Fact_Generacion
  ORDER BY generacion_gwh DESC
  LIMIT 5
) x
JOIN Dim_Proyecto p
  ON p.id_proyecto = x.id_proyecto
ORDER BY x.generacion_gwh DESC;

/* ============================================================================
   Q13) Proyectos con LCOE por debajo del promedio global (subconsulta escalar).
   ============================================================================ */
SELECT
  c.id_proyecto,
  p.nombre AS proyecto,
  c.anio,
  c.lcoe_usd_mwh
FROM Fact_Costos c
JOIN Dim_Proyecto p
  ON p.id_proyecto = c.id_proyecto
WHERE c.lcoe_usd_mwh < (SELECT AVG(lcoe_usd_mwh) FROM Fact_Costos)
ORDER BY c.lcoe_usd_mwh ASC;

/* ============================================================================
   Q14) LCOE promedio por fuente (JOIN + GROUP BY).
   ============================================================================ */
SELECT
  t.fuente,
  AVG(c.lcoe_usd_mwh) AS lcoe_promedio_usd_mwh
FROM Fact_Costos c
JOIN Dim_Proyecto p
  ON p.id_proyecto = c.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
ORDER BY lcoe_promedio_usd_mwh ASC;

/* ============================================================================
   Q15) Proyectos con CAPEX mayor al promedio de su propia fuente (subconsulta correlacionada).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  t.fuente,
  c.capex_musd
FROM Dim_Proyecto p
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
JOIN Fact_Costos c
  ON c.id_proyecto = p.id_proyecto
WHERE c.capex_musd > (
  SELECT AVG(c2.capex_musd)
  FROM Fact_Costos c2
  JOIN Dim_Proyecto p2
    ON p2.id_proyecto = c2.id_proyecto
  WHERE p2.id_tipo = p.id_tipo
)
ORDER BY t.fuente, c.capex_musd DESC;

/* ============================================================================
   Q16) Impacto ambiental por fuente: CO2 evitado total y ahorro de agua total.
   ============================================================================ */
SELECT
  t.fuente,
  SUM(i.co2_evitado_ton) AS co2_evitado_total_ton,
  SUM(i.ahorro_agua_m3) AS ahorro_agua_total_m3
FROM Fact_ImpactoAmbiental i
JOIN Dim_Proyecto p
  ON p.id_proyecto = i.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
ORDER BY co2_evitado_total_ton DESC;

/* ============================================================================
   Q17) CO2 evitado por MW instalado (indicador de intensidad) por proyecto.
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  t.fuente,
  p.capacidad_mw,
  i.co2_evitado_ton,
  (i.co2_evitado_ton / NULLIF(p.capacidad_mw, 0)) AS co2_evitado_por_mw
FROM Fact_ImpactoAmbiental i
JOIN Dim_Proyecto p
  ON p.id_proyecto = i.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
ORDER BY co2_evitado_por_mw DESC;

/* ============================================================================
   Q18) Cobertura: usuarios atendidos por fuente (JOIN + GROUP BY).
   ============================================================================ */
SELECT
  t.fuente,
  SUM(cb.usuarios) AS usuarios_totales
FROM Fact_Cobertura cb
JOIN Dim_Proyecto p
  ON p.id_proyecto = cb.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
ORDER BY usuarios_totales DESC;

/* ============================================================================
   Q19) Regulaciones aplicadas: cantidad de proyectos por ley (GROUP BY + COUNT DISTINCT).
   ============================================================================ */
SELECT
  r.ley,
  COUNT(DISTINCT cb.id_proyecto) AS proyectos_cubiertos
FROM Fact_Cobertura cb
JOIN Dim_Regulacion r
  ON r.id_regulacion = cb.id_reg
GROUP BY r.ley
ORDER BY proyectos_cubiertos DESC, r.ley;

/* ============================================================================
   Q20) Proyectos con alta disponibilidad (>= 99%) y su regulación aplicada.
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  r.ley,
  cb.disponibilidad_pct,
  cb.usuarios
FROM Fact_Cobertura cb
JOIN Dim_Proyecto p
  ON p.id_proyecto = cb.id_proyecto
JOIN Dim_Regulacion r
  ON r.id_regulacion = cb.id_reg
WHERE cb.disponibilidad_pct >= 99
ORDER BY cb.disponibilidad_pct DESC, cb.usuarios DESC;

/* ============================================================================
   Q21) Días por proyecto con generación por encima de su propio promedio (subconsulta correlacionada).
   ============================================================================ */
SELECT
  g.id_proyecto,
  p.nombre AS proyecto,
  g.fecha,
  g.generacion_gwh
FROM Fact_Generacion g
JOIN Dim_Proyecto p
  ON p.id_proyecto = g.id_proyecto
WHERE g.generacion_gwh > (
  SELECT AVG(g2.generacion_gwh)
  FROM Fact_Generacion g2
  WHERE g2.id_proyecto = g.id_proyecto
)
ORDER BY g.id_proyecto, g.generacion_gwh DESC;

/* ============================================================================
   Q22) Ranking de proyectos por generación total dentro de su fuente (subconsulta + join a agregados).
   ============================================================================ */
SELECT
  t.fuente,
  a.id_proyecto,
  p.nombre AS proyecto,
  a.total_gwh
FROM (
  SELECT id_proyecto, SUM(generacion_gwh) AS total_gwh
  FROM Fact_Generacion
  GROUP BY id_proyecto
) a
JOIN Dim_Proyecto p
  ON p.id_proyecto = a.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
ORDER BY t.fuente, a.total_gwh DESC;

/* ============================================================================
   Q23) Fuente más diversificada por número de proyectos (subconsulta para MAX).
   ============================================================================ */
SELECT
  x.fuente,
  x.cantidad_proyectos
FROM (
  SELECT t.fuente, COUNT(*) AS cantidad_proyectos
  FROM Dim_Proyecto p
  JOIN Dim_TipoEnergia t
    ON t.id_tipo_energia = p.id_tipo
  GROUP BY t.fuente
) x
WHERE x.cantidad_proyectos = (
  SELECT MAX(y.cantidad_proyectos)
  FROM (
    SELECT COUNT(*) AS cantidad_proyectos
    FROM Dim_Proyecto
    GROUP BY id_tipo
  ) y
);

/* ============================================================================
   Q24) Proyectos que NO tienen registro de costos (anti-join con NOT EXISTS).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  p.depto
FROM Dim_Proyecto p
WHERE NOT EXISTS (
  SELECT 1
  FROM Fact_Costos c
  WHERE c.id_proyecto = p.id_proyecto
)
ORDER BY p.id_proyecto;

/* ============================================================================
   Q25) Consistencia: proyectos que tienen generación pero faltan en impacto ambiental (NOT EXISTS).
   ============================================================================ */
SELECT DISTINCT
  g.id_proyecto,
  p.nombre AS proyecto
FROM Fact_Generacion g
JOIN Dim_Proyecto p
  ON p.id_proyecto = g.id_proyecto
WHERE NOT EXISTS (
  SELECT 1
  FROM Fact_ImpactoAmbiental i
  WHERE i.id_proyecto = g.id_proyecto
)
ORDER BY g.id_proyecto;

/* ============================================================================
   Q26) Indicador: usuarios por MW instalado por proyecto (JOIN + cálculo).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  t.fuente,
  p.capacidad_mw,
  cb.usuarios,
  (cb.usuarios / NULLIF(p.capacidad_mw, 0)) AS usuarios_por_mw
FROM Fact_Cobertura cb
JOIN Dim_Proyecto p
  ON p.id_proyecto = cb.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
ORDER BY usuarios_por_mw DESC;

/* ============================================================================
   Q27) Resumen por proyecto: generación total, LCOE, CO2 evitado y usuarios (join de tablas de hechos).
   ============================================================================ */
SELECT
  p.id_proyecto,
  p.nombre AS proyecto,
  t.fuente,
  SUM(g.generacion_gwh) AS total_gwh,
  c.lcoe_usd_mwh,
  i.co2_evitado_ton,
  cb.usuarios,
  cb.disponibilidad_pct
FROM Dim_Proyecto p
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
LEFT JOIN Fact_Generacion g
  ON g.id_proyecto = p.id_proyecto
LEFT JOIN Fact_Costos c
  ON c.id_proyecto = p.id_proyecto
LEFT JOIN Fact_ImpactoAmbiental i
  ON i.id_proyecto = p.id_proyecto
LEFT JOIN Fact_Cobertura cb
  ON cb.id_proyecto = p.id_proyecto
GROUP BY
  p.id_proyecto, p.nombre, t.fuente, c.lcoe_usd_mwh, i.co2_evitado_ton, cb.usuarios, cb.disponibilidad_pct
ORDER BY total_gwh DESC;

/* ============================================================================
   Q28) Fuentes con generación total y cantidad de proyectos con datos de generación (HAVING COUNT DISTINCT).
   ============================================================================ */
SELECT
  t.fuente,
  SUM(g.generacion_gwh) AS total_gwh,
  COUNT(DISTINCT g.id_proyecto) AS proyectos_con_generacion
FROM Fact_Generacion g
JOIN Dim_Proyecto p
  ON p.id_proyecto = g.id_proyecto
JOIN Dim_TipoEnergia t
  ON t.id_tipo_energia = p.id_tipo
GROUP BY t.fuente
HAVING COUNT(DISTINCT g.id_proyecto) >= 1
ORDER BY total_gwh DESC;

