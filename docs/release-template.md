# Release: vYYYY.MM.N — <title>

## Summary
<one paragraph: what this release delivers>

## Release manifest (ONLY these modules are upgraded — never "all")
| Module | Action (-i / -u) | Why |
|--------|------------------|-----|
|        |                  |     |

## Expected database changes
<new tables/columns; must be additive per Safe Development Rules>

## Pre-deployment checklist
- [ ] CI green on the release tag (validate + install-test)
- [ ] Staging deployed from this tag, prod-copy DB upgraded, acceptance done
- [ ] Regression suites pass on staging (baseline_8848 tags)
- [ ] Pre-deployment backup taken: `scripts/backup.sh <tag>` → id: ______
- [ ] Backup verified (checksums + off-server copy)
- [ ] docs/module-inventory.json updated if modules were added

## Rollback plan
- Backup id: ______
- Steps: docs/runbook-rollback.md §<n>
- Maximum acceptable downtime: 30 minutes

## Post-deployment verification
- [ ] scripts/healthcheck.sh (erp + portal + api hosts)
- [ ] scripts/module_inventory.py clean
- [ ] Smoke: login, Factory Dashboard, Franchisees kanban, portal /my/franchise
- [ ] Monitoring green for 30 minutes
