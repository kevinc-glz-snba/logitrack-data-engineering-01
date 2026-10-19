# Linaje de datos — Capa Gold

## Proyecto LogiTrack

### Objetivo

Documentar el origen, las transformaciones y el propósito de
los principales campos calculados en la capa Gold.

La arquitectura sigue el patrón Medallion:

PostgreSQL → Bronze → Silver → Gold → KPIs

---

## 1. Campo: tasa_entrega

**Tabla destino:** `kpi_resumen_ejecutivo`

**Fuente original:** `tms_envios`

**Campo original:** `estado_final`

**Recorrido:**

1. PostgreSQL: `tms_envios.estado_final`.
2. Bronze: extracción del registro original.
3. Silver: limpieza y estandarización.
4. Gold: `fact_envios.estado_final`.
5. Agregación: `agg_envios_diarios`.
6. KPI: `kpi_resumen_ejecutivo.tasa_entrega`.

**Transformación:**

```python
entregados = (estado_final == "Entregado").sum()

tasa_entrega = entregados / total_envios
```

**Propósito:**

Medir la proporción de envíos entregados exitosamente.

**Resultado de referencia:**

94.98 % sobre 2,000,000 de envíos.

---

## 2. Campo: tasa_cumplimiento_sla

**Tabla destino:** `kpi_resumen_ejecutivo`

**Fuentes originales:**

- `tms_envios`
- `cli_remitentes`

**Campos utilizados:**

- Fecha y hora de recepción.
- Fecha y hora estimada de entrega efectiva.
- SLA del remitente.

**Recorrido:**

1. PostgreSQL: `tms_envios` y `cli_remitentes`.
2. Bronze: extracción de ambas fuentes.
3. Silver: limpieza y tipado.
4. Gold: `fact_envios.cumple_sla`.
5. Agregación: `agg_envios_diarios.cumplen_sla`.
6. KPI: `kpi_resumen_ejecutivo.tasa_cumplimiento_sla`.

**Transformación:**

```python
cumple_sla = duracion_entrega_horas <= sla_horas

tasa_cumplimiento_sla = (
    envios_que_cumplen_sla / total_envios
)
```

**Propósito:**

Medir el cumplimiento del tiempo de entrega acordado.

**Resultado de referencia:**

51.70 %.

**Limitaciones:**

La fuente contiene la fecha real de entrega, pero no una hora
real de entrega independiente. La implementación estima el
momento de entrega utilizando los intentos registrados.

En los datos sintéticos utilizados, todos los remitentes
tienen un SLA de 24 horas.

Por tanto, el indicador depende de esas suposiciones.

---

## 3. Campo: score_desempeno

**Tabla destino:** `fact_desempeno_conductor`

**Fuentes originales:**

- `tms_envios`
- `gps_rutas`
- `cal_destinatarios`

**Recorrido:**

1. PostgreSQL: tres tablas operativas.
2. Bronze: extracción.
3. Silver: limpieza y validación.
4. Gold: `fact_envios` y `fact_rutas`.
5. Gold: `fact_desempeno_conductor`.

**Transformación:**

```text
score_desempeno =

    0.35 × tasa_exito
  + 0.20 × adherencia_normalizada
  + 0.20 × velocidad_normalizada
  + 0.15 × intentos_normalizados
  + 0.10 × calificacion_normalizada
```

El resultado se redondea a dos decimales.

**Propósito:**

Medir el desempeño operativo del conductor considerando
entregas, rutas, productividad, intentos y satisfacción.

**Resultado de referencia:**

- Evaluaciones totales: 130,500.
- Evaluaciones con score: 49,755.
- Cobertura: 38.13 %.
- Score promedio disponible: 0.8583.

**Limitaciones:**

- No se calcula score cuando faltan componentes.
- La velocidad utiliza un estándar provisional de 20 km/h.
- No se implementó un estándar específico por zona.
- La granularidad es conductor-fecha de recepción.

---

## 4. Campo: dias_desde_recepcion

**Tabla destino:** `fact_trazabilidad_envio`

**Fuentes originales:**

- `dir_novedades`
- `tms_envios`

**Campos utilizados:**

- `dir_novedades.fec_novedad`
- `tms_envios.fec_recepcion`

**Recorrido:**

PostgreSQL → Bronze → Silver → Gold.

**Transformación:**

```python
dias_desde_recepcion = (
    fec_novedad - fec_recepcion
).days
```

**Propósito:**

Medir cuántos días transcurrieron desde la recepción
del envío hasta el registro de una novedad.

**Limitación:**

La fecha de novedad no incluye hora.

El cálculo tiene precisión de días, no de horas.

---

## 5. Campo: genera_alerta

**Tabla destino:** `fact_alertas_zona`

**Fuente original:** `tms_envios`

**Campos utilizados:**

- `id_zona_destino`
- `fec_recepcion`
- `estado_final`

**Recorrido:**

1. PostgreSQL: `tms_envios`.
2. Bronze: extracción.
3. Silver: limpieza.
4. Gold: `fact_envios`.
5. Gold: `fact_alertas_zona`.

**Transformación:**

```python
tasa_fallo = envios_fallidos / total_envios

tasa_historica = (
    fallos_historicos / envios_historicos
)

incremento_relativo = (
    tasa_fallo - tasa_historica
) / tasa_historica

genera_alerta = incremento_relativo > 0.25
```

**Reglas adicionales:**

- Comparación con los cuatro mismos días de la semana
  anteriores: 7, 14, 21 y 28 días.
- Mínimo de 10 envíos históricos.
- Si la tasa histórica es cero, el incremento porcentual
  queda sin calcular.
- La fecha utilizada es la recepción del envío.

**Propósito:**

Identificar zonas con incrementos significativos en
su tasa de fallos.

**Resultado de referencia:**

28,104 alertas.

---

## Consideraciones generales

Los resultados documentados corresponden a datos
sintéticos de 2025.

Las transformaciones se ejecutaron localmente mediante
Python y pandas, con archivos Parquet.

La construcción local de Gold no demuestra por sí sola
la ejecución orquestada del pipeline completo en Azure.

Las decisiones y limitaciones documentadas deben
considerarse al interpretar los indicadores.