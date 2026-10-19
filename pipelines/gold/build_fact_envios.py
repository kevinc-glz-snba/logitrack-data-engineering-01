from pathlib import Path

import pandas as pd


ORIGEN = Path("data/silver/tms_envios")
DESTINO = Path("data/gold/fact_envios")

DIM_REMITENTES = Path("data/gold/dim_remitentes.parquet")


def combinar_fecha_hora(fechas, horas):
    """
    Combina fecha y hora en un timestamp.

    Los valores inválidos se convierten en NaT.
    """
    fecha = pd.to_datetime(fechas, errors="coerce")

    hora = pd.to_timedelta(
        horas.astype("string"),
        errors="coerce",
    )

    return fecha + hora


def clasificar_retraso(retraso, entregado):
    if not entregado:
        return "No entregado"

    if pd.isna(retraso):
        return "Sin determinar"

    if retraso <= 0:
        return "A tiempo"

    if retraso <= 4:
        return "Leve"

    if retraso <= 24:
        return "Moderado"

    return "Critico"


def transformar(df, remitentes):
    # 1. Relacionar envíos con SLA de cada remitente.
    fact = df.merge(
        remitentes,
        on="id_remitente",
        how="left",
        validate="many_to_one",
    )

    if fact["sla_entrega_horas"].isna().any():
        raise ValueError(
            "Existen envíos sin SLA de remitente"
        )

    # 2. Construir fecha y hora de recepción.
    fact["fecha_hora_recepcion"] = combinar_fecha_hora(
        fact["fec_recepcion"],
        fact["hra_recepcion"],
    )

    # 3. Construir timestamps de intentos.
    intento1 = combinar_fecha_hora(
        fact["fec_intento1"],
        fact["hra_intento1"],
    )

    intento2 = combinar_fecha_hora(
        fact["fec_intento2"],
        fact["hra_intento2"],
    )

    # 4. Identificar intentos exitosos.
    exito1 = (
        fact["resultado_intento1"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("exitoso")
        .fillna(False)
    )

    exito2 = (
        fact["resultado_intento2"]
        .astype("string")
        .str.strip()
        .str.lower()
        .eq("exitoso")
        .fillna(False)
    )

    entregado = fact["estado_final"].eq("Entregado")

    fecha_real = pd.to_datetime(
        fact["fec_entrega_real"],
        errors="coerce",
    )

    # 5. Usar el timestamp del intento exitoso.
    fact["fecha_hora_entrega_estimada"] = pd.NaT

    valido1 = (
        entregado
        & exito1
        & intento1.notna()
        & intento1.dt.normalize().eq(fecha_real)
    )

    valido2 = (
        entregado
        & ~valido1
        & exito2
        & intento2.notna()
        & intento2.dt.normalize().eq(fecha_real)
    )

    fact.loc[
        valido1, "fecha_hora_entrega_estimada"
    ] = intento1.loc[valido1]

    fact.loc[
        valido2, "fecha_hora_entrega_estimada"
    ] = intento2.loc[valido2]

    # 6. Calcular duración real estimada.
    fact["tiempo_entrega_horas"] = (
        (
            fact["fecha_hora_entrega_estimada"]
            - fact["fecha_hora_recepcion"]
        ).dt.total_seconds()
        / 3600
    ).round(2)

    # Una duración negativa indica inconsistencia.
    fact.loc[
        fact["tiempo_entrega_horas"] < 0,
        "tiempo_entrega_horas",
    ] = float("nan")

    # 7. Calcular número de intentos registrados.
    fact["num_intentos"] = (
        fact["fec_intento1"].notna().astype(int)
        + fact["fec_intento2"].notna().astype(int)
    )

    # 8. Calcular cumplimiento del SLA.
    fact["cumple_sla"] = (
        fact["tiempo_entrega_horas"]
        <= fact["sla_entrega_horas"]
    )

    # No asignar cumplimiento si no conocemos
    # la duración de un envío entregado.
    sin_duracion = (
        entregado
        & fact["tiempo_entrega_horas"].isna()
    )

    fact["cumple_sla"] = (
        fact["cumple_sla"].astype("boolean")
    )

    fact.loc[sin_duracion, "cumple_sla"] = pd.NA

    # Un envío fallido no cumple el SLA.
    fact.loc[~entregado, "cumple_sla"] = False

    # 9. Calcular retraso respecto al SLA.
    fact["retraso_horas"] = (
        fact["tiempo_entrega_horas"]
        - fact["sla_entrega_horas"]
    ).round(2)

    # 10. Clasificar retraso.
    fact["categoria_retraso"] = [
        clasificar_retraso(retraso, fue_entregado)
        for retraso, fue_entregado in zip(
            fact["retraso_horas"],
            entregado,
        )
    ]

    # 11. Conservar motivo de fallo.
    # No inventamos descripciones sin catálogo.
    fact["motivo_fallo_descripcion"] = (
        fact["motivo_fallo_cod"]
        .astype("string")
        .str.strip()
    )

    # 12. Seleccionar columnas de la tabla de hechos.
    columnas = [
        "id_envio",
        "id_remitente",
        "cond_id",
        "id_zona_destino",
        "tip_paquete",
        "peso_kg",
        "fec_recepcion",
        "fec_entrega_programada",
        "fec_entrega_real",
        "estado_final",
        "fecha_hora_recepcion",
        "fecha_hora_entrega_estimada",
        "sla_entrega_horas",
        "tiempo_entrega_horas",
        "cumple_sla",
        "num_intentos",
        "retraso_horas",
        "categoria_retraso",
        "motivo_fallo_cod",
        "motivo_fallo_descripcion",
        "vr_declarado",
    ]

    return fact[columnas].copy()


def main():
    archivos = sorted(ORIGEN.glob("*.parquet"))

    if not archivos:
        raise FileNotFoundError(
            "No se encontraron archivos Silver de envíos"
        )

    remitentes = pd.read_parquet(
        DIM_REMITENTES,
        columns=[
            "id_remitente",
            "sla_entrega_horas",
        ],
    )

    DESTINO.mkdir(parents=True, exist_ok=True)

    total = 0
    total_entregados = 0
    total_fallidos = 0
    total_sin_duracion = 0

    for numero, archivo in enumerate(archivos, start=1):
        df = pd.read_parquet(archivo)

        fact = transformar(df, remitentes)

        salida = DESTINO / (
            f"fact_envios_part_{numero:04d}.parquet"
        )

        fact.to_parquet(salida, index=False)

        cantidad = len(fact)
        total += cantidad

        total_entregados += (
            fact["estado_final"] == "Entregado"
        ).sum()

        total_fallidos += (
            fact["estado_final"] == "Fallido"
        ).sum()

        total_sin_duracion += (
            (fact["estado_final"] == "Entregado")
            & fact["tiempo_entrega_horas"].isna()
        ).sum()

        print(
            f"Archivo {numero}/{len(archivos)}: "
            f"{cantidad:,} registros"
        )

    print("\nFACT_ENVIOS GENERADA")
    print(f"Total de envíos: {total:,}")
    print(f"Entregados: {total_entregados:,}")
    print(f"Fallidos: {total_fallidos:,}")
    print(
        "Entregados sin duración calculable: "
        f"{total_sin_duracion:,}"
    )
    print(f"Archivos generados: {len(archivos)}")
    print(f"Destino: {DESTINO}")


if __name__ == "__main__":
    main()