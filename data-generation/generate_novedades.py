import csv
import random

from datetime import date, timedelta

from utils.configuration import cargar_configuracion
from utils.obtener_ruta_raw import obtener_ruta_raw


# CONFIGURACIÓN
config = cargar_configuracion()

SEMILLA = config["semilla"]
TOTAL_NOVEDADES = config["volumenes"]["dir_novedades"]

random.seed(SEMILLA)


# RUTAS
carpeta = obtener_ruta_raw()

ruta_envios = carpeta / "tms_envios.csv"
ruta_novedades = carpeta / "dir_novedades.csv"


# CATÁLOGO DE NOVEDADES
catalogo_novedades = {
    "DESTINATARIO_AUSENTE": (
        "El destinatario no se encontraba disponible",
        True
    ),
    "DIRECCION_INCORRECTA": (
        "La dirección registrada presenta inconsistencias",
        True
    ),
    "ACCESO_RESTRINGIDO": (
        "No fue posible acceder al lugar de entrega",
        True
    ),
    "REPROGRAMACION": (
        "La entrega fue reprogramada",
        True
    ),
    "RETRASO_OPERATIVO": (
        "Se presentó un retraso durante la operación",
        False
    ),
    "OBSERVACION_ENTREGA": (
        "Se registró una observación durante la entrega",
        False
    )
}


# CAMPOS
campos = [
    "id_novedad",
    "id_envio",
    "fec_novedad",
    "tip_novedad",
    "desc_novedad",
    "id_agente_registro",
    "requiere_accion"
]


# CARGAR ENVÍOS CANDIDATOS
# Priorizamos envíos con dificultades de entrega.

envios_con_dificultades = []
envios_normales = []

with open(ruta_envios, newline="", encoding="utf-8") as archivo:

    lector = csv.DictReader(archivo)

    for envio in lector:

        datos = (
            int(envio["id_envio"]),
            date.fromisoformat(envio["fec_recepcion"]),
            date.fromisoformat(envio["fec_intento1"]),
            envio["estado_final"]
        )

        if envio["resultado_intento1"] == "Fallido":
            envios_con_dificultades.append(datos)
        else:
            envios_normales.append(datos)


# 80 % de novedades asociadas a envíos con dificultades
cantidad_dificultades = min(
    int(TOTAL_NOVEDADES * 0.80),
    len(envios_con_dificultades)
)

cantidad_normales = TOTAL_NOVEDADES - cantidad_dificultades

if cantidad_normales > len(envios_normales):
    raise ValueError(
        "No hay suficientes envíos para generar novedades únicas."
    )


seleccionados = (
    random.sample(
        envios_con_dificultades,
        cantidad_dificultades
    )
    +
    random.sample(
        envios_normales,
        cantidad_normales
    )
)

random.shuffle(seleccionados)


# GENERACIÓN
with open(
    ruta_novedades,
    mode="w",
    newline="",
    encoding="utf-8"
) as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=campos
    )

    escritor.writeheader()

    for i, (
        id_envio,
        fecha_recepcion,
        fecha_intento1,
        estado_final
    ) in enumerate(seleccionados, start=1):

        # Fecha entre recepción y primer intento
        dias = (fecha_intento1 - fecha_recepcion).days

        fecha_novedad = fecha_recepcion + timedelta(
            days=random.randint(0, max(0, dias))
        )

        tipo_novedad = random.choice(
            list(catalogo_novedades.keys())
        )

        descripcion, requiere_accion = catalogo_novedades[
            tipo_novedad
        ]

        nueva_novedad = {
            "id_novedad": i,
            "id_envio": id_envio,
            "fec_novedad": fecha_novedad,
            "tip_novedad": tipo_novedad,
            "desc_novedad": descripcion,
            "id_agente_registro": random.randint(1, 50),
            "requiere_accion": requiere_accion
        }

        escritor.writerow(nueva_novedad)

        if i % 25000 == 0:
            print(
                f"Novedades generadas: "
                f"{i:,} / {TOTAL_NOVEDADES:,}"
            )

print("Generación de novedades completada.")