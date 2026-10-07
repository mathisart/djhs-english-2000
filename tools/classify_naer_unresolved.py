#!/usr/bin/env python3
"""Classify unresolved NAER-to-master misses without changing identity.

This diagnostic keeps exact official identity strict. Related production
compounds are evidence for review only and never count as official matches.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path

ABBREVIATION_OR_TITLE={
    "a.m","p.m","r.o.c./roc","u.s.a./usa","mr","mrs","ms"
}

# Reviewed semantic/compound relationships in the current production master.
# These are not identity aliases.
REVIEWED_RELATED_FORMS={
    "officer":["police officer"],
    "police":["police officer","police station"],
    "sore":["sore throat"],
    "burger":["hamburger"],
    "stationery":["stationery store"],
}

def load_words_js(path):
    text=Path(path).read_text(encoding="utf-8")
    m=re.search(r"window\.WORDS\s*=\s*(\[.*\])\s*;?\s*$",text,re.S)
    if not m:
        raise SystemExit("Could not parse window.WORDS")
    return json.loads(m.group(1))

def main():
    diff=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    master=load_words_js(sys.argv[2])
    out_path=Path(sys.argv[3])
    master_words={x.get("w","").casefold():x for x in master if x.get("w")}

    buckets={"abbreviationOrTitle":[],"relatedProductionCompound":[],"lexicalMissing":[]}
    unresolved=diff.get("unresolvedMissing",[])
    for item in unresolved:
        wid=item.get("wordId","").casefold()
        row={"wordId":item.get("wordId"),"officialRows":item.get("officialRows",[])}
        if wid in ABBREVIATION_OR_TITLE:
            buckets["abbreviationOrTitle"].append(row)
            continue
        related=[w for w in REVIEWED_RELATED_FORMS.get(wid,[]) if w.casefold() in master_words]
        if related:
            row["relatedProductionForms"]=related
            row["note"]="review evidence only; not an identity match"
            buckets["relatedProductionCompound"].append(row)
            continue
        buckets["lexicalMissing"].append(row)

    out={
        "schemaVersion":1,
        "diagnosticOnly":True,
        "note":"Buckets classify review work only. No bucket changes official identity or production membership.",
        "counts":{k:len(v) for k,v in buckets.items()},
        **buckets,
    }
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out["counts"],ensure_ascii=False))

if __name__=="__main__":
    main()
