#!/usr/bin/env python3
"""Validate normalized official vocabulary snapshots."""
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
    failures=[]
    if exact_dups: failures.append(f"{exact_dups} exact duplicate rows")
    if data.get("rejected"): failures.append(f"{len(data['rejected'])} rejected blocks")
    if data.get("layoutFragments") and data.get("review",{}).get("layoutFragments")!="pass": failures.append(f"{len(data['layoutFragments'])} layout fragments require review")
    if data.get("sourceId","").startswith("gept-"):
        valid_awl={f"L{i}" for i in range(1,11)}
        bad_awl=[e for e in entries if e.get("awl") and e["awl"] not in valid_awl]
        if bad_awl: failures.append(f"{len(bad_awl)} invalid AWL labels")
        valid_lists={"gept-elementary","gept-intermediate","gept-high-intermediate"}
        bad_lists=[e for e in entries if e.get("listId") not in valid_lists]
        if bad_lists: failures.append(f"{len(bad_lists)} invalid GEPT list IDs")
    if data.get("sourceId")=="moe-jh-108":
        if rows.get("moe-basic-1200")!=1200: failures.append(f"MOE basic rows={rows.get('moe-basic-1200',0)} expected=1200")
        if rows.get("moe-common-2000-extra")!=800: failures.append(f"MOE extra rows={rows.get('moe-common-2000-extra',0)} expected=800")
    report["failures"]=failures
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if failures: raise SystemExit("Validation failed: "+"; ".join(failures))
if __name__=="__main__": main()
