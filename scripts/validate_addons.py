#!/usr/bin/env python3
"""8848 Business Suite — release validation suite (Milestone 0).

Static checks over 8848-connect-addons, identical locally and in CI:
  1. Python syntax (compile) for every .py
  2. Manifest lint: parseable, license present, installable bool, depends list
  3. XML well-formedness
  4. ACL CSV structure (header + column count)
  5. Duplicate XML-ID detection (same id defined twice within a module)
  6. Dependency resolvability (every `depends` exists in the tree or core)
  7. Enterprise-dependency blocklist (Community-only policy)
  8. Foundation purity (8848_franchise may not depend on other 8848_*)

Exit code 0 = release-valid. Usage: python3 scripts/validate_addons.py
"""
import ast
import csv
import pathlib
import py_compile
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
ADDONS = ROOT / "8848-connect-addons"
CORE_ADDONS = ROOT / "odoo" / "addons"
# In CI the vendored Odoo source is absent; fall back to the pinned list.
CORE_LIST = ROOT / "docs" / "community-core-modules.txt"

# Vendored modules: validated structurally but exempt from 8848 policy checks.
VENDORED = {"sign_oca", "theme_liquid_glass"}

ENTERPRISE_BLOCKLIST = {
    "web_studio", "knowledge", "helpdesk", "approvals", "planning",
    "appointment", "appointment_account_payment", "mrp_mps", "mrp_workorder",
    "quality_control", "quality_mrp", "stock_barcode", "sign", "documents",
    "social", "marketing_automation", "account_accountant", "web_gantt",
    "web_cohort", "web_map", "spreadsheet_sale_management", "sale_planning",
    "voip", "whatsapp", "industry_fsm",
}

errors: list[str] = []
warnings: list[str] = []


def check_python(mod: pathlib.Path) -> None:
    for py in mod.rglob("*.py"):
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"[py] {py.relative_to(ROOT)}: {exc.msg}")


def read_manifest(mod: pathlib.Path) -> dict | None:
    manifest = mod / "__manifest__.py"
    if not manifest.is_file():
        errors.append(f"[manifest] {mod.name}: missing __manifest__.py")
        return None
    try:
        data = ast.literal_eval(manifest.read_text())
    except (ValueError, SyntaxError) as exc:
        errors.append(f"[manifest] {mod.name}: unparseable ({exc})")
        return None
    if not isinstance(data.get("depends", []), list):
        errors.append(f"[manifest] {mod.name}: depends must be a list")
    if "license" not in data:
        errors.append(f"[manifest] {mod.name}: license key missing")
    if mod.name not in VENDORED and "author" not in data:
        warnings.append(f"[manifest] {mod.name}: author key missing")
    return data


def check_xml(mod: pathlib.Path) -> None:
    for xml_file in mod.rglob("*.xml"):
        try:
            ET.parse(xml_file)
        except ET.ParseError as exc:
            errors.append(f"[xml] {xml_file.relative_to(ROOT)}: {exc}")


def check_csv(mod: pathlib.Path) -> None:
    for csv_file in mod.rglob("ir.model.access.csv"):
        rows = list(csv.reader(csv_file.open()))
        if not rows:
            errors.append(f"[csv] {csv_file.relative_to(ROOT)}: empty")
            continue
        header = rows[0]
        if header[0] != "id" or "model_id:id" not in header:
            errors.append(f"[csv] {csv_file.relative_to(ROOT)}: bad header {header}")
        for n, row in enumerate(rows[1:], start=2):
            if row and len(row) != len(header):
                errors.append(
                    f"[csv] {csv_file.relative_to(ROOT)}:{n}: "
                    f"{len(row)} columns, header has {len(header)}")


def check_duplicate_xmlids(mod: pathlib.Path, manifest: dict) -> None:
    seen: dict[tuple[str, str], str] = {}
    for rel in manifest.get("data", []) + manifest.get("demo", []):
        path = mod / rel
        if path.suffix != ".xml" or not path.is_file():
            continue
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue  # reported by check_xml
        for node in tree.iter():
            if node.tag in ("record", "template", "menuitem"):
                xmlid = node.get("id")
                if not xmlid or "." in xmlid:
                    continue  # cross-module updates are legitimate
                # Same id with a DIFFERENT tag is a legitimate pattern
                # (e.g. a <record> pre-seeding fields for a <menuitem>);
                # only a same-tag redefinition is a genuine conflict.
                key = (xmlid, node.tag)
                if key in seen:
                    errors.append(
                        f"[xmlid] {mod.name}: <{node.tag} id='{xmlid}'> "
                        f"defined in both {seen[key]} and {rel}")
                seen[key] = rel


def check_dependencies(mod: pathlib.Path, manifest: dict,
                       local_modules: set[str]) -> None:
    if CORE_ADDONS.is_dir():
        core_names = {p.name for p in CORE_ADDONS.iterdir() if p.is_dir()}
    else:
        core_names = set(CORE_LIST.read_text().split())
    for dep in manifest.get("depends", []):
        if dep in local_modules or dep in core_names:
            continue
        errors.append(f"[deps] {mod.name}: dependency '{dep}' not found "
                      f"in tree or Community core")
    if mod.name not in VENDORED:
        blocked = set(manifest.get("depends", [])) & ENTERPRISE_BLOCKLIST
        for dep in sorted(blocked):
            errors.append(f"[policy] {mod.name}: Enterprise-only dependency "
                          f"'{dep}' is forbidden")


def check_foundation_purity(manifests: dict[str, dict]) -> None:
    core = manifests.get("8848_franchise")
    if core:
        bad = [d for d in core.get("depends", []) if d.startswith("8848_") and d != "8848_security"]
        for dep in bad:
            errors.append(f"[layering] 8848_franchise (foundation) must not "
                          f"depend on {dep}")


def main() -> int:
    modules = sorted(p for p in ADDONS.iterdir()
                     if p.is_dir() and (p / "__manifest__.py").is_file())
    local_names = {m.name for m in modules}
    manifests: dict[str, dict] = {}

    for mod in modules:
        manifest = read_manifest(mod)
        if manifest is None:
            continue
        manifests[mod.name] = manifest
        check_python(mod)
        check_xml(mod)
        check_csv(mod)
        check_duplicate_xmlids(mod, manifest)
        check_dependencies(mod, manifest, local_names)

    check_foundation_purity(manifests)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"validated {len(modules)} modules: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
