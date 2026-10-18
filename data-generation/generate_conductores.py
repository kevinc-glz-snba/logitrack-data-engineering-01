from faker import Faker
import random
import csv
import hashlib
from datetime import date

from utils.catalogo_ciudades import ciudades
from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.configuration import cargar_configuracion



#CONFIGURACIÓN

config = cargar_configuracion()

TOTAL_CONDUCTORES = config["volumenes"]["ope_conductores"]

FECHA_INICIO = date.fromisoformat(config["fecha_inicio"])
FECHA_FIN = date.fromisoformat(config["fecha_fin"])

fake = Faker("es_CO")


#RUTAS DE ARCHIVOS

ruta_carpeta = obtener_ruta_raw()

ruta_csv = ruta_carpeta / "ope_conductores.csv"
ruta_zonas = ruta_carpeta / "geo_zonas.csv"

#SEMILLAS

SEMILLA = config["semilla"]
random.seed(SEMILLA)
fake.seed_instance(SEMILLA)

#DATOS PREDEFINIDOS

vehiculos = [
    "Moto",
    "Bicicleta",
    "Van",
    "Camion",
]

tipo_documento = [
    "CC",
    "CE",
]

#CAMPOS DE LA TABLA

campos = [
    "cond_id",
    "nomb_cond",
    "apell_cond",
    "tip_doc",
    "num_doc_hash",
    "fec_ingreso",
    "id_ciudad_base",
    "tip_vehiculo",
    "cod_zona_asignada",
    "activo",
    "calific_promedio_acum"
]


#CARGAR ZONAS AGRUPADAS POR CIUDAD

zonas_por_ciudad = {}

try:

    with open(
        ruta_zonas,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        lector = csv.DictReader(file)

        columnas_requeridas = {"id_zona", "id_ciudad"}

        if not columnas_requeridas.issubset(lector.fieldnames or []):
            raise ValueError(
                "geo_zonas.csv no contiene las columnas "
                "'id_zona' e 'id_ciudad'."
            )

        for fila in lector:

            id_zona = int(fila["id_zona"])
            id_ciudad = int(fila["id_ciudad"])

            # Validar que la ciudad pertenezca al catálogo
            if id_ciudad not in ciudades:
                raise ValueError(
                    f"La zona {id_zona} pertenece a una "
                    f"ciudad desconocida: {id_ciudad}"
                )

            # Crear la lista de zonas de la ciudad
            if id_ciudad not in zonas_por_ciudad:
                zonas_por_ciudad[id_ciudad] = []

            # Agregar la zona correspondiente
            zonas_por_ciudad[id_ciudad].append(id_zona)

except FileNotFoundError:

    raise SystemExit(
        f"ERROR: No se encontró el archivo {ruta_zonas}. "
        "Ejecuta primero generate_zonas.py."
    )

except (ValueError, KeyError) as error:

    raise SystemExit(
        f"ERROR al leer geo_zonas.csv: {error}"
    )


# Verificar que existan zonas disponibles
if not zonas_por_ciudad:

    raise SystemExit(
        "ERROR: geo_zonas.csv no contiene zonas disponibles."
    )


print(f"Ciudades con zonas disponibles: {len(zonas_por_ciudad)}")

print(
    f"Total de zonas disponibles: "
    f"{sum(len(zonas) for zonas in zonas_por_ciudad.values())}"
)

#GENERACIÓN DE CONDUCTORES

datos = []

for con in range(TOTAL_CONDUCTORES):

    cond_id = con + 1

    nomb_cond = fake.first_name()
    apell_cond = fake.last_name()

    tip_doc = random.choice(tipo_documento)

    numero_documento = str(
        fake.random_int(
            min=10000000,
            max=99999999
        )
    )

    num_doc_hash = hashlib.sha256(
        numero_documento.encode("utf-8")
    ).hexdigest()

    fec_ingreso = fake.date_between(
        start_date=FECHA_INICIO,
        end_date=FECHA_FIN
    )

    # Seleccionar una ciudad que tenga zonas disponibles
    id_ciudad_base = random.choice(
        list(zonas_por_ciudad.keys())
    )

    tip_vehiculo = random.choice(vehiculos)

    # Seleccionar una zona perteneciente a esa ciudad
    cod_zona_asignada = random.choice(
        zonas_por_ciudad[id_ciudad_base]
    )

    activo = random.choices(
        population=[True, False],
        weights=[85, 15],
        k=1
    )[0]

    calific_promedio_acum = round(
        random.uniform(1.0, 5.0),
        2
    )

    # Crear registro del conductor
    new_conductor = {
        "cond_id": cond_id,
        "nomb_cond": nomb_cond,
        "apell_cond": apell_cond,
        "tip_doc": tip_doc,
        "num_doc_hash": num_doc_hash,
        "fec_ingreso": fec_ingreso,
        "id_ciudad_base": id_ciudad_base,
        "tip_vehiculo": tip_vehiculo,
        "cod_zona_asignada": cod_zona_asignada,
        "activo": activo,
        "calific_promedio_acum": calific_promedio_acum
    }

    datos.append(new_conductor)


print(f"Total de conductores generados: {len(datos)}")


#EXPORTACIÓN CSV
with open(
    ruta_csv,
    mode="w",
    newline="",
    encoding="utf-8"
) as file:

    escritor = csv.DictWriter(
        file,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(datos)


print("Archivo 'ope_conductores.csv' generado con éxito.")