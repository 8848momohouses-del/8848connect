# 8848 Business Suite – Development Rules (Mandatory)

## Project Vision
This is not a collection of independent Odoo modules. It is a single, enterprise-grade ERP
platform built on **Odoo 19 Community Edition** exclusively for **8848 Momo House**.
Every module must work together as one system using a unified data model. The platform
manages the complete lifecycle of a franchise from first website enquiry through ongoing
operations for many years.

## Core Principle — One Franchise. One Record. One Source of Truth.
A person who submits a franchise enquiry must never become multiple records; their
information grows over time on the same Franchise Master Record.

Lifecycle: Website Visitor → Franchise Inquiry → CRM Lead → Brochure Sent → Application
Submitted → Qualified → Discovery Meeting → Agreement Signed → Deposit Received → Training
→ Store Fit-out → Grand Opening → Active Franchise → Operational Store → Renewal/Expansion.

Every module must use the same Franchise Master Record.

## Existing Codebase Policy (Very Important)
Before writing any code, ANALYSE the existing project: all custom modules, every model,
controller, XML view, security rule, workflow, relationship, menu, setting, scheduled
action, API, database field, dependency, and naming convention. Only then implement.

- Never assume something does not already exist.
- If functionality exists: reuse it, extend it, or refactor it carefully.
- Never create duplicate models, fields, APIs, or menus.
- Never break existing functionality.
- All changes remain backwards compatible unless explicitly instructed otherwise.

## Safe Development Rules
Every new feature must preserve: existing data, existing APIs, database integrity,
security, permissions, and current workflows.

If a database migration is required: explain it first, make it reversible where
practical, and never delete existing data.

## Module Dependency Rules
Every module must depend on the central Franchise Core module. Target architecture:

```
franchise_core
├── franchise_crm          ├── franchise_documents    ├── franchise_email
├── franchise_portal       ├── franchise_factory      ├── franchise_inventory
├── franchise_manufacturing├── franchise_accounting   ├── franchise_royalty
├── franchise_marketing    ├── franchise_support      ├── franchise_training
├── franchise_audit        ├── franchise_reports
```

No module may become an isolated system.

## Document Management
Every franchise automatically receives its own secure workspace. Uploaded documents are
auto-filed into categories (Initial Enquiry, Brochure, Applications, Agreements, Legal,
Financial, Statements, Royalty, Marketing Levy, Licences, Insurance, Food Safety, Council
Approvals, Lease, Training, Operations Manuals, Marketing Assets, Audit Reports, Cleaning
Audits, Food Safety Audits, Equipment Maintenance, Store Photos, Incident Reports,
Customer Complaints, Emails, Notes, Factory Orders, Delivery Records, Invoices, Credit
Notes, Payment History). Staff never manually organise files.

## Audit & Compliance System
Every active franchise participates in scheduled operational audits: daily checks
(optional), weekly operational inspections, monthly cleanliness audits, quarterly
compliance audits, food safety, brand standard, equipment, kitchen hygiene, staff
presentation, customer service, product quality, and marketing compliance reviews.

Each audit includes: checklist items, pass/fail scoring, numerical score, inspector
notes, corrective actions, due dates, assigned staff, before/after photos, attachments,
digital signatures, and automatic follow-up tasks. Every audit is permanent franchise
history. Repeated failures auto-generate alerts and management notifications. Audit
history surfaces in dashboards and reports.

## Portal Activation Rules
The Franchise Portal stays disabled until: franchise approved AND agreement signed AND
deposit received AND grand opening completed. Once operational it enables: factory
ordering, product catalogue, statements, royalty, marketing levy, delivery tracking,
training, marketing downloads, support tickets, account management.

## Development Workflow (every feature)
1. Analyse the existing implementation.
2. Explain the proposed design.
3. List every affected file.
4. Explain why each file changes.
5. Generate complete production-ready code.
6. Explain installation.
7. Explain testing.
8. Verify compatibility with previous modules.
9. Ensure no regressions are introduced.
10. Wait for confirmation before proceeding.

Never generate placeholder code. Never generate TODO comments. Never overwrite working
functionality. Never redesign an existing feature without a technical reason and an
explained migration path.

---

# Current Codebase Map (maintained by Claude — update when modules change)

Environment: Odoo 19.0 Community (vendored in `odoo/`), Python 3.14 venv (`venv/`,
run via `venv/bin/python setup/odoo -c odoo.conf`), PostgreSQL DB `Momohouse`,
custom addons in `8848-connect-addons/` (in addons_path). Git repo at project root.

Installed custom modules (as of 2026-07-15):
- `8848_core_branding` — brand layout/login overrides, fonts; owns the sequence-0
  "Dashboard" root menu (`menu_8848_dashboard_root`).
- `8848_glass_skin` — recolors `theme_liquid_glass` (vendored Cybrosys backend theme)
  to brand red/white/blue via SCSS variable injection; brand gradient background.
- `8848_dashboard` — board-based Factory Dashboard (store performance + royalty
  widgets); it is the login landing action (`action_8848_factory_dashboard`).
- `8848_franchise` — Franchise Master embryo: `res.partner` extension (`is_franchise`,
  `store_id`, `territory`, `franchise_status`, `royalty_percentage`,
  `marketing_fee_percentage`) + Franchise app menu. THIS is the current Franchise
  Core; extend it rather than creating a parallel model.
- `8848_royalty`, `8848_marketing_fee`, `8848_store_performance` — Phase 3 financial
  modules built on `8848_franchise`.
- `8848_factory`, `8848_inventory`, `8848_warehouse` (stock.lot QA/expiry fields),
  `8848_quality` — manufacturing/inventory layer.
- `8848_delivery`, `8848_driver`, `8848_portal`, `8848_supplier` — WIP.
- `sign_oca` 19.0.1.0.0 (OCA) — document e-signature (use for agreement signing).
- `theme_liquid_glass` — third-party theme, vendored; never edit its files directly
  (override via `8848_glass_skin`).

Known conventions: module prefix `8848_`, LGPL-3, version strings currently `1.0`.
Enterprise-only modules (knowledge, studio, barcode, planning, mrp_mps, quality
worksheets…) are NOT available — Community-safe implementations only.
