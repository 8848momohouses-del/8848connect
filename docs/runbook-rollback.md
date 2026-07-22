# 8848 Business Suite — Rollback Runbook (Milestone 0)

Every production release MUST have a pre-deployment backup created with
`scripts/backup.sh <release-tag>` and verified per the checklist below
**before** any module upgrade runs.

## Backup verification checklist (pre-deploy, mandatory)
1. `SHA256SUMS` verifies: `cd <backup-dir> && shasum -a 256 -c SHA256SUMS`
2. `manifest.json` lists the expected database and git ref
3. Off-server encrypted copy completed (restic/rclone per deployment/.env)
4. Restore drill current (monthly): last drill date recorded below

## Rollback procedures by failure type

### 1. Failed module installation
Odoo rolls the transaction back automatically (verified behaviour: failed
installs leave the DB intact). Actions: redeploy the previous git tag,
restart the service, run `scripts/healthcheck.sh`. No DB restore needed
unless `ir.module.module` shows the module stuck in a pending state — then
restore per §2.

### 2. Failed module upgrade / migration failure
1. Stop Odoo: `docker compose stop odoo` (prod) / kill local process
2. Restore: `scripts/restore.sh <backup-dir> <db-name> --force --with-filestore`
3. Check out / deploy the previous release tag
4. Start Odoo, run `scripts/healthcheck.sh` + `scripts/module_inventory.py`
5. Record the incident in the release ticket

### 3. Broken XML view (post-deploy discovery)
Views are data: prefer fix-forward via hotfix branch, `-u <module>` for the
single affected module. If the backend is unusable, restore per §2.

### 4. Broken Python model / server error
Code-only rollback: previous image/tag redeploy. The DB is untouched if the
release manifest ran no upgrades; otherwise restore per §2.

### 5. Corrupt deployment
Rebuild containers from pinned image tags, re-render config from templates,
restore latest verified backup per §2.

### 6. Complete server failure
1. Provision replacement VPS (Ubuntu LTS, root, Docker)
2. Clone repo at the last production tag; `deployment/` stack up
3. Restore latest off-server backup set per §2
4. Re-point DNS (erp/portal/api A records); target RTO ≤ 4 hours

## Release ticket requirements (every release)
- Pre-deployment backup id (directory name)
- Release manifest: EXACT modules to `-u` (never "all")
- Expected schema changes
- Rollback steps (reference this runbook + backup id)
- Maximum acceptable downtime (default: 30 minutes)

## Pending decisions (recorded, not yet approved)
- Untrack local `odoo.conf` in favour of `config/odoo.conf.example`
- Backend access model for erp.8848momofactory.com: IP allowlist vs VPN
- Spaceship plan confirmation: root-access KVM VPS (Docker requirement)
- Off-server backup target + restic credentials

## Drill log
| Date | Type | Result |
|------|------|--------|
| 2026-07-15 | Full restore to scratch DB (local) | PASS — 798 tables, 176 modules, data verified |
