#!/usr/bin/env python3
"""Cross-check cumulative GEPT snapshots parsed from the three official PDFs."""
from __future__ import annotations
import json,sys
from pathlib import Path
from collections import defaultdict

ORDER=["gept-elementary","gept-intermediate","gept-high-intermediate"]

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def ids(data,lids):
    out=defaultdict(set)
    for e in data["entries"]:
        if e["listId"] in lids: out[e["listId"]].add(e["wordId"])
    return out

def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: crosscheck_gept.py ELEMENTARY INTERMEDIATE HIGH_INTERMEDIATE OUT")
    elementary,intermediate,high=map(load,sys.argv[1:4]); out=Path(sys.argv[4])
    a=ids(elementary,{"gept-elementary"})
    b=ids(intermediate,{"gept-elementary","gept-intermediate"})
    c=ids(high,set(ORDER))
    checks={
      "elementaryMissingFromIntermediate":sorted(a["gept-elementary"]-b["gept-elementary"]),
      "elementaryMissingFromHigh":sorted(a["gept-elementary"]-c["gept-elementary"]),
      "intermediateMissingFromHigh":sorted(b["gept-intermediate"]-c["gept-intermediate"]),
      "elementaryUnexpectedInIntermediate":sorted(b["gept-elementary"]-a["gept-elementary"]),
      "elementaryUnexpectedInHigh":sorted(c["gept-elementary"]-a["gept-elementary"]),
      "intermediateUnexpectedInHigh":sorted(c["gept-intermediate"]-b["gept-intermediate"])
    }
    report={"schemaVersion":1,"counts":{k:len(v) for k,v in checks.items()},"details":checks}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))
    if any(checks.values()): raise SystemExit("GEPT cumulative PDF cross-check failed")
if __name__=="__main__": main()
