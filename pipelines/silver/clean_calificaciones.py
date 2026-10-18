from pathlib import Path

import pandas as pd


BRONZE_DIR = Path("data/bronze/cal_destinatarios")
SILVER_DIR = Path("data/silver")
ERROR_DIR = Path("data/errors")


def limpiar_calificaciones(df):
    df = df.copy()

    id_invalido = df["id_calificacion"].isna()
    envio_invalido = df["id_envio"].isna()

    puntaje_invalido = (
        df["puntaje_1_5"].isna()
        | ~df["puntaje_1_5"].between(1, 5)
    )

    duplicado = df.duplicated(
        subset=["id_calificacion"],
        keep="first",
    )

    df["motivo_rechazo"] = ""

    df.loc[id_invalido, "motivo_rechazo"] += "id_calificacion nulo; "
    df.loc[envio_invalido, "motivo_rechazo"] += "id_envio nulo; "
    df.loc[puntaje_invalido, "motivo_rechazo"] += "puntaje invalido; "
    df.loc[duplicado, "motivo_rechazo"] += "id_calificacion duplicado; "

    rechazados = df[df["motivo_rechazo"] != ""].copy()
    validos = df[df["motivo_rechazo"] == ""].copy()

    validos = validos.drop(columns=["motivo_rechazo"])

    return validos, rechazados


def main():
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    archivos = sorted(BRONZE_DIR.rglob("*.parquet"))

    if not archivos:
        raise FileNotFoundError("No se encontraron archivos Bronze")

    df = pd.concat(
        [pd.read_parquet(archivo) for archivo in archivos],
        ignore_index=True,
    )

    validos, rechazados = limpiar_calificaciones(df)

    validos.to_parquet(
        SILVER_DIR / "cal_destinatarios.parquet",
        index=False,
    )

    rechazados.to_parquet(
        ERROR_DIR / "cal_destinatarios_rechazados.parquet",
        index=False,
    )

    print(f"Registros de entrada: {len(df):,}")
    print(f"Registros válidos: {len(validos):,}")
    print(f"Registros rechazados: {len(rechazados):,}")
    print(
        "Comentarios nulos conservados:",
        validos["comentario_texto"].isna().sum(),
    )


if __name__ == "__main__":
    main()