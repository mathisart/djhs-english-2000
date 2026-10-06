#!/usr/bin/env python3
"""Validate normalized official vocabulary snapshots and emit a diff summary."""
from __future__ import annotations
import json,sys
from collections import Counter,defaultdict
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    data=load(sys.argv[1]); entries=data["entries"]
    rows=Counter(e["listId"] for e in entries)
    words=defaultdict(set)
    for e in entries: words[e["listId"]].add(e["wordId"])
    dup=Counter((e["listId"],e["wordId"],e.get("pos",""),e.get("zh","")) for e in entries)
    exact_dups=sum(v-1 for v in dup.values() if v>1)
    report={"sourceId":data.get("sourceId"),"rowsByList":dict(rows),
      "uniqueWordsByList":{k:len(v) for k,v in words.items()},
      "exactDuplicateRows":exact_dups,
      "overlap":{
        "elementary_intermediate":len(words["gept-elementary"] & words["gept-intermediate"]),
        "intermediate_highIntermediate":len(words["gept-intermediate"] & words["gept-high-intermediate"])
      }}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if exact_dups: raise SystemExit("Validation failed: exact duplicate rows found")
if __name__=="__main__": main()
