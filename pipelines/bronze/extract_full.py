import os
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

TABLES = [
    "geo_zonas",
    "ope_conductores",
    "cli_remitentes",
    "tms_envios",
    "gps_rutas",
    "cal_destinatarios",
    "dir_novedades",
]

CHUNK_SIZE = 50000

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("POSTGRES_USER", "logitrack_user"),
    password=os.environ["POSTGRES_PASSWORD"],
    host="localhost",
    port=5432,
    database=os.getenv("POSTGRES_DB", "logitrack"),
)

engine = create_engine(DATABASE_URL)


def extract_table(table_name, batch_id, ingestion_timestamp):
    start_time = time.perf_counter()

    ingestion_date = ingestion_timestamp.date()

    output_dir = (
        Path("data/bronze")
        / table_name
        / f"year={ingestion_date.year}"
        / f"month={ingestion_date.month:02d}"
        / f"day={ingestion_date.day:02d}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    total_records = 0
    total_bytes = 0

    query = text(f"SELECT * FROM {table_name}")

    with engine.connect().execution_options(
        stream_results=True
    ) as connection:

        chunks = pd.read_sql(
            query,
            connection,
            chunksize=CHUNK_SIZE,
        )

        for chunk_number, df in enumerate(chunks, start=1):
            df["ingestion_timestamp"] = ingestion_timestamp
            df["source_system"] = "postgresql_logitrack"
            df["batch_id"] = batch_id

            output_file = (
                output_dir
                / f"batch_{batch_id}_part_{chunk_number:04d}.parquet"
            )

            df.to_parquet(
                output_file,
                engine="pyarrow",
                index=False,
            )

            total_records += len(df)
            total_bytes += output_file.stat().st_size

    duration = time.perf_counter() - start_time

    print(
        f"{table_name}: "
        f"{total_records:,} registros | "
        f"{total_bytes:,} bytes | "
        f"{duration:.2f} segundos"
    )

    return total_records


def main():
    batch_id = str(uuid.uuid4())
    ingestion_timestamp = datetime.now(timezone.utc)

    print(f"Lote: {batch_id}")
    print(f"Fecha de ingesta: {ingestion_timestamp.isoformat()}")
    print()

    total = 0

    for table_name in TABLES:
        total += extract_table(
            table_name,
            batch_id,
            ingestion_timestamp,
        )

    print()
    print(f"Total de registros extraídos: {total:,}")


if __name__ == "__main__":
    main()