# LogiTrack — Data Engineering Pipeline

Proyecto desarrollado como parte de una prueba técnica de ingeniería
de datos, utilizando Python, PostgreSQL, Docker, Terraform y Microsoft Azure.

## 1. Descripción del proyecto

LogiTrack es un escenario de una empresa de logística de última milla.

El objetivo es construir una solución de ingeniería de datos que permita
procesar información sobre envíos, conductores, remitentes, zonas,
rutas, calificaciones y novedades operativas.

Para ello se implementó un pipeline basado en la arquitectura
Medallion (Bronze, Silver y Gold).

La solución utiliza procesamiento local con Python y almacenamiento
de los resultados en Azure Data Lake Storage Gen2.

## 2. Arquitectura implementada

```text
             GENERACIÓN DE DATOS
                    Python
                       |
                       v
              PostgreSQL 17
                  Docker
                       |
                       v
                CAPA BRONZE
           Extracción de datos
                       |
                       v
                CAPA SILVER
          Limpieza y validación
                       |
                       v
                 CAPA GOLD
       Modelo analítico e indicadores
                       |
                       v
          Azure Data Lake Storage Gen2
          ├── bronze
          ├── silver
          └── gold
```

Los procesos de transformación se ejecutan localmente.

Cada capa genera archivos Parquet que posteriormente se publican
en su contenedor correspondiente de Azure.

Azure Data Factory fue aprovisionado como parte de la infraestructura,
pero no se implementó una orquestación automática end-to-end.

## 3. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Generación, procesamiento y validación de datos |
| PostgreSQL 17 | Base de datos relacional de origen |
| Docker Compose | Ejecución local de PostgreSQL |
| pandas | Limpieza, transformación y agregación |
| PyArrow | Lectura y escritura de archivos Parquet |
| Faker | Generación de datos sintéticos |
| Azure Data Lake Storage Gen2 | Almacenamiento de las capas Medallion |
| Terraform | Infraestructura como código |
| Azure CLI | Administración y publicación de datos en Azure |
| Git | Control de versiones |

## 4. Datos generados

Se generaron siete conjuntos de datos sintéticos.

| Tabla | Registros |
|---|---:|
| `geo_zonas` | 300 |
| `ope_conductores` | 500 |
| `cli_remitentes` | 200 |
| `tms_envios` | 2.000.000 |
| `gps_rutas` | 100.000 |
| `cal_destinatarios` | 300.000 |
| `dir_novedades` | 150.000 |
| **Total** | **2.551.000** |

La generación utiliza una semilla fija para facilitar la
reproducción de los datos.

Los parámetros se encuentran en `config.json`.

## 5. Procesamiento de datos

### Bronze

Extrae las siete tablas desde PostgreSQL.

- Extracción completa.
- Almacenamiento en formato Parquet.
- Incorporación de metadatos de ingesta.
- Publicación en el contenedor `bronze`.

**Resultado:** 54 archivos Parquet.

### Silver

Aplica reglas de limpieza y validación sobre los datos.

- Estandarización de tipos.
- Validación de campos obligatorios.
- Reglas de calidad.
- Validaciones de integridad referencial.
- Tratamiento de información personal.

**Resultado:** siete conjuntos de datos procesados y 46 archivos
Parquet publicados en la ruta principal de Silver.

### Gold

Construye estructuras orientadas al análisis del negocio.

**Dimensiones:**
- Conductores.
- Remitentes.
- Zonas.

**Tablas de hechos:**
- Envíos.
- Rutas.
- Desempeño de conductores.
- Trazabilidad de envíos.
- Alertas por zona.

**Agregaciones:**
- Envíos diarios.
- Desempeño de conductores.
- Operación por zonas.

**Indicador ejecutivo:**
- Resumen general de la operación.

**Resultado:** 12 conjuntos de datos y 51 archivos Parquet
publicados en Azure.

Las definiciones de las agregaciones están documentadas en
[Agregaciones Gold](docs/gold/aggregations.md).

## 6. Estructura del repositorio

