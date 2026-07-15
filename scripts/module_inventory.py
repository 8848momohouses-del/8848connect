#!/usr/bin/env python3
"""8848 Business Suite — module inventory validation (Milestone 0).

Compares the modules installed in the database against the committed
baseline inventory (docs/module-inventory.json). Fails when a baseline
module is missing, uninstalled, or was removed from the addons tree.

Usage: python3 scripts/module_inventory.py [--db Momohouse] [--user suraj]
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "docs" / "module-inventory.json"


def db_modules(db: str, user: str) -> dict:
    query = (
        "SELECT name, COALESCE(latest_version,'?'), state FROM ir_module_module "
        "WHERE name LIKE '8848%' OR name IN ('sign_oca','theme_liquid_glass') "
        "ORDER BY name;"
    )
    out = subprocess.check_output(
        ["psql", "-U", user, "-d", db, "-tA", "-F", "|", "-c", query], text=True
    )
    mods = {}
    for line in out.strip().splitlines():
        name, ver, state = line.split("|")
        mods[name] = {"version": ver, "state": state}
    return mods


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="Momohouse")
    parser.add_argument("--user", default="suraj")
    args = parser.parse_args()

    baseline = json.loads(INVENTORY.read_text())["modules"]
    current = db_modules(args.db, args.user)
    errors, warnings = [], []

    for name, info in baseline.items():
        cur = current.get(name)
        if cur is None:
            errors.append(f"MISSING from DB: {name}")
        elif info["state"] == "installed" and cur["state"] != "installed":
            errors.append(f"STATE REGRESSION: {name} was installed, now {cur['state']}")
        elif cur["version"] != info["version"] and cur["state"] == "installed":
            warnings.append(
                f"version changed: {name} {info['version']} -> {cur['version']} (expected after upgrades)"
            )
        addon_dir = ROOT / "8848-connect-addons" / name
        if not addon_dir.is_dir():
            errors.append(f"MISSING from addons tree: {name}")

    for name in current:
        if name not in baseline:
            warnings.append(f"new module not in baseline: {name} (update inventory on release)")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"checked {len(baseline)} baseline modules against DB '{args.db}': "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
