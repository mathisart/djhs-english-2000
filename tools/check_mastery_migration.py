#!/usr/bin/env python3
"""Check whether a new catalog can preserve word-keyed student mastery."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from collections import defaultdict
from vocab_identity import canonical_id

def old_words(path):
    t=Path(path).read_text(encoding="utf-8")
    m=re.search(r"window\.WORDS\s*=\s*(\[.*\])\s*;?\s*$",t,re.S)
    if not m: raise SystemExit("Cannot parse words.js")
    return json.loads(m.group(1))

def main():
    old=old_words(sys.argv[1]); new=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    oldmap=defaultdict(list); newmap=defaultdict(list)
    for w in old: oldmap[canonical_id(w["w"])].append(w["w"])
    for w in new["words"]: newmap[canonical_id(w["id"])].append(w["id"])
    shared=oldmap.keys() & newmap.keys()
    report={
      "oldRows":len(old),"oldCanonical":len(oldmap),"newCanonical":len(newmap),
      "sharedCanonical":len(shared),
      "oldNotInNew":sorted(oldmap.keys()-newmap.keys()),
      "newNotInOld":sorted(newmap.keys()-oldmap.keys()),
      "duplicateOldIds":{k:v for k,v in oldmap.items() if len(v)>1},
      "duplicateNewIds":{k:v for k,v in newmap.items() if len(v)>1}
    }
    Path(sys.argv[3]).parent.mkdir(parents=True,exist_ok=True)
    Path(sys.argv[3]).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:(len(v) if isinstance(v,(list,dict)) else v) for k,v in report.items()},ensure_ascii=False,indent=2))
    if report["duplicateNewIds"]: raise SystemExit("Migration unsafe: duplicate canonical IDs in new catalog")
if __name__=="__main__": main()
