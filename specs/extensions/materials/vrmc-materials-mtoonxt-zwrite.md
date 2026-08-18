---
title: VRMC_materials_mtoonxt zWrite
aliases:
  - MToonXT zWrite
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMC_materials_mtoonxt zWrite

`zWrite` extra on [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md).

Optional boolean. Applied after stock MToon ZWrite mapping. `false` turns off depth
writes (Unity `_M_ZWrite` = 0). Omit to keep the mapping (cutout stays ZWrite on).
A non-boolean value MUST be ignored (hub rule 11).

Use `false` when a later material must overdraw this one despite closer depth (iris
under face highlight). Hair cutout `zWrite` false can break bangs; test per mesh.

## Related

- [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md)
- [ZTest](vrmc-materials-mtoonxt-ztest.md)
- [Render queue](vrmc-materials-mtoonxt-render-queue.md)
- [Stencil](vrmc-materials-mtoonxt-stencil.md)
