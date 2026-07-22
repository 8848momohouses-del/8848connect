# 8848 Business Suite - Production Runbook

## 1. Pre-Deployment Setup (VPS Provisioning)
1. **Provision Ubuntu 24.04 LTS** VPS.
2. **Install Dependencies**:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx git
   ```
3. **Configure DNS**:
   - Create A records for `erp.8848momofactory.com`, `portal.8848momofactory.com`, and `api.8848momofactory.com` pointing to the VPS IP.
4. **Clone Repository**:
   ```bash
   sudo mkdir -p /opt/8848-connect
   sudo chown $USER:$USER /opt/8848-connect
   git clone <repo_url> /opt/8848-connect
   cd /opt/8848-connect
   ```

## 2. Environment Configuration
1. Copy the example environment file:
   ```bash
   cd deployment
   cp .env.example .env
   ```
2. Edit `.env` to include the highly secure `DB_PASSWORD` and `ADMIN_PASSWORD`.

## 3. Nginx and SSL Configuration
1. Symlink Nginx configuration:
   ```bash
   sudo ln -s /opt/8848-connect/deployment/nginx/odoo.conf /etc/nginx/sites-available/odoo.conf
   sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/
   ```
2. Test Nginx and Restart:
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```
3. Provision SSL via Certbot:
   ```bash
   sudo certbot --nginx -d erp.8848momofactory.com -d portal.8848momofactory.com -d api.8848momofactory.com
   ```

## 4. Initial Deployment
1. Make deployment scripts executable:
   ```bash
   chmod +x deployment/scripts/*.sh
   ```
2. Run deployment:
   ```bash
   ./deployment/scripts/deploy.sh
   ```
3. Wait for Health Checks to complete successfully.

## 5. Daily Backup and Disaster Recovery
- Add a cron job to automatically backup nightly:
  ```bash
  0 2 * * * /opt/8848-connect/deployment/scripts/backup.sh >> /var/log/8848-backup.log 2>&1
  ```
- **Disaster Recovery**:
  If the server is destroyed, provision a new VPS, clone the repo, run Setup steps 1-3, then run:
  ```bash
  ./deployment/scripts/restore.sh <path_to_db_backup.sql.gz> <path_to_filestore.tar.gz>
  ```

## 6. GitHub CI/CD Configuration
- In the GitHub repository Settings > Secrets and Variables > Actions, add:
  - `PROD_SERVER_IP`: VPS Public IP.
  - `PROD_SSH_USER`: the deploy user (e.g., `ubuntu`).
  - `PROD_SSH_PRIVATE_KEY`: Private SSH key authorized for the VPS deploy user.
