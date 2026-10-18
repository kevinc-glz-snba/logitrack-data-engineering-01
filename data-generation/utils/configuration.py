import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def cargar_configuracion():
    ruta_config = BASE_DIR / "config.json"

    with open(ruta_config, mode= "r", encoding="utf-8") as archivo:
        return json.load(archivo)