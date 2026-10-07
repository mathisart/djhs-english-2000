#!/usr/bin/env python3
"""Shared vocabulary identity helpers.

Keep identity conservative: normalize typography and spacing, but never stem,
lemmatize, or guess that different spellings are the same word.
"""
from __future__ import annotations
import re,unicodedata

APOSTROPHES=str.maketrans({"’":"'","‘":"'","＇":"'"})
DASHES=str.maketrans({"‐":"-","‑":"-","‒":"-","–":"-","—":"-","−":"-"})

def display_normalize(value:str)->str:
    s=unicodedata.normalize("NFKC",value or "")
    s=s.translate(APOSTROPHES).translate(DASHES)
    return re.sub(r"\s+"," ",s.strip())

def canonical_id(value:str)->str:
    return display_normalize(value).casefold()

def base_and_parenthetical(value:str):
    s=display_normalize(value)
    m=re.match(r"^(.*?)\s*\((.*?)\)\s*$",s)
    if not m: return s,[]
    aliases=[display_normalize(x) for x in m.group(2).split(",") if x.strip()]
    return display_normalize(m.group(1)),aliases

POS_ALIASES={
 "n":"noun","n.":"noun","noun.":"noun","v":"verb","v.":"verb","verb.":"verb","a":"adj.","adj":"adj.","adjective":"adj.",
 "adv":"adv.","adverb":"adv.","prep":"prep.","preposition":"prep.","pron":"pron.","pronoun":"pron.",
 "conj":"conj.","conjunction":"conj.","art":"art.","article":"art.","det":"determiner","det.":"determiner"
}
def pos_tokens(value:str):
    """Return conservative normalized POS tokens from slash/comma/space notation."""
    s=display_normalize(value).lower()
    parts=[p.strip() for p in re.split(r"[/,;]+",s) if p.strip()]
    return {POS_ALIASES.get(p,p) for p in parts}
