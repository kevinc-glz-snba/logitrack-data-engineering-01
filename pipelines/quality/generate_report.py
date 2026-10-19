from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import pyarrow.parquet as pq


def contar_registros(directorio):
    archivos = Path(directorio).rglob("*.parquet")

    return sum(
        pq.read_metadata(archivo).num_rows
        for archivo in archivos
    )


def main():
    tablas = [
        {
            "tabla": "cal_destinatarios",
            "bronze": "data/bronze/cal_destinatarios",
            "silver": "data/silver/cal_destinatarios.parquet",
            "errores": "data/errors/cal_destinatarios_rechazados.parquet",
        },
        {
            "tabla": "tms_envios",
            "bronze": "data/bronze/tms_envios",
            "silver": "data/silver/tms_envios",
            "errores": "data/errors/tms_envios",
        },
    ]

    resultados = []

    for tabla in tablas:
        entrada = contar_registros(tabla["bronze"])
        validos = contar_registros(tabla["silver"])
        rechazados = contar_registros(tabla["errores"])

        porcentaje = (
            round((validos / entrada) * 100, 2)
            if entrada > 0 else 0
        )

        resultados.append({
            "fecha_reporte": datetime.now(timezone.utc).isoformat(),
            "tabla": tabla["tabla"],
            "registros_entrada": entrada,
            "registros_validos": validos,
            "registros_rechazados": rechazados,
            "porcentaje_validos": porcentaje,
        })

    reporte = pd.DataFrame(resultados)

    Path("docs/evidence").mkdir(parents=True, exist_ok=True)

    salida = "docs/evidence/silver_quality_report.csv"

    reporte.to_csv(salida, index=False)

    print(reporte.to_string(index=False))
    print(f"\nReporte guardado en: {salida}")


if __name__ == "__main__":
    main()