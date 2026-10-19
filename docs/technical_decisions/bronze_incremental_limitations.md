# Limitaciones de la ingesta incremental — Bronze

## Estado de implementación

La capa Bronze implementa una extracción completa (full load)
desde PostgreSQL hacia archivos Parquet almacenados en Azure Data Lake
Storage Gen2.

La ingesta incremental no fue implementada en esta versión.

## Limitación identificada

Las siete tablas de origen no disponen de columnas técnicas
como `created_at` o `updated_at` que permitan identificar
de forma confiable los registros modificados.

Aunque algunas tablas contienen fechas de negocio, estas
no representan necesariamente la fecha de última modificación.

Por tanto, utilizarlas como marcadores incrementales
podría ocasionar la pérdida de actualizaciones.

## Alternativa técnica propuesta

Implementar detección de cambios mediante:

1. Identificación de registros por clave primaria.
2. Cálculo de hashes sobre los atributos relevantes.
3. Almacenamiento del último hash procesado por registro.
4. Comparación con los registros actuales.
5. Procesamiento exclusivo de registros nuevos o modificados.

Esta alternativa requiere revisar los registros de origen
para detectar cambios, pero permite evitar la escritura
repetida de registros sin modificaciones.

Para un escenario productivo también se evaluaría
Change Data Capture (CDC), si la infraestructura
y los permisos disponibles lo permiten.

## Limitaciones de la implementación actual

- La extracción procesa todos los registros en cada ejecución.
- No existe un mecanismo de detección de actualizaciones.
- No se garantiza idempotencia en Bronze al repetir la extracción.
- Una nueva ejecución puede generar archivos adicionales
  que contengan registros ya procesados.

## Justificación del alcance

Debido al tiempo disponible para desarrollar la prueba técnica,
se priorizó la implementación y validación de las tres capas
de la arquitectura Medallion, las transformaciones de negocio,
los controles de calidad y las evidencias de ejecución.

La ingesta incremental queda identificada como una mejora
pendiente y no se presenta como una funcionalidad implementada.

## Evolución propuesta

1. Implementar una tabla de control de sincronización.
2. Desarrollar la detección de cambios por identificador y hash.
3. Registrar métricas de cada ejecución.
4. Incorporar una estrategia para eliminaciones.
5. Validar cargas iniciales, incrementales e idempotencia.
6. Integrar el mecanismo con Azure Data Factory.
