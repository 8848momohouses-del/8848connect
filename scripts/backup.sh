#!/usr/bin/env bash
# 8848 Business Suite — backup script (Milestone 0)
# Produces a timestamped backup set: database dump, filestore archive,
# odoo.conf copy, git reference and checksums, plus a manifest.
# Usage: scripts/backup.sh [label]
set -euo pipefail

DB_NAME="${ODOO_DB:-Momohouse}"
DB_USER="${ODOO_DB_USER:-suraj}"
FILESTORE="${ODOO_FILESTORE:-$HOME/Library/Application Support/Odoo/filestore/$DB_NAME}"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_ROOT="${BACKUP_ROOT:-$PROJECT_ROOT/backups}"
LABEL="${1:-manual}"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$BACKUP_ROOT/$STAMP-$LABEL"

mkdir -p "$DEST"
echo ">> Backup set: $DEST"

echo ">> 1/5 Database dump ($DB_NAME)"
pg_dump -U "$DB_USER" -Fc --no-owner "$DB_NAME" > "$DEST/db.dump"

echo ">> 2/5 Filestore archive"
if [ -d "$FILESTORE" ]; then
    tar -czf "$DEST/filestore.tar.gz" -C "$(dirname "$FILESTORE")" "$(basename "$FILESTORE")"
else
    echo "WARNING: filestore not found at $FILESTORE" | tee "$DEST/filestore.MISSING"
fi

echo ">> 3/5 Configuration copy"
[ -f "$PROJECT_ROOT/odoo.conf" ] && cp "$PROJECT_ROOT/odoo.conf" "$DEST/odoo.conf.bak"

echo ">> 4/5 Git reference"
git -C "$PROJECT_ROOT" log -1 --format='%H %d %s' > "$DEST/git-ref.txt" 2>/dev/null || echo "no-git" > "$DEST/git-ref.txt"

echo ">> 5/5 Checksums + manifest"
( cd "$DEST" && shasum -a 256 db.dump filestore.tar.gz 2>/dev/null > SHA256SUMS ) || true
cat > "$DEST/manifest.json" <<EOF
{
  "database": "$DB_NAME",
  "timestamp": "$STAMP",
  "label": "$LABEL",
  "filestore_source": "$FILESTORE",
  "git_ref": "$(git -C "$PROJECT_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)",
  "db_dump_bytes": $(stat -f%z "$DEST/db.dump" 2>/dev/null || stat -c%s "$DEST/db.dump")
}
EOF

echo ">> DONE. Contents:"
ls -lh "$DEST"
echo ">> Off-server copy: sync this directory with your encrypted remote target"
echo ">>   (configure restic/rclone in deployment/.env — see docs/runbook-rollback.md)"
