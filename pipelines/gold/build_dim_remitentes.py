from pathlib import Path

import pandas as pd


def main():
    # 1. Leer datos desde Silver
    origen = Path("data/silver/cli_remitentes.parquet")
    df = pd.read_parquet(origen)

    # 2. Seleccionar atributos de la dimensión
    columnas = [
        "id_remitente",
        "razon_social",
        "tipo_cliente",
        "ciudad_principal",
        "sla_entrega_horas",
        "penalidad_porc",
        "activo",
    ]

    dim = df[columnas].copy()

    # 3. Estandarizar tipo de cliente
    catalogo = {
        "ecommerce": "Ecommerce",
        "farmaceutico": "Farmaceutico",
        "retail": "Retail",
        "telecomunicaciones": "Telecomunicaciones",
        "otro": "Otro",
    }

    dim["tipo_cliente"] = (
        dim["tipo_cliente"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map(catalogo)
    )

    # 4. Garantizar que el SLA sea numérico
    dim["sla_entrega_horas"] = pd.to_numeric(
        dim["sla_entrega_horas"],
        errors="coerce",
    )

    # 5. Normalizar textos
    dim["razon_social"] = (
        dim["razon_social"].astype("string").str.strip()
    )

    dim["ciudad_principal"] = (
        dim["ciudad_principal"].astype("string").str.strip()
    )

    # 6. Validaciones de calidad
    assert dim["id_remitente"].notna().all(), (
        "Existen remitentes sin identificador"
    )

    assert dim["id_remitente"].is_unique, (
        "Existen identificadores duplicados"
    )

    assert dim["tipo_cliente"].notna().all(), (
        "Existen tipos de cliente fuera del catálogo"
    )

    assert dim["sla_entrega_horas"].notna().all(), (
        "Existen SLA no numéricos"
    )

    assert (dim["sla_entrega_horas"] > 0).all(), (
        "Existen SLA menores o iguales a cero"
    )

    assert dim["penalidad_porc"].notna().all(), (
        "Existen penalidades nulas"
    )

    assert dim["penalidad_porc"].between(0, 100).all(), (
        "Existen penalidades fuera del rango 0-100"
    )

    # 7. Guardar dimensión Gold
    destino = Path("data/gold/dim_remitentes.parquet")
    destino.parent.mkdir(parents=True, exist_ok=True)

    dim.to_parquet(destino, index=False)

    # 8. Mostrar resultados
    print("\nDIM_REMITENTES GENERADA")
    print(f"Registros: {len(dim):,}")
    print(
        f"Remitentes únicos: "
        f"{dim['id_remitente'].nunique():,}"
    )

    print("\nDistribución por tipo de cliente:")
    print(dim["tipo_cliente"].value_counts().to_string())

    print("\nEstadísticas del SLA:")
    print(dim["sla_entrega_horas"].describe().to_string())

    print("\nVista previa:")
    print(
        dim[
            [
                "id_remitente",
                "tipo_cliente",
                "ciudad_principal",
                "sla_entrega_horas",
            ]
        ].head().to_string(index=False)
    )

    print(f"\nArchivo generado: {destino}")


if __name__ == "__main__":
    main()