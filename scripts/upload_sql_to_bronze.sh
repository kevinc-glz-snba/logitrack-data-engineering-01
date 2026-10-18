#!/usr/bin/env bash

set -euo pipefail

STORAGE_ACCOUNT=$(cd infra && terraform output -raw datalake_name)

SOURCE_DIR="data/bronze"
CONTAINER="bronze"
PREFIX="logitrack_sql"

total=0

while IFS= read -r -d '' archivo; do

    ruta_relativa="${archivo#"$SOURCE_DIR"/}"
    destino="$PREFIX/$ruta_relativa"

    echo "Subiendo: $destino"

    az storage blob upload \
        --account-name "$STORAGE_ACCOUNT" \
        --container-name "$CONTAINER" \
        --name "$destino" \
        --file "$archivo" \
        --auth-mode login \
        --overwrite true \
        --output none

    total=$((total + 1))

done < <(find "$SOURCE_DIR" -type f -name "*.parquet" -print0)

echo ""
echo "Carga finalizada."
echo "Archivos procesados: $total"