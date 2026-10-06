#!/usr/bin/env python3
import importlib.util
from pathlib import Path
p=Path(__file__).with_name("crosscheck_naer_table3.py")
spec=importlib.util.spec_from_file_location("table3",p)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

table=m.norm("soy sauce, Father's Day, U.S.A./USA, bus stop")
assert m.contains_form(table,"soy-sauce")
assert m.contains_form(table,"soy sauce")
assert m.contains_form(table,"Father's Day")
assert m.contains_form(table,"bus stop")
assert not m.contains_form(table,"us")
assert not m.contains_form(table,"station")
print("NAER TABLE 3 TESTS: PASS")
