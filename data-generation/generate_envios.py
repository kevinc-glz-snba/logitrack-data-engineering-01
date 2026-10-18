from datetime import date, datetime, time, timedelta
import random
import csv

from utils.configuration import cargar_configuracion
from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.reglas_entrega import (
    calcular_fecha_programada,
    simular_intentos_entrega
)
from utils.cargar_identificadores import cargar_identificadores

#Cargamos configuracion
config = cargar_configuracion()

SEMILLA = config["semilla"]

FECHA_INICIO = date.fromisoformat(config["fecha_inicio"])
FECHA_FIN = date.fromisoformat(config["fecha_fin"])
TOTAL_ENVIOS = config["volumenes"]["tms_envios"]

carpeta = obtener_ruta_raw()
ruta_csv = carpeta / "tms_envios.csv"

random.seed(SEMILLA)

#Datos predefinidos
tipo_paquete = [
    "Documento",
    "Pequeno",
    "Mediano",
    "Grande"
]

campos = [
    "id_envio",
    "id_remitente",
    "cond_id",
    "id_zona_destino",
    "tip_paquete",
    "peso_kg",
    "fec_recepcion",
    "hra_recepcion",
    "fec_entrega_programada",
    "fec_intento1",
    "hra_intento1",
    "resultado_intento1",
    "fec_intento2",
    "hra_intento2",
    "resultado_intento2",
    "fec_entrega_real",
    "estado_final",
    "motivo_fallo_cod",
    "vr_declarado"
]

#Cargamos identificadores
ids_remitentes = cargar_identificadores(
    carpeta / "cli_remitentes.csv",
    "id_remitente"
)

ids_conductores = cargar_identificadores(
    carpeta / "ope_conductores.csv",
    "cond_id"
)

ids_zonas = cargar_identificadores(
    carpeta / "geo_zonas.csv",
    "id_zona"
)

#Obtenemmos fecha aleatoria 
dias_disponibles = (FECHA_FIN - FECHA_INICIO).days

with open (ruta_csv, mode="w", newline="", encoding="utf-8") as file:
    escritor = csv.DictWriter(
        file,
        fieldnames=campos
    )

    escritor.writeheader()

    for env in range(TOTAL_ENVIOS):
        
        fecha_recepcion = FECHA_INICIO + timedelta(
            days = random.randint(0, dias_disponibles)
        )
        #Recepcion unicamente en dias habiles
        while fecha_recepcion.weekday() >= 5:
            fecha_recepcion = FECHA_INICIO + timedelta(
                days = random.randint(0, dias_disponibles)
            )

        hora_recepcion = time(
            hour= random.randint(6, 16),
            minute=random.randint(0, 59)
        )

        fecha_programada = calcular_fecha_programada(
            fecha_recepcion,
            hora_recepcion
        )

        intentos = simular_intentos_entrega(
            fecha_programada,
            fecha_recepcion,
            hora_recepcion
        )


        id_remitente = random.choice(ids_remitentes)
        cond_id = random.choice(ids_conductores)
        id_zona_destino = random.choice(ids_zonas)

        #Tipo de paquete
        tip_paquete = random.choice(tipo_paquete)
        peso_kg = round(random.uniform(0.1, 30.0), 2)
        vr_declarado = round(random.uniform(10000, 2000000), 2)

        nuevo_envio = {
            "id_envio": env + 1,
            "id_remitente": id_remitente,
            "cond_id": cond_id,
            "id_zona_destino": id_zona_destino,
            "tip_paquete": tip_paquete,
            "peso_kg": peso_kg,
            "fec_recepcion": fecha_recepcion,
            "hra_recepcion": hora_recepcion,
            "fec_entrega_programada": fecha_programada,
            "fec_intento1": intentos["fec_intento1"],
            "hra_intento1": intentos["hra_intento1"],
            "resultado_intento1": intentos["resultado_intento1"],
            "fec_intento2": intentos["fec_intento2"],
            "hra_intento2": intentos["hra_intento2"],
            "resultado_intento2": intentos["resultado_intento2"],
            "fec_entrega_real": intentos["fec_entrega_real"],
            "estado_final": intentos["estado_final"],
            "motivo_fallo_cod": intentos["motivo_fallo_cod"],
            "vr_declarado": vr_declarado
        }

        escritor.writerow(nuevo_envio)
        if (env + 1) % 100000 == 0:
            print(
                f"Envíos generados: "
                f"{env + 1:,} / {TOTAL_ENVIOS:,}"
            )