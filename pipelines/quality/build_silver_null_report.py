from pathlib import Path
from datetime import datetime, timezone
import csv

import pyarrow.parquet as pq


SILVER_DIR = Path("data/silver")

OUTPUT_FILE = Path(
    "docs/evidence/entregables_03/"
    "silver_null_quality_report.csv"
)


def analizar_dataset(nombre_tabla, archivos):
    """
    Calcula el porcentaje de valores nulos por columna
    utilizando los metadatos de los archivos Parquet.

    Si las estadísticas de nulos no están disponibles,
    el valor se reporta como no disponible.
    """

    total_registros = 0
    nulos_por_columna = {}
    columnas_sin_estadisticas = set()

    for archivo in archivos:
        parquet = pq.ParquetFile(archivo)
        metadata = parquet.metadata

        total_registros += metadata.num_rows

        for row_group_idx in range(metadata.num_row_groups):
            row_group = metadata.row_group(row_group_idx)

            for col_idx in range(row_group.num_columns):
                columna = row_group.column(col_idx)

                nombre_columna = columna.path_in_schema

                if nombre_columna not in nulos_por_columna:
                    nulos_por_columna[nombre_columna] = 0

                estadisticas = columna.statistics

                if (
                    estadisticas is None
                    or not estadisticas.has_null_count
                ):
                    columnas_sin_estadisticas.add(nombre_columna)
                    continue

                nulos_por_columna[nombre_columna] += (
                    estadisticas.null_count
                )

    resultados = []

    for columna, cantidad_nulos in sorted(
        nulos_por_columna.items()
    ):
        if columna in columnas_sin_estadisticas:
            cantidad = None
            porcentaje = None
            estado = "SIN_ESTADISTICAS"
        else:
            cantidad = cantidad_nulos

            porcentaje = round(
                (cantidad / total_registros) * 100,
                4,
            ) if total_registros else 0.0

            estado = "CALCULADO"

        resultados.append({
            "fecha_reporte": datetime.now(
                timezone.utc
            ).isoformat(),
            "tabla": nombre_tabla,
            "columna": columna,
            "total_registros": total_registros,
            "cantidad_nulos": cantidad,
            "porcentaje_nulos": porcentaje,
            "estado": estado,
        })

    return resultados


def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultados = []

    for elemento in sorted(SILVER_DIR.iterdir()):

        if elemento.is_file():
            if elemento.suffix != ".parquet":
                continue

            nombre_tabla = elemento.stem
            archivos = [elemento]

        elif elemento.is_dir():
            nombre_tabla = elemento.name
            archivos = sorted(
                elemento.rglob("*.parquet")
            )

        else:
            continue

        if not archivos:
            continue

        resultados.extend(
            analizar_dataset(
                nombre_tabla,
                archivos,
            )
        )

        print(
            f"Analizado: {nombre_tabla} "
            f"({len(archivos)} archivos)"
        )

    columnas = [
        "fecha_reporte",
        "tabla",
        "columna",
        "total_registros",
        "cantidad_nulos",
        "porcentaje_nulos",
        "estado",
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

    print()
    print("REPORTE GENERADO CORRECTAMENTE")
    print(f"Archivo: {OUTPUT_FILE}")
    print(f"Columnas evaluadas: {len(resultados)}")


if __name__ == "__main__":
    main()
