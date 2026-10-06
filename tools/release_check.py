#!/usr/bin/env python3
"""Fail closed unless an official vocabulary release satisfies manifest-level gates."""
from __future__ import annotations
import json,sys
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    sources=load(sys.argv[1]); snapshots=[load(p) for p in sys.argv[2:]]
    source_by_id={x["id"]:x for x in sources["sources"]}
    failures=[]
    for snap in snapshots:
        sid=snap.get("sourceId"); src=source_by_id.get(sid)
        if not src:
            failures.append(f"{sid}: source missing from manifest")
            continue
        for field in ("publisher","title","url","version","checkedAt"):
            if not src.get(field):
                failures.append(f"{sid}: missing source field {field}")
        if src.get("active") is not True:
            failures.append(f"{sid}: source is not active")
        if src.get("trust")!="official":
            failures.append(f"{sid}: source trust is not official")
        revision=snap.get("sourceRevision")
        document_versions=src.get("documentVersions") or {}
        document_key={"GEPT_Elementary.pdf":"elementary","GEPT_Intermediate.pdf":"intermediate","GEPT_High-Intermediate.pdf":"highIntermediate"}.get(snap.get("sourceDocument"))
        expected_revision=document_versions.get(document_key) if document_versions else src.get("version")
        if document_versions and not document_key:
            failures.append(f"{sid}: sourceDocument {snap.get('sourceDocument')} has no documentVersions mapping")
        if revision is not None and expected_revision is not None and str(revision)!=str(expected_revision):
            failures.append(f"{sid}: snapshot revision {revision} != expected document revision {expected_revision}")
        if snap.get("catalogRole")=="validation-only":
            failures.append(f"{sid}: validation-only snapshot cannot be released as catalog source")
        if snap.get("verified") is not True:
            failures.append(f"{sid}: snapshot is not verified")
        if snap.get("rejected"):
            failures.append(f"{sid}: {len(snap['rejected'])} rejected blocks remain")
        review=snap.get("review",{})
        for gate in ("freshness","structure","diff","identity","masteryMigration"):
            if review.get(gate)!="pass":
                failures.append(f"{sid}: gate {gate} != pass")
        if not snap.get("retrievedAt"):
            failures.append(f"{sid}: missing retrievedAt")
    result={"ok":not failures,"checked":len(snapshots),"failures":failures}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
