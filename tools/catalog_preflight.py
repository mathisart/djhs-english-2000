#!/usr/bin/env python3
"""Post-verification catalog release QA.

Run only after snapshot preflight and human review have marked snapshots verified.
"""
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    print("+"," ".join(map(str,args)))
    subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
def main():
    if len(sys.argv)<2: raise SystemExit("usage: catalog_preflight.py SNAPSHOT [SNAPSHOT...]")
    snaps=sys.argv[1:]
    run("tools/check_identity_review.py","data/official/reports/identity-collision-review.json","--release")
    catalog="data/official/generated/catalog.json"
    migration="data/official/generated/mastery-migration.json"
    run("tools/build_catalog.py","data/official/lists.json",*snaps,catalog)
    run("tools/check_mastery_migration.py","words.js",catalog,migration)
    print("CATALOG MIGRATION PREFLIGHT: PASS")
if __name__=="__main__": main()
