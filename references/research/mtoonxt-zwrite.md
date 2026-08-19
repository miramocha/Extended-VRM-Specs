---
title: MToonXT zWrite (Unity experiment)
aliases:
  - MToonXT zWrite
tags:
  - extended-vrm
  - reference/engine
  - spec/materials
  - implementation/unity
type: reference
status: draft
---

# MToonXT zWrite (Unity experiment)

Non-normative. Not a [VRMC_materials_mtoonxt](../../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
extra. UniVRMXT may still read a `zWrite` boolean on that object (hub rule 12:
unrecognized keys ignored by other consumers).

Applied after stock MToon ZWrite mapping. `false` turns off depth writes (Unity
`_M_ZWrite` = 0). Omit to keep the mapping (cutout stays ZWrite on).

`false` lets a later material overdraw this one despite closer depth (iris under
face highlight). Hair cutout `zWrite` false can break bangs. This is overlay, not
stencil clip.

## Related

- [VRMC_materials_mtoonxt](../../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
- [MToonXT zTest](mtoonxt-ztest.md)
- [Stencil](../../specs/extensions/materials/vrmc-materials-mtoonxt/stencil.md)
- [renderQueueOffset](mtoonxt-render-queue.md)
