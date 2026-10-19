# Limitaciones conocidas — Fase 3

## Contexto

La solución implementa una arquitectura Medallion con Python,
PostgreSQL, archivos Parquet y Azure Data Lake Storage Gen2.

Se priorizó una implementación sencilla, reproducible y comprensible.

## 1. Ingesta incremental Bronze

La ingesta implementada es completa (full load).

No se implementó procesamiento incremental porque las tablas
de origen no cuentan con campos de seguimiento de modificaciones.

## 2. Reportes de calidad Silver

Se generaron reportes de valores nulos, registros conformes
y resultados de validaciones.

Actualmente estos reportes se generan mediante scripts
independientes y no automáticamente después de cada ejecución.

## 3. Integridad referencial

Se implementaron cinco validaciones de integridad referencial.

No se encontraron referencias inválidas en los datos generados.

La persistencia automática de referencias inválidas con su
motivo de rechazo queda pendiente.

## 4. Idempotencia

Se repitieron las diez transformaciones Gold.

De los 51 archivos generados, 50 conservaron exactamente
su hash SHA-256.

El archivo del KPI ejecutivo presentó una diferencia de hash,
por lo que no se confirmó su reproducibilidad binaria.

No se ha demostrado la idempotencia del pipeline completo.

## 5. Manejo de errores

Se implementó una tabla de errores en PostgreSQL y un
ejecutor que captura y registra fallos.

También se comprobó que un fallo no impide ejecutar
una tarea independiente.

La integración automática del ejecutor con todos los
pipelines y las notificaciones de incidentes están pendientes.

## 6. Optimización Gold

Las tablas Gold se almacenan en formato Parquet.

No se implementaron estrategias adicionales de
particionamiento o clustering para consultas analíticas.

## 7. Alcance

La solución es una implementación de evaluación técnica,
no una plataforma preparada para producción.

Las funcionalidades pendientes se identifican explícitamente
para evitar presentar capacidades que no fueron implementadas.
