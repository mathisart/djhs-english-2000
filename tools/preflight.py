#!/usr/bin/env python3
"""Run the mandatory pre-release checks in deterministic order."""
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
    run("tools/test_importers.py")
    for s in snaps: run("tools/validate_official.py",s)
    run("tools/release_check.py","data/official/sources.json",*snaps)
    print("OFFICIAL VOCABULARY PREFLIGHT: PASS")

if __name__=="__main__": main()
