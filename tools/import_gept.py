#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import canonical_id

SOURCE_ID="gept-current-2026-10-06"
LEVEL_MAP={"初級":"gept-elementary","中級":"gept-intermediate","中高級":"gept-high-intermediate","中高":"gept-high-intermediate"}
REVISION_MAP={"GEPT_Elementary.pdf":"2026-04-29","GEPT_Intermediate.pdf":"2026-08-21","GEPT_High-Intermediate.pdf":"2026-08-21"}
ATOM=r"(?:art[.]?|adj[.]?|adv[.]?|noun[.]?|verb(?:[(]aux[.][)])?[.]?|prep[.]?|conj[.]?|pron[.]?|aux[.]?|interj[.]?|number|det[.]?|determiner|modal|inf[.]?)"
POS_RE=rf"{ATOM}(?:/{ATOM})*"
ROW=re.compile(rf"^[ \t]*(?P<word>.+?)[ \t]+(?P<pos>{POS_RE})[ \t]+(?P<rest>.+?)[ \t]+(?P<level>初級|中級|中高級|中高)(?:[ \t]+(?P<awl>L[0-9]+))?(?:[ \t]+[0-9]+)?[ \t]*$")
HEADER=re.compile(r"字彙[ \t]*詞類[ \t]*中文[ \t]*註解[ \t]*級數[ \t]*學術字彙")
FOOTER=re.compile(r"^(?:全民英檢|GEPT).*(?:修訂|版權|LTTC)|^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}.*修訂")
WORD_TOKEN=re.compile(r"^[A-Za-z][A-Za-z'./()-]*$")

def clean_line(raw):
    line=HEADER.sub(" ",raw)
    line=re.sub(r"(?<=[^ \t])[ \t]+[0-9]+[ \t]*$","",line)
    return " ".join(line.split())

def emit(m):
    d=m.groupdict()
    return {"word":d["word"].strip(),"wordId":canonical_id(d["word"]),"pos":d["pos"],
      "zh":d["rest"].strip(),"level":d["level"],"listId":LEVEL_MAP[d["level"]],
      "awl":d.get("awl") or None}

def recover_prefixed_row(line):
    tokens=line.split()
    for i in range(1,len(tokens)-2):
        if not WORD_TOKEN.fullmatch(tokens[i]):
            continue
        candidate=" ".join(tokens[i:])
        m=ROW.match(candidate)
        if not m:
            continue
        prefix=" ".join(tokens[:i]).strip()
        if prefix and not re.search(r"[A-Za-z]",prefix):
            return m,prefix
    return None,None

def parse(text):
    out=[]; pending=""; rejected=[]; layout_fragments=[]; deferred=None
    for raw in text.splitlines():
        if raw.strip().isdigit():
            continue
        line=clean_line(raw)
        if not line or line.isdigit() or FOOTER.search(line):
            continue

        if deferred and not re.search(r"[A-Za-z]",line) and not re.search(r"初級|中級|中高級|中高",line):
            deferred["zhParts"].append(line)
            layout_fragments.append({"fragment":line,"rowWord":deferred["word"],"reason":"Chinese continuation attached to deferred word/POS/level row"})
            continue

        if deferred:
            if deferred["zhParts"]:
                out.append({"word":deferred["word"],"wordId":canonical_id(deferred["word"]),"pos":deferred["pos"],
                    "zh":" ".join(deferred["zhParts"]),"level":deferred["level"],"listId":LEVEL_MAP[deferred["level"]],"awl":deferred["awl"]})
            else:
                rejected.append(deferred["raw"])
            deferred=None

        partial=PARTIAL_ROW.match(line)
        if partial:
            d=partial.groupdict()
            deferred={"raw":line,"word":d["word"].strip(),"pos":d["pos"],"level":d["level"],"awl":d.get("awl") or None,"zhParts":[]}
            continue

        if out and not re.search(r"[A-Za-z]",line) and not re.search(r"初級|中級|中高級|中高",line):
            layout_fragments.append({"fragment":line,"rowWord":out[-1]["word"],"reason":"Chinese-only PDF layout continuation; preserved separately from semantic row"})
            continue

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
            continue

        recovered,prefix=recover_prefixed_row(candidate)
        if recovered:
            layout_fragments.append({"fragment":prefix,"rowWord":recovered.group("word"),"reason":"prefix before anchored word/POS row in joined PDF block"})
            out.append(emit(recovered))
            pending=""
            continue

        if len(candidate)<350:
            pending=candidate
        else:
            rejected.append(candidate)
            pending=""
    if pending:
        rejected.append(pending)
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
    payload={"schemaVersion":1,"sourceId":SOURCE_ID,"sourceDocument":source_document,
      "sourceUrl":source_url,"sourceRevision":revision,
      "catalogRole":"authoritative" if source_document=="GEPT_High-Intermediate.pdf" else "validation-only",
      "verified":False,"retrievedAt":None,"review":{},"entries":entries,
      "rejected":rejected,"layoutFragments":layout_fragments}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    levels={}
    for e in entries:
        levels[e["listId"]]=levels.get(e["listId"],0)+1
    print(json.dumps({"rows":len(entries),"rowsByLevel":levels,
      "uniqueWords":len({e["wordId"] for e in entries}),
      "rejectedBlocks":len(rejected),"layoutFragments":len(layout_fragments)},
      ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
