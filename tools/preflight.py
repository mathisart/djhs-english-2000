#!/usr/bin/env python3
"""Run mandatory snapshot-stage checks in deterministic order."""
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    print("+"," ".join(map(str,args)))
    subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
def main():
    if len(sys.argv)<2:
        raise SystemExit("usage: python tools/preflight.py SNAPSHOT [SNAPSHOT...]")
    snaps=sys.argv[1:]
    run("tools/validate_manifests.py","data/official/sources.json","data/official/lists.json")
    run("tools/test_importers.py")
    run("tools/audit_master.py","words.js","data/official/generated/master-audit.json")
    for s in snaps: run("tools/validate_official.py",s)
    run("tools/release_check.py","data/official/sources.json",*snaps)
    print("OFFICIAL VOCABULARY SNAPSHOT PREFLIGHT: PASS")
    print("Next: build catalog -> check_mastery_migration.py -> release_report.py")
if __name__=="__main__": main()
