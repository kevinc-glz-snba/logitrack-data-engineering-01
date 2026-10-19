from pathlib import Path

import pandas as pd


RUTA_NOVEDADES = Path(
    "data/silver/dir_novedades.parquet"
)

RUTA_ENVIOS = Path(
    "data/gold/fact_envios"
)

DESTINO = Path(
    "data/gold/fact_trazabilidad_envio.parquet"
)


def cargar_referencia_envios():
    """
    Construye una referencia de envíos con las
    columnas necesarias para la trazabilidad.

    Se leen los archivos por separado para
    evitar cargar todas las columnas de fact_envios.
    """
    archivos = sorted(
        RUTA_ENVIOS.glob("*.parquet")
    )

    if not archivos:
        raise FileNotFoundError(
            "No existen archivos de fact_envios"
        )

    columnas = [
        "id_envio",
        "cond_id",
        "id_zona_destino",
        "fec_recepcion",
        "estado_final",
    ]

    partes = []

    for numero, archivo in enumerate(
        archivos,
        start=1,
    ):
        df = pd.read_parquet(
            archivo,
            columns=columnas,
        )

        partes.append(df)

        print(
            f"Referencia de envíos: "
            f"{numero}/{len(archivos)}"
        )

    envios = pd.concat(
        partes,
        ignore_index=True,
    )

    if envios["id_envio"].duplicated().any():
        raise ValueError(
            "Existen identificadores de envío duplicados"
        )

    return envios


def main():
    print("\nCargando novedades...")

    novedades = pd.read_parquet(
        RUTA_NOVEDADES,
        columns=[
            "id_novedad",
            "id_envio",
            "fec_novedad",
            "tip_novedad",
            "desc_novedad",
            "id_agente_registro",
            "requiere_accion",
        ],
    )

    print(
        f"Novedades originales: "
        f"{len(novedades):,}"
    )

    if novedades["id_novedad"].isna().any():
        raise ValueError(
            "Existen novedades sin identificador"
        )

    if novedades["id_novedad"].duplicated().any():
        raise ValueError(
            "Existen novedades duplicadas"
        )

    print("\nCargando referencia de envíos...")

    envios = cargar_referencia_envios()

    print("\nRelacionando novedades y envíos...")

    fact = novedades.merge(
        envios,
        on="id_envio",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    # Validar integridad referencial.
    sin_envio = (
        fact["_merge"] != "both"
    ).sum()

    if sin_envio > 0:
        raise ValueError(
            f"Existen {sin_envio} novedades "
            "sin envío relacionado"
        )

    fact = fact.drop(columns=["_merge"])

    # Convertir fechas.
    fact["fec_novedad"] = pd.to_datetime(
        fact["fec_novedad"],
        errors="coerce",
    )

    fact["fec_recepcion"] = pd.to_datetime(
        fact["fec_recepcion"],
        errors="coerce",
    )

    if fact["fec_novedad"].isna().any():
        raise ValueError(
            "Existen novedades con fecha inválida"
        )

    if fact["fec_recepcion"].isna().any():
        raise ValueError(
            "Existen envíos con fecha de recepción inválida"
        )

    # Tiempo transcurrido en días.
    fact["dias_desde_recepcion"] = (
        fact["fec_novedad"]
        - fact["fec_recepcion"]
    ).dt.days

    # Ordenar eventos cronológicamente.
    # id_novedad funciona como desempate cuando
    # varias novedades tienen la misma fecha.
    fact = fact.sort_values(
        [
            "id_envio",
            "fec_novedad",
            "id_novedad",
        ]
    )

    fact["orden_evento_envio"] = (
        fact.groupby("id_envio")
        .cumcount()
        + 1
    )

    # Diferencia en días respecto al evento anterior.
    fact["dias_desde_evento_anterior"] = (
        fact.groupby("id_envio")["fec_novedad"]
        .diff()
        .dt.days
    )

    # Con una sola novedad por envío, este campo
    # será nulo porque no existe un evento anterior.

    # Orden final de columnas.
    columnas = [
        "id_novedad",
        "id_envio",
        "cond_id",
        "id_zona_destino",
        "fec_recepcion",
        "fec_novedad",
        "orden_evento_envio",
        "dias_desde_recepcion",
        "dias_desde_evento_anterior",
        "tip_novedad",
        "desc_novedad",
        "id_agente_registro",
        "requiere_accion",
        "estado_final",
    ]

    fact = fact[columnas]

    # Validaciones.
    assert len(fact) == len(novedades), (
        "Se perdió o duplicó información"
    )

    assert fact["id_novedad"].is_unique, (
        "La clave de novedad no es única"
    )

    DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_parquet(
        DESTINO,
        index=False,
    )

    print("\nFACT_TRAZABILIDAD_ENVIO GENERADA")

    print(
        f"Registros: {len(fact):,}"
    )

    print(
        "Envíos con novedades: "
        f"{fact['id_envio'].nunique():,}"
    )

    print(
        "Novedades que requieren acción: "
        f"{fact['requiere_accion'].sum():,}"
    )

    print(
        "Eventos anteriores no disponibles: "
        f"{fact['dias_desde_evento_anterior'].isna().sum():,}"
    )

    print(
        "Novedades anteriores a la recepción: "
        f"{(fact['dias_desde_recepcion'] < 0).sum():,}"
    )

    print("\nTIPOS DE NOVEDAD:")
    print(
        fact["tip_novedad"]
        .value_counts()
        .to_string()
    )

    print("\nPRIMEROS REGISTROS:")
    print(
        fact.head(5).to_string(index=False)
    )

    print(f"\nArchivo generado: {DESTINO}")


if __name__ == "__main__":
    main()