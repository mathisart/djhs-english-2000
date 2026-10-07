#!/usr/bin/env python3
"""Diagnostic cross-check of current-master-only forms against NAER Appendix 5 Table 3.

This is deliberately NOT a Table 3 membership parser. It reports normalized
text-layer occurrences only, so a hit is supporting evidence and never an
automatic identity/list-membership decision.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import display_normalize

T3_RE=re.compile(r"表三、")
def norm(s):
    s=display_normalize(s).casefold()
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

def contains_form(normalized_table, value):
    form=norm(value)
    return bool(form and (" "+form+" ") in (" "+normalized_table+" "))

def main():
    text=Path(sys.argv[1]).read_text(encoding="utf-8",errors="replace")
    diff=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    m=T3_RE.search(text)
    if not m: raise SystemExit("Could not locate NAER Appendix 5 Table 3")
    table3=norm(text[m.end():])
    padded=" "+table3+" "
    hits=[]; misses=[]
    for row in diff.get("masterOutsideOfficialMatches",[]):
        form=norm(row.get("w",""))
        target=hits if contains_form(table3,row.get("w","")) else misses
        target.append(row)
    explained_master_ids={m.get("master",{}).get("w") for m in diff.get("representationReviewCandidates",[])}
    explained=[x for x in misses if x.get("w") in explained_master_ids]
    residual=[x for x in misses if x.get("w") not in explained_master_ids]
    out={"schemaVersion":2,"diagnosticOnly":True,
         "note":"Text-layer occurrence is evidence only; not parsed Table 3 membership. Representation-explained misses remain review-only.",
         "counts":{"masterOnly":len(hits)+len(misses),"table3TextHits":len(hits),"table3TextMisses":len(misses),
                   "representationExplainedMisses":len(explained),"residualMisses":len(residual)},
         "hits":hits,"misses":misses,"representationExplainedMisses":explained,"residualMisses":residual}
    Path(sys.argv[3]).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out["counts"],ensure_ascii=False))
if __name__=="__main__": main()
