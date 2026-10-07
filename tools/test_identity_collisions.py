#!/usr/bin/env python3
import importlib.util
from pathlib import Path

p=Path(__file__).with_name("audit_identity_collisions.py")
spec=importlib.util.spec_from_file_location("identity_audit",p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

snapshot={"sourceId":"test","sourceDocument":"test.pdf","entries":[
  {"officialEntry":"may (might)","wordId":"may"},
  {"officialEntry":"May","wordId":"may"},
  {"officialEntry":"Miss","wordId":"miss"},
  {"officialEntry":"miss","wordId":"miss"},
  {"word":"record","wordId":"record","pos":"noun"},
  {"word":"record","wordId":"record","pos":"verb"},
]}
master=[{"w":"may"},{"w":"miss"},{"w":"record"}]
r=m.build_report(snapshot,master)
assert r["counts"]["collisionCanonicalIds"]==2,r
by={x["wordId"]:x for x in r["collisions"]}
assert by["may"]["sourceForms"]==["May","may"],by["may"]
assert by["miss"]["sourceForms"]==["Miss","miss"],by["miss"]
assert "record" not in by,by
print("IDENTITY COLLISION TESTS: PASS")
