#!/usr/bin/env python3
"""Validate source/list manifests before touching official snapshots."""
from __future__ import annotations
import json,sys
from pathlib import Path
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def main():
    sources=load(sys.argv[1]); lists=load(sys.argv[2]); failures=[]
    src={x["id"]:x for x in sources["sources"]}; ls={x["id"]:x for x in lists["lists"]}
    if len(src)!=len(sources["sources"]): failures.append("duplicate source IDs")
    if len(ls)!=len(lists["lists"]): failures.append("duplicate list IDs")
    for lid,d in ls.items():
        sid=d.get("sourceId")
        if sid not in src: failures.append(f"{lid}: unknown sourceId {sid}")
        parent=d.get("parent")
        if parent and parent not in ls: failures.append(f"{lid}: unknown parent {parent}")
        for x in d.get("derivedFrom",[]):
            if x not in ls: failures.append(f"{lid}: unknown derivedFrom {x}")
            if x==lid: failures.append(f"{lid}: derives from itself")
    # Detect derived-list cycles.
    def visit(n,stack,done):
        if n in stack: failures.append("derived cycle: "+" -> ".join(stack+[n])); return
        if n in done: return
        for x in ls[n].get("derivedFrom",[]):\n            if x in ls: visit(x,stack+[n],done)
        done.add(n)
    done=set()
    for n in ls: visit(n,[],done)
    print(json.dumps({"ok":not failures,"sources":len(src),"lists":len(ls),"failures":failures},ensure_ascii=False,indent=2))
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
