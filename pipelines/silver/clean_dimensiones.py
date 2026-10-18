from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


TABLAS = {
    "cli_remitentes": {
        "clave": "id_remitente",
    },
    "ope_conductores": {
        "clave": "cond_id",
    },
    "geo_zonas": {
        "clave": "id_zona",
    },
}


def procesar_tabla(nombre, clave):
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

    if clave not in df.columns:
        raise ValueError(
            f"La columna {clave} no existe en {nombre}"
        )

    # Validar clave primaria obligatoria.
    nulos = df[clave].isna()

    # Detectar duplicados, conservando la primera aparición.
    duplicados = df[clave].duplicated(keep="first")

    df["motivo_rechazo"] = ""

    df.loc[nulos, "motivo_rechazo"] += (
        f"{clave} nulo; "
    )

    df.loc[duplicados, "motivo_rechazo"] += (
        f"{clave} duplicado; "
    )

    rechazados = df[df["motivo_rechazo"] != ""].copy()
    validos = df[df["motivo_rechazo"] == ""].copy()

    validos = validos.drop(columns=["motivo_rechazo"])

    destino.parent.mkdir(parents=True, exist_ok=True)
    errores.parent.mkdir(parents=True, exist_ok=True)

    validos.to_parquet(destino, index=False)
    rechazados.to_parquet(errores, index=False)

    print(f"\nTabla: {nombre}")
    print(f"Entrada: {len(df):,}")
    print(f"Válidos: {len(validos):,}")
    print(f"Rechazados: {len(rechazados):,}")


def main():
    for nombre, configuracion in TABLAS.items():
        procesar_tabla(
            nombre,
            configuracion["clave"],
        )

    print("\nProcesamiento Silver finalizado.")


if __name__ == "__main__":
    main()