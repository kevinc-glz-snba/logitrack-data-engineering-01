from pathlib import Path

import pandas as pd


def procesar_tabla(nombre, clave, validar):
    origen = Path("data/bronze") / nombre
    destino = Path("data/silver") / f"{nombre}.parquet"
    errores = Path("data/errors") / f"{nombre}_rechazados.parquet"

    archivos = sorted(origen.rglob("*.parquet"))

    if not archivos:
        raise FileNotFoundError(
            f"No se encontraron archivos Bronze para {nombre}"
        )

    df = pd.concat(
        [pd.read_parquet(archivo) for archivo in archivos],
        ignore_index=True,
    )

    df["motivo_rechazo"] = ""

    # Clave primaria obligatoria
    df.loc[df[clave].isna(), "motivo_rechazo"] += (
        f"{clave} nulo; "
    )

    # Identificadores duplicados
    df.loc[
        df[clave].duplicated(keep="first"),
        "motivo_rechazo"
    ] += f"{clave} duplicado; "

    # Validaciones específicas
    validar(df)

    rechazados = df[df["motivo_rechazo"] != ""].copy()
    validos = df[df["motivo_rechazo"] == ""].copy()

    validos.drop(columns=["motivo_rechazo"], inplace=True)

    destino.parent.mkdir(parents=True, exist_ok=True)
    errores.parent.mkdir(parents=True, exist_ok=True)

    validos.to_parquet(destino, index=False)
    rechazados.to_parquet(errores, index=False)

    print(f"\nTabla: {nombre}")
    print(f"Registros de entrada: {len(df):,}")
    print(f"Registros válidos: {len(validos):,}")
    print(f"Registros rechazados: {len(rechazados):,}")


def validar_rutas(df):
    # Validar distancias.
    for columna in ["km_recorridos", "desviacion_ruta_km"]:
        invalidos = df[columna].isna() | (df[columna] < 0)

        df.loc[invalidos, "motivo_rechazo"] += (
            f"{columna} invalido; "
        )

    # Validar paradas planificadas.
    invalidos = (
        df["num_paradas_plan"].isna()
        | (df["num_paradas_plan"] <= 0)
    )

    df.loc[invalidos, "motivo_rechazo"] += (
        "num_paradas_plan invalido; "
    )

    # Convertir horas de inicio y fin.
    inicio = pd.to_timedelta(df["hra_inicio"].astype(str), errors="coerce")
    fin = pd.to_timedelta(df["hra_fin"].astype(str), errors="coerce")

    # Calcular duración en horas.
    duracion = (fin - inicio).dt.total_seconds() / 3600

    # Validar duración.
    invalidos = duracion.isna() | (duracion <= 0)

    df.loc[invalidos, "motivo_rechazo"] += (
        "duracion_ruta invalida; "
    )

    # Guardar la duración calculada.
    df["horas_trabajadas"] = duracion


def validar_novedades(df):
    # Cada novedad debe pertenecer a un envío.
    invalidos = df["id_envio"].isna()

    df.loc[invalidos, "motivo_rechazo"] += (
        "id_envio nulo; "
    )

    # Cada evento debe tener fecha.
    invalidos = df["fec_novedad"].isna()

    df.loc[invalidos, "motivo_rechazo"] += (
        "fec_novedad nula; "
    )


def main():
    procesar_tabla(
        "gps_rutas",
        "id_ruta",
        validar_rutas,
    )

    procesar_tabla(
        "dir_novedades",
        "id_novedad",
        validar_novedades,
    )

    print("\nProcesamiento Silver finalizado.")


if __name__ == "__main__":
    main()