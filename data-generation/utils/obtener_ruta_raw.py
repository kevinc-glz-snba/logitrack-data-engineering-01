from pathlib import Path

#Obtenemos la ruta a la carpeta data/raw
def obtener_ruta_raw() -> Path:

    BASE_DIR = Path(__file__).resolve().parents[2]
    ruta_carpeta = BASE_DIR / "data" / "raw"

    ruta_carpeta.mkdir(parents=True, exist_ok=True)

    return ruta_carpeta