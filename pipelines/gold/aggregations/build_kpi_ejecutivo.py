from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


GOLD = Path("data/gold")
AGG = GOLD / "aggregations"

DESTINO = GOLD / "kpi_resumen_ejecutivo.parquet"


def main():
    print("\nCargando agregaciones...")

    diarios = pd.read_parquet(
        AGG / "agg_envios_diarios.parquet"
    )

    conductores = pd.read_parquet(
        AGG / "agg_desempeno_conductores.parquet"
    )

    zonas = pd.read_parquet(
        AGG / "agg_operacion_zonas.parquet"
    )

    desempeno = pd.read_parquet(
        GOLD / "fact_desempeno_conductor.parquet",
        columns=["score_desempeno"],
    )

    total_envios = int(diarios["total_envios"].sum())
    entregados = int(diarios["entregados"].sum())
    fallidos = int(diarios["fallidos"].sum())
    cumplen_sla = int(diarios["cumplen_sla"].sum())

    total_evaluaciones = len(desempeno)

    evaluaciones_con_score = int(
        desempeno["score_desempeno"].notna().sum()
    )

    # Promedio de las evaluaciones disponibles.
    # No representa a los registros sin score.
    score_promedio = desempeno[
        "score_desempeno"
    ].mean()

    kpi = pd.DataFrame(
        [
            {
                "fecha_inicio": diarios["fecha"].min(),
                "fecha_fin": diarios["fecha"].max(),

                "total_envios": total_envios,
                "envios_entregados": entregados,
                "envios_fallidos": fallidos,

                "tasa_entrega": (
                    entregados / total_envios
                ),

                "tasa_fallo": (
                    fallidos / total_envios
                ),

                "tasa_cumplimiento_sla": (
                    cumplen_sla / total_envios
                ),

                "conductores_con_envios": int(
                    (conductores["total_envios"] > 0).sum()
                ),

                "zonas_con_envios": int(
                    (zonas["total_envios"] > 0).sum()
                ),

                "total_alertas_zona": int(
                    zonas["dias_con_alerta"].sum()
                ),

                "evaluaciones_desempeno": total_evaluaciones,

                "evaluaciones_con_score": evaluaciones_con_score,

                "cobertura_score": (
                    evaluaciones_con_score
                    / total_evaluaciones
                ),

                "score_promedio_disponible": (
                    score_promedio
                ),

                "fecha_generacion_utc": datetime.now(
                    timezone.utc
                ),
            }
        ]
    )

    # Validaciones.
    assert total_envios == 2_000_000, (
        "El total de envíos no coincide"
    )

    assert entregados + fallidos == total_envios, (
        "Los estados no suman el total de envíos"
    )

    assert kpi["tasa_entrega"].between(0, 1).all()
    assert kpi["tasa_fallo"].between(0, 1).all()
    assert kpi["tasa_cumplimiento_sla"].between(0, 1).all()
    assert kpi["cobertura_score"].between(0, 1).all()

    DESTINO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    kpi.to_parquet(
        DESTINO,
        index=False,
    )

    print("\nKPI_RESUMEN_EJECUTIVO GENERADO")

    for columna, valor in kpi.iloc[0].items():
        print(f"{columna}: {valor}")

    print(f"\nArchivo generado: {DESTINO}")


if __name__ == "__main__":
    main()