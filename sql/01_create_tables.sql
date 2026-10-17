-- =====================================================
-- PROYECTO: LOGITRACK
-- FASE 1: MODELO RELACIONAL
-- BASE DE DATOS: PostgreSQL 17
-- =====================================================


-- =====================================================
-- 1. CONDUCTORES
-- =====================================================

CREATE TABLE IF NOT EXISTS ope_conductores (

    cond_id INTEGER PRIMARY KEY,

    nomb_cond VARCHAR(100) NOT NULL,

    apell_cond VARCHAR(100) NOT NULL,

    tip_doc VARCHAR(20) NOT NULL,

    num_doc_hash VARCHAR(128) NOT NULL,

    fec_ingreso DATE NOT NULL,

    id_ciudad_base INTEGER NOT NULL,

    tip_vehiculo VARCHAR(30) NOT NULL,

    cod_zona_asignada VARCHAR(30),

    activo BOOLEAN NOT NULL,

    calific_promedio_acum NUMERIC(3,2)

);


-- =====================================================
-- 2. REMITENTES
-- =====================================================

CREATE TABLE IF NOT EXISTS cli_remitentes (

    id_remitente INTEGER PRIMARY KEY,

    razon_social VARCHAR(150) NOT NULL,

    tipo_cliente VARCHAR(50) NOT NULL,

    ciudad_principal VARCHAR(100) NOT NULL,

    sla_entrega_horas INTEGER NOT NULL,

    penalidad_porc NUMERIC(5,2) NOT NULL,

    activo BOOLEAN NOT NULL

);


-- =====================================================
-- 3. ZONAS GEOGRÁFICAS
-- =====================================================

CREATE TABLE IF NOT EXISTS geo_zonas (

    id_zona INTEGER PRIMARY KEY,

    nom_zona VARCHAR(100) NOT NULL,

    id_ciudad INTEGER NOT NULL,

    barrio_referencia VARCHAR(100),

    latitud_centroide NUMERIC(10,7),

    longitud_centroide NUMERIC(10,7),

    nivel_trafico_prom NUMERIC(4,2),

    tip_zona VARCHAR(30) NOT NULL,

    distancia_bodega_km NUMERIC(10,2)

);


-- =====================================================
-- 4. ENVÍOS
-- =====================================================

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
        REFERENCES geo_zonas(id_zona)

);


-- =====================================================
-- 5. RUTAS GPS
-- =====================================================

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
        REFERENCES ope_conductores(cond_id)

);


-- =====================================================
-- 6. CALIFICACIONES DE DESTINATARIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS cal_destinatarios (

    id_calificacion BIGINT PRIMARY KEY,

    id_envio BIGINT NOT NULL,

    fec_calificacion DATE NOT NULL,

    puntaje_1_5 INTEGER NOT NULL,

    comentario_texto TEXT,

    canal_calificacion VARCHAR(30),

    CONSTRAINT fk_calificacion_envio
        FOREIGN KEY (id_envio)
        REFERENCES tms_envios(id_envio)

);


-- =====================================================
-- 7. NOVEDADES
-- =====================================================

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
