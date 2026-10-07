#!/usr/bin/env python3
"""Regression tests for fail-closed official vocabulary release gates."""
from __future__ import annotations
import json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable

def run(*args):
    return subprocess.run([PY,*map(str,args)],cwd=ROOT,text=True,capture_output=True)

def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        lists={"schemaVersion":1,"lists":[{"id":"gept-elementary"},{"id":"gept-intermediate"},{"id":"gept-high-intermediate"}]}
        lists_p=td/"lists.json"; write(lists_p,lists)
        sources={"schemaVersion":1,"sources":[{
            "id":"gept-current-2026-10-06","publisher":"LTTC","title":"GEPT Word Lists",
            "url":"https://example.invalid","version":"mixed-current","checkedAt":"2026-10-06",
            "active":True,"trust":"official",
            "documentVersions":{"highIntermediate":"2026-08-21"}
        }]}
        sources_p=td/"sources.json"; write(sources_p,sources)
        base={
            "sourceId":"gept-current-2026-10-06","sourceDocument":"GEPT_High-Intermediate.pdf",
            "sourceRevision":"2026-08-21","catalogRole":"authoritative","verified":True,
            "retrievedAt":"2026-10-06T00:00:00Z","rejected":[],
            "layoutFragments":[{"fragment":"wrapped meaning","rowWord":"against"}],
            "review":{"freshness":"pass","structure":"pass","diff":"pass","identity":"pass","masteryMigration":"pass"},
            "entries":[{"word":"against","wordId":"against","pos":"prep.","zh":"反對","level":"初級","listId":"gept-elementary","awl":None}]
        }
        snap=td/"snap.json"; write(snap,base)

        r=run("tools/validate_official.py",snap)
        assert r.returncode!=0 and "layout fragments require review" in (r.stdout+r.stderr),r.stdout+r.stderr

        out=td/"catalog.json"
        r=run("tools/build_catalog.py",lists_p,snap,out)
        assert r.returncode!=0 and "unreviewed layout fragments" in (r.stdout+r.stderr),r.stdout+r.stderr

        r=run("tools/release_check.py",sources_p,snap)
        assert r.returncode!=0 and "layout fragments require review" in (r.stdout+r.stderr),r.stdout+r.stderr

        reviewed=json.loads(json.dumps(base))
        reviewed["review"]["layoutFragments"]="pass"
        write(snap,reviewed)
        r=run("tools/validate_official.py",snap)
        assert r.returncode==0,r.stdout+r.stderr
        r=run("tools/build_catalog.py",lists_p,snap,out)
        assert r.returncode==0,r.stdout+r.stderr
        built=json.loads(out.read_text(encoding="utf-8"))
        assert built["schemaVersion"]==2,built
        assert len(built["words"])==1,built
        assert len(built["memberships"])==1,built
        assert built["memberships"][0]["wordId"]=="against",built
        assert built["memberships"][0]["listId"]=="gept-elementary",built
        assert len(built["memberships"][0]["sourceEntryIds"])==1,built
        assert len(built["sourceEntries"])==1,built

        sense=json.loads(json.dumps(reviewed))
        sense["layoutFragments"]=[]
        sense["entries"]=[
            {"word":"record","wordId":"record","pos":"noun","zh":"紀錄","level":"初級","listId":"gept-elementary","awl":None},
            {"word":"record","wordId":"record","pos":"verb","zh":"記錄","level":"中級","listId":"gept-intermediate","awl":None},
        ]
        sense_p=td/"sense.json"; write(sense_p,sense)
        sense_out=td/"sense-catalog.json"
        r=run("tools/build_catalog.py",lists_p,sense_p,sense_out)
        assert r.returncode==0,r.stdout+r.stderr
        sense_catalog=json.loads(sense_out.read_text(encoding="utf-8"))
        assert len(sense_catalog["words"])==1,sense_catalog
        assert [(m["wordId"],m["listId"]) for m in sense_catalog["memberships"]]==[
            ("record","gept-elementary"),("record","gept-intermediate")
        ],sense_catalog
        assert all(len(m["sourceEntryIds"])==1 for m in sense_catalog["memberships"]),sense_catalog
        assert len(sense_catalog["sourceEntries"])==2,sense_catalog

        r=run("tools/release_check.py",sources_p,snap)
        assert r.returncode==0,r.stdout+r.stderr

        safe_layout=json.loads(json.dumps(reviewed))
        safe_layout["layoutFragments"]=[
            {"fragment":"前半","rowWord":"against","reason":"Chinese continuation preceding deferred word/POS/level row"},
            {"fragment":"後半","rowWord":"against","reason":"Chinese continuation attached to deferred word/POS/level row"},
            {"fragment":"adjective noun 形容詞 = adj. 中級","reason":"GEPT POS glossary row, not vocabulary"}
        ]
        write(snap,safe_layout)
        r=run("tools/review_layout_fragments.py",snap)
        assert r.returncode==0,r.stdout+r.stderr

        unsafe=json.loads(json.dumps(safe_layout))
        unsafe["layoutFragments"].append({"fragment":"mystery","reason":"unattached Chinese layout continuation"})
        write(snap,unsafe)
        r=run("tools/review_layout_fragments.py",snap)
        assert r.returncode!=0 and "unattached Chinese layout continuation" in (r.stdout+r.stderr),r.stdout+r.stderr

        bad=json.loads(json.dumps(reviewed)); bad["sourceRevision"]="2026-04-29"; write(snap,bad)
        r=run("tools/release_check.py",sources_p,snap)
        assert r.returncode!=0 and "expected document revision 2026-08-21" in (r.stdout+r.stderr),r.stdout+r.stderr

    print("RELEASE GATE TESTS: PASS")

if __name__=="__main__":
    main()
