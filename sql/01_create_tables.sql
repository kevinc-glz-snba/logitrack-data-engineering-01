-- =====================================================
-- PROYECTO: LOGITRACK
-- FASE 1: MODELO RELACIONAL
-- BASE DE DATOS: PostgreSQL 17
-- =====================================================

-- 1. ZONAS GEOGRAFICAS
-- Se crea primero porque ope_conductores referencia id_zona.
CREATE TABLE IF NOT EXISTS geo_zonas (
    id_zona INTEGER PRIMARY KEY,
    nom_zona VARCHAR(100) NOT NULL,
    id_ciudad INTEGER NOT NULL,
    barrio_referencia VARCHAR(100),
    latitud_centroide NUMERIC(10,7),
    longitud_centroide NUMERIC(10,7),
    nivel_trafico_prom NUMERIC(4,2),
    tip_zona VARCHAR(30) NOT NULL,
    distancia_bodega_km NUMERIC(10,2),
    CONSTRAINT chk_zona_trafico
        CHECK (nivel_trafico_prom BETWEEN 1 AND 5),
    CONSTRAINT chk_zona_distancia
        CHECK (distancia_bodega_km >= 0),
    CONSTRAINT chk_zona_latitud
        CHECK (latitud_centroide BETWEEN -90 AND 90),
    CONSTRAINT chk_zona_longitud
        CHECK (longitud_centroide BETWEEN -180 AND 180)
);
-- 2. CONDUCTORES
CREATE TABLE IF NOT EXISTS ope_conductores (
    cond_id INTEGER PRIMARY KEY,
    nomb_cond VARCHAR(100) NOT NULL,
    apell_cond VARCHAR(100) NOT NULL,
    tip_doc VARCHAR(20) NOT NULL,
    num_doc_hash VARCHAR(128) NOT NULL,
    fec_ingreso DATE NOT NULL,
    id_ciudad_base INTEGER NOT NULL,
    tip_vehiculo VARCHAR(30) NOT NULL,
    cod_zona_asignada INTEGER,
    activo BOOLEAN NOT NULL,
    calific_promedio_acum NUMERIC(3,2),
    CONSTRAINT fk_conductor_zona
        FOREIGN KEY (cod_zona_asignada)
        REFERENCES geo_zonas(id_zona),
    CONSTRAINT chk_conductor_calificacion
        CHECK (calific_promedio_acum BETWEEN 1 AND 5)
);

-- 3. REMITENTES
CREATE TABLE IF NOT EXISTS cli_remitentes (
    id_remitente INTEGER PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL,
    ciudad_principal VARCHAR(100) NOT NULL,
    sla_entrega_horas INTEGER NOT NULL,
    penalidad_porc NUMERIC(5,2) NOT NULL,
    activo BOOLEAN NOT NULL,
    CONSTRAINT chk_remitente_sla
        CHECK (sla_entrega_horas > 0),
    CONSTRAINT chk_remitente_penalidad
        CHECK (penalidad_porc BETWEEN 2 AND 8)
);

-- 4. ENVIOS
CREATE TABLE IF NOT EXISTS tms_envios (
    id_envio BIGINT PRIMARY KEY,
    id_remitente INTEGER NOT NULL,
    cond_id INTEGER NOT NULL,
    id_zona_destino INTEGER NOT NULL,
    tip_paquete VARCHAR(30) NOT NULL,
    peso_kg NUMERIC(10,2) NOT NULL,
    fec_recepcion DATE NOT NULL,
    hra_recepcion TIME NOT NULL,
    fec_entrega_programada DATE NOT NULL,
    fec_intento1 DATE,
    hra_intento1 TIME,
    resultado_intento1 VARCHAR(30),
    fec_intento2 DATE,
    hra_intento2 TIME,
    resultado_intento2 VARCHAR(30),
    fec_entrega_real DATE,
    estado_final VARCHAR(30) NOT NULL,
    motivo_fallo_cod VARCHAR(30),
    vr_declarado NUMERIC(14,2),
    CONSTRAINT fk_envio_remitente
        FOREIGN KEY (id_remitente)
        REFERENCES cli_remitentes(id_remitente),
    CONSTRAINT fk_envio_conductor
        FOREIGN KEY (cond_id)
        REFERENCES ope_conductores(cond_id),
    CONSTRAINT fk_envio_zona
        FOREIGN KEY (id_zona_destino)
        REFERENCES geo_zonas(id_zona),
    CONSTRAINT chk_envio_peso
        CHECK (peso_kg > 0),
    CONSTRAINT chk_envio_valor_declarado
        CHECK (vr_declarado >= 0)
);

-- 5. RUTAS GPS
CREATE TABLE IF NOT EXISTS gps_rutas (
    id_ruta BIGINT PRIMARY KEY,
    cond_id INTEGER NOT NULL,
    fec_ruta DATE NOT NULL,
    hra_inicio TIME NOT NULL,
    hra_fin TIME,
    km_recorridos NUMERIC(10,2),
    num_paradas_plan INTEGER,
    num_paradas_real INTEGER,
    desviacion_ruta_km NUMERIC(10,2),
    consumo_combustible NUMERIC(10,2),
    CONSTRAINT fk_ruta_conductor
        FOREIGN KEY (cond_id)
        REFERENCES ope_conductores(cond_id),
    CONSTRAINT chk_ruta_km
        CHECK (km_recorridos >= 0),
    CONSTRAINT chk_ruta_paradas_plan
        CHECK (num_paradas_plan >= 0),
    CONSTRAINT chk_ruta_paradas_real
        CHECK (num_paradas_real >= 0),
    CONSTRAINT chk_ruta_desviacion
        CHECK (desviacion_ruta_km >= 0),
    CONSTRAINT chk_ruta_combustible
        CHECK (consumo_combustible >= 0)
);

-- 6. CALIFICACIONES DE DESTINATARIOS
CREATE TABLE IF NOT EXISTS cal_destinatarios (
    id_calificacion BIGINT PRIMARY KEY,
    id_envio BIGINT NOT NULL,
    fec_calificacion DATE NOT NULL,
    puntaje_1_5 INTEGER NOT NULL,
    comentario_texto TEXT,
    canal_calificacion VARCHAR(30),
    CONSTRAINT fk_calificacion_envio
        FOREIGN KEY (id_envio)
        REFERENCES tms_envios(id_envio),
    CONSTRAINT chk_calificacion_puntaje
        CHECK (puntaje_1_5 BETWEEN 1 AND 5)
);

-- 7. NOVEDADES
CREATE TABLE IF NOT EXISTS dir_novedades (
    id_novedad BIGINT PRIMARY KEY,
    id_envio BIGINT NOT NULL,
    fec_novedad DATE NOT NULL,
    tip_novedad VARCHAR(50) NOT NULL,
    desc_novedad TEXT,
    id_agente_registro INTEGER,
    requiere_accion BOOLEAN NOT NULL,
    CONSTRAINT fk_novedad_envio
        FOREIGN KEY (id_envio)
        REFERENCES tms_envios(id_envio)
);