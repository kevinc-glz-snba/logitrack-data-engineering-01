import csv
import sys

from utils.obtener_ruta_raw import obtener_ruta_raw


# Rutas de archivos CSV
ruta_carpeta = obtener_ruta_raw()

ruta_zonas = ruta_carpeta / "geo_zonas.csv"
ruta_conductores = ruta_carpeta / "ope_conductores.csv"


# Estructuras para validación
zonas = {}

zonas_no_existentes = []
ciudades_no_coincidentes = []

conductores_validos = 0
total_conductores = 0

# 1. LECTURA DE ZONAS

try:
    with open(ruta_zonas, mode="r", encoding="utf-8-sig", newline="") as file:

        lector = csv.DictReader(file)

        # Comprobar que existan las columnas necesarias
        columnas_requeridas = {"id_zona", "id_ciudad"}

        if not columnas_requeridas.issubset(lector.fieldnames or []):
            raise KeyError(
                f"Faltan columnas: {columnas_requeridas - set(lector.fieldnames or [])}"
            )

        for fila in lector:

            id_zona = int(fila["id_zona"])
            id_ciudad = int(fila["id_ciudad"])

            if id_zona in zonas:
                raise ValueError(f"ID de zona duplicado: {id_zona}")

            # Guardamos la relación zona -> ciudad
            zonas[id_zona] = id_ciudad

except FileNotFoundError:
    print(
        f"No se encontró el archivo de zonas: {ruta_zonas}",
        file=sys.stderr
    )
    sys.exit(1)

except (KeyError, ValueError) as e:
    print(f"Error en geo_zonas.csv: {e}", file=sys.stderr)
    sys.exit(1)

except Exception as e:
    print(
        f"Error inesperado al leer geo_zonas.csv: {e}",
        file=sys.stderr
    )
    sys.exit(1)


print(f"Zonas cargadas correctamente: {len(zonas)}")


#VALIDACIÓN DE CONDUCTORES

try:
    with open(
        ruta_conductores,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        lector = csv.DictReader(file)

        columnas_requeridas = {
            "cond_id",
            "cod_zona_asignada",
            "id_ciudad_base"
        }

        if not columnas_requeridas.issubset(lector.fieldnames or []):
            raise KeyError(
                f"Faltan columnas: {columnas_requeridas - set(lector.fieldnames or [])}"
            )

        for fila in lector:

            total_conductores += 1

            cond_id = int(fila["cond_id"])
            id_zona = int(fila["cod_zona_asignada"])
            id_ciudad_base = int(fila["id_ciudad_base"])

            # Validación 1: la zona debe existir
            if id_zona not in zonas:

                zonas_no_existentes.append({
                    "cond_id": cond_id,
                    "cod_zona_asignada": id_zona
                })

                continue

            # Validación 2: la ciudad debe coincidir
            id_ciudad_zona = zonas[id_zona]

            if id_ciudad_base != id_ciudad_zona:

                ciudades_no_coincidentes.append({
                    "cond_id": cond_id,
                    "id_ciudad_base": id_ciudad_base,
                    "cod_zona_asignada": id_zona,
                    "id_ciudad_zona": id_ciudad_zona
                })

                continue

            # El conductor superó ambas validaciones
            conductores_validos += 1

except FileNotFoundError:
    print(
        f"No se encontró el archivo de conductores: {ruta_conductores}",
        file=sys.stderr
    )
    sys.exit(1)

except (KeyError, ValueError) as e:
    print(f"Error en ope_conductores.csv: {e}", file=sys.stderr)
    sys.exit(1)

except Exception as e:
    print(
        f"Error inesperado al leer ope_conductores.csv: {e}",
        file=sys.stderr
    )
    sys.exit(1)


#RESUMEN DE VALIDACIÓN

print("\n========== RESUMEN DE VALIDACIÓN ==========")

print(f"Total de zonas: {len(zonas)}")
print(f"Total de conductores: {total_conductores}")

print(f"Conductores válidos: {conductores_validos}")

print(
    f"Conductores con zonas inexistentes: "
    f"{len(zonas_no_existentes)}"
)

print(
    f"Conductores con ciudades inconsistentes: "
    f"{len(ciudades_no_coincidentes)}"
)

#DETALLE DE ERRORES

if zonas_no_existentes:

    print("\nZonas inexistentes:")

    for error in zonas_no_existentes[:10]:
        print(error)


if ciudades_no_coincidentes:

    print("\nCiudades inconsistentes:")

    for error in ciudades_no_coincidentes[:10]:
        print(error)


#RESULTADO FINAL

if zonas_no_existentes or ciudades_no_coincidentes:

    print("\nVALIDACIÓN FALLIDA")

    sys.exit(1)

else:

    print("\nVALIDACIÓN EXITOSA")

    sys.exit(0)