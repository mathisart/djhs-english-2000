#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from vocab_identity import canonical_id
T1_RE=re.compile(r"表一、基本 *1 *, *200 *字（依字母排列）")
T2_RE=re.compile(r"表二、其他常用 *800 *字（依字母排列）")
T3_RE=re.compile(r"表三、")
def canon(s): return re.sub(r"\s+"," ",s.strip()).casefold()
def split_entries(block):
    block=re.sub(r"(?m)^ *[0-9]+ *$"," ",block)
    block=re.sub(r"(?m)^ *[A-Z] *[–-] *",", ",block)
    block=re.sub(r"\s+"," ",block)
    block=re.sub(r" +[0-9]+ +([A-Z]) *[–-] +",r", ",block)
    block=re.sub(r" +[0-9]+ +",", ",block)
    block=re.sub(r" +[A-Z] *[–-] +",", ",block)
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
    m1=T1_RE.search(text); m2=T2_RE.search(text,m1.end() if m1 else 0)
    if not m1 or not m2 or m2.start()<=m1.start(): raise SystemExit("Could not locate NAER Appendix 5 Table 1/Table 2 headings")
    m3=T3_RE.search(text,m2.end()); basic=split_entries(text[m1.end():m2.start()]); extra=split_entries(text[m2.end():m3.start() if m3 else None])
    entries=[]
    for raw,lid in [(x,"moe-basic-1200") for x in basic]+[(x,"moe-common-2000-extra") for x in extra]:
        entries.append({"officialEntry":raw,"wordId":canonical_id(raw.split(" (")[0]),"aliases":aliases(raw),"listId":lid})
    payload={"schemaVersion":1,"sourceId":"moe-jh-108","verified":False,"retrievedAt":None,"review":{},"rejected":[],"entries":entries,
      "derivedLists":{"moe-common-2000":["moe-basic-1200","moe-common-2000-extra"]}}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"basicRows":len(basic),"extraRows":len(extra),"combinedRows":len(entries)},ensure_ascii=False))
if __name__=="__main__": main()
