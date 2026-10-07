#!/usr/bin/env python3
import json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    sources={"sources":[{"id":"moe","active":True,"version":"v1","checkedAt":"2026-10-07","publisher":"NAER"}]}
    catalog={"words":[{"wordId":"a","memberships":["moe-basic-1200"]},{"wordId":"b","memberships":["gept-elementary"]}]}
    audit={"rows":2,"canonicalWords":2,"duplicateCanonicalIds":0,"missingRequiredFields":{}}
    naer={"sourceId":"moe","counts":{"exactMatchedWords":2}}
    gept={"sourceId":"gept","sourceDocument":"GEPT_High-Intermediate.pdf","diagnosticOnly":True,"counts":{"matchedMasterWords":2}}
    migration={"oldCanonical":2,"newCanonical":2,"sharedCanonical":2,"oldNotInNew":[],"newNotInOld":[],"duplicateNewIds":{}}
    vals={"sources":sources,"catalog":catalog,"audit":audit,"naer":naer,"gept":gept,"migration":migration}
    for name,obj in vals.items():
        (d/f"{name}.json").write_text(json.dumps(obj),encoding="utf-8")
    out=d/"report.json"
    subprocess.run([sys.executable,str(ROOT/"tools/release_report.py"),str(d/"sources.json"),str(d/"catalog.json"),str(d/"audit.json"),str(d/"naer.json"),str(d/"gept.json"),str(d/"migration.json"),str(out)],check=True,capture_output=True,text=True)
    report=json.loads(out.read_text(encoding="utf-8"))
    assert report["schemaVersion"]==2,report
    assert len(report["officialDiffs"])==2,report
    assert [x["sourceId"] for x in report["officialDiffs"]]==["moe","gept"],report
    assert "officialDiff" not in report,report

    single=d/"single.json"
    subprocess.run([sys.executable,str(ROOT/"tools/release_report.py"),str(d/"sources.json"),str(d/"catalog.json"),str(d/"audit.json"),str(d/"naer.json"),str(d/"migration.json"),str(single)],check=True,capture_output=True,text=True)
    one=json.loads(single.read_text(encoding="utf-8"))
    assert one["officialDiff"]=={"exactMatchedWords":2},one
print("RELEASE REPORT TESTS: PASS")
