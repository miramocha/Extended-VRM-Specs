---
title: VRMC_materials_mtoonxt zTest
aliases:
  - MToonXT zTest
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMC_materials_mtoonxt zTest

`zTest` extra on [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md).

Forward / outline / add depth compare. Omitted or `"lessEqual"` matches stock MToon.
`"always"` ignores all closer depth, including props in front of the camera.

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `zTest` | string | no | Compare function; omit for `"lessEqual"` |

Allowed strings: `never`, `less`, `equal`, `lessEqual`, `greater`, `notEqual`,
`greaterEqual`, `always`. Unrecognized values MUST be ignored (hub rule 11); shader
default `"lessEqual"`.

Unity maps this to `_M_ZTest`. Shader assignment leaves that float at `0`
(Disabled). Consumers MUST write the resolved enum after swap (`lessEqual` = `4`
when the key is omitted).

Eyebrow over hair without covering scene props: keep brow `"lessEqual"`. `"always"`
draws over the whole scene. Pair with [ZWrite](vrmc-materials-mtoonxt-zwrite.md) and
[render queue](vrmc-materials-mtoonxt-render-queue.md) as needed. Stencil punch of
soft-alpha hair cuts holes; prefer depth/queue for that overlay.

## Related

- [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md)
- [ZWrite](vrmc-materials-mtoonxt-zwrite.md)
- [Render queue](vrmc-materials-mtoonxt-render-queue.md)
- [Stencil](vrmc-materials-mtoonxt-stencil.md)
