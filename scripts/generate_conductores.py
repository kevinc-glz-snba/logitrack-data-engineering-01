from faker import Faker
import random
from pathlib import Path
import csv
import hashlib
from datetime import date

fake = Faker("es_CO")

#Ruta para guardar el archivo CSV

BASE_DIR = Path(__file__).resolve().parent.parent
ruta_carpeta = BASE_DIR / "data" / "raw"
ruta_carpeta.mkdir(parents=True, exist_ok=True)
ruta_csv = ruta_carpeta / "ope_conductores.csv"

#Semillas
random.seed(42)
fake.seed_instance(42)

# Datos predefinidos
vehiculos = [
    "moto",
    "bicicleta",
    "van",
    "camion",
]

ciudades = {
    "Bogotá": 1,
    "Barranquilla": 2,
    "Medellín": 3,
    "Bucaramanga": 4,
    "Pereira": 5,
    "Manizales": 6,
    "Cartagena": 7,
    "Santa Marta": 8,
    "Cucutá": 9,
}

tipo_documento = [
    "Licencia_Conducir",
    "Cedula_Ciudadania",
]

# Campos de la tabla conductores
campos = [
    "cond_id",
    "nombre_cond", 
    "apellido_cond", 
    "tipo_doc", 
    "num_doc_hash", 
    "fec_ingreso", 
    "id_ciudad_base", 
    "tipo_vehiculo", 
    "cod_zona_asignada", 
    "activo", 
    "calificacion"
]

total_conductores = 0

datos = []


# Generación de datos para la tabla conductores
for con in range(50):

    cond_id = con + 1
    nombre_cond = fake.first_name()
    apellido_cond = fake.last_name()
    tipo_doc = random.choice(tipo_documento)
    num_doc_hash = hashlib.sha256(str(fake.random_int(min=10000000, max=99999999)).encode()).hexdigest()
    fec_ingreso = fake.date_between(start_date= date(2025, 1, 1), end_date= date(2025, 12, 31))
    id_ciudad_base = random.choice(list(ciudades.values()))
    tipo_vehiculo = random.choice(vehiculos)
    cod_zona_asignada = random.randint(1, 30)
    activo = random.choices(population=[True, False], weights=[85, 15],k=1)[0]  # 85% de probabilidad de ser True
    calificacion = round(random.uniform(1.0, 5.0), 2)

    # Crear un diccionario para cada conductor generado
    new_conductor = {
        "cond_id": cond_id,
        "nombre_cond": nombre_cond,
        "apellido_cond": apellido_cond,
        "tipo_doc": tipo_doc,
        "num_doc_hash": num_doc_hash,
        "fec_ingreso": fec_ingreso,
        "id_ciudad_base": id_ciudad_base,
        "tipo_vehiculo": tipo_vehiculo,
        "cod_zona_asignada": cod_zona_asignada,
        "activo": activo,
        "calificacion": calificacion
    }

    datos.append(new_conductor)


print(f"Total de conductores generados: {len(datos)}")

with open(f"{ruta_csv}", mode = "w", newline = "", encoding="utf-8") as file:
    escritor = csv.DictWriter(file, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(datos)

print( "Archivo 'ope_conductores.csv' generado con éxito.")