# Fase 3 — Pipeline de datos Medallion

## 1. Objetivo

Implementar un pipeline de procesamiento de datos para el escenario
LogiTrack, utilizando una arquitectura Medallion con tres capas:
Bronze, Silver y Gold.

El procesamiento se desarrolló localmente mediante Python y PostgreSQL.
Los resultados se almacenaron en formato Parquet y se publicaron en
Azure Data Lake Storage Gen2.

## 2. Arquitectura implementada

```text
PostgreSQL 17 (Docker)
        |
        v
Bronze — Extracción de datos
        |
        v
Silver — Limpieza y validación
        |
        v
Gold — Modelado y métricas de negocio
        |
        v
Azure Data Lake Storage Gen2
```

Cada capa se procesa localmente y sus archivos se publican en el
contenedor correspondiente de Azure: `bronze`, `silver` o `gold`.

La ejecución de las transformaciones es manual mediante scripts Python.
No se implementó una orquestación automática end-to-end.

## 3. Capa Bronze

**Código:** `pipelines/bronze/extract_full.py`

Se implementó una extracción completa de las siete tablas de PostgreSQL.

Los datos se almacenan en formato Parquet, conservando los campos
originales e incorporando metadatos de ingesta:

- `ingestion_timestamp`
- `source_system`
- `batch_id`

**Resultados:**

- 7 tablas extraídas.
- 2.551.000 registros procesados.
- 54 archivos Parquet generados.

Los archivos se publicaron en el contenedor `bronze` de Azure.

**Limitación:** no se implementó ingesta incremental.

## 4. Capa Silver

**Código:** `pipelines/silver/`

Se implementaron transformaciones para las siete tablas de origen.

Las principales operaciones incluyen:

- Limpieza y estandarización de datos.
- Validación de campos obligatorios.
- Validación de reglas de negocio.
- Comprobaciones de integridad referencial.
- Tratamiento de información personal.
- Generación de reportes de calidad.

**Resultados:**

- 7 conjuntos de datos procesados.
- 2.551.000 registros válidos en la ejecución principal.
- 46 archivos Parquet publicados en la ruta principal de Silver.

También se realizaron pruebas controladas con datos incorrectos
para comprobar las reglas de rechazo.

**Reportes de calidad:**

- `silver_null_quality_report.csv`
- `silver_quality_summary.csv`

**Limitación:** los reportes no se generan automáticamente después
de cada ejecución del pipeline.

## 5. Capa Gold

**Código:** `pipelines/gold/`

Se implementaron dimensiones, tablas de hechos, agregaciones e
indicadores de negocio para analizar la operación logística.

### Dimensiones

- `dim_conductores`
- `dim_remitentes`
- `dim_zonas`

### Tablas de hechos

- `fact_envios`
- `fact_rutas`
- `fact_desempeno_conductor`
- `fact_trazabilidad_envio`
- `fact_alertas_zona`

### Agregaciones

- `agg_envios_diarios`
- `agg_desempeno_conductores`
- `agg_operacion_zonas`

### Indicador ejecutivo

- `kpi_resumen_ejecutivo`

**Resultados:**

- 12 conjuntos de datos Gold.
- 51 archivos Parquet.
- Archivos publicados y verificados en Azure Data Lake Storage Gen2.

Las definiciones de las agregaciones se encuentran en:

`docs/gold/aggregations.md`

El linaje de indicadores seleccionados se encuentra en:

`docs/lineage/gold_data_lineage.md`

## 6. Pruebas de calidad

Se implementaron validaciones automatizadas para comprobar:

- Reglas de limpieza de envíos.
- Reglas de limpieza de calificaciones.
- Integridad referencial.
- Integridad de las tablas Gold.

También se realizaron pruebas controladas del registro de errores
y de la continuidad de tareas independientes.

Los resultados están disponibles en:

`docs/evidence/entregables_03/`

La documentación de las verificaciones se encuentra en:

`docs/quality/automated_data_quality_checks.md`

## 7. Manejo de errores

Se creó una tabla PostgreSQL para registrar errores del pipeline:

`pipeline_error_log`

Su definición está en:

`sql/monitoring/create_pipeline_error_log.sql`

También se implementaron módulos Python para registrar errores
y ejecutar tareas capturando excepciones.

Se comprobó el registro de errores mediante pruebas controladas.

**Limitación:** estos componentes no están integrados en un
orquestador que ejecute automáticamente todas las capas.

## 8. Publicación en Azure

Se utilizaron los siguientes scripts:

- `scripts/upload_sql_to_bronze.sh`
- `scripts/upload_to_silver.sh`
- `scripts/upload_to_gold.sh`

Los archivos se almacenaron en los contenedores correspondientes
de Azure Data Lake Storage Gen2.

Se verificó la correspondencia entre los archivos locales y
los publicados en las rutas principales de Silver y Gold.

## 9. Limitaciones conocidas

La implementación tiene las siguientes limitaciones:

- Bronze utiliza extracción completa, no incremental.
- Los reportes Silver se generan mediante scripts independientes.
- No se automatizó la persistencia de todas las referencias inválidas.
- No se demostró la idempotencia completa del pipeline.
- No se implementó una orquestación automática end-to-end.
- No se configuraron notificaciones automáticas de incidentes.

Las limitaciones de la fase se explican con más detalle en:

`docs/technical_decisions/phase_3_limitations.md`

## 10. Conclusión

Se implementó un pipeline Medallion funcional para el escenario
LogiTrack, utilizando procesamiento local con Python y almacenamiento
en Azure Data Lake Storage Gen2.

La solución permite generar, transformar, validar y publicar datos
para su posterior análisis.

La automatización integral y la orquestación quedaron pendientes
para una siguiente etapa del proyecto.