```text
logitrack-data-engineering-01/
├── config.json
├── data-generation/
├── docs/
│   ├── diagrams/
│   ├── evidence/
│   ├── gold/
│   ├── lineage/
│   ├── quality/
│   └── technical_decisions/
├── infra/
├── pipelines/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── quality/
│   └── common/
├── scripts/
├── sql/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 7. Requisitos para ejecutar el proyecto

Se requiere:

- Python 3.12.
- Docker y Docker Compose.
- PostgreSQL mediante el contenedor del proyecto.
- Dependencias de `requirements.txt`.
- Azure CLI y acceso a una suscripción Azure para publicar archivos.
- Terraform, únicamente para administrar la infraestructura.

### Preparar el entorno Python

Desde la raíz del repositorio:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configurar PostgreSQL

Crear un archivo `.env` con las variables necesarias para
la conexión local.

No se incluyen credenciales reales en el repositorio.

Iniciar PostgreSQL:

```bash
docker compose up -d
```

### Generar y cargar los datos

Las instrucciones detalladas se encuentran en:

[Documentación de la fase 1](docs/FASE_1.md).

### Ejecutar el pipeline

El código de las transformaciones se encuentra en:

- `pipelines/bronze/`
- `pipelines/silver/`
- `pipelines/gold/`

La documentación de las capas y sus resultados está disponible en:

[Documentación de la fase 3](docs/FASE_3.md).

La ejecución se realiza mediante scripts Python locales.
No existe un comando único que ejecute automáticamente las tres capas.

## 8. Calidad de datos

Se implementaron validaciones automatizadas para comprobar
reglas de limpieza, integridad referencial y consistencia
de los resultados Gold.

También se realizaron pruebas controladas con datos incorrectos
y verificaciones del registro de errores.

Documentación:

- [Pruebas de calidad](docs/quality/automated_data_quality_checks.md)
- [Política de valores nulos](docs/quality/silver_null_policy.md)
- [Linaje de datos](docs/lineage/gold_data_lineage.md)

Las evidencias se encuentran en `docs/evidence/`.

## 9. Infraestructura en Azure

La infraestructura se definió mediante Terraform.

Se aprovisionaron recursos para almacenamiento, administración
de secretos, monitoreo y futura orquestación.

Los archivos Terraform se encuentran en `infra/`.

La documentación está disponible en:

[Documentación de la fase 2](docs/FASE_2.md).

La infraestructura fue verificada en el entorno de desarrollo (`dev`).

## 10. Alcance y limitaciones

La solución implementa generación de datos, almacenamiento,
procesamiento Medallion y validaciones de calidad.

Sin embargo, no cubre todos los requisitos de la prueba técnica.

**Principales limitaciones:**

- La extracción Bronze es completa, no incremental.
- Los reportes de calidad Silver no se generan automáticamente
  después de cada ejecución.
- No se demostró la idempotencia del pipeline completo.
- No se implementó orquestación automática con Azure Data Factory.
- No se configuraron notificaciones automáticas de incidentes.
- La fase de gobierno y seguridad no se completó integralmente.

La infraestructura incluye algunos recursos de seguridad y monitoreo,
pero esto no equivale a una implementación completa de esas funciones.

Para más información:

[Limitaciones de la fase 3](docs/technical_decisions/phase_3_limitations.md).

## 11. Documentación

| Documento | Contenido |
|---|---|
| [Fase 1](docs/FASE_1.md) | Generación de datos y PostgreSQL |
| [Fase 2](docs/FASE_2.md) | Infraestructura en Azure |
| [Fase 3](docs/FASE_3.md) | Procesamiento Bronze, Silver y Gold |
| [Agregaciones Gold](docs/gold/aggregations.md) | Definiciones de indicadores |
| [Linaje](docs/lineage/gold_data_lineage.md) | Trazabilidad de métricas |
| [Calidad](docs/quality/automated_data_quality_checks.md) | Validaciones automatizadas |
| [Limitaciones](docs/technical_decisions/phase_3_limitations.md) | Funcionalidades pendientes |

## 12. Conclusión

LogiTrack presenta una implementación funcional de procesamiento
de datos mediante una arquitectura Medallion.

El proyecto permitió trabajar con generación de datos sintéticos,
modelado relacional, transformaciones, controles de calidad,
infraestructura como código y almacenamiento en Microsoft Azure.

