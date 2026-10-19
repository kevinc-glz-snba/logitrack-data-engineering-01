from pathlib import Path

import pandas as pd


def normalizar(serie):
    """
    Normalización min-max entre 0 y 1.
    Si todos los valores son iguales, devuelve 0.
    """
    minimo = serie.min()
    maximo = serie.max()

    if maximo == minimo:
        return pd.Series(0.0, index=serie.index)

    return (serie - minimo) / (maximo - minimo)


def main():
    # 1. Leer zonas desde Silver.
    origen = Path("data/silver/geo_zonas.parquet")
    df = pd.read_parquet(origen)

    # 2. Validar columnas necesarias.
    requeridas = [
        "id_zona",
        "nivel_trafico_prom",
        "distancia_bodega_km",
    ]

    faltantes = [
        columna
        for columna in requeridas
        if columna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Columnas faltantes: {faltantes}"
        )

    dim = df.copy()

    # 3. Convertir variables a numéricas.
    for columna in [
        "nivel_trafico_prom",
        "distancia_bodega_km",
    ]:
        dim[columna] = pd.to_numeric(
            dim[columna],
            errors="coerce",
        )

    # 4. Validaciones de calidad.
    assert dim["id_zona"].notna().all(), (
        "Existen zonas sin identificador"
    )

    assert dim["id_zona"].is_unique, (
        "Existen zonas duplicadas"
    )

    assert dim["nivel_trafico_prom"].notna().all(), (
        "Existen valores de tráfico inválidos"
    )

    assert dim["distancia_bodega_km"].notna().all(), (
        "Existen distancias inválidas"
    )

    assert dim["nivel_trafico_prom"].between(1, 5).all(), (
        "Existen niveles de tráfico fuera del rango 1-5"
    )

    assert (dim["distancia_bodega_km"] >= 0).all(), (
        "Existen distancias negativas"
    )

    # 5. Normalizar variables.
    dim["trafico_normalizado"] = normalizar(
        dim["nivel_trafico_prom"]
    )

    dim["distancia_normalizada"] = normalizar(
        dim["distancia_bodega_km"]
    )

    # 6. Calcular índice de dificultad.
    dim["indice_dificultad"] = (
        1
        + 4
        * (
            0.60 * dim["trafico_normalizado"]
            + 0.40 * dim["distancia_normalizada"]
        )
    ).round(2)

    # 7. Validar resultado.
    assert dim["indice_dificultad"].between(1, 5).all(), (
        "El índice de dificultad está fuera del rango"
    )

    # 8. Guardar dimensión Gold.
    destino = Path("data/gold/dim_zonas.parquet")
    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dim.to_parquet(destino, index=False)

    # 9. Mostrar resultados.
    print("\nDIM_ZONAS GENERADA")
    print(f"Registros: {len(dim):,}")
    print(f"Zonas únicas: {dim['id_zona'].nunique():,}")

    print("\nEstadísticas del índice de dificultad:")
    print(
        dim["indice_dificultad"]
        .describe()
        .to_string()
    )

    print("\nVista previa:")
    print(
        dim[
            [
                "id_zona",
                "nivel_trafico_prom",
                "distancia_bodega_km",
                "indice_dificultad",
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print(f"\nArchivo generado: {destino}")


if __name__ == "__main__":
    main()