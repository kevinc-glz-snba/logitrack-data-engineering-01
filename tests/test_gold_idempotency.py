import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT / "data" / "gold"

MODULOS = [
    "pipelines.gold.build_dim_conductores",
    "pipelines.gold.build_dim_remitentes",
    "pipelines.gold.build_dim_zonas",
    "pipelines.gold.build_fact_envios",
    "pipelines.gold.build_fact_rutas",
    "pipelines.gold.build_fact_desempeno_conductor",
    "pipelines.gold.build_fact_trazabilidad_envio",
    "pipelines.gold.build_fact_alertas_zona",
    "pipelines.gold.aggregations.build_aggregations",
    "pipelines.gold.aggregations.build_kpi_ejecutivo",
]


def calcular_hash(archivo):
    sha256 = hashlib.sha256()

    with open(archivo, "rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(bloque)

    return sha256.hexdigest()


def obtener_hashes():
    return {
        str(archivo.relative_to(GOLD_DIR)): calcular_hash(archivo)
        for archivo in sorted(GOLD_DIR.rglob("*.parquet"))
    }


def main():
    if not GOLD_DIR.is_dir():
        raise FileNotFoundError(GOLD_DIR)

    print("========== PRUEBA DE IDEMPOTENCIA GOLD ==========", flush=True)

    originales = obtener_hashes()

    assert len(originales) == 51, (
        f"Se esperaban 51 archivos, encontrados: {len(originales)}"
    )

    with tempfile.TemporaryDirectory(prefix="logitrack_gold_backup_") as temporal:
        respaldo = Path(temporal) / "gold"

        print("Creando respaldo temporal...", flush=True)
        shutil.copytree(GOLD_DIR, respaldo)

        try:
            for modulo in MODULOS:
                print(f"\nEjecutando: {modulo}", flush=True)

                subprocess.run(
                    [sys.executable, "-m", modulo],
                    cwd=ROOT,
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                )

                print(f"PASS: ejecución de {modulo}", flush=True)

            nuevos = obtener_hashes()

            faltantes = sorted(set(originales) - set(nuevos))
            adicionales = sorted(set(nuevos) - set(originales))

            diferentes = sorted(
                nombre
                for nombre in originales.keys() & nuevos.keys()
                if originales[nombre] != nuevos[nombre]
            )

            print("\n========== RESULTADOS ==========")
            print(f"Archivos originales: {len(originales)}")
            print(f"Archivos posteriores: {len(nuevos)}")
            print(f"Archivos faltantes: {len(faltantes)}")
            print(f"Archivos adicionales: {len(adicionales)}")
            print(f"Archivos con hash diferente: {len(diferentes)}")

            if faltantes:
                print("\nFALTANTES:")
                for nombre in faltantes:
                    print(nombre)

            if adicionales:
                print("\nADICIONALES:")
                for nombre in adicionales:
                    print(nombre)

            if diferentes:
                print("\nHASH DIFERENTE:")
                for nombre in diferentes:
                    print(nombre)

            if faltantes or adicionales or diferentes:
                print("\nRESULTADO: FAIL - Archivos no idénticos")
                raise SystemExit(1)

            print("\nRESULTADO: PASS - Los 51 archivos son idénticos")

        finally:
            print("\nRestaurando archivos Gold originales...", flush=True)

            if GOLD_DIR.exists():
                shutil.rmtree(GOLD_DIR)

            shutil.copytree(respaldo, GOLD_DIR)

            print("Respaldo restaurado.", flush=True)


if __name__ == "__main__":
    main()

