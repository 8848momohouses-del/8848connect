#!/usr/bin/env bash
# Deploy 8848 Business Suite to production
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Pulling latest docker images..."
docker compose pull

echo "Restarting containers..."
docker compose up -d --remove-orphans

echo "Deployment triggered successfully."
echo "Running healthcheck..."
./scripts/healthcheck.sh
