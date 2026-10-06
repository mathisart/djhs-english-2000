#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import canonical_id

SOURCE_ID="gept-2026-04-29"
LEVEL_MAP={"初級":"gept-elementary","中級":"gept-intermediate","中高級":"gept-high-intermediate","中高":"gept-high-intermediate"}
ATOM=r"(?:art[.]|adj[.]|adv[.]|noun|verb|prep[.]|conj[.]|pron[.]|aux[.]|interj[.]|number|det[.]|determiner|modal)"
POS_RE=rf"{ATOM}(?:/{ATOM})*"
ROW=re.compile(rf"^\\s*(?P<word>.+?)\\s+(?P<pos>{POS_RE})\\s+(?P<rest>.+?)\\s+(?P<level>初級|中級|中高級|中高)(?:\\s+(?P<awl>L\\d+))?(?:\\s+\\d+)?\\s*$")
HEADER=re.compile(r"字彙\\s*詞類\\s*中文\\s*註解\\s*級數\\s*學術字彙")

def clean_line(raw):
    line=HEADER.sub(" ",raw)
    line=re.sub(r"(?<=\\S)\\s+\\d+\\s*$","",line)
    return re.sub(r"\\s+"," ",line).strip()

def parse(text):
    out=[]; pending=""; rejected=[]
    for raw in text.splitlines():
        # Standalone PDF page numbers are layout noise, never row continuations.
        if re.fullmatch(r"\\s*\\d+\\s*",raw): continue
        line=clean_line(raw)
        if not line or re.fullmatch(r"\\d+",line): continue
        candidate=(pending+" "+line).strip() if pending else line
        m=ROW.match(candidate)
        if not m:
            if len(candidate)<350: pending=candidate
            else: rejected.append(candidate); pending=""
            continue
        d=m.groupdict()
        out.append({"word":d["word"].strip(),"wordId":canonical_id(d["word"]),"pos":d["pos"],
          "zh":d["rest"].strip(),"level":d["level"],"listId":LEVEL_MAP[d["level"]],
          "awl":d.get("awl") or None})
        pending=""
    if pending: rejected.append(pending)
    return out,rejected

def main():
    if len(sys.argv) not in (3,5):
        raise SystemExit("usage: import_gept.py INPUT_TEXT OUTPUT_JSON [SOURCE_DOCUMENT SOURCE_URL]")
    src,out=map(Path,sys.argv[1:3])
    source_document=sys.argv[3] if len(sys.argv)==5 else "GEPT_High-Intermediate.pdf"
    source_url=sys.argv[4] if len(sys.argv)==5 else "https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_High-Intermediate.pdf"
    entries,rejected=parse(src.read_text(encoding="utf-8",errors="replace"))
    payload={"schemaVersion":1,"sourceId":SOURCE_ID,
      "sourceDocument":"GEPT_High-Intermediate.pdf",
      "sourceUrl":"https://www.lttc.ntu.edu.tw/resources/GEPT/GEPT_High-Intermediate.pdf",
      "sourceRevision":"2026-04-29",
      "verified":False,"retrievedAt":None,"review":{},"entries":entries,"rejected":rejected}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    levels={}
    for e in entries: levels[e["listId"]]=levels.get(e["listId"],0)+1
    print(json.dumps({"rows":len(entries),"rowsByLevel":levels,
      "uniqueWords":len({e["wordId"] for e in entries}),"rejectedBlocks":len(rejected)},
      ensure_ascii=False,indent=2))
if __name__=="__main__": main()
