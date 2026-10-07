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

def contains_compact_source_form(normalized_table, value):
    """Conservative source-representation check for joined master spellings.

    Example: production stopwatch vs official Table 3 stop watch.
    Only single-token master forms are considered, and only 2-3 adjacent
    source tokens may be joined. This is diagnostic evidence, not membership.
    """
    form=norm(value)
    if not form or " " in form:
        return False
    tokens=normalized_table.split()
    for width in (2,3):
        for i in range(len(tokens)-width+1):
            if "".join(tokens[i:i+width])==form:
                return True
    return False

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
    source_representation_ids={x.get("w") for x in misses if contains_compact_source_form(table3,x.get("w",""))}
    explained_ids=explained_master_ids | source_representation_ids
    explained=[x for x in misses if x.get("w") in explained_ids]
    residual=[x for x in misses if x.get("w") not in explained_ids]
    source_explained=[x for x in misses if x.get("w") in source_representation_ids]
    out={"schemaVersion":3,"diagnosticOnly":True,
         "note":"Text-layer occurrence is evidence only; not parsed Table 3 membership. Representation-explained misses remain review-only; compact source matches cover conservative joined-vs-split spellings such as stopwatch/stop watch.",
         "counts":{"masterOnly":len(hits)+len(misses),"table3TextHits":len(hits),"table3TextMisses":len(misses),
                   "representationExplainedMisses":len(explained),"sourceRepresentationExplainedMisses":len(source_explained),"residualMisses":len(residual)},
         "hits":hits,"misses":misses,"representationExplainedMisses":explained,
         "sourceRepresentationExplainedMisses":source_explained,"residualMisses":residual}
    Path(sys.argv[3]).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out["counts"],ensure_ascii=False))
if __name__=="__main__": main()
