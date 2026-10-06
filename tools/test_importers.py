#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))

def load(name):
    p=ROOT/"tools"/f"{name}.py"
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

naer=load("import_naer")
gept=load("import_gept")
identity=load("vocab_identity")

# NAER: commas inside parenthetical aliases must not split an entry.
parts=naer.split_entries("color (colour, colors), dog, take care of")
assert parts==["color (colour, colors)","dog","take care of"],parts

# GEPT: dotted/slashed POS and all three levels.
sample="""apple noun 蘋果 初級
compound adj./noun 測試二 中級
numberword number/pron./noun/adj. 測試 初級
zeal noun 熱忱 中高級
"""
entries,rejected=gept.parse(sample)[:2]
assert not rejected,rejected
assert len(entries)==4,(entries,rejected)
assert entries[0]["listId"]=="gept-elementary"
assert entries[1]["pos"]=="adj./noun"
assert entries[1]["listId"]=="gept-intermediate"
assert entries[3]["listId"]=="gept-high-intermediate"

# Real LTTC PDF text-layer patterns: wrapped rows, standalone page number,
# and repeated page header glued to the prior row.
real_layout="""iron noun
12
鐵 初級
affect verb 影響、(疾病)感染 初級 L2 1字彙 詞類 中文 註解 級數 學術字彙
affection noun 喜愛、鍾愛 中級
vinegar noun
醋 初級
"""
assert gept.clean_line("affect verb 影響 初級 L2 1字彙 詞類 中文 註解 級數 學術字彙")=="affect verb 影響 初級 L2"
real_entries,real_rejected=gept.parse(real_layout)[:2]
assert not real_rejected,real_rejected
assert [(e["word"],e["listId"]) for e in real_entries]==[
    ("iron","gept-elementary"),
    ("affect","gept-elementary"),
    ("affection","gept-intermediate"),
    ("vinegar","gept-elementary"),
],real_entries

# Shared canonical identity and POS normalization.
fragmented="""magic noun 魔法 初級
magician noun 魔術師 初級
orphan noun
heavenly adj. 天上的 中級
"""
frag_entries,frag_rejected=gept.parse(fragmented)[:2]
assert [e["word"] for e in frag_entries]==["magic","magician","heavenly"],frag_entries
assert frag_rejected==["orphan noun"],frag_rejected

shifted="反對；靠著 against prep. 反對、靠著 初級"
shift_entries,shift_rejected,shift_fragments=gept.parse(shifted)
assert len(shift_entries)==1 and shift_entries[0]["word"]=="against",shift_entries
assert shift_rejected==[],shift_rejected
assert shift_fragments and shift_fragments[0]["fragment"]=="反對；靠著",shift_fragments

assert identity.canonical_id(" Colour ")=="colour"
assert identity.canonical_id("COLOR")=="color"
assert identity.canonical_id("color")!=identity.canonical_id("colour")
assert identity.pos_tokens("noun/verb")=={"noun","verb"}
assert identity.pos_tokens("n./v.")=={"noun","verb"}
assert identity.pos_tokens("adjective") & identity.pos_tokens("adj.")



def test_gept_deferred_row():
    text="""again adv. 再一次 初級
against prep. 初級
緊貼著、倚靠著；逆著...的方向、迎著；反對、與...相反
about prep. 關於 初級
"""
    entries,rejected,fragments=gept.parse(text)
    by_word={e["word"]:e for e in entries}
    assert by_word["against"]["zh"].startswith("緊貼著"),by_word["against"]
    assert by_word["again"]["zh"]=="再一次",by_word["again"]
    assert rejected==[],rejected
    assert any(x.get("rowWord")=="against" for x in fragments),fragments

test_gept_deferred_row()


def test_gept_meaning_wraps_before_and_after_partial_row():
    text="""again adv. 再一次 初級
緊貼著、倚靠著；逆著...的方向、迎著；反對、與...相反；以...為
against prep. 初級
背景、襯托；防...、抗...
about prep. 關於 初級
"""
    entries,rejected,fragments=gept.parse(text)
    by_word={e["word"]:e for e in entries}
    assert by_word["against"]["zh"]=="緊貼著、倚靠著；逆著...的方向、迎著；反對、與...相反；以...為背景、襯托；防...、抗...",by_word["against"]
    assert by_word["again"]["zh"]=="再一次",by_word["again"]
    assert rejected==[],rejected

def test_gept_pos_glossary_is_layout_not_vocabulary():
    entries,rejected,fragments=gept.parse("adjective noun 形容詞 = adj. 中級\nauxiliary noun 助動詞 = aux. 中級")
    assert entries==[],entries
    assert rejected==[],rejected
    assert len(fragments)==2,fragments

test_gept_meaning_wraps_before_and_after_partial_row()
test_gept_pos_glossary_is_layout_not_vocabulary()

def test_gept_cjk_wrap_spacing_is_stable():
    a=gept.parse("以...為背景、襯托；\nagainst prep. 初級\n防...、抗...")[0]
    b=gept.parse("以...為\nagainst prep. 初級\n背景、襯托；防...、抗...")[0]
    assert a[0]["zh"]==b[0]["zh"],(a[0],b[0])

test_gept_cjk_wrap_spacing_is_stable()

def test_gept_revision_footer_with_layout_counters_is_ignored():
    entries,rejected,fragments=gept.parse("zoom verb 放大 中高級\n1 1 1 1 2026/08/21修訂")
    assert len(entries)==1,entries
    assert rejected==[],rejected
    assert fragments==[],fragments

test_gept_revision_footer_with_layout_counters_is_ignored()

def test_naer_real_pdf_heading_spacing():
    text="""附錄五：參考字彙表（2,000 字）
  表一、基本 1, 200 字（依字母排列）
A- a/an, able
表二、其他常用 800 字（依字母排列）
A- absent, accept
表三、參考字彙表（2,000 字），依主題、詞性分類
1. People
"""
    m1=naer.T1_RE.search(text); m2=naer.T2_RE.search(text,m1.end())
    m3=naer.T3_RE.search(text,m2.end())
    assert m1 and m2 and m3
    assert naer.split_entries(text[m1.end():m2.start()])==["a/an","able"]
    assert naer.split_entries(text[m2.end():m3.start()])==["absent","accept"]

test_naer_real_pdf_heading_spacing()

def test_naer_alphabet_label_does_not_consume_previous_entry():
    assert naer.split_entries("husband,\nI- I (me, my, mine, myself), ice")==[
        "husband","I (me, my, mine, myself)","ice"
    ]

test_naer_alphabet_label_does_not_consume_previous_entry()

print("IMPORTER TESTS: PASS")