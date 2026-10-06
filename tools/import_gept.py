#!/usr/bin/env python3
"""Normalize LTTC GEPT PDF text exported with pdftotext -layout.

Usage:
  pdftotext -layout GEPT_Intermediate.pdf gept.txt
  python tools/import_gept.py gept.txt data/official/generated/gept-intermediate.json

The LTTC cumulative PDFs contain lower-level entries too. Membership is determined
from the official 級數 column per row, never from the PDF filename.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path

LEVEL_MAP={"初級":"gept-elementary","中級":"gept-intermediate","中高級":"gept-high-intermediate"}
POS_RE=r"(?:art\.|adj\.|adv\.|noun|verb|prep\.|conj\.|pron\.|aux\.|interj\.|number|det\.|modal)(?:/(?:adj\.|adv\.|noun|verb|prep\.|conj\.|pron\.|aux\.|interj\.|number|det\.))*"
ROW=re.compile(rf"^\s*(?P<word>.+?)\s+(?P<pos>{POS_RE})\s+(?P<rest>.+?)\s+(?P<level>初級|中級|中高級)(?:\s+(?P<awl>L\d+))?\s*$")

def canonical(s:str)->str:
    return re.sub(r"\s+"," ",s.strip()).casefold()

def parse(text:str):
    out=[]; pending=""
    for raw in text.splitlines():
        line=re.sub(r"\s+"," ",raw).strip()
        if not line or line.startswith("字彙 詞類 中文") or re.fullmatch(r"\d+",line):
            continue
        candidate=(pending+" "+line).strip() if pending else line
        m=ROW.match(candidate)
        if not m:
            pending=candidate if len(candidate)<350 else ""
            continue
        d=m.groupdict(); rest=d["rest"].strip()
        out.append({"word":d["word"].strip(),"wordId":canonical(d["word"]),"pos":d["pos"],
                    "zh":rest,"level":d["level"],"listId":LEVEL_MAP[d["level"]],
                    "awl":d.get("awl") or None})
        pending=""
    return out

def main():
    src,out=map(Path,sys.argv[1:3])
    entries=parse(src.read_text(encoding="utf-8",errors="replace"))
    payload={"schemaVersion":1,"sourceId":"gept-2024-02","entries":entries}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    levels={}
    for e in entries: levels[e["listId"]]=levels.get(e["listId"],0)+1
    print(json.dumps({"rows":len(entries),"rowsByLevel":levels,
      "uniqueWords":len({e["wordId"] for e in entries})},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
