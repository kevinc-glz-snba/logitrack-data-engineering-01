import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT))

from pipelines.common.error_logger import registrar_error


def main():
    print("\nPRUEBA DE REGISTRO DE ERRORES\n")

    try:
        # Error provocado intencionalmente.
        resultado = 10 / 0

    except ZeroDivisionError as error:

        registrado = registrar_error(
            capa="GOLD",
            proceso="test_pipeline_error_logger",
            excepcion=error,
            batch_id="TEST_ERROR_001",
        )

        if not registrado:
            raise RuntimeError(
                "La excepción no pudo registrarse "
                "en PostgreSQL"
            )

        print("Excepción capturada correctamente")
        print("Tipo: ZeroDivisionError")
        print("Capa: GOLD")
        print("Batch: TEST_ERROR_001")
        print("Registro enviado a PostgreSQL")

    print("\nPRUEBA FINALIZADA CORRECTAMENTE")


if __name__ == "__main__":
    main()
