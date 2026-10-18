#!/usr/bin/env bash

set -euo pipefail

CONTAINER="logitrack-postgres"
DB_USER="logitrack_user"
DB_NAME="logitrack"

TABLES=(
    "geo_zonas"
    "ope_conductores"
    "cli_remitentes"
    "tms_envios"
    "gps_rutas"
    "cal_destinatarios"
    "dir_novedades"
)

echo "========================================="
echo " INICIANDO CARGA DE DATOS - LOGITRACK"
echo "========================================="

for TABLE in "${TABLES[@]}"; do

    FILE="data/raw/${TABLE}.csv"

    if [[ ! -f "$FILE" ]]; then
        echo "ERROR: No existe el archivo $FILE"
        exit 1
    fi

    echo ""
    echo "Cargando tabla: $TABLE"

    docker exec -i "$CONTAINER" \
        psql \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -v ON_ERROR_STOP=1 \
        -c "\COPY ${TABLE} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')" \
        < "$FILE"

    echo "Carga completada: $TABLE"

done

echo ""
echo "========================================="
echo " CARGA FINALIZADA CORRECTAMENTE"
echo "========================================="