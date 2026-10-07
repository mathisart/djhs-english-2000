#!/usr/bin/env python3
"""Build the deployable vocabulary catalog only from verified snapshots.

Schema v2 keeps WORD, WORD-LIST membership, and SOURCE ENTRY as separate
entities. Membership evidence points to source rows so sense/POS-specific GEPT
levels are never flattened into the canonical word record.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from collections import defaultdict

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def generated_source_entry_id(snapshot,entry,index):
    payload={
      "sourceId":snapshot.get("sourceId"),
      "sourceDocument":snapshot.get("sourceDocument"),
      "index":index,
      "entry":entry,
    }
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return "src-"+hashlib.sha256(raw).hexdigest()[:20]

def main():
    if len(sys.argv)<4:
        raise SystemExit("usage: build_catalog.py LISTS SNAPSHOT [SNAPSHOT...] OUTPUT")
    manifest=load(sys.argv[1]); snapshots=[load(p) for p in sys.argv[2:-1]]
    output=Path(sys.argv[-1])

    words={}
    source_entries=[]
    membership_evidence=defaultdict(set)
    direct_memberships=set()

    for snap in snapshots:
        if snap.get("catalogRole")=="validation-only":
            raise SystemExit(f"Refusing validation-only snapshot as catalog input: {snap.get('sourceDocument')}")
        if snap.get("verified") is not True:
            raise SystemExit(f"Refusing unverified snapshot: {snap.get('sourceId')}")
        if snap.get("rejected"):
            raise SystemExit(f"Refusing snapshot with rejected blocks: {snap.get('sourceId')}")
        if snap.get("layoutFragments") and snap.get("review",{}).get("layoutFragments")!="pass":
            raise SystemExit(f"Refusing snapshot with unreviewed layout fragments: {snap.get('sourceId')}")

        for index,e in enumerate(snap["entries"]):
            wid=e["wordId"]; list_id=e["listId"]
            candidate=e.get("word") or e.get("officialEntry") or wid
            if wid not in words:
                words[wid]={"id":wid,"form":candidate}
            else:
                words[wid]["form"]=min((words[wid]["form"],candidate),key=lambda x:(x.casefold(),x))

            source_entry_id=e.get("sourceEntryId") or generated_source_entry_id(snap,e,index)
            source_entry={
              "id":source_entry_id,
              "sourceId":snap.get("sourceId"),
              "sourceDocument":snap.get("sourceDocument"),
              "sourceRevision":snap.get("sourceRevision"),
              **{k:v for k,v in e.items() if k!="sourceEntryId"},
            }
            source_entries.append(source_entry)
            key=(wid,list_id)
            direct_memberships.add(key)
            membership_evidence[key].add(source_entry_id)

    defs={x["id"]:x for x in manifest["lists"]}
    all_memberships=set(direct_memberships)
    changed=True
    while changed:
        changed=False
        current=set(all_memberships)
        words_with=defaultdict(set)
        for wid,lid in current:
            words_with[wid].add(lid)
        for wid,lids in words_with.items():
            for lid,d in defs.items():
                parents=set(d.get("derivedFrom",[]))
                if parents and lids & parents and (wid,lid) not in all_memberships:
                    all_memberships.add((wid,lid)); changed=True

    memberships=[]
    for wid,lid in sorted(all_memberships):
        if (wid,lid) in direct_memberships:
            memberships.append({
              "wordId":wid,
              "listId":lid,
              "scope":"source-entry",
              "sourceEntryIds":sorted(membership_evidence[(wid,lid)]),
            })
            continue
        parents=set(defs.get(lid,{}).get("derivedFrom",[]))
        inherited=set()
        used_parents=[]
        for parent in sorted(parents):
            key=(wid,parent)
            if key in all_memberships:
                used_parents.append(parent)
                inherited.update(membership_evidence.get(key,set()))
        membership_evidence[(wid,lid)].update(inherited)
        memberships.append({
          "wordId":wid,
          "listId":lid,
          "scope":"derived-word",
          "derivedFrom":used_parents,
          "sourceEntryIds":sorted(inherited),
        })

    source_entries=sorted(source_entries,key=lambda e:(
        e.get("sourceId",""),e.get("sourceDocument",""),e.get("listId",""),
        e.get("wordId",""),e.get("pos",""),e.get("zh",""),e["id"]))
    payload={
      "schemaVersion":2,
      "words":sorted(words.values(),key=lambda x:x["id"]),
      "memberships":memberships,
      "sourceEntries":source_entries,
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    by_list=defaultdict(int)
    for m in memberships: by_list[m["listId"]]+=1
    print(json.dumps({
      "canonicalWords":len(payload["words"]),
      "membershipRows":len(memberships),
      "sourceEntries":len(source_entries),
      "membershipsByList":dict(sorted(by_list.items())),
    },ensure_ascii=False))

if __name__=="__main__":
    main()
