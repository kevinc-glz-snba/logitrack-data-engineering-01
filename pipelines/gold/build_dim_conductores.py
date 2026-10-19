from pathlib import Path
import pandas as pd


def main():
    # 1. Leer datos limpios desde Silver.
    origen = "data/silver/ope_conductores.parquet"
    df = pd.read_parquet(origen)

    # 2. Seleccionar columnas necesarias para el análisis.
    columnas = [
        "cond_id",
        "num_doc_hash",
        "fec_ingreso",
        "id_ciudad_base",
        "tip_vehiculo",
        "cod_zona_asignada",
        "activo",
        "calific_promedio_acum",
    ]

    dim = df[columnas].copy()

    # 3. Convertir fecha de ingreso.
    dim["fec_ingreso"] = pd.to_datetime(
        dim["fec_ingreso"],
        errors="coerce",
    )

    # 4. Calcular antigüedad en años completos.
    # Usamos una fecha de corte fija para obtener resultados reproducibles.
    fecha_corte = pd.Timestamp("2025-12-31")

    antiguedad = (
        fecha_corte.year - dim["fec_ingreso"].dt.year
        - (
            (fecha_corte.month < dim["fec_ingreso"].dt.month)
            | (
                (fecha_corte.month == dim["fec_ingreso"].dt.month)
                & (fecha_corte.day < dim["fec_ingreso"].dt.day)
            )
        ).astype(int)
    )

    dim["antiguedad_anios"] = antiguedad.clip(lower=0)

    # 5. Estandarizar tipo de vehículo.
    catalogo = {
        "moto": "Moto",
        "bicicleta": "Bicicleta",
        "van": "Van",
        "camion": "Camion",
    }

    dim["tip_vehiculo"] = (
        dim["tip_vehiculo"]
        .str.strip()
        .str.lower()
        .map(catalogo)
    )

    # 6. Validaciones básicas.
    assert dim["cond_id"].notna().all(), (
        "Existen conductores sin identificador"
    )

    assert dim["cond_id"].is_unique, (
        "Existen conductores duplicados"
    )

    assert dim["fec_ingreso"].notna().all(), (
        "Existen fechas de ingreso inválidas"
    )

    assert (dim["fec_ingreso"] <= fecha_corte).all(), (
        "Existen fechas de ingreso posteriores a la fecha de corte"
    )

    assert dim["tip_vehiculo"].notna().all(), (
        "Existen tipos de vehículo fuera del catálogo"
    )

    # 7. Guardar dimensión Gold.
    destino = Path("data/gold/dim_conductores.parquet")
    destino.parent.mkdir(parents=True, exist_ok=True)

    dim.to_parquet(destino, index=False)

    # 8. Mostrar resultados.
    print("\nDIM_CONDUCTORES GENERADA")
    print(f"Registros: {len(dim):,}")
    print(f"Conductores únicos: {dim['cond_id'].nunique():,}")

    print("\nDistribución de vehículos:")
    print(dim["tip_vehiculo"].value_counts().to_string())

    print("\nVista previa:")
    print(
        dim[
            [
                "cond_id",
                "tip_vehiculo",
                "fec_ingreso",
                "antiguedad_anios",
            ]
        ].head().to_string(index=False)
    )

    print(f"\nArchivo generado: {destino}")


if __name__ == "__main__":
    main()