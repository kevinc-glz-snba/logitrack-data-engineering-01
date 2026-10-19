from pipelines.common.pipeline_runner import ejecutar_pipeline


def main():
    print("\nPRUEBA DE CONTINUIDAD ENTRE TAREAS INDEPENDIENTES\n")

    # Primera tarea: fallo intencional.
    resultado_fallido = ejecutar_pipeline(
        capa="GOLD",
        modulo="pipelines.gold.modulo_inexistente",
        batch_id="TEST_CONTINUITY_001",
    )

    # Segunda tarea: independieçnte de la anterior.
    # Usamos un módulo estándar de Python para evitar
    # ejecutar transformaciones reales.
    resultado_independiente = ejecutar_pipeline(
        capa="GOLD",
        modulo="this",
        batch_id="TEST_CONTINUITY_001",
    )

    assert resultado_fallido is False, (
        "La tarea inexistente debería fallar"
    )

    assert resultado_independiente is True, (
        "La tarea independiente debería ejecutarse"
    )

    print("\nRESULTADO: PASS")
    print("El fallo de una tarea no impidió ejecutar otra independiente.")


if __name__ == "__main__":
    main()
