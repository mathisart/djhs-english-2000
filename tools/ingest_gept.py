#!/usr/bin/env python3
"""Normalize and cross-check the three official LTTC GEPT cumulative text extracts."""
from __future__ import annotations
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

DOCS=[
 ("elementary","GEPT_Elementary.pdf","https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_Elementary.pdf"),
 ("intermediate","GEPT_Intermediate.pdf","https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_Intermediate.pdf"),
 ("high-intermediate","GEPT_High-Intermediate.pdf","https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_High-Intermediate.pdf")
]
def run(*args):
    print("+"," ".join(map(str,args)))
    subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,check=True)
def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: ingest_gept.py ELEMENTARY.txt INTERMEDIATE.txt HIGH_INTERMEDIATE.txt OUTPUT_DIR")
    inputs=sys.argv[1:4]; out=Path(sys.argv[4]); out.mkdir(parents=True,exist_ok=True)
    snapshots=[]
    for src,(slug,doc,url) in zip(inputs,DOCS):
        dest=out/f"gept-2026-04-29-{slug}.json"
        run("tools/import_gept.py",src,dest,doc,url); snapshots.append(str(dest))
    report=out/"gept-2026-04-29-crosscheck.json"
    run("tools/crosscheck_gept.py",*snapshots,report)
    print("GEPT INGEST: PASS")
    print("Catalog source:",snapshots[2])
if __name__=="__main__": main()
