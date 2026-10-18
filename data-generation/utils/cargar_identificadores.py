import csv

def cargar_identificadores(ruta_csv, columna_id):
    identificadores = []

    with open(ruta_csv, newline="", encoding="utf-8") as file:

        lector = csv.DictReader(file)

        for fila in lector:
            identificadores.append(int(fila[columna_id]))
    
    return identificadores