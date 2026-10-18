from faker import Faker
import random
import csv

from utils.catalogo_ciudades import ciudades
from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.configuration import cargar_configuracion

fake = Faker("es_CO")
config = cargar_configuracion()
TOTAL_REMITENTES = config["volumenes"]["cli_remitentes"]

#Ruta de csv
carpeta = obtener_ruta_raw()
ruta_csv = carpeta / "cli_remitentes.csv"

#Semillas
SEMILLA = config["semilla"]
random.seed(SEMILLA)
fake.seed_instance(SEMILLA)


#campos tabla
campos = [
    "id_remitente",
    "razon_social",
    "tipo_cliente",
    "ciudad_principal",
    "sla_entrega_horas",
    "penalidad_porc",
    "activo" 
]

#datos predefinidios
tipos_cliente = [
    "Ecommerce",
    "Farmaceutico",
    "Retail",
    "Telecomunicaciones",
    "Otro"
]

datos = []

for remitente in range(TOTAL_REMITENTES):
    id_remitente = remitente + 1
    razon_social = fake.company()
    tipo_cliente = random.choice(tipos_cliente)
    ciudad_principal = ciudades[random.choice(list(ciudades.keys()))][0]
    sla_entrega_horas = 24
    penalidad_porc = round(random.uniform(2.0, 8.0), 2)
    activo = random.choices(population=[True, False], weights=[90, 10], k=1)[0]

    #Registro de remitente
    new_remitente = {
        "id_remitente": id_remitente,
        "razon_social": razon_social,
        "tipo_cliente": tipo_cliente,
        "ciudad_principal": ciudad_principal,
        "sla_entrega_horas": sla_entrega_horas,
        "penalidad_porc" : penalidad_porc,
        "activo": activo
    }

    datos.append(new_remitente)

print(f"Total de remitentes generados: {len(datos)}")

#Exportacion a CSV
with open(ruta_csv, mode="w", newline="", encoding="utf-8") as file:
    escritor = csv.DictWriter(file, fieldnames=campos)

    escritor.writeheader()
    escritor.writerows(datos)

print("Archivo 'cli_remitentes' generado con éxito.")