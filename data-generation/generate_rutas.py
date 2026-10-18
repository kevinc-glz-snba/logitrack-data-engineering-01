import csv
import random

from datetime import date, time, datetime, timedelta

from utils.configuration import cargar_configuracion
from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.cargar_identificadores import cargar_identificadores


# CONFIGURACIÓN
config = cargar_configuracion()

SEMILLA = config["semilla"]
TOTAL_RUTAS = config["volumenes"]["gps_rutas"]

FECHA_INICIO = date.fromisoformat(config["fecha_inicio"])
FECHA_FIN = date.fromisoformat(config["fecha_fin"])

random.seed(SEMILLA)


# RUTAS DE ARCHIVOS
carpeta = obtener_ruta_raw()

ruta_csv = carpeta / "gps_rutas.csv"


# Cargar conductores y sus tipos de vehículo
conductores = {}

with open(
    carpeta / "ope_conductores.csv",
    newline="",
    encoding="utf-8"
) as archivo:

    lector = csv.DictReader(archivo)

    for conductor in lector:
        conductores[int(conductor["cond_id"])] = conductor["tip_vehiculo"]

ids_conductores = list(conductores.keys())


# CAMPOS
campos = [
    "id_ruta",
    "cond_id",
    "fec_ruta",
    "hra_inicio",
    "hra_fin",
    "km_recorridos",
    "num_paradas_plan",
    "num_paradas_real",
    "desviacion_ruta_km",
    "consumo_combustible"
]


# PERIODO DISPONIBLE
dias_disponibles = (FECHA_FIN - FECHA_INICIO).days


# GENERACIÓN
with open(ruta_csv, mode="w", newline="", encoding="utf-8") as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=campos
    )

    escritor.writeheader()

    for i in range(TOTAL_RUTAS):

        cond_id = random.choice(ids_conductores)
        tipo_vehiculo = conductores[cond_id]

        # Fecha de ruta
        fecha_ruta = FECHA_INICIO + timedelta(
            days=random.randint(0, dias_disponibles)
        )

        # Horario de inicio
        hora_inicio = time(
            hour=random.randint(6, 10),
            minute=random.randint(0, 59)
        )

        # Duración entre 2 y 9 horas
        duracion_minutos = random.randint(120, 540)

        inicio = datetime.combine(
            fecha_ruta,
            hora_inicio
        )

        fin = inicio + timedelta(
            minutes=duracion_minutos
        )

        # Distancia recorrida
        km_recorridos = round(
            random.uniform(10, 180),
            2
        )

        # Paradas
        num_paradas_plan = random.randint(5, 30)

        variacion = random.randint(-3, 3)

        num_paradas_real = max(
            0,
            num_paradas_plan + variacion
        )

        # Desviación de ruta
        desviacion_ruta_km = round(
            random.uniform(0, 15),
            2
        )

        # Consumo aproximado: 10 litros por 100 km
        if tipo_vehiculo == "Bicicleta":
            consumo_combustible = 0.0
        else:
            consumo_combustible = round(
                km_recorridos * 0.10,
                2
            )

        nueva_ruta = {
            "id_ruta": i + 1,
            "cond_id": cond_id,
            "fec_ruta": fecha_ruta,
            "hra_inicio": hora_inicio,
            "hra_fin": fin.time(),
            "km_recorridos": km_recorridos,
            "num_paradas_plan": num_paradas_plan,
            "num_paradas_real": num_paradas_real,
            "desviacion_ruta_km": desviacion_ruta_km,
            "consumo_combustible": consumo_combustible
        }

        escritor.writerow(nueva_ruta)

        if (i + 1) % 10000 == 0:
            print(
                f"Rutas generadas: "
                f"{i + 1:,} / {TOTAL_RUTAS:,}"
            )

print("Generación de rutas completada.")