---
title: VRMC_materials_mtoonxt stencil
aliases:
  - MToonXT stencil
  - stencil clip
  - coverage clip
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

Coverage clip extras on [VRMC_materials_mtoonxt](README.md). Serialized names stay
`stencil` (body / forward) and `outlineStencil` (inverse-hull outline pass, when the
shader has one). The identifier matches existing VTuber / Unity search. The extra
describes coverage clip.

Stock importers ignore the extra. Supporting consumers MUST produce the coverage
relationship below. How they do it is local (GPU stencil, engine `stencil_mode`,
material stencil state, or another method that keeps the same pixels).

## Intention

A **writer** is a coverage source. A **reader** is clipped against listed writers.

| `op` | Intention |
|------|-----------|
| `write` | This material stamps coverage (Y). |
| `inside` | Draw this material (X) only where a listed writer covered the pixel. |
| `outside` | Draw this material (X) except where a listed writer covered the pixel. |
| `same` | Outline only: use the body's clip relationship on the hull. |

Coverage is **screen coverage after pose and skinning**, in the pass that draws the
material (body vs outline). It is binary: cutout and soft alpha still stamp. Union of
several listed writers is OR. AND of two different writer sets is out of scope.

Writers MUST be presented before `inside` / `outside` readers that list them, so the
coverage exists when the reader clips. Mesh primitive order MAY be enough. A supporting
implementation SHOULD draw body `write` first when it controls pass order.

On a shared mesh (VRoid Face: iris submesh before sclera), also draw `inside` before
other cutout on that mesh so eyelids can cover iris-card pixels outside the stamp.

Do not treat these as matching the intention:

- deleting or Boolean-cutting triangles in object space
- always drawing X on top of Y (overdraw / depth-read-only receiver)
- a shade, rim, or alpha **texture** named mask

Unity render-queue integers are not a stencil field. See
[renderQueueOffset](../../../../references/research/mtoonxt-render-queue.md)
(non-normative).

## Scope

| Item | Value |
|------|-------|
| Extra names | `stencil`, `outlineStencil` |
| Parent | `materials[i].extensions.VRMC_materials_mtoonxt` |
| Meaning | coverage clip (`write` / `inside` / `outside`) |

`stencil` applies to the body / forward pass. `outlineStencil` applies to the outline
pass when the MToonXT shader has one. Depth-only, shadow, and similar utility passes
have no coverage clip unless a consumer profile says otherwise.

Files MUST NOT serialize GPU stencil state on these objects: `enabled`, `ref`,
`readMask`, `writeMask`, `comp`, `pass`, `fail`, `zfail`.

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

Clip this material to the union (OR) of listed writers. `materials` MUST be a
non-empty array of in-range indices. Each listed material MUST have body `stencil.op`
`write`. A self-index is unresolvable (rule 11).

### `same` (outline only)

`outlineStencil.op` `same` uses the body's clip relationship on the outline hull
(same writers, same inside / outside / write). `materials` MUST be absent. `op` `same`
on body `stencil` is unresolvable.

### Omit

Missing `outlineStencil` means the outline pass has no coverage clip. The consumer
MUST NOT copy body clip onto the outline hull.

Outline width `none` means the outline pass does not draw; `outlineStencil` then has
no visible effect. Do not set outline `write` on a sclera writer: the hull would grow
the coverage region.

### Unresolvable objects

Skip that extra object only (hub rule 11):

- missing or unrecognized `op`
- two `inside`/`outside` lists share a writer index but the sorted lists are not equal
- listed writer without body `op` `write`
- out-of-range index
- `write` with `materials`
- `inside`/`outside` without `materials`
- `same` on body `stencil`

## Examples

Non-normative. Same ops as `mirabunny2026_2.stencil_2.vrm` (White `3`, Iris `1`,
Brow `4`, Hair `16`).

- Iris `inside` White: draw iris only on sclera coverage.
- Hair-Highlight `outside` Brow: skip highlight on brow coverage.
- White and Brow `write`: coverage sources. Brow outline `write` stamps in the outline
  pass. Iris and Hair-Highlight `outlineStencil` `same` follow the body clip.

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
          "stencil": { "op": "write" }
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

## GPU stencil consumer (non-normative)

Typical mapping when the engine exposes an 8-bit stencil on the toon color pass.
File-local. Unique sorted writer-index sets (from `inside`/`outside` lists, plus
singleton `{i}` for a `write` material that no reader lists) receive `Ref` 1, 2, … .

| `op` | compare | stencil op | enabled |
|------|---------|------------|---------|
| `write` | always | replace | true |
| `inside` | equal | keep | true |
| `outside` | notEqual | keep | true |
| omit / off | always | keep | false |

`readMask` / `writeMask` 255. `fail` / `zfail` `keep`.

Unity Comp 0 is Disabled and hides the mesh. After this mapping, write Always (8)
when clip is off.

Unity pass notes: BIRP ForwardAdd uses body clip; ShadowCaster has none. URP
UniversalForward uses body clip; DepthOnly / DepthNormals / ShadowCaster have none.
See [MToon10 stencil shader fork](../../../../references/research/mtoon10-stencil-shader-fork.md).

## Related

- [VRMC_materials_mtoonxt](README.md)
- [MToonXT renderQueueOffset](../../../../references/research/mtoonxt-render-queue.md) (non-normative)
- [MToonXT zWrite](../../../../references/research/mtoonxt-zwrite.md) (non-normative)
- [MToon10 stencil shader fork](../../../../references/research/mtoon10-stencil-shader-fork.md)
