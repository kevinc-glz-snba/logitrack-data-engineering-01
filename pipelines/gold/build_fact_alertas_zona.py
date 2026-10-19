from pathlib import Path

import numpy as np
import pandas as pd


ORIGEN = Path("data/gold/fact_envios")
DESTINO = Path("data/gold/fact_alertas_zona.parquet")

UMBRAL_INCREMENTO = 0.25
MIN_ENVIOS_HISTORICOS = 10


def preparar_datos_diarios():
    archivos = sorted(ORIGEN.glob("*.parquet"))

    if not archivos:
        raise FileNotFoundError(
            "No existen archivos de fact_envios"
        )

    partes = []

    for numero, archivo in enumerate(archivos, start=1):
        df = pd.read_parquet(
            archivo,
            columns=[
                "id_zona_destino",
                "fec_recepcion",
                "estado_final",
            ],
        )

        df["fecha"] = pd.to_datetime(
            df["fec_recepcion"],
            errors="coerce",
        ).dt.normalize()

        if df["fecha"].isna().any():
            raise ValueError(
                "Existen fechas de recepción inválidas"
            )

        df["fallido"] = (
            df["estado_final"] == "Fallido"
        ).astype(int)

        diario = (
            df.groupby(
                ["id_zona_destino", "fecha"],
                as_index=False,
            )
            .agg(
                total_envios=("fallido", "size"),
                envios_fallidos=("fallido", "sum"),
            )
        )

        partes.append(diario)

        print(
            f"Procesados {numero}/{len(archivos)} archivos"
        )

    # Consolidar días repetidos entre archivos.
    diario = (
        pd.concat(partes, ignore_index=True)
        .groupby(
            ["id_zona_destino", "fecha"],
            as_index=False,
        )
        .agg(
            total_envios=("total_envios", "sum"),
            envios_fallidos=("envios_fallidos", "sum"),
        )
    )

    diario["tasa_fallo"] = (
        diario["envios_fallidos"]
        / diario["total_envios"]
    )

    diario["dia_semana"] = (
        diario["fecha"].dt.dayofweek
    )

    return diario


def calcular_alertas(diario):
    diario = diario.sort_values(
        ["id_zona_destino", "fecha"]
    ).copy()

    # Crear referencia histórica de cada zona.
    # Reindexamos por día para que la ventana de
    # 28 días represente días calendario y no
    # simplemente 28 registros disponibles.
    resultados = []

    for zona, grupo in diario.groupby("id_zona_destino"):
        grupo = grupo.set_index("fecha").sort_index()

        calendario = pd.date_range(
            start=grupo.index.min(),
            end=grupo.index.max(),
            freq="D",
        )

        serie = grupo.reindex(calendario)

        serie["id_zona_destino"] = zona

        # Los días sin operaciones aportan cero
        # envíos y cero fallos al historial.
        serie["total_envios"] = (
            serie["total_envios"].fillna(0)
        )

        serie["envios_fallidos"] = (
            serie["envios_fallidos"].fillna(0)
        )

        serie["dia_semana"] = serie.index.dayofweek

        # Historial de las cuatro semanas anteriores:
        # 7, 14, 21 y 28 días antes.
        historico_envios = sum(
            serie["total_envios"].shift(dias).fillna(0)
            for dias in (7, 14, 21, 28)
        )

        historico_fallos = sum(
            serie["envios_fallidos"].shift(dias).fillna(0)
            for dias in (7, 14, 21, 28)
        )

        serie["envios_historicos"] = historico_envios

        serie["fallos_historicos"] = historico_fallos

        serie["tasa_fallo_historica"] = (
            historico_fallos
            / historico_envios.replace(0, np.nan)
        )

        # Conservar solamente fechas con operaciones.
        serie = serie[
            serie["total_envios"] > 0
        ].copy()

        serie["tasa_fallo"] = (
            serie["envios_fallidos"]
            / serie["total_envios"]
        )

        # Referencia histórica suficiente.
        suficiente = (
            serie["envios_historicos"]
            >= MIN_ENVIOS_HISTORICOS
        )

        historico_positivo = (
            serie["tasa_fallo_historica"] > 0
        )

        serie["incremento_relativo"] = np.nan

        calculable = suficiente & historico_positivo

        serie.loc[
            calculable,
            "incremento_relativo",
        ] = (
            (
                serie.loc[calculable, "tasa_fallo"]
                - serie.loc[
                    calculable,
                    "tasa_fallo_historica",
                ]
            )
            / serie.loc[
                calculable,
                "tasa_fallo_historica",
            ]
        )

        serie["genera_alerta"] = (
            serie["incremento_relativo"]
            > UMBRAL_INCREMENTO
        )

        serie["estado_referencia"] = np.select(
            [
                ~suficiente,
                suficiente & ~historico_positivo,
            ],
            [
                "Historial insuficiente",
                "Sin referencia porcentual",
            ],
            default="Referencia disponible",
        )

        serie.index.name = "fecha"

        resultados.append(
            serie.reset_index()
        )

    fact = pd.concat(
        resultados,
        ignore_index=True,
    )

    columnas = [
        "id_zona_destino",
        "fecha",
        "dia_semana",
        "total_envios",
        "envios_fallidos",
        "tasa_fallo",
        "envios_historicos",
        "fallos_historicos",
        "tasa_fallo_historica",
        "incremento_relativo",
        "genera_alerta",
        "estado_referencia",
    ]

    return fact[columnas]


def main():
    print("\nPreparando información diaria...")
    diario = preparar_datos_diarios()

    print("\nCalculando referencias históricas...")
    fact = calcular_alertas(diario)

    # Validaciones.
    assert not fact.duplicated(
        ["id_zona_destino", "fecha"]
    ).any(), "Existen zonas-fecha duplicadas"

    assert fact["tasa_fallo"].between(0, 1).all(), (
        "Existen tasas de fallo inválidas"
    )

    assert (
        fact["envios_fallidos"]
        <= fact["total_envios"]
    ).all(), "Existen más fallos que envíos"

    DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_parquet(
        DESTINO,
        index=False,
    )

    print("\nFACT_ALERTAS_ZONA GENERADA")
    print(f"Registros zona-fecha: {len(fact):,}")

    print(
        "Alertas generadas: "
        f"{fact['genera_alerta'].sum():,}"
    )

    print("\nESTADO DE REFERENCIAS:")
    print(
        fact["estado_referencia"]
        .value_counts()
        .to_string()
    )

    print("\nPRIMERAS ALERTAS:")
    print(
        fact.loc[
            fact["genera_alerta"],
            [
                "id_zona_destino",
                "fecha",
                "tasa_fallo",
                "tasa_fallo_historica",
                "incremento_relativo",
            ],
        ]
        .head(10)
        .to_string(index=False)
    )

    print(f"\nArchivo generado: {DESTINO}")


if __name__ == "__main__":
    main()