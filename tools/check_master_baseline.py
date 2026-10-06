#!/usr/bin/env python3
import json,sys
from pathlib import Path
actual=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
base=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
keys=("rows","canonicalWords","duplicateCanonicalIds","missingRequiredFields")
diff={k:{"expected":base.get(k),"actual":actual.get(k)} for k in keys if base.get(k)!=actual.get(k)}
print(json.dumps({"ok":not diff,"diff":diff},ensure_ascii=False,indent=2))
if diff: raise SystemExit(1)
