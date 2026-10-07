#!/usr/bin/env python3
"""Cross-check current learning master against authoritative cumulative GEPT rows.

Diagnostic only. GEPT level is sense/POS-specific, so official rows are preserved
instead of flattening a canonical word to one level.
"""
from __future__ import annotations
import json,sys
from collections import defaultdict,Counter
from pathlib import Path
from vocab_identity import canonical_id,pos_tokens
from diff_official import load_words_js

LEVEL_ORDER={"gept-elementary":0,"gept-intermediate":1,"gept-high-intermediate":2}

def build_report(official,master):
    if official.get("catalogRole")!="authoritative":
        raise ValueError("GEPT master cross-check requires authoritative cumulative snapshot")

    by_id=defaultdict(list)
    for row in official.get("entries",[]):
        by_id[canonical_id(row.get("wordId") or row.get("word",""))].append(row)

    matched=[]; unmatched=[]; pos_review=[]; multi_level=[]
    by_level=Counter()
    for w in master:
        wid=canonical_id(w["w"]); rows=by_id.get(wid,[])
        if not rows:
            unmatched.append(w); continue
        levels=sorted({r.get("listId") for r in rows if r.get("listId")},key=lambda x:LEVEL_ORDER.get(x,99))
        for level in levels: by_level[level]+=1
        master_pos=pos_tokens(w.get("p",""))
        pos_rows=[]
        if master_pos:
            pos_rows=[r for r in rows if master_pos & pos_tokens(r.get("pos",""))]
        item={"wordId":wid,"master":w,"officialRows":rows,"levels":levels,"posMatchedRows":pos_rows}
        matched.append(item)
        if len(levels)>1: multi_level.append(item)
        if master_pos and rows and not pos_rows:
            pos_review.append(item)

    report={
      "schemaVersion":1,
      "diagnosticOnly":True,
      "sourceId":official.get("sourceId"),
      "sourceDocument":official.get("sourceDocument"),
      "sourceRevision":official.get("sourceRevision"),
      "note":"Official GEPT rows are preserved because level can be sense/POS-specific; word-level level sets are diagnostic only.",
      "counts":{
        "masterRows":len(master),
        "matchedMasterWords":len(matched),
        "unmatchedMasterWords":len(unmatched),
        "multiLevelMatchedWords":len(multi_level),
        "posReviewWords":len(pos_review),
        "matchedMasterWordsByLevel":dict(sorted(by_level.items(),key=lambda kv:LEVEL_ORDER.get(kv[0],99)))
      },
      "matched":matched,
      "unmatched":unmatched,
      "multiLevelReview":multi_level,
      "posReview":pos_review
    }
    return report

def main():
    if len(sys.argv)!=4:
        raise SystemExit("usage: crosscheck_gept_master.py GEPT_HIGH_SNAPSHOT.json words.js OUTPUT.json")
    official=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    master=load_words_js(sys.argv[2])
    try:
        report=build_report(official,master)
    except ValueError as e:
        raise SystemExit(str(e))
    out=Path(sys.argv[3]); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
