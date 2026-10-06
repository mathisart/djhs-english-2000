#!/usr/bin/env python3
"""Parse NAER curriculum Appendix 5 Table 1 / Table 2 from pdftotext output.

The parser preserves the official printed entry and also derives searchable aliases
from parenthetical variants. It does not count the separate country/festival
recognition appendix as part of the basic 1,200.
"""
from __future__ import annotations
import json,re,sys
from pathlib import Path

T1="表一、基本1,200字"
T2="表二、其他常用800字"

def canon(s):
    return re.sub(r"\s+"," ",s.strip()).casefold()

def split_entries(block):
    # Normalize line wrapping while retaining comma-delimited official entries.
    block=re.sub(r"\n\s*[A-Z]\s*[–-]\s*", "\n", block)
    block=re.sub(r"\s+"," ",block)
    return [x.strip(" .") for x in block.split(",") if x.strip(" .")]

def aliases(entry):
    vals={canon(entry)}
    # e.g. airplane (plane), father (dad, daddy), be (am, is, are...)
    m=re.match(r"^(.*?)\s*\((.*?)\)\s*$",entry)
    if m:
        vals.add(canon(m.group(1)))
        vals.update(canon(x) for x in m.group(2).split(",") if x.strip())
    return sorted(vals)

def main():
    src,out=map(Path,sys.argv[1:3])
    text=src.read_text(encoding="utf-8",errors="replace")
    i1=text.find(T1); i2=text.find(T2)
    if i1<0 or i2<0 or i2<=i1:
        raise SystemExit("Could not locate NAER Appendix 5 Table 1/Table 2 headings")
    # Table 1 ends at Table 2. Table 2 ends before Table 3 if present.
    i3=text.find("表三、",i2)
    b1=text[i1+len(T1):i2]
    b2=text[i2+len(T2):i3 if i3>0 else None]
    basic=split_entries(b1); extra=split_entries(b2)
    entries=[]
    for raw,list_id in [(x,"moe-basic-1200") for x in basic]+[(x,"moe-common-2000-extra") for x in extra]:
        entries.append({"officialEntry":raw,"wordId":canon(raw.split(" (")[0]),"aliases":aliases(raw),"listId":list_id})
    payload={"schemaVersion":1,"sourceId":"moe-jh-108","verified":False,"rejected":[],"entries":entries,
      "derivedLists":{"moe-common-2000":["moe-basic-1200","moe-common-2000-extra"]}}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"basicRows":len(basic),"extraRows":len(extra),"combinedRows":len(basic)+len(extra)},ensure_ascii=False))
if __name__=="__main__": main()
