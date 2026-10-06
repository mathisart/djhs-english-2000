#!/usr/bin/env python3
"""Generate a compact auditable report for an official vocabulary release."""
from __future__ import annotations
import json,sys
from pathlib import Path
from datetime import datetime,timezone

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    if len(sys.argv)!=6:
        raise SystemExit("usage: release_report.py SOURCES CATALOG MASTER_AUDIT DIFF MIGRATION OUT")
    sources,catalog,audit,diff,migration=map(load,sys.argv[1:6])
    out=Path(sys.argv[6]) if len(sys.argv)>6 else None
    # Kept explicit below for compatibility with the intended six-input CLI.
if __name__=="__main__": main()
