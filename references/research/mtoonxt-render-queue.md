---
title: MToonXT renderQueueOffset (Unity experiment)
aliases:
  - MToonXT render queue
  - MToonXT renderQueueOffset
tags:
  - extended-vrm
  - reference/engine
  - spec/materials
  - implementation/unity
type: reference
status: draft
---

# MToonXT renderQueueOffset (Unity experiment)

Non-normative. Not a
[VRMXT_materials_mtoonxt](../../specs/extensions/materials/vrmxt-materials-mtoonxt/README.md)
extra. UniVRMXT ignores `renderQueueOffset` on that object (hub rule 12). Stock
MToon still uses `renderQueueOffsetNumber` on `VRMC_materials_mtoon`.

The retired stencil format required `write` before `inside` / `outside` readers.
Current root graphs instead compile coverage and color passes according to their
presentation flags; the old queue nudges do not describe that compiler.
This historical integer is a Unity queue nudge after stock MToon
mapping (`alphaMode` / `transparentWithZWrite`, then `_AlphaMode` restore). MToon
`renderQueueOffsetNumber` on `MASK` is always 0 (Unity `AlphaTest` 2450).

| File value (historical) | Meaning if a consumer applied it |
|-------------------------|----------------------------------|
| omit or `0` | keep the mapped queue |
| `N` | mapped queue + `N` |

The older UniVRMXT body `write` mapping drew earlier as stencil pass order.
That was not this file key.

No ±9 clamp. Cutout 2450 − 2 = 2448; 2450 + 551 = 3001 (transparent bucket). Final
Unity queue outside `[0, 5000]` is ignored. Non-integer ignored.

`BLEND` at 2449 is the opaque bucket in Unity.

On `mirabunny2026_2.stencil_2.vrm`, White `-2` / Iris `-1` ordered sclera before
iris; Hair `551` moved hair to ~3001. Iris-in-sclera and brow-through-hair use
retired stencil operations; see the replacement
[root stencil graph](../../specs/extensions/materials/vrmxt-materials-mtoonxt/stencil.md).

## Related

- [VRMXT_materials_mtoonxt](../../specs/extensions/materials/vrmxt-materials-mtoonxt/README.md)
- [Stencil](../../specs/extensions/materials/vrmxt-materials-mtoonxt/stencil.md)
- [MToonXT zWrite](mtoonxt-zwrite.md)
- [MToonXT zTest](mtoonxt-ztest.md)
