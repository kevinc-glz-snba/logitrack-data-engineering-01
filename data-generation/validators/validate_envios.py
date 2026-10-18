import csv
import sys 

from datetime import date, time, datetime

from utils.obtener_ruta_raw import obtener_ruta_raw
from utils.cargar_identificadores import cargar_identificadores
from utils.reglas_entrega import calcular_fecha_programada

carpeta = obtener_ruta_raw()

ruta_envios = carpeta / "tms_envios.csv"


ids_remitentes = set(cargar_identificadores(
    carpeta / "cli_remitentes.csv",
    "id_remitente"
))

ids_conductores = set(cargar_identificadores(
    carpeta / "ope_conductores.csv",
    "cond_id"
))

ids_zonas = set(cargar_identificadores(
    carpeta / "geo_zonas.csv",
    "id_zona"
))

#Leer envios de forma incremental 
errores = 0
total_envios = 0
ids_envios = set()

with open(ruta_envios, newline="", encoding="utf-8") as file:
    lector = csv.DictReader(file)

    for envio in lector:
        total_envios += 1

        #VALIDACION DE CLAVES UNICAS
        id_envio = int(envio["id_envio"])

        if id_envio in ids_envios:
            errores += 1
            print(f"Envío {id_envio}: identificador duplicado")
        else:
            ids_envios.add(id_envio)
        
        #VALIDACION DE CLAVES FORANEAS

        id_remitente = int(envio["id_remitente"])
        cond_id = int(envio["cond_id"])
        id_zona_destino = int(envio["id_zona_destino"])

        if id_remitente not in ids_remitentes:
            errores += 1
            print(f"Envio {id_envio}: remitente inexistente")

        if cond_id not in ids_conductores:
            errores += 1
            print(f"Envío {id_envio}: conductor inexistente")

        if id_zona_destino not in ids_zonas:
            errores += 1
            print(f"Envío {id_envio}: zona inexistente")

        #VALIDACION DE FECHAS PROGRAMADAS
        fecha_recepcion = date.fromisoformat(
            envio["fec_recepcion"]
        )

        hora_recepcion = time.fromisoformat(
            envio["hra_recepcion"]
        )

        fecha_programada = date.fromisoformat(
            envio["fec_entrega_programada"]
        )

        fecha_esperada = calcular_fecha_programada(
            fecha_recepcion,
            hora_recepcion
        )

        if fecha_programada != fecha_esperada:
            errores += 1
            print(f"Envío {id_envio}: fecha programada incorrecta")


        #VALIDACION DE LA CRONOLOGIA DE LOS INTENTOS
        intento1 = None
        intento2 = None

        fecha_intento1 = (
            date.fromisoformat(envio["fec_intento1"])
            if envio["fec_intento1"]
            else None
        )

        fecha_intento2 = (
            date.fromisoformat(envio["fec_intento2"])
            if envio["fec_intento2"]
            else None
        )

        fecha_entrega_real = (
            date.fromisoformat(envio["fec_entrega_real"])
            if envio["fec_entrega_real"]
            else None
        )

        hora_intento1 = (
            time.fromisoformat(envio["hra_intento1"])
            if envio["hra_intento1"]
            else None
        )

        hora_intento2 = (
            time.fromisoformat(envio["hra_intento2"])
            if envio["hra_intento2"]
            else None
        )

        recepcion = datetime.combine(
            fecha_recepcion,
            hora_recepcion
        )

        if (fecha_intento1 is None) != (hora_intento1 is None):
            errores += 1
            print(f"Envío {id_envio}: primer intento incompleto")

        if (fecha_intento2 is None) != (hora_intento2 is None):
            errores += 1
            print(f"Envío {id_envio}: segundo intento incompleto")

        if fecha_intento1 is not None and hora_intento1 is not None:
            intento1 = datetime.combine(
                fecha_intento1,
                hora_intento1
            )

            if intento1 <= recepcion:
                errores += 1
                print(f"Envío {id_envio}: intento anterior a recepción")

        if fecha_intento2 is not None and hora_intento2 is not None:
            intento2 = datetime.combine(
                fecha_intento2,
                hora_intento2
            )

            if intento1 is None:
                errores += 1
                print(f"Envío {id_envio}: segundo intento sin primero")

            elif intento2 <= intento1:
                errores += 1
                print(f"Envío {id_envio}: cronología incorrecta")

        #VALIDACION DE ESTADOS FINALES
        if envio["estado_final"] == "Entregado":

            if fecha_entrega_real is None:
                errores += 1
                print(f"Envío {id_envio}: fecha de entrega real vacia")

            if envio["motivo_fallo_cod"]:
                errores += 1
                print(f"Envío {id_envio}: cuenta con mitivo de fallo")

        elif envio["estado_final"] == "Fallido":

            if fecha_entrega_real is not None:
                errores += 1
                print(f"Envío {id_envio}: Cuenta con fecha de entrega y el estado final es Fallido")

            if not envio["motivo_fallo_cod"]:
                errores += 1
                print(f"Envío {id_envio}: La entrega fallo y no tiene codigo de mitovo de fallo")

        else:
            errores += 1
            print(f"Envío {id_envio}: estado desconocido")

        #Entrega en primer intetno
        if envio["resultado_intento1"] == "Exitoso":

            if fecha_entrega_real != fecha_intento1:
                errores += 1
                print(f"Envío {id_envio}: la entrega se hizo en el intento uno pero fecha de entrega real no coincide")

            if any([
                fecha_intento2 is not None,
                hora_intento2 is not None,
                bool(envio["resultado_intento2"])
            ]):
                errores += 1
                print(f"Envío {id_envio}: Entrega echo en intento uno pero intetno dos tiene datos")

            if envio["estado_final"] != "Entregado":
                errores += 1
                print(f"Envío {id_envio}: El paquete fue entregado pero su estado final es diferente")

        #Entrega en segundo intento
        elif (
            envio["resultado_intento1"] == "Fallido"
            and envio["resultado_intento2"] == "Exitoso"
        ):

            if fecha_entrega_real != fecha_intento2:
                errores += 1
                print(f"Envío {id_envio}: cronología incorrecta intento 2")

            if envio["estado_final"] != "Entregado":
                errores += 1
                print(f"Envío {id_envio}: Estado final erroneo, entrega en inteto dos")

        #Ambos intentos fallidos
        elif (
            envio["resultado_intento1"] == "Fallido"
            and envio["resultado_intento2"] == "Fallido"
        ):

            if fecha_entrega_real is not None:
                errores += 1
                print(f"Envío {id_envio}: cronología incorrecta: Ambos intentos fallaron")

            if envio["estado_final"] != "Fallido":
                errores += 1
                print(f"Envío {id_envio}: cronología incorrecta. Estado final incorrecto")

        else:
            errores += 1
            print(
                f"Envío {id_envio}: "
                "combinación de resultados de intentos inválida"
            )

        #VALIDACION DE VALORES NUMERICOS 
        peso_kg = float(envio["peso_kg"])
        vr_declarado = float(envio["vr_declarado"])

        if peso_kg <= 0:
            errores += 1
            print(f"Envío {id_envio}: El peso del paquete es invalido")

        if vr_declarado <= 0:
            errores += 1
            print(f"Envío {id_envio}: El valor declarado es invalido")

#RESULTADOS DE PRUEBAS
print("=" * 50)
print("VALIDACIÓN DE TMS_ENVIOS")
print("=" * 50)
print(f"Total de envíos: {total_envios}")
print(f"Inconsistencias encontradas: {errores}")

# CÓDIGO DE SALIDA
sys.exit(1 if errores > 0 else 0)