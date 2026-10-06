#!/usr/bin/env python3
"""Audit parser layout fragments before an official snapshot may be reviewed as safe."""
from __future__ import annotations
import json,sys
from pathlib import Path

SAFE_REASONS={
    "GEPT POS glossary row, not vocabulary",
    "Chinese continuation preceding deferred word/POS/level row",
    "Chinese continuation attached to deferred word/POS/level row",
}

def main():
    p=Path(sys.argv[1])
    output=Path(sys.argv[2]) if len(sys.argv)>2 else None
    data=json.loads(p.read_text(encoding="utf-8"))
    entries=data.get("entries",[])
    words={e.get("word") for e in entries}
    failures=[]; reviewed=[]
    for i,f in enumerate(data.get("layoutFragments",[])):
        reason=f.get("reason"); row_word=f.get("rowWord")
        ok=reason in SAFE_REASONS
        if reason.startswith("Chinese continuation"):
            ok=ok and bool(row_word) and row_word in words
        if not ok:
            failures.append({"index":i,"fragment":f})
        reviewed.append({"index":i,"ok":ok,"reason":reason,"rowWord":row_word})
    report={
        "sourceId":data.get("sourceId"),
        "sourceDocument":data.get("sourceDocument"),
        "fragments":len(data.get("layoutFragments",[])),
        "safe":len(reviewed)-len(failures),
        "failures":failures,
        "ok":not failures,
    }
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\\n"
    print(rendered,end="")
    if output:
        output.write_text(rendered,encoding="utf-8")
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
