from pathlib import Path

import pandas as pd
import numpy as np


RUTA_ENVIOS = Path("data/gold/fact_envios")
RUTA_RUTAS = Path("data/gold/fact_rutas.parquet")
RUTA_CALIFICACIONES = Path(
    "data/silver/cal_destinatarios.parquet"
)

DESTINO = Path(
    "data/gold/fact_desempeno_conductor.parquet"
)

VELOCIDAD_ESTANDAR_KMH = 20.0


def preparar_envios():
    """
    Lee los envíos por partes y genera:
    1. Agregados diarios por conductor.
    2. Relación id_envio -> conductor y fecha,
       necesaria para asociar las calificaciones.
    """
    archivos = sorted(RUTA_ENVIOS.glob("*.parquet"))

    if not archivos:
        raise FileNotFoundError(
            "No existen archivos Gold de fact_envios"
        )

    agregados = []
    relaciones = []

    for numero, archivo in enumerate(archivos, start=1):
        df = pd.read_parquet(
            archivo,
            columns=[
                "id_envio",
                "cond_id",
                "fec_recepcion",
                "estado_final",
                "num_intentos",
            ],
        )

        df["fecha"] = pd.to_datetime(
            df["fec_recepcion"],
            errors="coerce",
        ).dt.normalize()

        df["entregado"] = (
            df["estado_final"] == "Entregado"
        ).astype(int)

        resumen = (
            df.groupby(
                ["cond_id", "fecha"],
                as_index=False,
            )
            .agg(
                total_envios=("id_envio", "count"),
                envios_exitosos=("entregado", "sum"),
                suma_intentos=("num_intentos", "sum"),
            )
        )

        agregados.append(resumen)

        relaciones.append(
            df[
                ["id_envio", "cond_id", "fecha"]
            ].copy()
        )

        print(
            f"Envíos procesados: "
            f"{numero}/{len(archivos)}"
        )

    # Consolidar agregados de los distintos archivos.
    envios_diarios = (
        pd.concat(agregados, ignore_index=True)
        .groupby(
            ["cond_id", "fecha"],
            as_index=False,
        )
        .agg(
            total_envios=("total_envios", "sum"),
            envios_exitosos=("envios_exitosos", "sum"),
            suma_intentos=("suma_intentos", "sum"),
        )
    )

    envios_diarios["tasa_exito"] = (
        envios_diarios["envios_exitosos"]
        / envios_diarios["total_envios"]
    )

    envios_diarios["intentos_promedio"] = (
        envios_diarios["suma_intentos"]
        / envios_diarios["total_envios"]
    )

    relacion_envios = pd.concat(
        relaciones,
        ignore_index=True,
    )

    return envios_diarios, relacion_envios


def preparar_rutas():
    rutas = pd.read_parquet(
        RUTA_RUTAS,
        columns=[
            "cond_id",
            "fec_ruta",
            "adherencia_ruta",
            "productividad_km_h",
        ],
    )

    rutas["fecha"] = pd.to_datetime(
        rutas["fec_ruta"],
        errors="coerce",
    ).dt.normalize()

    # Normalizar adherencia al rango [0, 1].
    adherencia = rutas["adherencia_ruta"]

    rutas["adherencia_normalizada"] = np.where(
        adherencia > 0,
        np.minimum(
            adherencia,
            1 / adherencia.replace(0, np.nan),
        ),
        0,
    )

    # Comparación contra estándar provisional.
    rutas["velocidad_normalizada"] = (
        rutas["productividad_km_h"]
        / VELOCIDAD_ESTANDAR_KMH
    ).clip(lower=0, upper=1)

    return (
        rutas.groupby(
            ["cond_id", "fecha"],
            as_index=False,
        )
        .agg(
            total_rutas=("adherencia_ruta", "size"),
            adherencia_normalizada=(
                "adherencia_normalizada",
                "mean",
            ),
            velocidad_normalizada=(
                "velocidad_normalizada",
                "mean",
            ),
        )
    )


def preparar_calificaciones(relacion_envios):
    calificaciones = pd.read_parquet(
        RUTA_CALIFICACIONES,
        columns=[
            "id_envio",
            "puntaje_1_5",
        ],
    )

    calificaciones = calificaciones.merge(
        relacion_envios,
        on="id_envio",
        how="left",
        validate="many_to_one",
    )

    if calificaciones["cond_id"].isna().any():
        raise ValueError(
            "Existen calificaciones sin envío relacionado"
        )

    calificaciones["calificacion_normalizada"] = (
        calificaciones["puntaje_1_5"] / 5
    )

    return (
        calificaciones.groupby(
            ["cond_id", "fecha"],
            as_index=False,
        )
        .agg(
            total_calificaciones=(
                "puntaje_1_5",
                "count",
            ),
            calificacion_normalizada=(
                "calificacion_normalizada",
                "mean",
            ),
        )
    )


def main():
    print("\nPreparando envíos...")
    envios, relacion_envios = preparar_envios()

    print("\nPreparando rutas...")
    rutas = preparar_rutas()

    print("\nPreparando calificaciones...")
    calificaciones = preparar_calificaciones(
        relacion_envios
    )

    # Una fila por conductor y fecha con envíos.
    fact = envios.merge(
        rutas,
        on=["cond_id", "fecha"],
        how="left",
        validate="one_to_one",
    )

    fact = fact.merge(
        calificaciones,
        on=["cond_id", "fecha"],
        how="left",
        validate="one_to_one",
    )

    # Evitar división entre cero.
    fact["intentos_normalizados"] = (
        1
        / fact["intentos_promedio"].replace(
            0,
            np.nan,
        )
    ).clip(lower=0, upper=1)

    # Calcular puntuación únicamente cuando
    # los cinco componentes estén disponibles.
    componentes = [
        "tasa_exito",
        "adherencia_normalizada",
        "velocidad_normalizada",
        "intentos_normalizados",
        "calificacion_normalizada",
    ]

    completos = fact[componentes].notna().all(axis=1)

    fact["score_desempeno"] = np.nan

    fact.loc[completos, "score_desempeno"] = (
        0.35 * fact.loc[completos, "tasa_exito"]
        + 0.20
        * fact.loc[completos, "adherencia_normalizada"]
        + 0.20
        * fact.loc[completos, "velocidad_normalizada"]
        + 0.15
        * fact.loc[completos, "intentos_normalizados"]
        + 0.10
        * fact.loc[completos, "calificacion_normalizada"]
    ).round(2)

    # Validaciones.
    assert not fact.duplicated(
        ["cond_id", "fecha"]
    ).any(), "Existen conductores-fecha duplicados"

    scores = fact["score_desempeno"].dropna()

    assert scores.between(0, 1).all(), (
        "Existen puntuaciones fuera del rango 0-1"
    )

    DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_parquet(
        DESTINO,
        index=False,
    )

    print("\nFACT_DESEMPENO_CONDUCTOR GENERADA")
    print(f"Registros: {len(fact):,}")

    print(
        "Registros con score calculado: "
        f"{fact['score_desempeno'].notna().sum():,}"
    )

    print(
        "Registros sin score calculable: "
        f"{fact['score_desempeno'].isna().sum():,}"
    )

    print("\nESTADÍSTICAS DEL SCORE:")
    print(
        fact["score_desempeno"]
        .describe()
        .to_string()
    )

    print(f"\nArchivo generado: {DESTINO}")


if __name__ == "__main__":
    main()