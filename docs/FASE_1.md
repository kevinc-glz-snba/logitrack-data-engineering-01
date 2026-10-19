# Fase 1 — Generación de datos y modelo relacional

## 1. Descripción

Para la prueba técnica se eligió el escenario **LogiTrack**, una empresa de logística de última milla. En esta primera fase se generaron datos de prueba sobre envíos, conductores, clientes, zonas, rutas, calificaciones y novedades. Después se cargaron en una base de datos PostgreSQL local para utilizarlos como origen del pipeline en las siguientes fases.

Se eligió **PostgreSQL 17 con Docker** porque es gratuito, fácil de ejecutar localmente y permite trabajar con relaciones entre tablas sin crear recursos de pago en la nube. Para el resto del proyecto se utilizará **Microsoft Azure**.

## 2. Herramientas utilizadas

- **Python:** generación y validación de datos.
- **CSV y Parquet:** formatos de salida de los datos.
- **PostgreSQL 17:** base de datos relacional de origen.
- **Docker Compose:** ejecución de PostgreSQL sin instalarlo directamente en el equipo.
- **Git y GitHub:** control de versiones de los scripts y documentos.

## 3. Datos generados

La configuración se encuentra en `config.json`. Se utilizó la **semilla 42** y el período de referencia **01/01/2025 al 31/12/2025**.

| Tabla | Descripción | Registros |
|---|---|---:|
| `geo_zonas` | Zonas de distribución | 300 |
| `ope_conductores` | Conductores | 500 |
| `cli_remitentes` | Clientes remitentes | 200 |
| `tms_envios` | Envíos y entregas | 2.000.000 |
| `gps_rutas` | Recorridos de los conductores | 100.000 |
| `cal_destinatarios` | Calificaciones de las entregas | 300.000 |
| `dir_novedades` | Novedades de los envíos | 150.000 |
| **Total** | | **2.551.000** |

Los generadores están en `data-generation/`. Utilizan valores aleatorios dentro de rangos definidos, selecciones de categorías y algunas probabilidades ponderadas para simular situaciones operativas. Por ejemplo, los remitentes tienen penalizaciones entre 2 % y 8 %, los paquetes tienen pesos variables y los comentarios de calificaciones incluyen aproximadamente un 5 % de valores nulos. Esto no significa que todos los campos tengan un 5 % de nulos.

Los archivos principales se generan en `data/raw/` (CSV) y se convierten a `data/parquet/` (Parquet). Estos datos no se suben al repositorio debido a su tamaño.

## 4. Modelo relacional

La base de datos contiene **siete tablas**, con claves primarias y foráneas. La tabla principal es `tms_envios`, relacionada con remitentes, conductores y zonas. Las calificaciones y novedades se relacionan con los envíos; las rutas se relacionan con los conductores; y los conductores tienen una zona asignada.

El diagrama completo está en [Diagrams ](diagrams/Modelo_E-R_LogiTrack.pdf).

## 5. Anomalías de prueba

También se prepararon tres casos intencionalmente incorrectos para probar los controles de calidad del futuro pipeline:

1. Un envío con **peso negativo**.
2. Una calificación **fuera del rango de 1 a 5**.
3. Una ruta con **distancia negativa**.

Los archivos están en `data/anomalies/`, separados de los datos principales. Su detección y tratamiento dentro del pipeline corresponden a las siguientes fases.

## 6. Cómo ejecutar esta fase localmente

### Requisitos

Tener instalados **Python**, las dependencias utilizadas por los generadores y **Docker con Docker Compose**. Los comandos se ejecutan desde la raíz del repositorio.

### Paso 1. Configurar el proyecto

Revisar los parámetros de `config.json`, especialmente la semilla, las fechas y la cantidad de registros. Crear un archivo `.env` en la raíz con una contraseña local:

```env
POSTGRES_PASSWORD=CAMBIAR_POR_UNA_CONTRASENA_SEGURA
```

**No subir `.env` a GitHub.**

### Paso 2. Generar los CSV

Ejecutar los scripts en este orden, para que primero existan las entidades referenciadas por las demás:

```bash
python data-generation/generate_zonas.py
python data-generation/generate_conductores.py
python data-generation/generate_remitentes.py
python data-generation/generate_envios.py
python data-generation/generate_rutas.py
python data-generation/generate_calificaciones.py
python data-generation/generate_novedades.py
```

Los CSV deben quedar en `data/raw/`. Para generar los archivos adicionales se utilizan los scripts del repositorio:

```bash
python data-generation/converters/csv_to_parquet.py
python data-generation/generate_anomalias.py.py
```

### Paso 3. Iniciar PostgreSQL

```bash
docker compose up -d
docker compose ps
```

Esperar a que el contenedor `logitrack-postgres` aparezca como saludable (*healthy*). La base de datos se llama `logitrack` y el usuario es `logitrack_user`.

### Paso 4. Crear las tablas

**Solo en una base de datos nueva o vacía:**

```bash
docker exec -i logitrack-postgres \
  psql -U logitrack_user -d logitrack -v ON_ERROR_STOP=1 \
  < sql/01_create_tables.sql
```

### Paso 5. Cargar los CSV

```bash
chmod +x sql/02_load_data.sh
./sql/02_load_data.sh
```

El script utiliza `\COPY` y carga las tablas en el orden necesario para respetar sus relaciones. **No volver a ejecutar la carga sobre tablas que ya tienen registros**, porque puede producir errores por claves duplicadas.

### Paso 6. Validar los resultados

```bash
mkdir -p docs/evidence

docker exec -i logitrack-postgres \
  psql -U logitrack_user -d logitrack -v ON_ERROR_STOP=1 \
  < sql/03_validate_counts.sql \
  > docs/evidence/postgresql_counts.txt
```

Se espera obtener **2.551.000 registros** en total y **cero referencias inválidas** en las comprobaciones de integridad.

## 7. Resultado y evidencias

Se completaron la generación de los siete conjuntos de datos, su conversión a Parquet y su carga en PostgreSQL. Se ejecutaron las validaciones de cantidad e integridad sin errores reportados.

Archivos importantes para revisar esta fase:

- `config.json`: parámetros de generación.
- `data-generation/`: scripts Python.
- `sql/01_create_tables.sql`: creación de tablas.
- `sql/02_load_data.sh`: carga de datos.
- `sql/03_validate_counts.sql`: comprobaciones.
- `docs/evidence/`: resultados guardados de las consultas SQL.
- `docs/diagrams/Modelo_E-R_LogiTrack.pdf`: diagrama de las tablas y relaciones.

## 8. Próxima etapa

La siguiente fase será preparar la infraestructura en **Microsoft Azure** con **Terraform**, manteniendo el desarrollo local siempre que sea posible.
