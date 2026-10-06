#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,sys
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
        source_key=(lid+"\0"+raw).encode("utf-8")
        entries.append({"sourceEntryId":"naer-"+hashlib.sha256(source_key).hexdigest()[:16],"officialEntry":raw,"wordId":canonical_id(raw.split(" (")[0]),"aliases":aliases(raw),"listId":lid})
    payload={"schemaVersion":1,"sourceId":"moe-jh-108","sourceDocument":"naer-english-curriculum-108","sourceUrl":"https://www.naer.edu.tw/upload/1/16/doc/812/%28%E7%99%BC%E5%B8%83%E7%89%88%29%E5%9C%8B%E6%B0%91%E4%B8%AD%E5%B0%8F%E5%AD%B8%E6%9A%A8%E6%99%AE%E9%80%9A%E5%9E%8B%E9%AB%98%E7%B4%9A%E4%B8%AD%E7%AD%89%E5%AD%B8%E6%A0%A1-%E8%AA%9E%E6%96%87%E9%A0%98%E5%9F%9F-%E8%8B%B1%E8%AA%9E%E6%96%87%E8%AA%B2%E7%A8%8B%E7%B6%B1%E8%A6%81.pdf","sourceRevision":"108課綱現行版","catalogRole":"authoritative","verified":False,"retrievedAt":None,"review":{},"rejected":[],"entries":entries,
      "declaredCounts":{"moe-basic-1200":1200,"moe-common-2000-extra":800,"moe-common-2000":2000},
      "derivedLists":{"moe-common-2000":["moe-basic-1200","moe-common-2000-extra"]}}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"basicRows":len(basic),"extraRows":len(extra),"combinedRows":len(entries)},ensure_ascii=False))
if __name__=="__main__": main()
