#!/usr/bin/env python3
"""Cross-check cumulative GEPT snapshots parsed independently from official PDFs."""
from __future__ import annotations
import json,sys
from pathlib import Path

ELEMENTARY="gept-elementary"
INTERMEDIATE="gept-intermediate"
HIGH="gept-high-intermediate"

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def row_key(e):
    return (
        e.get("wordId",""),
        e.get("pos",""),
        e.get("zh",""),
        e.get("level",""),
        e.get("awl",""),
    )

def rows(data,lid):
    return {row_key(e) for e in data["entries"] if e.get("listId")==lid}

def words(rowset):
    return {r[0] for r in rowset}

def diff(label,left,right):
    missing=sorted(left-right)
    unexpected=sorted(right-left)
    return {
        "label":label,
        "missingRows":missing,
        "unexpectedRows":unexpected,
        "missingWords":sorted(words(left)-words(right)),
        "unexpectedWords":sorted(words(right)-words(left)),
    }

def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: crosscheck_gept.py ELEMENTARY INTERMEDIATE HIGH_INTERMEDIATE OUT")
    elementary,intermediate,high=map(load,sys.argv[1:4])
    out=Path(sys.argv[4])

    checks=[
        diff("elementary_vs_intermediate",rows(elementary,ELEMENTARY),rows(intermediate,ELEMENTARY)),
        diff("elementary_vs_high",rows(elementary,ELEMENTARY),rows(high,ELEMENTARY)),
        diff("intermediate_vs_high",rows(intermediate,INTERMEDIATE),rows(high,INTERMEDIATE)),
    ]
    report={
        "schemaVersion":2,
        "ok":all(not c["missingRows"] and not c["unexpectedRows"] for c in checks),
        "checks":checks,
        "counts":{
            c["label"]:{
                "missingRows":len(c["missingRows"]),
                "unexpectedRows":len(c["unexpectedRows"]),
                "missingWords":len(c["missingWords"]),
                "unexpectedWords":len(c["unexpectedWords"]),
            } for c in checks
        },
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))
    if not report["ok"]:
        raise SystemExit("GEPT cumulative row/sense cross-check failed")

if __name__=="__main__":
    main()
