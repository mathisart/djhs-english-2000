#!/usr/bin/env python3
"""Diff a normalized official snapshot against the current master vocabulary.

Usage:
  python tools/diff_official.py data/official/generated/moe.json words.js report.json

This tool never edits production data.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from collections import defaultdict

def canon(s):
    return re.sub(r"\s+"," ",s.strip()).casefold()

def load_words_js(path):
    text=Path(path).read_text(encoding="utf-8")
    m=re.search(r"window\.WORDS\s*=\s*(\[.*\])\s*;?\s*$",text,re.S)
    if not m: raise SystemExit("Could not parse window.WORDS")
    return json.loads(m.group(1))

def load_official(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    off=load_official(sys.argv[1]); master=load_words_js(sys.argv[2])
    out_path=Path(sys.argv[3])
    by_id=defaultdict(list)
    for w in master: by_id[canon(w["w"])].append(w)

    matched=[]; alias_matched=[]; missing=[]; ambiguous=[]
    official_ids=set()
    for e in off["entries"]:
        wid=canon(e.get("wordId") or e.get("word") or e.get("officialEntry",""))
        official_ids.add(wid)
        hits=by_id.get(wid,[])
        if len(hits)==1:
            matched.append({"official":e,"master":hits[0]})
            continue
        if len(hits)>1:
            ambiguous.append({"official":e,"reason":"duplicate-master-id","candidates":hits})
            continue
        aliases=[canon(a) for a in e.get("aliases",[]) if canon(a)!=wid]
        ah=[(a,by_id[a]) for a in aliases if a in by_id]
        flat=[x for _,xs in ah for x in xs]
        if len(flat)==1:
            alias_matched.append({"official":e,"alias":next(a for a,xs in ah if flat[0] in xs),"master":flat[0]})
        elif flat:
            ambiguous.append({"official":e,"reason":"multiple-alias-candidates","candidates":flat})
        else:
            missing.append(e)

    master_extra=[w for w in master if canon(w["w"]) not in official_ids]
    report={
      "schemaVersion":1,
      "sourceId":off.get("sourceId"),
      "masterCount":len(master),
      "officialRows":len(off["entries"]),
      "officialUniqueIds":len(official_ids),
      "counts":{"exactMatched":len(matched),"aliasMatched":len(alias_matched),
                "missingFromMaster":len(missing),"ambiguous":len(ambiguous),
                "masterOutsideOfficialUniqueIds":len(master_extra)},
      "missingFromMaster":missing,
      "aliasMatched":alias_matched,
      "ambiguous":ambiguous,
      "masterOutsideOfficialUniqueIds":master_extra
    }
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))

if __name__=="__main__": main()
