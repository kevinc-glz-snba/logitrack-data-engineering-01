import csv
from datetime import date

carpeta = "data/raw/"

envios_entregados = {}

with open(carpeta + "tms_envios.csv", encoding="utf-8") as archivo:
    for fila in csv.DictReader(archivo):
        if fila["estado_final"] == "Entregado":
            envios_entregados[int(fila["id_envio"])] = date.fromisoformat(
                fila["fec_entrega_real"]
            )

total = 0
errores = 0
comentarios_nulos = 0
ids_calificaciones = set()
envios_calificados = set()

with open(carpeta + "cal_destinatarios.csv", encoding="utf-8") as archivo:
    for fila in csv.DictReader(archivo):
        total += 1

        id_calificacion = int(fila["id_calificacion"])
        id_envio = int(fila["id_envio"])
        puntaje = int(fila["puntaje_1_5"])
        fecha = date.fromisoformat(fila["fec_calificacion"])

        if id_calificacion in ids_calificaciones:
            errores += 1
        ids_calificaciones.add(id_calificacion)

        if id_envio in envios_calificados:
            errores += 1
        envios_calificados.add(id_envio)

        if id_envio not in envios_entregados:
            errores += 1
        elif fecha < envios_entregados[id_envio]:
            errores += 1

        if not 1 <= puntaje <= 5:
            errores += 1

        if not fila["comentario_texto"]:
            comentarios_nulos += 1

print(f"Calificaciones: {total}")
print(f"Inconsistencias: {errores}")
print(f"Comentarios nulos: {comentarios_nulos}")
print(f"Porcentaje de nulos: {comentarios_nulos / total * 100:.2f}%")
