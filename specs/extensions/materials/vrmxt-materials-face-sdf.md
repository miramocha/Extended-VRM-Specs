---
title: VRMXT_materials_face_sdf
aliases:
  - MToonXT Face SDF
  - faceSdf
  - Face SDF
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_materials_face_sdf

Per-material glTF extension. Face shade lookup for a VRM 1.0 MToon material. Sibling
of `VRMC_materials_mtoon` on the same `materials[]` entry. Independent of
[VRMXT_materials_mtoonxt](vrmxt-materials-mtoonxt/README.md),
[VRMXT_materials_stencil](vrmxt-materials-stencil.md), and
[VRMXT_materials_directional_dissolve](vrmxt-materials-directional-dissolve.md).

This document is an Extended VRM draft. It is not a VRM Consortium specification.

Stock VRM 1.0 importers ignore the extension. No shipping consumer applies it yet.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_materials_face_sdf` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | `materials[i].extensions.VRMXT_materials_face_sdf` |
| Required sibling | `VRMC_materials_mtoon` on the same material |
| Root `extensions` | not used |
| Stock importer | no required change |

Do not write Face SDF fields inside `VRMC_materials_mtoon` or as a nested extra on
`VRMXT_materials_mtoonxt`.

## Conformance

This specification conforms to [VRMXT Conformance](../../core/vrmxt-conformance.md).

## Normative requirements

1. Files that use this extension MUST list `VRMXT_materials_face_sdf` in
   `extensionsUsed`.
2. The extension object MUST appear under
   `materials[i].extensions.VRMXT_materials_face_sdf`.
3. The same material MUST contain `extensions.VRMC_materials_mtoon`. If that sibling
   is missing, a supporting implementation MUST ignore this extension on that material.
4. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
5. Files MUST NOT list `VRMXT_materials_face_sdf` in `extensionsRequired`.
6. Implementations that do not support the extension MUST ignore it.
7. The skippable unit is this material's `VRMXT_materials_face_sdf` object. Invalid
   data there MUST NOT make the glTF or VRM 1.0 asset invalid.
8. Unrecognized properties on the extension object MUST be ignored.
9. When `VRMXT_materials_override` **applies** on the same material, a supporting
   implementation MUST NOT apply this extension on that material.
10. An exporter that emits `sdfTexture` MUST register the referenced image through its
    normal glTF texture export path so the index resolves in the output file.

## Fields

Omit the extension object to leave Face SDF off. When the object is present:

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `specVersion` | string | yes | | `"1.0"` for this draft |
| `enabled` | boolean | no | `false` | Apply Face SDF |
| `sdfTexture` | textureInfo | no | none | glTF texture info (`index`, optional `texCoord`); R channel |
| `softness` | number | no | `0` | Inclusive `[0,1]`; `0` is a hard edge |
| `flipLuminance` | boolean | no | `false` | Sample `1 - R` |

`sdfTexture.index` MUST be a valid zero-based index into `textures[]` when `enabled` is
true. An out-of-range index, a missing texture, or a `softness` outside `[0,1]` makes
the object unresolvable (rule 7). `texCoord` follows glTF textureInfo; default `0`.

Fields sit next to `specVersion`.

## Sampling

When `enabled` is true and `sdfTexture` resolves, the consumer MUST sample **R** at
the mesh UV given by `texCoord`. Light direction does not map to texture UV.

The consumer MUST derive a shade factor from that R value and the **horizontal
azimuth of the main light** in VRM humanoid `head` bone object space, orbiting the
head **up** axis. If the humanoid `head` bone is missing, it MUST use the object
space of the node that owns the mesh.

Angle convention (consumer):

- **0°** = light from head **back** (−head forward)
- **180°** = light from head **front**

VRM 1.0 avatars are Y-up, Z-forward in model space. Head bone local axes follow that
humanoid. Blender Front Axis (CL SDF Tools default **+Y**) is authoring-tool space.
A PNG from that add-on is **not** required to match this azimuth until an exporter
remap or a bake-space field exists (**TBD**).

If `flipLuminance` is true, the consumer MUST use `1 - R`. Default `false`. CL SDF
Tools Invert is often on at convert; do not assume that matches this default.

The consumer MUST sample R as **data**, not as sRGB-decoded color. The glTF image or
sampler MAY still be marked sRGB; Face SDF lookup MUST NOT use that decode for the
threshold.

Stock sibling `shadingShiftFactor` and `shadingToonyFactor` MUST still shape the
factor after the SDF lookup.

**TBD:** exact packing of R (threshold vs signed distance), `softness` filter
(smoothstep width vs mip), left/right flip texture and blend window. Other engines
MUST NOT assume a packing until this specification locks one.

## Example

Non-normative. Texture `4` is the Face SDF map.

```json
"VRMXT_materials_face_sdf": {
  "specVersion": "1.0",
  "enabled": true,
  "sdfTexture": { "index": 4 },
  "softness": 0.1
}
```

## Open questions

- [ ] Bake space: remapping CL SDF Tools yaw (Blender Front Axis) onto VRM head
      azimuth, or a file field for bake convention
- [ ] Whether SDF fully replaces N·L or only remaps it before shift/toony
- [ ] `softness` filter (smoothstep width vs mip)
- [ ] Extra fields: tint, second UV, blend-with-NdotL, `flipTexture`, blend degrees
- [ ] `flipLuminance` default vs typical CL Invert-on bakes

## Related

- [VRMXT Conformance](../../core/vrmxt-conformance.md)
- [VRMXT_materials_mtoonxt](vrmxt-materials-mtoonxt/README.md)
- [VRMXT_materials_stencil](vrmxt-materials-stencil.md)
- [VRMXT_materials_directional_dissolve](vrmxt-materials-directional-dissolve.md)
- [VRMC_materials_mtoon 1.0](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_materials_mtoon-1.0/README.md)
- [Architecture Naming](../../../architecture.md#naming)
