CREATE TABLE IF NOT EXISTS pipeline_error_log (
    id_error BIGSERIAL PRIMARY KEY,

    fecha_error TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    capa VARCHAR(20) NOT NULL,

    proceso VARCHAR(150) NOT NULL,

    tipo_error VARCHAR(100) NOT NULL,

    mensaje_error TEXT NOT NULL,

    batch_id VARCHAR(100),

    estado VARCHAR(20) NOT NULL
        DEFAULT 'PENDIENTE',

    CONSTRAINT chk_pipeline_error_capa
        CHECK (
            capa IN ('BRONZE', 'SILVER', 'GOLD')
        ),

    CONSTRAINT chk_pipeline_error_estado
        CHECK (
            estado IN ('PENDIENTE', 'RESUELTO')
        )
);

CREATE INDEX IF NOT EXISTS idx_pipeline_error_fecha
    ON pipeline_error_log (fecha_error);

CREATE INDEX IF NOT EXISTS idx_pipeline_error_capa
    ON pipeline_error_log (capa);

CREATE INDEX IF NOT EXISTS idx_pipeline_error_batch
    ON pipeline_error_log (batch_id);
