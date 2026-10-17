import csv
import sys
from pathlib import Path

#Ruta de aarchivos csv
BASE_DIR = Path(__file__).resolve().parent.parent
ruta_carpeta = BASE_DIR / "data" / "raw"


primary_key_zona = set()
foreing_key_not_exist = []

con_validas = 0

#Lectura y validacion de geo_zonas
try: 
    with open(f"{ruta_carpeta}/geo_zonas.csv", mode = "r", encoding="utf-8-sig") as file:
        lector = csv.DictReader(file)

        for fila in lector:
            primary_key_zona.add(int(fila["id_zona"]))


except FileNotFoundError:
    print(f"No se encontro el archivo de geo_zona en: {ruta_carpeta}")
    sys.exit(1)

except KeyError as e:
    print(f"Falta la columna 'id_zona' en geo_zonas.csv. Detalles: {e}", file=sys.stderr)
    sys.exit(1)
except ValueError:
    print("Se encontró un valor no numérico en la columna 'id_zona'.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado al leer geo_zonas.csv: {e}", file=sys.stderr)
    sys.exit(1)

print("Valores extraídos con éxito de geo_zonas")

try: 
    with open(f"{ruta_carpeta}/ope_conductores.csv", mode = "r", encoding= "utf-8-sig") as file:
        lector = csv.DictReader(file)

        for fila in lector:
            foreig_key = int(fila["cod_zona_asignada"])
            if foreig_key in primary_key_zona:
                con_validas += 1
            else:
                cond_invalidate = {
                    "cond_id" : fila["cond_id"],
                    "cod_zona_asignada" : fila["cod_zona_asignada"]
                }
                foreing_key_not_exist.append(cond_invalidate)

except FileNotFoundError:
    print(f"No se encontró el archivo de conductores en: '{ruta_carpeta}'", file=sys.stderr)
    sys.exit(1)
except KeyError as e:
    print(f"Columnas requeridas ('cod_zona_asignada' o 'cond_id') no encontradas. Detalles: {e}", file=sys.stderr)
    sys.exit(1)
except ValueError:
    print("Se encontró un valor no numérico en 'cod_zona_asignada'.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado al leer ope_conductores.csv: {e}", file=sys.stderr)
    sys.exit(1)

print("Resumen de validación")
print(f"Conductores con codigo de zona asignada existentes: {con_validas}")
print(f"Conductores con codigo de zona asignada no existentes: {len(foreing_key_not_exist)}")

if len(foreing_key_not_exist) > 0:
    print(f" Codigo de zonas no existentes: {foreing_key_not_exist}")
