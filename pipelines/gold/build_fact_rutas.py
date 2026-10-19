from pathlib import Path

import pandas as pd


def main():
    # 1. Leer datos Silver.
    origen = Path("data/silver/gps_rutas.parquet")
    df = pd.read_parquet(origen)

    # 2. Seleccionar columnas.
    columnas = [
        "id_ruta",
        "cond_id",
        "fec_ruta",
        "hra_inicio",
        "hra_fin",
        "km_recorridos",
        "num_paradas_plan",
        "num_paradas_real",
        "desviacion_ruta_km",
        "consumo_combustible",
        "horas_trabajadas",
    ]

    fact = df[columnas].copy()

    # 3. Validaciones previas.
    assert fact["id_ruta"].notna().all(), (
        "Existen rutas sin identificador"
    )

    assert fact["id_ruta"].is_unique, (
        "Existen rutas duplicadas"
    )

    assert (fact["num_paradas_plan"] > 0).all(), (
        "Existen rutas con cero paradas planificadas"
    )

    assert (fact["horas_trabajadas"] > 0).all(), (
        "Existen rutas con duración inválida"
    )

    assert (fact["km_recorridos"] >= 0).all(), (
        "Existen rutas con kilómetros negativos"
    )

    # 4. Adherencia a la ruta.
    fact["adherencia_ruta"] = (
        fact["num_paradas_real"]
        / fact["num_paradas_plan"]
    ).round(4)

    # 5. Productividad: kilómetros por hora.
    fact["productividad_km_h"] = (
        fact["km_recorridos"]
        / fact["horas_trabajadas"]
    ).round(2)

    # 6. Desviación porcentual.
    # Si km_recorridos es 0, el porcentaje no
    # puede calcularse y se conserva como nulo.
    fact["desviacion_ruta_pct"] = (
        fact["desviacion_ruta_km"]
        / fact["km_recorridos"].replace(0, float("nan"))
        * 100
    ).round(2)

    # 7. Validaciones posteriores.
    assert fact["adherencia_ruta"].notna().all(), (
        "Existen adherencias no calculables"
    )

    assert fact["productividad_km_h"].notna().all(), (
        "Existen productividades no calculables"
    )

    # 8. Guardar Gold.
    destino = Path("data/gold/fact_rutas.parquet")
    destino.parent.mkdir(parents=True, exist_ok=True)

    fact.to_parquet(destino, index=False)

    # 9. Mostrar resultados.
    print("\nFACT_RUTAS GENERADA")
    print(f"Registros: {len(fact):,}")
    print(f"Rutas únicas: {fact['id_ruta'].nunique():,}")

    print("\nESTADÍSTICAS DE INDICADORES:")
    print(
        fact[
            [
                "adherencia_ruta",
                "productividad_km_h",
                "desviacion_ruta_pct",
            ]
        ].describe().to_string()
    )

    print("\nRUTAS SIN DESVIACIÓN CALCULABLE:")
    print(
        fact["desviacion_ruta_pct"].isna().sum()
    )

    print("\nVISTA PREVIA:")
    print(
        fact[
            [
                "id_ruta",
                "cond_id",
                "horas_trabajadas",
                "adherencia_ruta",
                "productividad_km_h",
                "desviacion_ruta_pct",
            ]
        ].head().to_string(index=False)
    )

    print(f"\nArchivo generado: {destino}")


if __name__ == "__main__":
    main()