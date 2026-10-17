from faker import Faker
import random
from pathlib import Path
import csv

from catalogo_ciudades import ciudades

fake = Faker("es_CO")

#Ruta para guardar el archivo CSV
BASE_DIR = Path(__file__).resolve().parent.parent
ruta_carpeta = BASE_DIR / "data" / "raw"

ruta_carpeta.mkdir(parents=True, exist_ok=True)
ruta_csv = ruta_carpeta / "geo_zonas.csv"

#Semillas 
random.seed(42)
fake.seed_instance(42)

#campos de la tabla zonas
campos = [
    "id_zona",
    "nombre_zona",
    "id_ciudad" ,
    "barrio_referencia",
    "latitud_centroide" ,
    "longitud_centroide" ,
    "nivel_trafico_prom" ,
    "tip_zona" ,
    "distancia_bodega_km"
]

datos = []

#Variacion en las coordenadas
VARIACION_MAXIMA = 0.005

for zona in range(30):
    id_zona = zona + 1
    nombre_zona = f"ZONA-{id_zona:03d}"
    id_ciudad = random.choice(list(ciudades.keys()))
    barrio_referencia = f"Sector {str(zona)}"
    latitud_centroide = ((ciudades[id_ciudad][1]) + (random.uniform(-VARIACION_MAXIMA, VARIACION_MAXIMA)))
    longitud_centroide = ((ciudades[id_ciudad][2]) + (random.uniform(-VARIACION_MAXIMA, VARIACION_MAXIMA)))
    nivel_trafico_prom = round(random.uniform(1.0, 5.0), 2)
    tip_zona = "Rural" if (id_zona % 3 == 0) else "Urbana"
    distancia_bodega_km = round((id_zona % 20) * 1.5, 2)

    new_zona = {
        "id_zona" : id_zona,
        "nombre_zona": nombre_zona,
        "id_ciudad" : id_ciudad,
        "barrio_referencia": barrio_referencia,
        "latitud_centroide" : latitud_centroide,
        "longitud_centroide" : longitud_centroide,
        "nivel_trafico_prom" : nivel_trafico_prom,
        "tip_zona" : tip_zona,
        "distancia_bodega_km" : distancia_bodega_km
    }

    datos.append(new_zona)

print(f"Total de zonas generadas: {len(datos)}")

with open(f"{ruta_csv}", mode="w", newline="", encoding="utf-8") as file:
    escritor = csv.DictWriter(file, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(datos)

print("Archivo 'geo_zonas.csv' generado con éxito.")