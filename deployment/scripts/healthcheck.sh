#!/usr/bin/env bash
# Perform health checks on the production services
set -euo pipefail

cd "$(dirname "$0")/.."
source .env

echo "Checking PostgreSQL connection..."
if docker exec 8848_db pg_isready -U "${DB_USER}" -d "${DB_NAME:-postgres}" > /dev/null 2>&1; then
    echo "[OK] PostgreSQL is accepting connections."
else
    echo "[ERROR] PostgreSQL is not ready!"
    exit 1
fi

echo "Checking Odoo HTTP endpoint..."
# We wait for up to 30 seconds for Odoo to become responsive
for i in {1..30}; do
    if curl -s -f http://127.0.0.1:8069/web/webclient/version_info > /dev/null 2>&1; then
        echo "[OK] Odoo HTTP endpoint is responsive."
        exit 0
    fi
    echo "Waiting for Odoo to start ($i/30)..."
    sleep 2
done

echo "[ERROR] Odoo HTTP endpoint failed to respond."
exit 1
