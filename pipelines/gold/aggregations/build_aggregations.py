from pathlib import Path

import pandas as pd


GOLD = Path("data/gold")
DESTINO = GOLD / "aggregations"

DESTINO.mkdir(parents=True, exist_ok=True)


def cargar_envios():
    archivos = sorted(
        (GOLD / "fact_envios").glob("*.parquet")
    )

    if not archivos:
        raise FileNotFoundError(
            "No se encontraron archivos de fact_envios"
        )

    partes = []

    for archivo in archivos:
        df = pd.read_parquet(
            archivo,
            columns=[
                "id_envio",
                "cond_id",
                "id_zona_destino",
                "fec_recepcion",
                "estado_final",
                "cumple_sla",
            ],
        )

        df["fecha"] = pd.to_datetime(
            df["fec_recepcion"],
            errors="coerce",
        ).dt.normalize()

        df["entregado"] = (
            df["estado_final"] == "Entregado"
        ).astype(int)

        df["fallido"] = (
            df["estado_final"] == "Fallido"
        ).astype(int)

        df["sla_cumplido"] = (
            df["cumple_sla"].eq(True).astype(int)
        )

        partes.append(df)

    return pd.concat(partes, ignore_index=True)


def agregar_envios_diarios(envios):
    agg = (
        envios.groupby("fecha", as_index=False)
        .agg(
            total_envios=("id_envio", "count"),
            entregados=("entregado", "sum"),
            fallidos=("fallido", "sum"),
            cumplen_sla=("sla_cumplido", "sum"),
        )
    )

    agg["tasa_entrega"] = (
        agg["entregados"] / agg["total_envios"]
    ).round(4)

    agg["tasa_cumplimiento_sla"] = (
        agg["cumplen_sla"] / agg["total_envios"]
    ).round(4)

    return agg


def agregar_desempeno_conductores(envios):
    base = (
        envios.groupby("cond_id", as_index=False)
        .agg(
            total_envios=("id_envio", "count"),
            entregados=("entregado", "sum"),
        )
    )

    base["tasa_exito"] = (
        base["entregados"] / base["total_envios"]
    ).round(4)

    desempeno = pd.read_parquet(
        GOLD / "fact_desempeno_conductor.parquet",
        columns=[
            "cond_id",
            "score_desempeno",
        ],
    )

    resumen_scores = (
        desempeno.groupby("cond_id", as_index=False)
        .agg(
            dias_evaluados=("score_desempeno", "size"),
            dias_con_score=("score_desempeno", "count"),
            score_promedio=("score_desempeno", "mean"),
        )
    )

    resumen_scores["cobertura_score"] = (
        resumen_scores["dias_con_score"]
        / resumen_scores["dias_evaluados"]
    ).round(4)

    resumen_scores["score_promedio"] = (
        resumen_scores["score_promedio"].round(4)
    )

    return base.merge(
        resumen_scores,
        on="cond_id",
        how="left",
        validate="one_to_one",
    )


def agregar_operacion_zonas(envios):
    base = (
        envios.groupby(
            "id_zona_destino",
            as_index=False,
        )
        .agg(
            total_envios=("id_envio", "count"),
            fallidos=("fallido", "sum"),
        )
    )

    base["tasa_fallo"] = (
        base["fallidos"] / base["total_envios"]
    ).round(4)

    alertas = pd.read_parquet(
        GOLD / "fact_alertas_zona.parquet",
        columns=[
            "id_zona_destino",
            "genera_alerta",
        ],
    )

    resumen_alertas = (
        alertas.groupby(
            "id_zona_destino",
            as_index=False,
        )
        .agg(
            dias_analizados=("genera_alerta", "size"),
            dias_con_alerta=("genera_alerta", "sum"),
        )
    )

    return base.merge(
        resumen_alertas,
        on="id_zona_destino",
        how="left",
        validate="one_to_one",
    )


def main():
    print("Cargando envíos Gold...")
    envios = cargar_envios()

    print("Construyendo agregaciones...")

    agregaciones = {
        "agg_envios_diarios": agregar_envios_diarios(
            envios
        ),
        "agg_desempeno_conductores": (
            agregar_desempeno_conductores(envios)
        ),
        "agg_operacion_zonas": (
            agregar_operacion_zonas(envios)
        ),
    }

    for nombre, df in agregaciones.items():
        salida = DESTINO / f"{nombre}.parquet"

        df.to_parquet(
            salida,
            index=False,
        )

        print(
            f"{nombre}: {len(df):,} registros"
        )

        print(f"Archivo: {salida}")

    # Comprobar que la agregación diaria
    # conserva el total de envíos.
    assert (
        agregaciones["agg_envios_diarios"][
            "total_envios"
        ].sum()
        == len(envios)
    ), "No coincide el total de envíos"

    print("\nAGREGACIONES GENERADAS CORRECTAMENTE")


if __name__ == "__main__":
    main()
    