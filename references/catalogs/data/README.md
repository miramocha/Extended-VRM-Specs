---
title: Materials Override Catalog Data
aliases: []
tags:
  - extended-vrm
  - reference/materials-override
type: reference
status: draft
---

# Materials Override Catalog Data

Machine-readable catalog JSON for
[Materials Override Catalogs](../materials-override-catalogs.md) lives in this folder.

| File | `shaderName` | Status |
|------|--------------|--------|
| `unity-liltoon.json` | `lilToon` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-liltoon-cutout.json` | `Hidden/lilToonCutout` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-liltoon-transparent.json` | `Hidden/lilToonTransparent` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-vrmxt-test-override-builtin.json` | `VRMXT/Samples/TestOverrideBuiltin` | shipped (UniVRMXT test sample, 11 props) |
| `unity-vrmxt-test-override-urp.json` | `VRMXT/Samples/TestOverrideURP` | shipped (UniVRMXT test sample, 11 props) |
| `unity-poiyomi.json` | — | planned |

Family notes: [Unity lilToon](../unity-liltoon.md),
[Unity VRMXT Test Override](../unity-vrmxt-test-override.md),
[Unity Poiyomi](../unity-poiyomi.md).

Consumers vendor-copy these files; see **Distribution** on the catalogs index.
Do not treat this folder as a glTF schema.
