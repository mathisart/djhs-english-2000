#!/usr/bin/env python3
import importlib.util
from pathlib import Path

p=Path(__file__).with_name("crosscheck_gept_master.py")
spec=importlib.util.spec_from_file_location("gept_master",p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

official={
  "catalogRole":"authoritative",
  "sourceId":"test-gept",
  "sourceDocument":"GEPT_High-Intermediate.pdf",
  "sourceRevision":"test",
  "entries":[
    {"word":"record","wordId":"record","pos":"noun","zh":"紀錄","level":"初級","listId":"gept-elementary","awl":None},
    {"word":"record","wordId":"record","pos":"verb","zh":"記錄","level":"中級","listId":"gept-intermediate","awl":None},
    {"word":"advanced","wordId":"advanced","pos":"adj.","zh":"進階的","level":"中高級","listId":"gept-high-intermediate","awl":None},
    {"word":"email","wordId":"email","pos":"noun","zh":"電子郵件","level":"初級","listId":"gept-elementary","awl":None},
  ]
}
master=[
  {"w":"record","p":"n.","z":"紀錄"},
  {"w":"advanced","p":"adj.","z":"進階的"},
  {"w":"e-mail","p":"n.","z":"電子郵件"},
  {"w":"legacy phrase","p":"conj.","z":"舊詞組"},
]
r=m.build_report(official,master)
assert r["counts"]["matchedMasterWords"]==2,r["counts"]
assert r["counts"]["unmatchedMasterWords"]==2,r["counts"]
assert r["counts"]["representationReviewWords"]==1,r["counts"]
assert r["counts"]["residualUnmatchedWords"]==1,r["counts"]
assert r["counts"]["multiLevelMatchedWords"]==1,r["counts"]
record=next(x for x in r["matched"] if x["wordId"]=="record")
assert record["levels"]==["gept-elementary","gept-intermediate"],record
assert len(record["officialRows"])==2,record
assert len(record["posMatchedRows"])==1 and record["posMatchedRows"][0]["pos"]=="noun",record
assert r["representationReview"][0]["master"]["w"]=="e-mail",r["representationReview"]
assert r["representationReview"][0]["candidates"][0]["wordId"]=="email",r["representationReview"]
assert r["residualUnmatched"][0]["w"]=="legacy phrase",r["residualUnmatched"]
print("GEPT MASTER CROSSCHECK TESTS: PASS")
