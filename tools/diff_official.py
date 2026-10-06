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
            exact.append({"wordId":wid,"officialRows":rows,"master":hits[0]}); consumed.add(canonical_id(hits[0]["w"]))
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

    # Conservative review candidates only. These never alter identity automatically.
    def review_key(value):
        s=canonical_id(value).replace("-","").replace(" ","").replace(".","").replace("/","")
        if s.endswith("s") and len(s)>3: s=s[:-1]
        return s
    missing_keys=defaultdict(list)
    extra_keys=defaultdict(list)
    for x in missing:
        forms={x["wordId"]}
        for row in x.get("officialRows",[]):
            forms.update(a for a in row.get("aliases",[]) if a)
            raw=row.get("officialEntry","")
            forms.update(part.strip() for part in raw.split("/") if part.strip())
        for form in forms: missing_keys[review_key(form)].append(x)
    for x in master_extra: extra_keys[review_key(x["w"])].append(x)
    representation_candidates=[]
    for k in sorted(set(missing_keys)&set(extra_keys)):
        for m in missing_keys[k]:
            for x in extra_keys[k]:
                representation_candidates.append({"officialWordId":m["wordId"],"officialRows":m["officialRows"],"master":x})

    # Descriptive buckets for current-master-only rows. These are not validity judgments.
    pronoun_forms={"her","hers","herself","him","himself","his","its","itself","me","mine","my","myself","our","ours","ourselves","their","theirs","them","themselves","us","your","yours","yourself","yourselves"}
    def extra_bucket(word):
        wid=canonical_id(word["w"])
        if wid in pronoun_forms: return "pronoun-form"
        if " " in wid: return "multi-word"
        if word["w"][:1].isupper(): return "proper-or-titlecase"
        return "other"
    master_extra_buckets=defaultdict(list)
    for x in master_extra: master_extra_buckets[extra_bucket(x)].append(x)

    representation_word_ids={x["officialWordId"] for x in representation_candidates}
    unresolved_missing=[x for x in missing if x["wordId"] not in representation_word_ids]

    report={"schemaVersion":2,"sourceId":off.get("sourceId"),"masterRows":len(master),
      "masterCanonicalWords":len(by_id),"officialRows":len(off["entries"]),
      "officialCanonicalWords":len(official_by_id),
      "counts":{"exactMatchedWords":len(exact),"aliasMatchedWords":len(alias),
        "missingCanonicalWords":len(missing),"ambiguousCanonicalWords":len(ambiguous),
        "masterRowsOutsideOfficialMatches":len(master_extra),"posReviewWords":len(pos_review),"representationReviewCandidates":len(representation_candidates),"representationReviewWords":len(representation_word_ids),"unresolvedMissingWords":len(unresolved_missing),"masterOutsideOfficialBuckets":{k:len(v) for k,v in sorted(master_extra_buckets.items())}},
      "exactMatched":exact,"aliasMatched":alias,"missingFromMaster":missing,
      "ambiguous":ambiguous,"posReview":pos_review,"representationReviewCandidates":representation_candidates,"unresolvedMissing":unresolved_missing,"masterOutsideOfficialMatches":master_extra,"masterOutsideOfficialBuckets":dict(master_extra_buckets)}
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report["counts"],ensure_ascii=False,indent=2))
if __name__=="__main__": main()
