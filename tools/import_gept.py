#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import canonical_id

SOURCE_ID="gept-current-2026-10-06"
LEVEL_MAP={"初級":"gept-elementary","中級":"gept-intermediate","中高級":"gept-high-intermediate","中高":"gept-high-intermediate"}
REVISION_MAP={
    "GEPT_Elementary.pdf":"2026-04-29",
    "GEPT_Intermediate.pdf":"2026-08-21",
    "GEPT_High-Intermediate.pdf":"2026-08-21",
}
ATOM=r"(?:art[.]?|adj[.]?|adv[.]?|noun[.]?|verb(?:[(]aux[.][)])?[.]?|prep[.]?|conj[.]?|pron[.]?|aux[.]?|interj[.]?|number|det[.]?|determiner|modal|inf[.]?)"
POS_RE=rf"{ATOM}(?:/{ATOM})*"
ROW=re.compile(rf"^[ 	]*(?P<word>.+?)[ 	]+(?P<pos>{POS_RE})[ 	]+(?P<rest>.+?)[ 	]+(?P<level>初級|中級|中高級|中高)(?:[ 	]+(?P<awl>L[0-9]+))?(?:[ 	]+[0-9]+)?[ 	]*$")
HEADER=re.compile(r"字彙[ 	]*詞類[ 	]*中文[ 	]*註解[ 	]*級數[ 	]*學術字彙")

def clean_line(raw):
    line=HEADER.sub(" ",raw)
    line=re.sub(r"(?<=[^ 	])[ 	]+[0-9]+[ 	]*$","",line)
    return " ".join(line.split())

def emit(m):
    d=m.groupdict()
    return {"word":d["word"].strip(),"wordId":canonical_id(d["word"]),"pos":d["pos"],
      "zh":d["rest"].strip(),"level":d["level"],"listId":LEVEL_MAP[d["level"]],
      "awl":d.get("awl") or None}

def parse(text):
    out=[]; pending=""; rejected=[]
    for raw in text.splitlines():
        if raw.strip().isdigit(): continue
        line=clean_line(raw)
        if not line or line.isdigit(): continue

        # Prefer a complete row on the current physical line. This prevents a
        # leftover fragment from the previous PDF row swallowing the next word.
        single=ROW.match(line)
        if single:
            if pending:
                rejected.append(pending)
                pending=""
            out.append(emit(single))
            continue

        recovered,prefix=recover_prefixed_row(line)
        if recovered:
            if pending:
                layout_fragments.append({"fragment":pending,"reason":"preceded recovered row"})
                pending=""
            layout_fragments.append({"fragment":prefix,"rowWord":recovered.group("word"),"reason":"prefix before anchored word/POS row"})
            out.append(emit(recovered))
            continue

        candidate=(pending+" "+line).strip() if pending else line
        joined=ROW.match(candidate)
        if joined:
            out.append(emit(joined))
            pending=""
        elif len(candidate)<350:
            pending=candidate
        else:
            rejected.append(candidate)
            pending=""
    if pending: rejected.append(pending)
    return out,rejected,layout_fragments

def main():
    if len(sys.argv) not in (3,5):
        raise SystemExit("usage: import_gept.py INPUT_TEXT OUTPUT_JSON [SOURCE_DOCUMENT SOURCE_URL]")
    src,out=map(Path,sys.argv[1:3])
    source_document=sys.argv[3] if len(sys.argv)==5 else "GEPT_High-Intermediate.pdf"
    source_url=sys.argv[4] if len(sys.argv)==5 else "https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_High-Intermediate.pdf"
    revision=REVISION_MAP.get(source_document)
    if not revision:
        raise SystemExit(f"Unknown GEPT source document revision: {source_document}")
    entries,rejected,layout_fragments=parse(src.read_text(encoding="utf-8",errors="replace"))
    payload={"schemaVersion":1,"sourceId":SOURCE_ID,
      "sourceDocument":source_document,"sourceUrl":source_url,"sourceRevision":revision,
      "catalogRole":"authoritative" if source_document=="GEPT_High-Intermediate.pdf" else "validation-only",
      "verified":False,"retrievedAt":None,"review":{},"entries":entries,"rejected":rejected,"layoutFragments":layout_fragments}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    levels={}
    for e in entries: levels[e["listId"]]=levels.get(e["listId"],0)+1
    print(json.dumps({"rows":len(entries),"rowsByLevel":levels,
      "uniqueWords":len({e["wordId"] for e in entries}),"rejectedBlocks":len(rejected),"layoutFragments":len(layout_fragments)},
      ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
