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
[Materials Override Catalogs](../../materials-override-catalogs.md) lives in this folder.

| File | `shaderName` | Status |
|------|--------------|--------|
| `unity-liltoon.json` | `lilToon` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-liltoon-cutout.json` | `Hidden/lilToonCutout` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-liltoon-transparent.json` | `Hidden/lilToonTransparent` | shipped (lilToon `2.3.4`, 359 props) |
| `unity-liltoon-warudo.json` | `lilToon` | shipped (lilToon `1.10.3` Warudo, 356 props) |
| `unity-liltoon-warudo-cutout.json` | `Hidden/lilToonCutout` | shipped (lilToon `1.10.3` Warudo, 356 props) |
| `unity-liltoon-warudo-transparent.json` | `Hidden/lilToonTransparent` | shipped (lilToon `1.10.3` Warudo, 356 props) |
| `unity-vrmxt-test-override-builtin.json` | `VRMXT/Samples/TestOverrideBuiltin` | shipped (UniVRMXT test sample, 11 props) |
| `unity-vrmxt-test-override-urp.json` | `VRMXT/Samples/TestOverrideURP` | shipped (UniVRMXT test sample, 11 props) |
| `unity-poiyomi.json` | — | planned |

Family notes: [Unity lilToon](../unity-liltoon.md),
[Unity lilToon Warudo](../unity-liltoon-warudo.md),
[Unity VRMXT Test Override](../unity-vrmxt-test-override.md),
[Unity Poiyomi](../unity-poiyomi.md).

Consumers vendor-copy these files; see **Distribution** on the catalogs index.
Pin bump / regen: [Maintaining catalogs](../maintaining-catalogs.md).
Do not treat this folder as a glTF schema.
