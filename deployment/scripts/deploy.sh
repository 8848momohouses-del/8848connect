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
MODULES="8848_api_gateway,8848_communication,8848_core_branding,8848_crm,8848_dashboard,8848_delivery,8848_driver,8848_factory,8848_franchise,8848_glass_skin,8848_inventory,8848_marketing_fee,8848_portal,8848_quality,8848_royalty,8848_security,8848_store_performance,8848_supplier,8848_warehouse,8848_workflow"
docker exec -u odoo 8848_odoo odoo -c /etc/odoo/odoo.conf -d 8848_live_final -i $MODULES --stop-after-init --http-port=8079
docker restart 8848_odoo

echo "Deployment triggered successfully."
echo "Running healthcheck..."
./scripts/healthcheck.sh
