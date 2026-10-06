#!/usr/bin/env python3
"""Small parser regression tests using known official-layout edge cases."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

naer=mod("naer","tools/import_naer.py")
gept=mod("gept","tools/import_gept.py")

# A comma inside aliases is not an entry delimiter.
x=naer.split_entries("father (dad, daddy), mother (mom, mommy), airplane (plane)")
assert x==["father (dad, daddy)","mother (mom, mommy)","airplane (plane)"],x
assert "daddy" in naer.aliases(x[0])

# Multiple POS components and both high-intermediate labels are accepted.
sample="""abandon verb 放棄 中級 L8
numberword number/pron./noun/adj. 測試 初級
zeal noun 熱忱 中高級
zipper noun 拉鍊 中級
"""
entries,rejected=gept.parse(sample)
assert len(entries)==4,(entries,rejected)
assert not rejected,rejected
assert entries[2]["listId"]=="gept-high-intermediate"

print("parser regression tests: PASS")
