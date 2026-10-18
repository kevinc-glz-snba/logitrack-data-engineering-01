from datetime import datetime, timedelta, time
import random

#=====================================================================
# CALCULAR PROXIMO DIA HABIL
def siguiente_dia_habil(fecha):
    fecha += timedelta(days=1)

    while fecha.weekday() >= 5:
        fecha += timedelta(days=1)

    return fecha 


# CALCULAR FECHA PARA PROGRAMAR ENTREGA
def calcular_fecha_programada(fecha_recepcion, hora_recepcion):
    hora_corte = time(10,0)

    if hora_recepcion < hora_corte:
        return fecha_recepcion

    return siguiente_dia_habil(fecha_recepcion)
#=====================================================================

#=====================================================================
#REGLA DE SIMULACION DE INTENTOS DE ENTREGA
def simular_intentos_entrega(fecha_programada, fecha_recepcion, hora_recepcion):
    
    #Seleccion de escenario
    escenario = random.choices(
    population=[
        "primer_intento",
        "segundo_intento",
        "fallido"
    ],
    weights=[80, 15, 5],
    k=1
    )[0]

    hora_intento1 = time(
        hour=random.randint(8, 17),
        minute=random.randint(0, 59)
    )

    #La hora de entrega del mismo dia de recpcion no puede
    #ser menor a la hora de recepcion
    if fecha_programada == fecha_recepcion:
        hora_minima = (
            datetime.combine(fecha_recepcion, hora_recepcion)
            + timedelta(minutes=30)
        ).time()

        if hora_intento1 <= hora_minima:
            hora_intento1 = hora_minima

    hora_intento2 = time(
        hour=random.randint(8, 17),
        minute=random.randint(0, 59)
    )

    fecha_intento2 = siguiente_dia_habil(fecha_programada)

    motivo_fallo = [
        "DESTINATARIO_AUSENTE",
        "DIRECCION_INCORRECTA",
        "RECHAZADO",
        "ACCESO_RESTRINGIDO"
    ]

    if escenario == "primer_intento":
        return {
            "fec_intento1": fecha_programada,
            "hra_intento1": hora_intento1,
            "resultado_intento1": "Exitoso",
            "fec_intento2": None,
            "hra_intento2": None,
            "resultado_intento2": None,
            "fec_entrega_real": fecha_programada,
            "estado_final": "Entregado",
            "motivo_fallo_cod": None
        }

    elif escenario == "segundo_intento":

        return  {
            "fec_intento1": fecha_programada,
            "hra_intento1": hora_intento1,
            "resultado_intento1": "Fallido",
            "fec_intento2": fecha_intento2,
            "hra_intento2": hora_intento2,
            "resultado_intento2": "Exitoso",
            "fec_entrega_real": fecha_intento2,
            "estado_final": "Entregado",
            "motivo_fallo_cod": None
        }

    elif escenario == "fallido":
        motivo_fallo_cod = random.choice(motivo_fallo)

        return {
            "fec_intento1": fecha_programada,
            "hra_intento1": hora_intento1,
            "resultado_intento1": "Fallido",
            "fec_intento2": fecha_intento2,
            "hra_intento2": hora_intento2,
            "resultado_intento2": "Fallido",
            "fec_entrega_real": None,
            "estado_final": "Fallido",
            "motivo_fallo_cod": motivo_fallo_cod
        }
