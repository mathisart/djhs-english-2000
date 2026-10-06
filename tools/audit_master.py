#!/usr/bin/env python3
"""Audit current words.js before official migration."""
from __future__ import annotations
import json,re,sys
from collections import defaultdict,Counter
from pathlib import Path
from vocab_identity import canonical_id

def load(path):
    t=Path(path).read_text(encoding="utf-8")
    m=re.search(r"window\.WORDS\s*=\s*(\[.*\])\s*;?\s*$",t,re.S)
    if not m: raise SystemExit("Cannot parse window.WORDS")
    return json.loads(m.group(1))

def main():
    words=load(sys.argv[1]); out=Path(sys.argv[2])
    ids=defaultdict(list); missing=Counter()
    for i,w in enumerate(words):
        ids[canonical_id(w.get("w",""))].append({"index":i,"word":w.get("w"),"pos":w.get("p"),"zh":w.get("z")})
        for k in ("w","p","z"): 
            if not w.get(k): missing[k]+=1
    duplicates={k:v for k,v in ids.items() if len(v)>1}
    report={"rows":len(words),"canonicalWords":len(ids),"duplicateCanonicalIds":len(duplicates),
      "missingRequiredFields":dict(missing),"duplicates":duplicates}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="duplicates"},ensure_ascii=False,indent=2))
    if missing.get("w"): raise SystemExit("Master contains rows without word form")
if __name__=="__main__": main()
