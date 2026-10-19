# Agregaciones de la capa Gold

## Objetivo

Las agregaciones permiten consultar indicadores del negocio sin tener
que procesar nuevamente todos los registros de envíos.

Se generan mediante el script:

`pipelines/gold/aggregations/build_aggregations.py`

Los resultados se almacenan en formato Parquet dentro de
`data/gold/aggregations/` y están publicados en Azure Data Lake Storage Gen2.

---

## 1. agg_envios_diarios

**Archivo:** `agg_envios_diarios.parquet`

**Origen:** `fact_envios`

**Agrupación:** fecha de recepción del envío.

**Métricas:**

| Campo | Definición |
|---|---|
| fecha | Fecha de recepción del envío. |
| total_envios | Cantidad total de envíos recibidos en la fecha. |
| entregados | Cantidad de envíos con estado final `Entregado`. |
| fallidos | Cantidad de envíos con estado final `Fallido`. |
| cumplen_sla | Cantidad de envíos que cumplen el SLA. |
| tasa_entrega | `entregados / total_envios`. |
| tasa_cumplimiento_sla | `cumplen_sla / total_envios`. |

**Uso de negocio:**

Permite conocer el volumen diario de envíos, el porcentaje de entregas
exitosas y el cumplimiento del SLA.

**Resultado:** 261 registros.

---

## 2. agg_desempeno_conductores

**Archivo:** `agg_desempeno_conductores.parquet`

**Origen:**
- `fact_envios`
- `fact_desempeno_conductor`

**Agrupación:** identificador del conductor (`cond_id`).

**Métricas:**

| Campo | Definición |
|---|---|
| cond_id | Identificador del conductor. |
| total_envios | Cantidad de envíos asociados al conductor. |
| entregados | Cantidad de envíos entregados. |
| tasa_exito | `entregados / total_envios`. |
| dias_evaluados | Cantidad de registros diarios de desempeño. |
| dias_con_score | Cantidad de registros con score disponible. |
| score_promedio | Promedio de los scores disponibles. |
| cobertura_score | `dias_con_score / dias_evaluados`. |

**Uso de negocio:**

Permite comparar el desempeño de los conductores mediante su tasa de
entregas exitosas y su puntuación promedio.

El score promedio puede ser nulo cuando no existen evaluaciones
con puntuación disponible.

**Resultado:** 500 registros.

---

## 3. agg_operacion_zonas

**Archivo:** `agg_operacion_zonas.parquet`

**Origen:**
- `fact_envios`
- `fact_alertas_zona`

**Agrupación:** identificador de la zona de destino (`id_zona_destino`).

**Métricas:**

| Campo | Definición |
|---|---|
| id_zona_destino | Identificador de la zona. |
| total_envios | Cantidad de envíos destinados a la zona. |
| fallidos | Cantidad de envíos fallidos. |
| tasa_fallo | `fallidos / total_envios`. |
| dias_analizados | Cantidad de registros diarios analizados para alertas. |
| dias_con_alerta | Cantidad de registros diarios que generan una alerta. |

**Uso de negocio:**

Permite identificar zonas con mayores tasas de fallo y consultar
cuántos días presentaron alertas operativas.

**Resultado:** 300 registros.

---

## Ejecución

Desde la raíz del proyecto:

```bash
python -m pipelines.gold.aggregations.build_aggregations
```

El script genera los tres archivos Parquet y verifica que la suma
de los envíos diarios coincida con el total de registros de `fact_envios`.

## Almacenamiento en Azure

Cuenta: `stlogitrackdeveus201`

Contenedor: `gold`

Rutas:

- `aggregations/agg_envios_diarios.parquet`
- `aggregations/agg_desempeno_conductores.parquet`
- `aggregations/agg_operacion_zonas.parquet`
