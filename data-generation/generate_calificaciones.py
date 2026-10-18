import csv
import random

from datetime import date, timedelta

from utils.configuration import cargar_configuracion
from utils.obtener_ruta_raw import obtener_ruta_raw


# CONFIGURACIÓN
config = cargar_configuracion()

SEMILLA = config["semilla"]
TOTAL_CALIFICACIONES = config["volumenes"]["cal_destinatarios"]

random.seed(SEMILLA)


# RUTAS
carpeta = obtener_ruta_raw()

ruta_envios = carpeta / "tms_envios.csv"
ruta_calificaciones = carpeta / "cal_destinatarios.csv"


# CATÁLOGOS
canales = [
    "Web",
    "App",
    "WhatsApp",
    "SMS"
]

comentarios = {
    1: [
        "Entrega muy deficiente",
        "Mala experiencia",
        "No recomiendo el servicio"
    ],
    2: [
        "Entrega con inconvenientes",
        "El servicio puede mejorar",
        "Experiencia poco satisfactoria"
    ],
    3: [
        "Servicio aceptable",
        "Entrega normal",
        "Experiencia regular"
    ],
    4: [
        "Buen servicio",
        "Entrega satisfactoria",
        "Buena atención"
    ],
    5: [
        "Excelente servicio",
        "Entrega rápida y segura",
        "Muy buena experiencia"
    ]
}


# CAMPOS
campos = [
    "id_calificacion",
    "id_envio",
    "fec_calificacion",
    "puntaje_1_5",
    "comentario_texto",
    "canal_calificacion"
]


# CARGAR ENVÍOS ENTREGADOS
# Guardamos únicamente el ID y la fecha de entrega,
# no los 19 campos completos del envío.

envios_entregados = []

with open(ruta_envios, newline="", encoding="utf-8") as archivo:

    lector = csv.DictReader(archivo)

    for envio in lector:

        if envio["estado_final"] == "Entregado":

            envios_entregados.append((
                int(envio["id_envio"]),
                date.fromisoformat(envio["fec_entrega_real"])
            ))


if len(envios_entregados) < TOTAL_CALIFICACIONES:
    raise ValueError(
        "No existen suficientes envíos entregados "
        "para generar calificaciones únicas."
    )


# SELECCIONAR ENVÍOS SIN REPETICIONES
# Cada envío seleccionado tendrá una calificación.

envios_seleccionados = random.sample(
    envios_entregados,
    TOTAL_CALIFICACIONES
)


# GENERACIÓN
with open(ruta_calificaciones, mode="w", newline="", encoding="utf-8" ) as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=campos
    )

    escritor.writeheader()

    for i, (id_envio, fecha_entrega) in enumerate(
        envios_seleccionados,
        start=1
    ):

        # Calificación entre 0 y 7 días después
        fecha_calificacion = fecha_entrega + timedelta(
            days=random.randint(0, 7)
        )

        # Distribución de satisfacción
        puntaje = random.choices(
            population=[1, 2, 3, 4, 5],
            weights=[5, 10, 20, 30, 35],
            k=1
        )[0]

        # Aproximadamente 5 % de comentarios nulos
        if random.random() < 0.05:
            comentario = None
        else:
            comentario = random.choice(
                comentarios[puntaje]
            )

        nueva_calificacion = {
            "id_calificacion": i,
            "id_envio": id_envio,
            "fec_calificacion": fecha_calificacion,
            "puntaje_1_5": puntaje,
            "comentario_texto": comentario,
            "canal_calificacion": random.choice(canales)
        }

        escritor.writerow(nueva_calificacion)

        if i % 50000 == 0:
            print(
                f"Calificaciones generadas: "
                f"{i:,} / {TOTAL_CALIFICACIONES:,}"
            )

print("Generación de calificaciones completada.")