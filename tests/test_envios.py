import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path("pipelines/silver").resolve()))

from pipelines.silver.clean_envios import limpiar_envios


def main():
    # Leer un archivo Bronze
    archivo = next(
        Path("data/bronze/tms_envios").rglob("*.parquet")
    )

    # Seleccionar 10 registros válidos
    df = pd.read_parquet(archivo).head(10).copy()
    df = df.reset_index(drop=True)

    # Introducir cuatro anomalías
    df.loc[0, "peso_kg"] = -5
    df.loc[1, "estado_final"] = "Desconocido"

    df.loc[2, "estado_final"] = "Entregado"
    df.loc[2, "fec_entrega_real"] = None

    df.loc[3, "id_envio"] = df.loc[4, "id_envio"]

    # Ejecutar la limpieza
    ids_procesados = set()

    validos, rechazados = limpiar_envios(
        df,
        ids_procesados,
    )

    # Verificar resultados
    assert len(validos) == 6, "Se esperaban 6 registros válidos"
    assert len(rechazados) == 4, "Se esperaban 4 rechazos"

    motivos = rechazados["motivo_rechazo"]

    assert motivos.str.contains("peso invalido").any()
    assert motivos.str.contains("estado_final invalido").any()
    assert motivos.str.contains("entregado sin fecha real").any()
    assert motivos.str.contains("id_envio duplicado").any()

    # Guardar evidencia de prueba
    directorio = Path("data/errors")
    directorio.mkdir(parents=True, exist_ok=True)

    rechazados.to_parquet(
        directorio / "envios_rechazados_prueba.parquet",
        index=False,
    )

    print("Registros de prueba:", len(df))
    print("Registros válidos:", len(validos))
    print("Registros rechazados:", len(rechazados))

    print("\nMotivos de rechazo:")
    print(
        rechazados[
            ["id_envio", "motivo_rechazo"]
        ].to_string(index=False)
    )

    print("\nPRUEBA SUPERADA")


if __name__ == "__main__":
    main()