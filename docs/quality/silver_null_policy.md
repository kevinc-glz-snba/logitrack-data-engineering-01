# Política de valores nulos — Silver

## Objetivo

Definir el tratamiento de valores nulos en los datasets
Silver de LogiTrack.

La presencia de valores nulos no implica automáticamente
que un registro sea inválido.

## Resultados

Se analizaron 91 columnas pertenecientes a siete datasets
Silver, correspondientes a 2,551,000 registros.

Se identificaron seis columnas con valores nulos.

## Política por columna

| Tabla | Columna | Política |
|---|---|---|
| cal_destinatarios | comentario_texto | Nulo permitido: comentario opcional. |
| tms_envios | fec_entrega_real | Nulo permitido cuando estado_final = Fallido. |
| tms_envios | fec_intento2 | Nulo permitido cuando no existe segundo intento. |
| tms_envios | hra_intento2 | Debe tener la misma presencia que fec_intento2. |
| tms_envios | resultado_intento2 | Debe tener la misma presencia que fec_intento2. |
| tms_envios | motivo_fallo_cod | Nulo permitido cuando estado_final = Entregado. |

## Validaciones realizadas

Se comprobaron los siguientes resultados:

- 1,899,666 envíos entregados tienen fecha de entrega.
- 1,899,666 envíos entregados no tienen motivo de fallo.
- 100,334 envíos fallidos no tienen fecha de entrega.
- 100,334 envíos fallidos tienen motivo de fallo.
- No se encontraron inconsistencias de presencia entre
  fecha, hora y resultado del segundo intento.

## Conclusión

Los valores nulos identificados en los campos evaluados
son coherentes con las reglas de negocio establecidas.

La política documenta las condiciones bajo las cuales
estos valores se consideran aceptables.

## Alcance

Las validaciones anteriores se realizaron sobre los archivos
Silver existentes.

No sustituyen las validaciones de integridad referencial,
duplicados, tipos de datos ni el registro de rechazos.
