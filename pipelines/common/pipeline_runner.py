import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from pipelines.common.error_logger import registrar_error


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def ejecutar_pipeline(capa: str, modulo: str, batch_id: str | None = None) -> bool:
    """
    Ejecuta un módulo Python y registra sus fallos.

    Devuelve True cuando termina correctamente.
    Devuelve False cuando falla.
    """

    print(f"\nIniciando: {modulo}", flush=True)

    try:
        resultado = subprocess.run(
            [sys.executable, "-m", modulo],
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            check=True,
        )

        print(f"PASS: {modulo}", flush=True)
        return True

    except subprocess.CalledProcessError as error:
        print(
            f"FAIL: {modulo} | Código de salida: {error.returncode}",
            flush=True,
        )

        registrado = registrar_error(
            capa=capa,
            proceso=modulo,
            excepcion=error,
            batch_id=batch_id,
        )

        print(
            f"Error registrado en PostgreSQL: {registrado}",
            flush=True,
        )

        return False

    except Exception as error:
        print(f"FAIL: {modulo} | {error}", flush=True)

        registrado = registrar_error(
            capa=capa,
            proceso=modulo,
            excepcion=error,
            batch_id=batch_id,
        )

        print(
            f"Error registrado en PostgreSQL: {registrado}",
            flush=True,
        )

        return False


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--capa",
        required=True,
        choices=["BRONZE", "SILVER", "GOLD"],
    )

    parser.add_argument(
        "--modulo",
        required=True,
    )

    parser.add_argument(
        "--batch-id",
        default=None,
    )

    argumentos = parser.parse_args()

    # Compatibilidad con la configuración PostgreSQL del proyecto.
    if not os.getenv("PGPASSWORD") and os.getenv("POSTGRES_PASSWORD"):
        os.environ["PGPASSWORD"] = os.environ["POSTGRES_PASSWORD"]

    exitoso = ejecutar_pipeline(
        capa=argumentos.capa,
        modulo=argumentos.modulo,
        batch_id=argumentos.batch_id,
    )

    sys.exit(0 if exitoso else 1)


if __name__ == "__main__":
    main()
