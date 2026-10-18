import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
ANOMALIES_DIR = ROOT / "data" / "anomalies"

ANOMALIES_DIR.mkdir(parents=True, exist_ok=True)


ANOMALIAS = {
    "tms_envios": {
        "campo": "peso_kg",
        "valor": "-5",
    },
    "cal_destinatarios": {
        "campo": "puntaje_1_5",
        "valor": "8",
    },
    "gps_rutas": {
        "campo": "km_recorridos",
        "valor": "-20",
    },
}


for dataset, configuracion in ANOMALIAS.items():

    ruta_origen = RAW_DIR / f"{dataset}.csv"

    ruta_destino = (
        ANOMALIES_DIR / f"{dataset}_anomalies.csv"
    )

    with open(ruta_origen, newline="", encoding="utf-8" ) as origen:

        lector = csv.DictReader(origen)

        fila = next(lector)
        campos = lector.fieldnames

    fila[configuracion["campo"]] = configuracion["valor"]

    with open( ruta_destino, "w",  newline="",  encoding="utf-8" ) as destino:

        escritor = csv.DictWriter(
            destino,
            fieldnames=campos
        )

        escritor.writeheader()
        escritor.writerow(fila)

    print(
        f"Anomalía generada: {dataset} - "
        f"{configuracion['campo']} = "
        f"{configuracion['valor']}"
    )


print("Generación de anomalías completada.")