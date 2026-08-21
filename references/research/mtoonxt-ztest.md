---
title: MToonXT zTest (Unity experiment)
aliases:
  - MToonXT zTest
tags:
  - extended-vrm
  - reference/engine
  - spec/materials
  - implementation/unity
type: reference
status: draft
---

# MToonXT zTest (Unity experiment)

Non-normative. Not a [VRMC_materials_mtoonxt](../../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
extra. Clip-region overdraw in the extra is
[`stencil.op`](../../specs/extensions/materials/vrmc-materials-mtoonxt/stencil.md)
`insideOverlay`. UniVRMXT may still read a `zTest` string on the parent object (hub
rule 12: unrecognized keys ignored by other consumers).

Forward / outline / add depth compare. Omit or `"lessEqual"` matches stock MToon.
`"always"` ignores closer depth, including scene props in front of the camera.

Allowed strings: `never`, `less`, `equal`, `lessEqual`, `greater`, `notEqual`,
`greaterEqual`, `always`. Unity maps this to `_M_ZTest`. Shader assignment leaves
that float at `0` (Disabled). After swap, write the resolved enum (`lessEqual` = `4`
when omitted).

Eyebrow over hair without covering props: keep brow `"lessEqual"`. `"always"` draws
over the whole scene. Soft-alpha hair stencil still cuts hard holes. See
[zWrite](mtoonxt-zwrite.md) and [renderQueueOffset](mtoonxt-render-queue.md).

## Related

- [VRMC_materials_mtoonxt](../../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
- [MToonXT zWrite](mtoonxt-zwrite.md)
- [Stencil](../../specs/extensions/materials/vrmc-materials-mtoonxt/stencil.md)
