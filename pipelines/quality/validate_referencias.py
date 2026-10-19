from pathlib import Path

import pandas as pd


def leer_tabla(nombre, columnas):
    ruta = Path("data/silver") / nombre

    if ruta.is_file():
        archivos = [ruta]
    elif ruta.is_dir():
        archivos = sorted(ruta.rglob("*.parquet"))
    else:
        raise FileNotFoundError(f"No existe: {ruta}")

    if not archivos:
        raise ValueError(f"No hay archivos Parquet en: {ruta}")

    return pd.concat(
        [
            pd.read_parquet(archivo, columns=columnas)
            for archivo in archivos
        ],
        ignore_index=True,
    )


def validar_relacion(
    origen,
    columna_origen,
    destino,
    columna_destino,
):
    ids_validos = set(destino[columna_destino].dropna())

    invalidos = (
        origen[columna_origen].isna()
        | ~origen[columna_origen].isin(ids_validos)
    )

    cantidad = int(invalidos.sum())

    estado = "APROBADA" if cantidad == 0 else "FALLIDA"

    print(
        f"{columna_origen} -> {columna_destino}: "
        f"{cantidad:,} referencias inválidas | {estado}"
    )

    return cantidad


def main():
    envios = leer_tabla(
        "tms_envios",
        ["id_envio", "id_remitente", "cond_id"],
    )

    remitentes = leer_tabla(
        "cli_remitentes.parquet",
        ["id_remitente"],
    )

    conductores = leer_tabla(
        "ope_conductores.parquet",
        ["cond_id"],
    )

    rutas = leer_tabla(
        "gps_rutas.parquet",
        ["cond_id"],
    )

    novedades = leer_tabla(
        "dir_novedades.parquet",
        ["id_envio"],
    )

    calificaciones = leer_tabla(
        "cal_destinatarios.parquet",
        ["id_envio"],
    )

    print("\nVALIDACIONES DE INTEGRIDAD REFERENCIAL\n")

    total_errores = 0

    relaciones = [
        (envios, "id_remitente", remitentes, "id_remitente"),
        (envios, "cond_id", conductores, "cond_id"),
        (rutas, "cond_id", conductores, "cond_id"),
        (novedades, "id_envio", envios, "id_envio"),
        (calificaciones, "id_envio", envios, "id_envio"),
    ]

    for origen, col_origen, destino, col_destino in relaciones:
        total_errores += validar_relacion(
            origen,
            col_origen,
            destino,
            col_destino,
        )

    print(f"\nTotal de referencias inválidas: {total_errores:,}")

    if total_errores == 0:
        print("VALIDACIONES SUPERADAS")
    else:
        print("SE DETECTARON PROBLEMAS DE INTEGRIDAD")
        raise SystemExit(1)


if __name__ == "__main__":
    main()