#!/usr/bin/env python3
"""Diff two normalized snapshots of the same official source."""
from __future__ import annotations
import json,sys
from pathlib import Path
from collections import defaultdict

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def key(e): return (e.get("wordId"),e.get("listId"),e.get("pos",""),e.get("zh",""),e.get("level",""))
def main():
    old,new=map(load,sys.argv[1:3]); out=Path(sys.argv[3])
    a={key(e):e for e in old["entries"]}; b={key(e):e for e in new["entries"]}
    old_words=defaultdict(list); new_words=defaultdict(list)
    for e in old["entries"]: old_words[e["wordId"]].append(e)
    for e in new["entries"]: new_words[e["wordId"]].append(e)
    added=[b[k] for k in b.keys()-a.keys()]
    removed=[a[k] for k in a.keys()-b.keys()]
    changed=[]
    for wid in old_words.keys() & new_words.keys():
        if {key(x) for x in old_words[wid]} != {key(x) for x in new_words[wid]}:
            changed.append({"wordId":wid,"before":old_words[wid],"after":new_words[wid]})
    report={"schemaVersion":1,"from":old.get("sourceId"),"to":new.get("sourceId"),
      "counts":{"addedRows":len(added),"removedRows":len(removed),"changedWords":len(changed)},
      "added":added,"removed":removed,"changed":changed}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))
if __name__=="__main__": main()
