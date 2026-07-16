# Deployment Architecture

## Prerequisites
- **Odoo Version:** STRICTLY Odoo 19.0. (No `latest` tags used).
- **PostgreSQL Version:** 16
- **Reverse Proxy:** Nginx (Handles SSL, Websocket upgrades on port 8072, and static file caching).

## Automated Assertions
The deployment pipeline (GitHub Actions) contains explicit version assertions against the running Odoo binary to prevent environment drift or accidental Odoo 17/18 deployments.
