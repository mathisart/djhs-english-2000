#!/usr/bin/env python3
"""Generate an auditable, read-only vocabulary release report."""
from __future__ import annotations
import json,sys
from pathlib import Path
from datetime import datetime,timezone

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def main():
    if len(sys.argv)<7:
        raise SystemExit("usage: release_report.py SOURCES CATALOG MASTER_AUDIT DIFF [DIFF...] MIGRATION OUT")
    sources=load(sys.argv[1]); catalog=load(sys.argv[2]); audit=load(sys.argv[3])
    diffs=[load(p) for p in sys.argv[4:-2]]
    migration=load(sys.argv[-2]); out=Path(sys.argv[-1])
    active=[{"id":s["id"],"version":s.get("version"),"checkedAt":s.get("checkedAt"),
             "publisher":s.get("publisher")} for s in sources["sources"] if s.get("active")]
    memberships={}
    for w in catalog["words"]:
        for lid in w.get("memberships",[]): memberships[lid]=memberships.get(lid,0)+1
    official_diffs=[]
    for d in diffs:
        official_diffs.append({
          "sourceId":d.get("sourceId"),
          "sourceDocument":d.get("sourceDocument"),
          "sourceRevision":d.get("sourceRevision"),
          "diagnosticOnly":d.get("diagnosticOnly"),
          "counts":d.get("counts",{})
        })
    report={
      "schemaVersion":2,
      "generatedAt":datetime.now(timezone.utc).isoformat(),
      "activeSources":active,
      "catalog":{"canonicalWords":len(catalog["words"]),"memberships":memberships},
      "currentMaster":{"rows":audit.get("rows"),"canonicalWords":audit.get("canonicalWords"),
                       "duplicateCanonicalIds":audit.get("duplicateCanonicalIds"),
                       "missingRequiredFields":audit.get("missingRequiredFields")},
      "officialDiffs":official_diffs,
      "masteryMigration":{
        "oldCanonical":migration.get("oldCanonical"),"newCanonical":migration.get("newCanonical"),
        "sharedCanonical":migration.get("sharedCanonical"),
        "oldNotInNew":len(migration.get("oldNotInNew",[])),
        "newNotInOld":len(migration.get("newNotInOld",[])),
        "duplicateNewIds":len(migration.get("duplicateNewIds",{}))
      }
    }
    if len(official_diffs)==1:
        report["officialDiff"]=official_diffs[0]["counts"]
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
