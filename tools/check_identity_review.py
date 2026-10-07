#!/usr/bin/env python3
"""Validate identity-collision review registry and optionally require release approval."""
from __future__ import annotations
import json,sys
from pathlib import Path

ALLOWED={"pending","approved","rejected"}

def main():
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: check_identity_review.py REVIEW.json [--release]")
    review=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    release=(len(sys.argv)==3 and sys.argv[2]=="--release")
    failures=[]
    rows=review.get("collisions",[])
    seen=set()
    for i,row in enumerate(rows):
        wid=row.get("wordId")
        if not wid:
            failures.append(f"row {i}: missing wordId"); continue
        if wid in seen:
            failures.append(f"{wid}: duplicate registry entry")
        seen.add(wid)
        forms=row.get("sourceForms") or []
        if len(set(forms))<2:
            failures.append(f"{wid}: sourceForms must contain at least two distinct forms")
        status=row.get("status")
        if status not in ALLOWED:
            failures.append(f"{wid}: invalid status {status!r}")
        if release and status!="approved":
            failures.append(f"{wid}: identity review status {status!r} is not approved")
    declared=review.get("counts",{})
    actual={
      "collisionCanonicalIds":len(rows),
      "pending":sum(r.get("status")=="pending" for r in rows),
      "approved":sum(r.get("status")=="approved" for r in rows),
    }
    for key,val in actual.items():
        if declared.get(key)!=val:
            failures.append(f"counts.{key}={declared.get(key)!r} != actual {val}")
    result={"ok":not failures,"releaseMode":release,"counts":actual,"failures":failures}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
