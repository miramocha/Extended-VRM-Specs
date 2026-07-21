---
name: inspect-vrm-json
description: Parse, extract, summarize, and compare JSON and binary chunks in VRM, GLB, and glTF files. Use when checking VRM extensions, VRMXT metadata, round-trip survival, GLB hashes, chunk equality, or semantic JSON differences.
---

# Inspect VRM JSON

Use `scripts/inspect_vrm.py`. It needs Python 3 and only uses the standard library.

## Commands

Run paths relative to this skill directory, or use absolute paths.

```powershell
python scripts/inspect_vrm.py summary "model.vrm"
python scripts/inspect_vrm.py summary "model.vrm" --extension VRMXT
python scripts/inspect_vrm.py extract "model.vrm" --pretty -o "model.gltf.json"
python scripts/inspect_vrm.py compare "before.vrm" "after.vrm"
```

## Workflow

1. Use `summary` to report file hash, GLB chunks, glTF counts, `extensionsUsed`,
   root extensions, and every nested extension attachment.
2. Add `--extension VRMXT` when only VRMXT payloads matter.
3. Use `compare` for round trips. Report separately:
   - whole-file hash and size;
   - JSON and BIN chunk byte equality;
   - parsed JSON semantic equality;
   - float-spelling differences when equal JSON was reserialized.
4. Use `extract` only when the user wants the complete JSON written or printed.

Never infer data loss from a changed whole-file hash alone. GLB JSON may change byte
length because equivalent floats use fixed or scientific notation. Treat equal parsed
JSON plus an equal BIN chunk as a semantic round trip.
