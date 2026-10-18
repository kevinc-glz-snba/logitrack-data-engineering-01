from faker import Faker
import random
import csv

from utils.catalogo_ciudades import ciudades
from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.configuration import cargar_configuracion


# Configuración
config = cargar_configuracion()

TOTAL_ZONAS = config["volumenes"]["geo_zonas"]

fake = Faker("es_CO")


# Ruta para guardar el archivo CSV
ruta_carpeta = obtener_ruta_raw()
ruta_csv = ruta_carpeta / "geo_zonas.csv"


# Semillas
SEMILLA = config["semilla"]
random.seed(SEMILLA)
fake.seed_instance(SEMILLA)


# Campos de la tabla geo_zonas
campos = [
    "id_zona",
    "nom_zona",
    "id_ciudad",
    "barrio_referencia",
    "latitud_centroide",
    "longitud_centroide",
    "nivel_trafico_prom",
    "tip_zona",
    "distancia_bodega_km"
]


# Variación máxima de coordenadas
VARIACION_MAXIMA = 0.005

datos = []


# Generación de zonas
for zona in range(TOTAL_ZONAS):

    id_zona = zona + 1

    nom_zona = f"ZONA-{id_zona:03d}"

    id_ciudad = random.choice(list(ciudades.keys()))

    barrio_referencia = f"Sector {id_zona}"

    latitud_centroide = round(
        ciudades[id_ciudad][1]
        + random.uniform(-VARIACION_MAXIMA, VARIACION_MAXIMA),
        7
    )

    longitud_centroide = round(
        ciudades[id_ciudad][2]
        + random.uniform(-VARIACION_MAXIMA, VARIACION_MAXIMA),
        7
    )

    nivel_trafico_prom = round(
        random.uniform(1.0, 5.0),
        2
    )

    tip_zona = "Rural" if id_zona % 3 == 0 else "Urbana"

    distancia_bodega_km = round(
        (id_zona % 20) * 1.5,
        2
    )

    # Registro de la zona
    new_zona = {
        "id_zona": id_zona,
        "nom_zona": nom_zona,
        "id_ciudad": id_ciudad,
        "barrio_referencia": barrio_referencia,
        "latitud_centroide": latitud_centroide,
        "longitud_centroide": longitud_centroide,
        "nivel_trafico_prom": nivel_trafico_prom,
        "tip_zona": tip_zona,
        "distancia_bodega_km": distancia_bodega_km
    }

    datos.append(new_zona)


print(f"Total de zonas generadas: {len(datos)}")


# Exportación CSV
with open(ruta_csv, mode="w", newline="", encoding="utf-8") as file:

    escritor = csv.DictWriter(
        file,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(datos)


print("Archivo 'geo_zonas.csv' generado con éxito.")