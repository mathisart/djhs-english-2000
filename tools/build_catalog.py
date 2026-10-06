#!/usr/bin/env python3
"""Build the deployable vocabulary catalog only from verified snapshots.

The output keeps one canonical word record and separate list memberships.
It refuses unverified inputs or snapshots with rejected blocks.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
from collections import defaultdict

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    manifest=load(sys.argv[1]); snapshots=[load(p) for p in sys.argv[2:-1]]
    output=Path(sys.argv[-1])
    catalog=defaultdict(lambda:{"memberships":[],"sourceEntries":[]})
    for snap in snapshots:
        if snap.get("catalogRole")=="validation-only":
            raise SystemExit(f"Refusing validation-only snapshot as catalog input: {snap.get('sourceDocument')}")
        if snap.get("verified") is not True:
            raise SystemExit(f"Refusing unverified snapshot: {snap.get('sourceId')}")
        if snap.get("rejected"):
            raise SystemExit(f"Refusing snapshot with rejected blocks: {snap.get('sourceId')}")
        for e in snap["entries"]:
            wid=e["wordId"]
            row=catalog[wid]
            row["id"]=wid
            candidate=e.get("word") or e.get("officialEntry") or wid
            if "form" not in row:
                row["form"]=candidate
            else:
                # Stable regardless of snapshot argument order.
                row["form"]=min((row["form"],candidate),key=lambda x:(x.casefold(),x))
            list_id=e["listId"]
            if list_id not in row["memberships"]: row["memberships"].append(list_id)
            row["sourceEntries"].append({"sourceId":snap["sourceId"],**e})
    # Derived list memberships (e.g. MOE 2000 = 1200 + extra 800)
    defs={x["id"]:x for x in manifest["lists"]}
    for row in catalog.values():
        current=set(row["memberships"])
        changed=True
        while changed:
            changed=False
            current=set(row["memberships"])
            for lid,d in defs.items():
                parents=set(d.get("derivedFrom",[]))
                # derivedFrom is a union unless a future manifest explicitly
                # introduces another derivation operator.
                if parents and current & parents and lid not in current:
                    row["memberships"].append(lid); changed=True
        row["memberships"]=sorted(set(row["memberships"]))
    for row in catalog.values():
        row["sourceEntries"]=sorted(row["sourceEntries"],key=lambda e:(
            e.get("sourceId",""),e.get("listId",""),e.get("pos",""),e.get("zh","")))
    payload={"schemaVersion":1,"words":sorted(catalog.values(),key=lambda x:x["id"])}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"canonicalWords":len(payload["words"]),
      "memberships":sum(len(w["memberships"]) for w in payload["words"])},ensure_ascii=False))
if __name__=="__main__": main()
