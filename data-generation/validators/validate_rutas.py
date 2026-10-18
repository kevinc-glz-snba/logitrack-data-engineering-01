import csv

carpeta = "data/raw/"

with open(carpeta + "ope_conductores.csv", encoding="utf-8") as archivo:
    bicicletas = {
        int(fila["cond_id"])
        for fila in csv.DictReader(archivo)
        if fila["tip_vehiculo"] == "Bicicleta"
    }

total_bicicletas = 0
errores = 0

with open(carpeta + "gps_rutas.csv", encoding="utf-8") as archivo:
    for ruta in csv.DictReader(archivo):

        if int(ruta["cond_id"]) in bicicletas:
            total_bicicletas += 1

            if float(ruta["consumo_combustible"]) != 0:
                errores += 1

print(f"Rutas realizadas en bicicleta: {total_bicicletas}")
print(f"Inconsistencias de combustible: {errores}")