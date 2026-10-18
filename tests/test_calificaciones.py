import sys
from pathlib import Path

import pandas as pd

# Permitir importar nuestro módulo Silver
sys.path.insert(0, str(Path("pipelines/silver").resolve()))

from pipelines.silver.clean_calificaciones import limpiar_calificaciones


def main():
    # Leer un archivo Bronze original
    archivo = next(
        Path("data/bronze/cal_destinatarios").rglob("*.parquet")
    )

    # Tomar 10 registros válidos
    df = pd.read_parquet(archivo).head(10).copy()

    # Introducir tres errores controlados
    df.loc[0, "puntaje_1_5"] = 8
    df.loc[1, "id_envio"] = None
    df.loc[2, "id_calificacion"] = df.loc[3, "id_calificacion"]

    # Ejecutar nuestra transformación
    validos, rechazados = limpiar_calificaciones(df)

    # Guardar evidencia de los errores detectados
    directorio_errores = Path("data/errors")
    directorio_errores.mkdir(parents=True, exist_ok=True)

    rechazados.to_parquet(
        directorio_errores / "calificaciones_rechazadas_prueba.parquet",
        index=False,
)
    # Verificar resultados
    assert len(df) == 10, "Cantidad de entrada incorrecta"
    assert len(validos) == 7, "Se esperaban 7 registros válidos"
    assert len(rechazados) == 3, "Se esperaban 3 rechazos"

    assert rechazados["motivo_rechazo"].str.contains(
        "puntaje invalido"
    ).any(), "No se detectó el puntaje inválido"

    assert rechazados["motivo_rechazo"].str.contains(
        "id_envio nulo"
    ).any(), "No se detectó el envío nulo"

    assert rechazados["motivo_rechazo"].str.contains(
        "id_calificacion duplicado"
    ).any(), "No se detectó el duplicado"

    print("Registros de prueba:", len(df))
    print("Registros válidos:", len(validos))
    print("Registros rechazados:", len(rechazados))

    print("\nMotivos de rechazo:")
    print(rechazados[["id_calificacion", "motivo_rechazo"]].to_string(index=False))

    print("\nPRUEBA SUPERADA")


if __name__ == "__main__":
    main()