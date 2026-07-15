#!/usr/bin/env bash
# Restore PostgreSQL database and Odoo filestore
set -euo pipefail

cd "$(dirname "$0")/.."
source .env

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <db_backup.sql.gz> <filestore_backup.tar.gz>"
    exit 1
fi

DB_BACKUP=$(realpath "$1")
FILESTORE_BACKUP=$(realpath "$2")

if [ ! -f "$DB_BACKUP" ] || [ ! -f "$FILESTORE_BACKUP" ]; then
    echo "Error: Backup files not found."
    exit 1
fi

echo "Stopping Odoo container..."
docker compose stop odoo

echo "Dropping and recreating database..."
docker exec 8848_db psql -U "${DB_USER}" -d postgres -c "DROP DATABASE IF EXISTS \"${DB_NAME:-postgres}\";"
docker exec 8848_db psql -U "${DB_USER}" -d postgres -c "CREATE DATABASE \"${DB_NAME:-postgres}\" OWNER \"${DB_USER}\";"

echo "Restoring database..."
gunzip -c "$DB_BACKUP" | docker exec -i 8848_db psql -U "${DB_USER}" -d "${DB_NAME:-postgres}"

echo "Restoring filestore..."
# Clear existing filestore first
docker run --rm -v 8848connect_odoo-filestore:/var/lib/odoo alpine sh -c "rm -rf /var/lib/odoo/*"
docker run --rm -v 8848connect_odoo-filestore:/var/lib/odoo -v "$(dirname "$FILESTORE_BACKUP"):/backup" alpine tar -xzf "/backup/$(basename "$FILESTORE_BACKUP")" -C /var/lib/odoo

echo "Starting Odoo container..."
docker compose start odoo

echo "Restore completed successfully."
