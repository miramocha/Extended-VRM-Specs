---
title: VRMXT Package Payload
aliases:
  - VRMXTPKG payload
  - vrm1 payloadKind
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
  - compatibility/vrm1
type: specification
status: draft
---

# VRMXT Package Payload

Typed descriptors for `payloadKind` `"vrm1"`. Conforms to
[VRMXT Package Format](README.md).

The compiler MAY read a source `.vrm`. The packaged form MUST describe the same runtime
semantics without storing a reconstructible glTF JSON + BIN pairing.

## Required kinds

A `vrm1` package MUST include chunks (or an equivalent combined chunk) covering:

| Kind | Role |
|------|------|
| `graph` | Nodes, parent indices, local TRS, mesh/skin/morph bindings |
| `mesh` | Attributes, indices, primitives |
| `material` | MToon / PBR / unlit parameters and texture ids |
| `humanoid` | VRM 1.0 human bone map (node ids, not glTF names as the only key) |
| `expression` | Preset and custom expressions, morph and material binds |
| `meta` | Display meta the runtime is allowed to show |

Recommended: `skin`, `morph`, `image`, `lookAt`, `firstPerson`, `springBone`,
`nodeConstraint`. Omit only when the source asset has no corresponding data.

`vrmxt` holds portable `VRMXT_*` capability objects keyed by original attachment
(material index, root, node). Values MUST be the extension JSON as in the source glTF,
not engine types. A consumer that does not implement a capability MUST ignore that
object. Packed `VRMXT_*` data MUST still obey
[VRMXT Conformance](../../core/vrmxt-conformance.md) skip/fallback rules.

## Identifier rules

- Payload ids are package-local strings or integers. They MUST NOT be required to equal
  source glTF `nodes[].name`.
- Humanoid bones MUST use VRM 1.0 human bone names (`hips`, `head`, …) as map keys.
- Expression preset names MUST use VRM 1.0 presets (`blink`, `aa`, `oh`, …) when the
  source used presets.
- Non-semantic mesh/material/node labels MAY be renamed. Bindings MUST be rewritten to
  the new ids.

## Graph

`graph` JSON (codec `identity` or `zstd`):

| Property | Type | Required |
|----------|------|----------|
| `nodes` | object[] | yes |
| `nodes[].id` | string | yes |
| `nodes[].parent` | string or null | yes |
| `nodes[].translation` | number[3] | yes |
| `nodes[].rotation` | number[4] | yes (xyzw) |
| `nodes[].scale` | number[3] | yes |
| `nodes[].mesh` | string | no |
| `nodes[].skin` | string | no |
| `root` | string | yes |

Units and axes: glTF / VRM 1.0.

## Mesh and morph

`mesh` references attribute buffers by chunk id + byte range. Attributes MUST include
enough data to skin and shade (POSITION, and when present NORMAL, TANGENT, TEXCOORD_n,
JOINTS_n, WEIGHTS_n).

Morph targets are a `morph` kind or sub-ranges of `mesh`. Expression morph binds MUST
use package mesh primitive ids + morph index, not Three.js mesh names.

`codec` `meshopt` buffer layout MUST be documented in the chunk as:

| Property | Type | Meaning |
|----------|------|---------|
| `filter` | string | meshoptimizer filter name |
| `count` | integer | vertex or index count |
| `byteStride` | integer | |

A Runtime profile that applies shader swizzle (see [Runtime](runtime.md)) still stores
authoring-space attributes in the **plaintext** chunk. Swizzle is a consumer step, not a
second on-disk codec in this draft.

## Images and materials

`image` chunks are KTX2 (`codec` `ktx2`) or PNG/JPEG (`identity`) after decrypt.
Materials reference `image` ids. `VRMC_materials_mtoon` fields MUST be preserved as
named properties (same names as the VRM 1.0 spec). Sibling `VRMXT_materials_mtoonxt` and
`VRMXT_materials_override` live under `vrmxt` keyed by material id.

## Humanoid, look-at, first person, spring, constraints

JSON objects equivalent to VRM 1.0 extension bodies, with node **package ids** instead
of glTF node indices.

Spring collider and joint node ids MUST resolve in `graph`.

## Expressions

Each expression:

| Property | Type | Required |
|----------|------|----------|
| `name` | string | yes |
| `preset` | string or null | yes |
| `isBinary` | boolean | no |
| `morphBinds` | object[] | no |
| `materialColorBinds` | object[] | no |
| `textureTransformBinds` | object[] | no |
| `overrideBlink` | string | no |
| `overrideLookAt` | string | no |
| `overrideMouth` | string | no |

`morphBinds[].node` / `mesh` / `index` / `weight` MUST be package ids and morph indices.

A Three.js consumer MUST be able to implement `setValue(name, weight)` for every
packaged expression, including presets `blink`, `aa`, and `oh` when present in the
source.

## Meta

MUST include enough fields for UI (name, version, authors, allowed user / commercial /
license URLs as in `VRMC_vrm.meta`) unless the distributor strips them at compile time.
Stripping MUST be an explicit compiler flag. Default is preserve.

## Parity

A compiler MUST reject output when golden checks fail: humanoid bone count and names,
expression names, morph bind counts, material count, spring joint/collider counts,
bounds within a documented epsilon.

## Out of scope (v1)

- `.vrma` / `VRMC_vrm_animation`
- VRM 0.0 as input unless converted to 1.0 first
- Reconstructing source glTF JSON for round-trip identity

## Open questions

- [ ] Combined vs split mesh/morph chunks
- [ ] Whether `vrmxt` is one JSON blob or per-capability chunks
- [ ] Quantization (`KHR_mesh_quantization`) as a first-class codec vs meshopt only

## Related

- VRM 1.0 `VRMC_vrm`, `VRMC_materials_mtoon`, `VRMC_springBone`, `VRMC_node_constraint`
- [Runtime](runtime.md)
- [Container](container.md)
