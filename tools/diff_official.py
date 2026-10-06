#!/usr/bin/env python3
"""Diff normalized official source rows against the current learning master.

Source rows remain row-level evidence; migration counts are canonical-word level.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from collections import defaultdict
from vocab_identity import canonical_id,pos_tokens

def load_words_js(path):
    text=Path(path).read_text(encoding="utf-8")
    m=re.search(r"window\.WORDS\s*=\s*(\[.*\])\s*;?\s*$",text,re.S)
    if not m: raise SystemExit("Could not parse window.WORDS")
    return json.loads(m.group(1))

def main():
    off=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    master=load_words_js(sys.argv[2]); out_path=Path(sys.argv[3])
    by_id=defaultdict(list)
    for w in master: by_id[canonical_id(w["w"])].append(w)

    official_by_id=defaultdict(list)
    aliases_by_id=defaultdict(set)
    for e in off["entries"]:
        wid=canonical_id(e.get("wordId") or e.get("word") or e.get("officialEntry",""))
        official_by_id[wid].append(e)
        aliases_by_id[wid].update(canonical_id(a) for a in e.get("aliases",[]) if canonical_id(a)!=wid)

    exact=[]; alias=[]; missing=[]; ambiguous=[]; pos_review=[]; consumed=set()
    for wid,rows in official_by_id.items():
        hits=by_id.get(wid,[])
        if len(hits)==1:
            exact.append({"wordId":wid,"officialRows":rows,"master":hits[0]}); consumed.add(wid)
            official_pos=set()
            for e in rows:
                if e.get("pos"): official_pos |= pos_tokens(e["pos"])
            mp=hits[0].get("p"); master_pos=pos_tokens(mp) if mp else set()
            if official_pos and master_pos and not (official_pos & master_pos):
                pos_review.append({"wordId":wid,"officialPos":sorted(official_pos),"masterPos":mp,
                  "officialRows":rows,"masterZh":hits[0].get("z")})
            continue
        if len(hits)>1:
            ambiguous.append({"wordId":wid,"reason":"duplicate-master-id","officialRows":rows,"candidates":hits}); continue
        ah=[]
        for a in aliases_by_id[wid]:
            ah.extend((a,x) for x in by_id.get(a,[]))
        unique={canonical_id(x["w"]):x for _,x in ah}
        if len(unique)==1:
            mw=next(iter(unique.values()))
            alias.append({"wordId":wid,"aliases":sorted(aliases_by_id[wid]),"officialRows":rows,"master":mw})
            consumed.add(canonical_id(mw["w"]))
        elif unique:
            ambiguous.append({"wordId":wid,"reason":"multiple-alias-candidates","officialRows":rows,
                              "candidates":list(unique.values())})
        else:
            missing.append({"wordId":wid,"officialRows":rows})

    master_extra=[w for w in master if canonical_id(w["w"]) not in consumed]
    report={"schemaVersion":2,"sourceId":off.get("sourceId"),"masterRows":len(master),
      "masterCanonicalWords":len(by_id),"officialRows":len(off["entries"]),
      "officialCanonicalWords":len(official_by_id),
      "counts":{"exactMatchedWords":len(exact),"aliasMatchedWords":len(alias),
        "missingCanonicalWords":len(missing),"ambiguousCanonicalWords":len(ambiguous),
        "masterRowsOutsideOfficialMatches":len(master_extra),"posReviewWords":len(pos_review)},
      "exactMatched":exact,"aliasMatched":alias,"missingFromMaster":missing,
      "ambiguous":ambiguous,"posReview":pos_review,"masterOutsideOfficialMatches":master_extra}
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))
if __name__=="__main__": main()
