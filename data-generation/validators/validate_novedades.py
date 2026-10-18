import csv

from datetime import date

from utils.obtener_ruta_raw import obtener_ruta_raw


carpeta = obtener_ruta_raw()

envios = {}

with open(
    carpeta / "tms_envios.csv",
    newline="",
    encoding="utf-8"
) as archivo:

    for fila in csv.DictReader(archivo):
        envios[int(fila["id_envio"])] = (
            date.fromisoformat(fila["fec_recepcion"]),
            date.fromisoformat(fila["fec_intento1"])
        )


total = 0
errores = 0
ids_novedades = set()

with open(
    carpeta / "dir_novedades.csv",
    newline="",
    encoding="utf-8"
) as archivo:

    for novedad in csv.DictReader(archivo):

        total += 1

        id_novedad = int(novedad["id_novedad"])
        id_envio = int(novedad["id_envio"])

        if id_novedad in ids_novedades:
            errores += 1

        ids_novedades.add(id_novedad)

        if id_envio not in envios:
            errores += 1
            continue

        fecha_recepcion, fecha_intento1 = envios[id_envio]

        fecha_novedad = date.fromisoformat(
            novedad["fec_novedad"]
        )

        if not fecha_recepcion <= fecha_novedad <= fecha_intento1:
            errores += 1

        if not novedad["tip_novedad"]:
            errores += 1

        if not novedad["desc_novedad"]:
            errores += 1

        if novedad["requiere_accion"] not in ("True", "False"):
            errores += 1


print("=" * 50)
print("VALIDACIÓN DE DIR_NOVEDADES")
print("=" * 50)
print(f"Novedades: {total}")
print(f"Inconsistencias: {errores}")