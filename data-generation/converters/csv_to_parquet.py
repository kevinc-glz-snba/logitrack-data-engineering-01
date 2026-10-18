import csv
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


# RUTAS DEL PROYECTO
ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = ROOT / "data" / "raw"
PARQUET_DIR = ROOT / "data" / "parquet"

PARQUET_DIR.mkdir(parents=True, exist_ok=True)


# DATASETS
DATASETS = [
    "geo_zonas",
    "ope_conductores",
    "cli_remitentes",
    "tms_envios",
    "gps_rutas",
    "cal_destinatarios",
    "dir_novedades",
]


# Tamaño de procesamiento para evitar cargar
# los dos millones de envíos en memoria.
BATCH_SIZE = 50_000


def convertir_csv_a_parquet(nombre_dataset):

    ruta_csv = RAW_DIR / f"{nombre_dataset}.csv"
    ruta_parquet = PARQUET_DIR / f"{nombre_dataset}.parquet"

    if not ruta_csv.exists():
        raise FileNotFoundError(ruta_csv)

    writer = None
    total = 0

    try:
        with open( ruta_csv, newline="", encoding="utf-8") as archivo:

            lector = csv.DictReader(archivo)

            batch = []

            for fila in lector:

                batch.append(fila)

                if len(batch) >= BATCH_SIZE:

                    tabla = pa.Table.from_pylist(batch)

                    if writer is None:
                        writer = pq.ParquetWriter(
                            ruta_parquet,
                            tabla.schema,
                            compression="snappy"
                        )

                    writer.write_table(tabla)

                    total += len(batch)
                    batch = []

            if batch:

                tabla = pa.Table.from_pylist(batch)

                if writer is None:
                    writer = pq.ParquetWriter(
                        ruta_parquet,
                        tabla.schema,
                        compression="snappy"
                    )

                writer.write_table(tabla)

                total += len(batch)

    finally:
        if writer is not None:
            writer.close()

    print(
        f"{nombre_dataset}: "
        f"{total:,} registros convertidos."
    )


if __name__ == "__main__":

    for dataset in DATASETS:
        convertir_csv_a_parquet(dataset)

    print("Conversión completada.")