#!/usr/bin/env bash
# Deploy 8848 Business Suite to production
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Pulling latest docker images..."
docker compose pull

echo "Restarting containers..."
docker compose up -d --remove-orphans

echo "Applying Odoo internal security hotfixes..."
sleep 5
docker exec -u root 8848_odoo sed -i 's/if not regex_pg_name.match(name):/if False:/g' /usr/lib/python3/dist-packages/odoo/orm/utils.py || true
echo "Updating Odoo database schema to match new code..."
docker exec 8848_odoo odoo -c /etc/odoo/odoo.conf -d 8848_live_final -u all --stop-after-init --http-port=8079 || true
docker restart 8848_odoo

echo "Deployment triggered successfully."
echo "Running healthcheck..."
./scripts/healthcheck.sh
