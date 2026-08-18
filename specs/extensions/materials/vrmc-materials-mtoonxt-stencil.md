---
title: VRMC_materials_mtoonxt stencil
aliases:
  - MToonXT stencil
  - stencil clip
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMC_materials_mtoonxt stencil

Body / forward (`stencil`) and inverse-hull outline (`outlineStencil`) extras on
[VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md).

Authors describe **write** vs **clip inside / outside** using glTF `materials[]`
indices. Consumers compile that to GPU stencil `Ref` / compare / op. Files MUST NOT
serialize `enabled`, `ref`, `readMask`, `writeMask`, `comp`, `pass`, `fail`, or `zfail`
on these objects.

## Scope

| Item | Value |
|------|-------|
| Extra names | `stencil`, `outlineStencil` |
| Parent | `materials[i].extensions.VRMC_materials_mtoonxt` |
| GPU buffer | one 8-bit stencil; one `Ref` per distinct writer-index set |

`stencil` applies to the body / forward pass. `outlineStencil` applies to the outline
pass when the MToonXT shader has one. ShadowCaster, URP DepthOnly / DepthNormals have
no stencil (BIRP ForwardAdd uses body stencil).

## `op` schema

`op` is required when the object is present.

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `op` | string | yes | `write`, `inside`, `outside`; outline only: `same` |
| `materials` | integer array | for `inside` / `outside` | zero-based `materials[]` indices to clip against |

### `write`

Stamps coverage. `materials` MUST be absent. The material MUST have this extension so
rule 7 can swap to MToonXT.

### `inside` / `outside`

Clip this material to the **union** (OR) of listed writers. `materials` MUST be a
non-empty array of in-range indices. Each listed material MUST have body `stencil.op`
`write`. A self-index is unresolvable (rule 11).

`inside` draws only where a listed writer covered the pixel. `outside` skips those
pixels.

True AND of two different writer sets is out of scope.

### `same` (outline only)

`outlineStencil.op` `same` copies the **compiled** body stencil (Ref, compare, pass)
into the outline pass. `materials` MUST be absent. `op` `same` on body `stencil` is
unresolvable.

### Omit

Missing `outlineStencil` is outline stencil-off (Always / Keep, not enabled). The
consumer MUST NOT copy body stencil onto the outline pass.

Outline width `none` means the outline pass does not draw; `outlineStencil` then has
no visible effect. Do not set outline `write` on a sclera writer: the hull would grow
the clip mask.

## Compile (consumers)

File-local. Unique sorted writer-index sets (from `inside`/`outside` lists, plus
singleton `{i}` for a `write` material that no reader lists) receive `Ref` 1, 2, … .

| `op` | compare | stencil op | enabled |
|------|---------|------------|---------|
| `write` | always | replace | true |
| `inside` | equal | keep | true |
| `outside` | notEqual | keep | true |
| omit / off | always | keep | false |

`readMask` / `writeMask` 255. `fail` / `zfail` `keep`.

If two `inside`/`outside` lists share a writer index and the sorted lists are not
equal, those stencil objects are unresolvable (rule 11). A listed writer without
`op` `write`, an out-of-range index, `write` with `materials`, `inside`/`outside`
without `materials`, or `same` on body: skip that object only.

Writers MUST draw before `inside` / `outside` readers that list them. Mesh primitive
order MAY be enough. A supporting implementation SHOULD draw body `write` before
those readers when it controls pass order. Stencil is binary: soft alpha still
writes.

[`renderQueueOffset`](vrmc-materials-mtoonxt-render-queue.md) is a separate extra.
It is not a stencil field. Hosts that sort with a queue MAY use it when primitive
order is wrong.

An object without `op`, or with unrecognized `op`, is unresolvable (hub rule 11).
Unity Comp 0 is Disabled and hides the mesh; after compile, consumers MUST write
Always (8) when stencil is off.

## Examples

Non-normative. Same ops as `mirabunny2026_2.stencil_2.vrm` (White `3`, Iris `1`,
Brow `4`, Hair `16`). Queue / `zWrite` extras on that file are not stencil fields.

```json
{
  "materials": [
    {
      "name": "Iris_Eye-NoRim.NoOutline.MatcapTexture",
      "extensions": {
        "VRMC_materials_mtoonxt": {
          "specVersion": "1.0",
          "stencil": { "op": "inside", "materials": [3] },
          "outlineStencil": { "op": "same" }
        }
      }
    },
    {
      "name": "White-NoRim.NoOutline",
      "extensions": {
        "VRMC_materials_mtoonxt": {
          "specVersion": "1.0",
          "stencil": { "op": "write" },
          "outlineStencil": { "op": "write" }
        }
      }
    },
    {
      "name": "Brow_Face-NoRim",
      "extensions": {
        "VRMC_materials_mtoonxt": {
          "specVersion": "1.0",
          "stencil": { "op": "write" },
          "outlineStencil": { "op": "write" }
        }
      }
    },
    {
      "name": "Hair-Highlight",
      "extensions": {
        "VRMC_materials_mtoonxt": {
          "specVersion": "1.0",
          "stencil": { "op": "outside", "materials": [4] },
          "outlineStencil": { "op": "same" }
        }
      }
    }
  ]
}
```

Union (OR) of two sclera writers: Iris `"materials": [3, 7]` and both listed
materials `"op": "write"`.

## Unity authoring

glTF stores indices. The material ShaderGUI MUST NOT persist a material list (shader
properties cannot). UniVRMXT: `VrmcMaterialsMtoonxtInstance` editor uses `Material`
object fields; export writes indices. Warudo uses JSON only.

## Related

- [VRMC_materials_mtoonxt](vrmc-materials-mtoonxt.md)
- [Render queue](vrmc-materials-mtoonxt-render-queue.md)
- [ZWrite](vrmc-materials-mtoonxt-zwrite.md)
- [MToon10 stencil shader fork](../../../references/research/mtoon10-stencil-shader-fork.md)
