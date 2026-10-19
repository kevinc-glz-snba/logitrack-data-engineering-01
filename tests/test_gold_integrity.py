from pathlib import Path

import pandas as pd


GOLD = Path("data/gold")
AGG = GOLD / "aggregations"


def verificar(condicion, mensaje):
    if not condicion:
        raise AssertionError(mensaje)

    print(f"OK - {mensaje}")


def main():
    print("\nVALIDACIÓN INTEGRAL DE GOLD\n")

    # 1. Cargar dimensiones
    conductores = pd.read_parquet(
        GOLD / "dim_conductores.parquet"
    )

    remitentes = pd.read_parquet(
        GOLD / "dim_remitentes.parquet"
    )

    zonas = pd.read_parquet(
        GOLD / "dim_zonas.parquet"
    )

    # 2. Cargar tablas de hechos
    rutas = pd.read_parquet(
        GOLD / "fact_rutas.parquet"
    )

    desempeno = pd.read_parquet(
        GOLD / "fact_desempeno_conductor.parquet"
    )

    trazabilidad = pd.read_parquet(
        GOLD / "fact_trazabilidad_envio.parquet"
    )

    alertas = pd.read_parquet(
        GOLD / "fact_alertas_zona.parquet"
    )

    # 3. Cargar agregaciones
    agg_diarios = pd.read_parquet(
        AGG / "agg_envios_diarios.parquet"
    )

    agg_conductores = pd.read_parquet(
        AGG / "agg_desempeno_conductores.parquet"
    )

    agg_zonas = pd.read_parquet(
        AGG / "agg_operacion_zonas.parquet"
    )

    print("1. DIMENSIONES")

    verificar(
        len(conductores) == 500,
        "500 conductores"
    )

    verificar(
        len(remitentes) == 200,
        "200 remitentes"
    )

    verificar(
        len(zonas) == 300,
        "300 zonas"
    )

    print("\n2. TABLAS DE HECHOS")

    verificar(
        len(rutas) == 100_000,
        "100,000 rutas"
    )

    verificar(
        len(desempeno) == 130_500,
        "130,500 registros de desempeño"
    )

    verificar(
        len(trazabilidad) == 150_000,
        "150,000 registros de trazabilidad"
    )

    verificar(
        len(alertas) == 78_300,
        "78,300 registros zona-fecha"
    )

    print("\n3. INTEGRIDAD DE CLAVES")

    verificar(
        conductores["cond_id"].is_unique,
        "Conductores sin claves duplicadas"
    )

    verificar(
        remitentes["id_remitente"].is_unique,
        "Remitentes sin claves duplicadas"
    )

    verificar(
        zonas["id_zona"].is_unique,
        "Zonas sin claves duplicadas"
    )

    verificar(
        trazabilidad["id_novedad"].is_unique,
        "Novedades sin claves duplicadas"
    )

    verificar(
        not desempeno.duplicated(
            ["cond_id", "fecha"]
        ).any(),
        "Desempeño sin conductor-fecha duplicados"
    )

    verificar(
        not alertas.duplicated(
            ["id_zona_destino", "fecha"]
        ).any(),
        "Alertas sin zona-fecha duplicados"
    )

    print("\n4. INDICADORES")

    verificar(
        desempeno["score_desempeno"]
        .dropna()
        .between(0, 1)
        .all(),
        "Scores de desempeño entre 0 y 1"
    )

    verificar(
        alertas["tasa_fallo"]
        .between(0, 1)
        .all(),
        "Tasas de fallo entre 0 y 1"
    )

    verificar(
        agg_diarios["tasa_entrega"]
        .between(0, 1)
        .all(),
        "Tasas diarias de entrega válidas"
    )

    verificar(
        agg_diarios["tasa_cumplimiento_sla"]
        .between(0, 1)
        .all(),
        "Tasas diarias de SLA válidas"
    )

    print("\n5. AGREGACIONES")

    verificar(
        agg_diarios["total_envios"].sum()
        == 2_000_000,
        "Agregación diaria conserva 2,000,000 de envíos"
    )

    verificar(
        len(agg_conductores) == len(conductores),
        "Agregación incluye los 500 conductores"
    )

    verificar(
        len(agg_zonas) == len(zonas),
        "Agregación incluye las 300 zonas"
    )

    verificar(
        agg_zonas["dias_con_alerta"].sum()
        == alertas["genera_alerta"].sum(),
        "Alertas agregadas coinciden con tabla de alertas"
    )

    print("\nVALIDACIONES GOLD SUPERADAS")


if __name__ == "__main__":
    main()