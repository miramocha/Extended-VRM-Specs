---
title: VRMC_materials_mtoonxt Face SDF
aliases:
  - MToonXT Face SDF
  - faceSdf
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMC_materials_mtoonxt Face SDF

`faceSdf` extra on [VRMC_materials_mtoonxt](README.md).

## `faceSdf`

Omit the object to leave Face SDF off. When the object is present:

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `enabled` | boolean | no | `false` | Apply Face SDF |
| `sdfTexture` | textureInfo | no | none | glTF texture info (`index`, optional `texCoord`); R channel |
| `softness` | number | no | `0` | Inclusive `[0,1]`; `0` is a hard edge |
| `flipLuminance` | boolean | no | `false` | Sample `1 - R` |

`sdfTexture.index` MUST be a valid zero-based index into `textures[]` when `enabled` is
true. An out-of-range index, a missing texture, or a `softness` outside `[0,1]` makes
`faceSdf` unresolvable (hub rule 11). `texCoord` follows glTF textureInfo; default `0`.

When `enabled` is true and `sdfTexture` resolves, the consumer MUST derive a shade
factor from the texture **R** channel using the **main light direction in VRM humanoid
`head` bone object space**. If the humanoid `head` bone is missing, it MUST use the
object space of the node that owns the mesh. If `flipLuminance` is true, it MUST use
`1 - R`. Stock sibling `shadingShiftFactor` and `shadingToonyFactor` MUST still shape
that factor.

How the head-space light direction maps to UV (azimuth-only vs spherical, left/right
bake convention) is **TBD**. The first Unity BIRP fork documents the layout it samples;
other engines MUST NOT assume a layout until this specification locks one.

An exporter that emits `faceSdf.sdfTexture` MUST register the referenced image through
its normal glTF texture export path (hub rule 16).

## Example

Non-normative. Texture `4` is the Face SDF map.

```json
"VRMC_materials_mtoonxt": {
  "specVersion": "1.0",
  "faceSdf": {
    "enabled": true,
    "sdfTexture": { "index": 4 },
    "softness": 0.1
  }
}
```

## Related

- [VRMC_materials_mtoonxt](README.md)
- [MToon10 stencil shader fork](../../../../references/research/mtoon10-stencil-shader-fork.md)
