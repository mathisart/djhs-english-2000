#!/usr/bin/env python3
"""Audit distinct source spellings that collapse to one learning canonical ID.

Diagnostic only. A collision is not permission to split or merge mastery IDs.
"""
from __future__ import annotations
import json,re,sys
from collections import defaultdict
from pathlib import Path
from vocab_identity import canonical_id,display_normalize
from diff_official import load_words_js

def source_surface(row):
    if row.get("word"):
        return display_normalize(row["word"])
    raw=display_normalize(row.get("officialEntry",""))
    m=re.match(r"^(.*?)\s*\((.*?)\)\s*$",raw)
    return display_normalize(m.group(1) if m else raw)

def build_report(snapshot,master):
    grouped=defaultdict(list)
    for row in snapshot.get("entries",[]):
        surface=source_surface(row)
        grouped[canonical_id(surface)].append((surface,row))
    master_by_id=defaultdict(list)
    for row in master:
        master_by_id[canonical_id(row.get("w",""))].append(row)

    collisions=[]
    for wid,items in sorted(grouped.items()):
        forms=sorted({surface for surface,_ in items})
        if len(forms)<2:
            continue
        collisions.append({
          "wordId":wid,
          "sourceForms":forms,
          "sourceRows":[row for _,row in items],
          "masterRows":master_by_id.get(wid,[])
        })
    return {
      "schemaVersion":1,
      "diagnosticOnly":True,
      "sourceId":snapshot.get("sourceId"),
      "sourceDocument":snapshot.get("sourceDocument"),
      "counts":{"sourceRows":len(snapshot.get("entries",[])),"collisionCanonicalIds":len(collisions)},
      "collisions":collisions,
      "note":"Distinct source forms collapsing to one canonical ID require explicit identity and mastery-migration review."
    }

def main():
    if len(sys.argv)!=4:
        raise SystemExit("usage: audit_identity_collisions.py SNAPSHOT.json words.js OUTPUT.json")
    snapshot=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    master=load_words_js(sys.argv[2])
    report=build_report(snapshot,master)
    out=Path(sys.argv[3]); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False))
    for x in report["collisions"]:
        print("IDENTITY_COLLISION",repr(x["wordId"]),x["sourceForms"])

if __name__=="__main__":
    main()
