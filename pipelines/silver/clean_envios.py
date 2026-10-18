from pathlib import Path

import pandas as pd


BRONZE_DIR = Path("data/bronze/tms_envios")
SILVER_DIR = Path("data/silver/tms_envios")
ERROR_DIR = Path("data/errors/tms_envios")


def limpiar_envios(df, ids_procesados):
    df = df.copy()

    # Identificar errores
    id_nulo = df["id_envio"].isna()
    remitente_nulo = df["id_remitente"].isna()
    conductor_nulo = df["cond_id"].isna()

    peso_invalido = (
        df["peso_kg"].isna()
        | (df["peso_kg"] <= 0)
    )

    recepcion_nula = df["fec_recepcion"].isna()

    estado_invalido = ~df["estado_final"].isin(
        ["Entregado", "Fallido"]
    )

    fecha_entregado_invalida = (
        (df["estado_final"] == "Entregado")
        & df["fec_entrega_real"].isna()
    )

    fecha_fallido_invalida = (
        (df["estado_final"] == "Fallido")
        & df["fec_entrega_real"].notna()
    )

    # Detectar duplicados dentro y entre archivos
    duplicado = (
        df["id_envio"].duplicated(keep="first")
        | df["id_envio"].isin(ids_procesados)
    )

    # Registrar motivos de rechazo
    df["motivo_rechazo"] = ""

    reglas = [
        (id_nulo, "id_envio nulo"),
        (remitente_nulo, "id_remitente nulo"),
        (conductor_nulo, "cond_id nulo"),
        (peso_invalido, "peso invalido"),
        (recepcion_nula, "fec_recepcion nula"),
        (estado_invalido, "estado_final invalido"),
        (fecha_entregado_invalida, "entregado sin fecha real"),
        (fecha_fallido_invalida, "fallido con fecha real"),
        (duplicado, "id_envio duplicado"),
    ]

    for condicion, motivo in reglas:
        df.loc[condicion, "motivo_rechazo"] += motivo + "; "

    # Separar registros
    rechazados = df[df["motivo_rechazo"] != ""].copy()
    validos = df[df["motivo_rechazo"] == ""].copy()

    # Registrar todos los IDs encontrados para detectar
    # duplicados en los siguientes archivos.
    ids_procesados.update(df["id_envio"].dropna().tolist())

    validos = validos.drop(columns=["motivo_rechazo"])

    return validos, rechazados


def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    archivos = sorted(BRONZE_DIR.rglob("*.parquet"))

    if not archivos:
        raise FileNotFoundError("No se encontraron archivos Bronze")

    ids_procesados = set()

    total_entrada = 0
    total_validos = 0
    total_rechazados = 0

    for numero, archivo in enumerate(archivos, start=1):
        df = pd.read_parquet(archivo)

        validos, rechazados = limpiar_envios(
            df,
            ids_procesados,
        )

        validos.to_parquet(
            SILVER_DIR / f"envios_part_{numero:04d}.parquet",
            index=False,
        )

        if not rechazados.empty:
            rechazados.to_parquet(
                ERROR_DIR / f"rechazados_part_{numero:04d}.parquet",
                index=False,
            )

        total_entrada += len(df)
        total_validos += len(validos)
        total_rechazados += len(rechazados)

        print(
            f"Archivo {numero}/{len(archivos)} | "
            f"Válidos: {len(validos):,} | "
            f"Rechazados: {len(rechazados):,}"
        )

    print("\nRESUMEN SILVER")
    print(f"Registros de entrada: {total_entrada:,}")
    print(f"Registros válidos: {total_validos:,}")
    print(f"Registros rechazados: {total_rechazados:,}")


if __name__ == "__main__":
    main()