#!/usr/bin/env python3
"""Small parser regression tests using known official-layout edge cases."""
import importlib.util,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

naer=mod("naer","tools/import_naer.py")
gept=mod("gept","tools/import_gept.py")
identity=mod("identity","tools/vocab_identity.py")

x=naer.split_entries("father (dad, daddy), mother (mom, mommy), airplane (plane)")
assert x==["father (dad, daddy)","mother (mom, mommy)","airplane (plane)"],x
assert "daddy" in naer.aliases(x[0])

sample="""abandon verb 放棄 中級 L8
numberword number/pron./noun/adj. 測試 初級
zeal noun 熱忱 中高級
zipper noun 拉鍊 中級
"""
entries,rejected=gept.parse(sample)
assert len(entries)==4,(entries,rejected)
assert not rejected,rejected
assert entries[2]["listId"]=="gept-high-intermediate"

# Real LTTC PDF text-layer patterns: wrapped rows and page header glued to prior row.
real_layout="""iron noun\n12
鐵 初級
affect verb 影響、(疾病)感染 初級 L2 1字彙 詞類 中文 註解 級數 學術字彙
affection noun 喜愛、鍾愛 中級
vinegar noun
醋 初級
"""
assert gept.clean_line("affect verb 影響 初級 L2 1字彙 詞類 中文 註解 級數 學術字彙")=="affect verb 影響 初級 L2"
real_entries,real_rejected=gept.parse(real_layout)
assert not real_rejected,real_rejected
assert [(e["word"],e["listId"]) for e in real_entries]==[
 ("iron","gept-elementary"),("affect","gept-elementary"),
 ("affection","gept-intermediate"),("vinegar","gept-elementary")],real_entries

assert identity.canonical_id("  Mother’s   Day ")=="mother's day"
assert identity.canonical_id("well–known")=="well-known"
assert identity.canonical_id("colour")!=identity.canonical_id("color")
assert identity.pos_tokens("noun/verb")=={"noun","verb"}
assert identity.pos_tokens("n./v.")=={"noun","verb"}
assert identity.pos_tokens("adjective") & identity.pos_tokens("adj.")
print("parser and identity regression tests: PASS")
