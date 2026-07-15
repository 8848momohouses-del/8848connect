#!/usr/bin/env bash
# 8848 Business Suite — HTTP health check (Milestone 0)
# Exit 0 when the Odoo login page answers 200 within the timeout.
# Usage: scripts/healthcheck.sh [base-url]
set -euo pipefail

BASE_URL="${1:-${ODOO_URL:-http://localhost:8069}}"
TIMEOUT="${HEALTH_TIMEOUT:-10}"

code=$(curl -s -o /dev/null -m "$TIMEOUT" -w "%{http_code}" "$BASE_URL/web/login" || echo "000")
if [ "$code" = "200" ]; then
    echo "OK: $BASE_URL/web/login -> 200"
    exit 0
fi
echo "FAIL: $BASE_URL/web/login -> $code"
exit 1
