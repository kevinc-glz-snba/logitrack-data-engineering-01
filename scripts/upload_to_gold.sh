#!/usr/bin/env bash

set -euo pipefail

STORAGE_ACCOUNT="stlogitrackdeveus201"
CONTAINER="gold"
LOCAL_DIR="data/gold"

echo "=========================================="
echo "PUBLICACIÓN GOLD EN AZURE ADLS GEN2"
echo "=========================================="

if [[ ! -d "$LOCAL_DIR" ]]; then
    echo "ERROR: No existe el directorio $LOCAL_DIR"
    exit 1
fi

TOTAL_LOCAL=$(find "$LOCAL_DIR" -type f -name "*.parquet" | wc -l)

echo "Cuenta de almacenamiento: $STORAGE_ACCOUNT"
echo "Contenedor: $CONTAINER"
echo "Archivos locales: $TOTAL_LOCAL"
echo

if [[ "$TOTAL_LOCAL" -ne 51 ]]; then
    echo "ERROR: Se esperaban 51 archivos Parquet."
    exit 1
fi

echo "Iniciando carga..."
echo

CONTADOR=0

while IFS= read -r ARCHIVO; do

    RUTA_RELATIVA="${ARCHIVO#"$LOCAL_DIR"/}"

    echo "Subiendo: $RUTA_RELATIVA"

    az storage blob upload \
        --account-name "$STORAGE_ACCOUNT" \
        --container-name "$CONTAINER" \
        --name "$RUTA_RELATIVA" \
        --file "$ARCHIVO" \
        --auth-mode login \
        --overwrite true \
        --only-show-errors \
        --output none

    CONTADOR=$((CONTADOR + 1))

done < <(find "$LOCAL_DIR" -type f -name "*.parquet" | sort)

echo
echo "=========================================="
echo "PUBLICACIÓN FINALIZADA"
echo "=========================================="
echo "Archivos enviados: $CONTADOR"
