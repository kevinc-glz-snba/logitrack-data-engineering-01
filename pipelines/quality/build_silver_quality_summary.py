from pathlib import Path
from datetime import datetime, timezone
import csv

import pyarrow.parquet as pq


SILVER_DIR = Path("data/silver")
ERROR_DIR = Path("data/errors")

OUTPUT_FILE = Path(
    "docs/evidence/entregables_03/"
    "silver_quality_summary.csv"
)

TABLES = [
    "cal_destinatarios",
    "cli_remitentes",
    "dir_novedades",
    "geo_zonas",
    "gps_rutas",
    "ope_conductores",
    "tms_envios",
]


def contar_registros(archivos):
    return sum(
        pq.ParquetFile(archivo).metadata.num_rows
        for archivo in archivos
    )


def archivos_silver(tabla):
    archivo = SILVER_DIR / f"{tabla}.parquet"

    if archivo.exists():
        return [archivo]

    directorio = SILVER_DIR / tabla

    if directorio.exists():
        return sorted(directorio.rglob("*.parquet"))

    return []


def archivos_rechazados(tabla):
    if tabla == "tms_envios":
        directorio = ERROR_DIR / "tms_envios"

        if not directorio.exists():
            return []

        return sorted(directorio.rglob("*.parquet"))

    archivo = ERROR_DIR / f"{tabla}_rechazados.parquet"

    return [archivo] if archivo.exists() else []


def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultados = []

    for tabla in TABLES:
        silver = archivos_silver(tabla)
        errores = archivos_rechazados(tabla)

        if not silver:
            raise FileNotFoundError(
                f"No existen archivos Silver para {tabla}"
            )

        validos = contar_registros(silver)

        if errores:
            rechazados = contar_registros(errores)
            entrada = validos + rechazados

            porcentaje = (
                round(validos / entrada * 100, 4)
                if entrada > 0 else 0.0
            )

            estado = "CONCILIADO_CON_ARCHIVOS"

        else:
            rechazados = None
            entrada = None
            porcentaje = None
            estado = "RECHAZOS_NO_VERIFICADOS"

        resultados.append({
            "fecha_reporte": datetime.now(
                timezone.utc
            ).isoformat(),
            "tabla": tabla,
            "registros_entrada": entrada,
            "registros_validos": validos,
            "registros_rechazados": rechazados,
            "porcentaje_validos": porcentaje,
            "estado_verificacion": estado,
        })

    columnas = [
        "fecha_reporte",
        "tabla",
        "registros_entrada",
        "registros_validos",
        "registros_rechazados",
        "porcentaje_validos",
        "estado_verificacion",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as archivo:
        writer = csv.DictWriter(
            archivo,
            fieldnames=columnas,
        )

        writer.writeheader()
        writer.writerows(resultados)

    print("\nREPORTE CONSOLIDADO SILVER\n")

    for resultado in resultados:
        print(
            f"{resultado['tabla']}: "
            f"{resultado['registros_validos']:,} válidos | "
            f"Estado: {resultado['estado_verificacion']}"
        )

    print(f"\nArchivo generado: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
