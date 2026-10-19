# Controles automatizados de calidad de datos

## Objetivo

Verificar reglas de calidad en las capas Silver y Gold del proyecto
LogiTrack, utilizando pruebas automatizadas reproducibles.

## Resultados de ejecución

Fecha de ejecución: 2026-10-18/19 (según entorno local).

Suites ejecutadas: 4
Suites aprobadas: 4
Suites fallidas: 0

## Controles Silver

| ID | Control | Resultado |
|---|---|---|
| DQ-01 | Calificaciones dentro del rango permitido (1 a 5) | PASS |
| DQ-02 | Detección de identificadores duplicados | PASS |
| DQ-03 | Rechazo de referencias obligatorias nulas | PASS |
| DQ-04 | Validación de peso positivo en envíos | PASS |
| DQ-05 | Validación de estados permitidos en envíos | PASS |
| DQ-06 | Coherencia entre estado y fecha de entrega | PASS |
| DQ-07 | Integridad referencial entre datasets Silver | PASS |

Las pruebas de limpieza utilizan anomalías controladas.
Se introdujeron siete registros inválidos y los siete fueron rechazados.

La validación referencial comprobó cinco relaciones y encontró
cero referencias inválidas.

## Controles Gold

| ID | Control | Resultado |
|---|---|---|
| DQ-08 | Cantidades esperadas de dimensiones y hechos | PASS |
| DQ-09 | Unicidad de claves de dimensiones y hechos | PASS |
| DQ-10 | Indicadores dentro del rango de 0 a 1 | PASS |
| DQ-11 | Conciliación de agregaciones con datos base | PASS |

## Ejecución

Desde la raíz del proyecto:

```bash
python -m tests.test_calificaciones
python -m tests.test_envios
python -m pipelines.quality.validate_referencias
python -m tests.test_gold_integrity
