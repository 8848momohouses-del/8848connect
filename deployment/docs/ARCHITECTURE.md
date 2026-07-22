# 8848 Business Suite - Production Architecture

## Overview
The platform uses a single-node Linux VPS (Ubuntu LTS) with Docker Compose for the Odoo stack and a host-level Nginx reverse proxy.

## Components

### 1. Nginx Reverse Proxy (Host Level)
- Handles incoming HTTP/HTTPS traffic.
- Forces HTTPS via Let's Encrypt managed SSL.
- Proxies `erp.8848momofactory.com`, `portal.8848momofactory.com`, and `api.8848momofactory.com` to the Odoo Docker container.
- Separates Longpolling/Websockets (port 8072) from standard HTTP (port 8069).
- Caches static `/web/static/` assets for performance.

### 2. Odoo Container (Docker)
- Runs Odoo 19 Community.
- Mounts `8848-connect-addons` as read-only.
- Mounts custom `odoo.conf` as read-only.
- Maps `/var/lib/odoo` to a Docker Volume for persistent filestore.

### 3. PostgreSQL Container (Docker)
- Runs PostgreSQL 16 Alpine.
- Maps `/var/lib/postgresql/data` to a Docker Volume.
- Isolated in a private bridge network (`internal_net`), inaccessible from the public internet.

## Network Architecture
- **Port 80/443 (Host)** -> Nginx -> Proxies to `127.0.0.1:8069` & `8072` (Docker exposed ports).
- **Docker `internal_net`** -> Connects Odoo and PostgreSQL internally.

## Security Model
- No database ports exposed to the host network.
- HTTPS enforced at the edge.
- Docker containers run isolated.
- `.env` isolates all secrets from the codebase.
- Independent from WordPress marketing site (no shared auth or db).
