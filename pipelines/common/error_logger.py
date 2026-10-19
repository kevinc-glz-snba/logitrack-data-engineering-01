import os
import logging

import psycopg


logger = logging.getLogger(__name__)


def registrar_error(
    capa: str,
    proceso: str,
    excepcion: Exception,
    batch_id: str | None = None,
) -> bool:
    """
    Registra una excepción en PostgreSQL.

    Devuelve True si el registro fue exitoso.
    Devuelve False si no pudo registrarse.
    """

    sql = """
        INSERT INTO pipeline_error_log (
            capa,
            proceso,
            tipo_error,
            mensaje_error,
            batch_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    try:
        with psycopg.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=int(os.getenv("PGPORT", "5432")),
            dbname=os.getenv("PGDATABASE", "logitrack"),
            user=os.getenv("PGUSER", "logitrack_user"),
            password=os.environ["PGPASSWORD"],
        ) as conexion:

            with conexion.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        capa.upper(),
                        proceso,
                        type(excepcion).__name__,
                        str(excepcion),
                        batch_id,
                    ),
                )

        logger.info(
            "Error registrado correctamente: %s",
            proceso,
        )

        return True

    except Exception:
        logger.exception(
            "No fue posible registrar el error "
            "del proceso %s en PostgreSQL",
            proceso,
        )

        return False
