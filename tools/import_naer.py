#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import canonical_id,base_and_parenthetical
T1="表一、基本1,200字"; T2="表二、其他常用800字"
def canon(s): return re.sub(r"\s+"," ",s.strip()).casefold()
def split_entries(block):
    block=re.sub(r"\n\s*[A-Z]\s*[–-]\s*","\n",block)
    block=re.sub(r"\s+"," ",block)
    out=[]; buf=[]; depth=0
    for ch in block:
        if ch=="(": depth+=1
        elif ch==")" and depth: depth-=1
        if ch=="," and depth==0:
            item="".join(buf).strip(" .")
            if item: out.append(item)
            buf=[]
        else: buf.append(ch)
    item="".join(buf).strip(" .")
    if item: out.append(item)
    return out
def aliases(entry):
    vals={canonical_id(entry)}
    m=re.match(r"^(.*?)\s*\((.*?)\)\s*$",entry)
    if m:
        vals.add(canonical_id(m.group(1)))
        vals.update(canonical_id(x) for x in m.group(2).split(",") if x.strip())
    return sorted(vals)
def main():
    src,out=map(Path,sys.argv[1:3]); text=src.read_text(encoding="utf-8",errors="replace")
    i1=text.find(T1); i2=text.find(T2)
    if i1<0 or i2<0 or i2<=i1: raise SystemExit("Could not locate NAER Appendix 5 Table 1/Table 2 headings")
    i3=text.find("表三、",i2); basic=split_entries(text[i1+len(T1):i2]); extra=split_entries(text[i2+len(T2):i3 if i3>0 else None])
    entries=[]
    for raw,lid in [(x,"moe-basic-1200") for x in basic]+[(x,"moe-common-2000-extra") for x in extra]:
        entries.append({"officialEntry":raw,"wordId":canonical_id(raw.split(" (")[0]),"aliases":aliases(raw),"listId":lid})
    payload={"schemaVersion":1,"sourceId":"moe-jh-108","verified":False,"retrievedAt":None,"review":{},"rejected":[],"entries":entries,
      "derivedLists":{"moe-common-2000":["moe-basic-1200","moe-common-2000-extra"]}}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"basicRows":len(basic),"extraRows":len(extra),"combinedRows":len(entries)},ensure_ascii=False))
if __name__=="__main__": main()
