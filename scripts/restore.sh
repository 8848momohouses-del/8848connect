#!/usr/bin/env bash
# 8848 Business Suite — restore script (Milestone 0)
# Restores a backup set produced by scripts/backup.sh into a target database.
# Refuses to overwrite an existing database unless --force is given.
# Usage: scripts/restore.sh <backup-dir> <target-db> [--force] [--with-filestore]
set -euo pipefail

BACKUP_DIR="${1:?usage: restore.sh <backup-dir> <target-db> [--force] [--with-filestore]}"
TARGET_DB="${2:?usage: restore.sh <backup-dir> <target-db> [--force] [--with-filestore]}"
DB_USER="${ODOO_DB_USER:-suraj}"
FORCE=0; WITH_FILESTORE=0
for arg in "${@:3}"; do
    [ "$arg" = "--force" ] && FORCE=1
    [ "$arg" = "--with-filestore" ] && WITH_FILESTORE=1
done

[ -f "$BACKUP_DIR/db.dump" ] || { echo "ERROR: $BACKUP_DIR/db.dump not found"; exit 1; }

echo ">> Verifying checksums"
( cd "$BACKUP_DIR" && shasum -a 256 -c SHA256SUMS ) || { echo "ERROR: checksum mismatch"; exit 1; }

if psql -U "$DB_USER" -lqt | cut -d'|' -f1 | grep -qw "$TARGET_DB"; then
    if [ "$FORCE" -ne 1 ]; then
        echo "ERROR: database '$TARGET_DB' already exists. Use --force to drop and restore."
        exit 1
    fi
    echo ">> Dropping existing database $TARGET_DB (forced)"
    dropdb -U "$DB_USER" "$TARGET_DB"
fi

echo ">> Creating database $TARGET_DB"
createdb -U "$DB_USER" "$TARGET_DB"

echo ">> Restoring dump"
pg_restore -U "$DB_USER" --no-owner -d "$TARGET_DB" "$BACKUP_DIR/db.dump"

if [ "$WITH_FILESTORE" -eq 1 ] && [ -f "$BACKUP_DIR/filestore.tar.gz" ]; then
    FS_PARENT="${ODOO_FILESTORE_PARENT:-$HOME/Library/Application Support/Odoo/filestore}"
    echo ">> Restoring filestore into $FS_PARENT/$TARGET_DB"
    TMP=$(mktemp -d)
    tar -xzf "$BACKUP_DIR/filestore.tar.gz" -C "$TMP"
    SRC=$(find "$TMP" -maxdepth 1 -mindepth 1 -type d | head -1)
    rm -rf "$FS_PARENT/$TARGET_DB"
    mv "$SRC" "$FS_PARENT/$TARGET_DB"
    rm -rf "$TMP"
fi

echo ">> RESTORE COMPLETE: $TARGET_DB"
echo ">> Post-restore check: table count ="
psql -U "$DB_USER" -d "$TARGET_DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"
