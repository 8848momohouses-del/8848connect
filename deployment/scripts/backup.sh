#!/usr/bin/env bash
# Backup PostgreSQL database and Odoo filestore
set -euo pipefail

cd "$(dirname "$0")/.."
source .env

BACKUP_DIR="../backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_BACKUP="${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz"
FILESTORE_BACKUP="${BACKUP_DIR}/filestore_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Backing up database..."
docker exec 8848_db pg_dump -U "${DB_USER}" -d "${DB_NAME:-postgres}" | gzip > "$DB_BACKUP"

echo "Backing up filestore..."
# Assumes odoo-filestore is a named volume mapped to /var/lib/odoo inside container
docker run --rm -v 8848connect_odoo-filestore:/var/lib/odoo -v "$(realpath "$BACKUP_DIR"):/backup" alpine tar -czf "/backup/filestore_${TIMESTAMP}.tar.gz" -C /var/lib/odoo .

echo "Backup completed successfully."
echo "DB: $DB_BACKUP"
echo "Filestore: $FILESTORE_BACKUP"
