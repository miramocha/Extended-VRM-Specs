---
title: VRMC_materials_mtoonxt renderQueueOffset
aliases:
  - MToonXT render queue
  - MToonXT renderQueueOffset
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMC_materials_mtoonxt renderQueueOffset

`renderQueueOffset` extra on [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md).

Optional integer. Applied **after** stock MToon queue mapping from `alphaMode` /
`transparentWithZWrite` (Unity: after restoring pass settings from `_AlphaMode`).
The consumer adds this value to that mapped queue.

| File value | Meaning |
|------------|---------|
| omit or `0` | keep the mapped queue |
| `N` | mapped queue + `N` |

Do not clamp to MToon's `renderQueueOffsetNumber` bands (`MASK` offset is always 0
there; `BLEND` is ±9). This extra may sort inside a band (cutout 2450 − 2) or leave
it (cutout 2450 + 551 → transparent 3001).

If the **final** Unity queue is outside inclusive `[0, 5000]`, ignore the extra (hub
rule 11) and keep the mapped queue. A non-integer value MUST be ignored.

Stock MToon `renderQueueOffsetNumber` stays in `VRMC_materials_mtoon`. UniVRM still
zeros it on `MASK`. This extra runs after that restore.

Stencil writers MUST draw before clip readers. When mesh primitive order is wrong
(iris before sclera), use a negative offset on the reader or writer so cutout
materials sort inside `AlphaTest` (2450). Example: White `-2` (2448), iris `-1`
(2449). Do not put `BLEND` materials at 2449: Unity treats that as the opaque
bucket.

## Related

- [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md)
- [Stencil](vrmc-materials-mtoonxt-stencil.md)
- [ZWrite](vrmc-materials-mtoonxt-zwrite.md)
