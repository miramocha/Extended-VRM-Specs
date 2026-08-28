---
title: VRMXT_lattice
aliases:
  - VRM lattice
  - lattice deform
  - FFD cage
tags:
  - extended-vrm
  - spec/lattice
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_lattice

Root glTF extension for a portable free-form deformation (FFD) cage on a VRM 1.0
avatar. The cage is a regular 3D grid of handles. Each binding samples that grid
and displaces mesh vertices **after** morph targets and joint skinning.

Stock VRM 1.0 importers that ignore the extension MUST load the model with no
runtime cage.

This specification conforms to [VRMXT Conformance](../../core/vrmxt-conformance.md).
Lattice is a mesh-deformation capability. It is not a particle or billboard effect
([VFX capability boundaries](../../../decisions/vfx-capability-boundaries.md)).

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_lattice` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_lattice` |
| Entries | `lattices[]`, `bindings[]` |
| Apply stage (v1) | After morph targets and skinning |
| Stock importer | no required change |
| Consumer package | optional |

Out of v1:

- Apply stage before skinning (bind-pose FFD)
- Per-handle animation channels
- Surface-only cages (ignore interior handles)
- Transform-only deform (lights, empties)
- Engine override tables
- Bit-identical vertices across implementations

## Why after-skin only

Pre-skin FFD rewrites rest positions, then the engine skins those verts. GPU
skinning, vertex-shader LBS, and packed skin buffers usually expose the **posed**
result. Injecting a second deform *before* joints means a custom skin path or a
CPU rest-pose rewrite every time the cage moves.

After-skin FFD takes world (or equivalent) positions that already include morphs
and joints, maps them into the cage node, and adds the interpolated handle
offset. That insert exists on every engine that can skin a VRM: compute on the
skinned buffer, extra instructions at the end of the skinning vertex shader, or
a deformer node after the skeleton.

Bind-pose volume edits (reshape T-pose, then animate) stay as morphs or baked
rest mesh. The cage is for posed-space squash and stretch.

## Normative requirements

1. Files that use this extension MUST list `VRMXT_lattice` in `extensionsUsed`.
2. The extension object MUST appear at root `extensions.VRMXT_lattice`.
3. The extension object MUST contain `specVersion` with value `"1.0"`.
4. The extension object MUST contain `lattices` and `bindings` arrays. Either
   array MAY be empty.
5. Files MUST NOT list `VRMXT_lattice` in `extensionsRequired`.
6. Each lattice MUST contain `node` and `resolution`.
7. `node` MUST be a valid zero-based index into glTF `nodes[]`. If `node` is
   missing or out of range, the consumer MUST skip that lattice and every
   binding that references it.
8. `resolution` MUST be three integers, each greater than or equal to `2`.
   Order is U, V, W in lattice local +X, +Y, +Z.
9. Rest volume of a lattice is the unit cube `[0, 1]³` in the local space of
   `nodes[node]`. The node's evaluated world matrix places, orients, and scales
   that cube. Exporters that need an offset or non-uniform fit MUST encode it
   on that node (or a helper child), not as extra translation fields on the
   lattice object.
10. Handle count MUST equal `resolution[0] * resolution[1] * resolution[2]`.
    Index `i = u + v * resU + w * resU * resV` with `u` in `[0, resU)`, same
    for `v`, `w`. Rest position of handle `(u,v,w)` is
    `(u/(resU-1), v/(resV-1), w/(resW-1))` in lattice local.
11. `handleOffsets`, when present, MUST contain one `number[3]` per handle,
    lattice-local meters relative to that rest position. Missing
    `handleOffsets` means all offsets are `(0,0,0)`. A length mismatch makes
    the lattice invalid; skip it and its bindings.
12. Each binding MUST contain `lattice` and `mesh`, zero-based indices into
    `lattices[]` and glTF `meshes[]`. Out of range → skip that binding only.
13. A binding deforms every primitive of `meshes[mesh]` unless a future field
    narrows the set. v1 has no primitive filter.
14. Apply stage is after morph targets and joint skinning. v1 has no
    `skinPhase` field. Consumers MUST NOT apply this extension's cage to
    bind-pose rest positions and then skin.
15. Unskinned meshes use the same formula: morphs first, then cage, using the
    mesh node's world matrix in place of a skin.
16. `interpolation` values are `linear`, `catmullRom`, and `bSpline`. Omitted
    value is `bSpline`. Unknown value → skip that lattice.
17. `strength` defaults to `1`. It MUST be finite. The consumer clamps it to
    `[0, 1]` when applying. Values outside that range are invalid for the
    binding.
18. `weightAttribute`, when present, names a mesh vertex attribute (`COLOR_0`,
    …). The consumer uses the **R** channel in `[0, 1]` as a per-vertex
    multiplier. Missing attribute → treat weights as `1`.
19. Numeric data uses glTF meters and Y-up node space.
20. Smallest skippable unit: one lattice (plus dependent bindings) or one
    binding. Invalid lattice or binding MUST NOT invalidate the glTF or VRM 1.0
    asset.
21. Runtime cage state is instance-scoped per
    [VRMXT Conformance](../../core/vrmxt-conformance.md).

## Evaluation

Non-normative labels in comments. The math is normative.

Let `M` be the world matrix of `nodes[lattice.node]`. For each deformed vertex,
let `p_world` be the position **after** morph targets and skinning (glTF world).

```
p_l = inverse(M) * p_world          // lattice local
s   = resolution - (1,1,1)
t   = p_l * s                       // cell coordinates
```

For each axis independently:

- `linear`: interpolate the two surrounding handles (fractional part of `t`).
  Sample indices clamp to `[0, res-1]`.
- `catmullRom`: cubic Catmull–Rom on four handles, tension `0.5`, same 4-tap
  neighborhood as a uniform cubic (indices `floor(t)-1 … floor(t)+2`, clamped).
- `bSpline`: uniform cubic B-spline basis on that same 4-tap neighborhood
  (does not interpolate handles).

Weights are separable: `W = wU(u) * wV(v) * wW(w)`.

```
offset_l = Σ W_i * handleOffsets[i]
p_l'     = p_l + offset_l
p_world' = lerp(p_world, M * p_l', strength * weight_r)
```

Vertices with lattice-local coordinates outside `[0, 1]³` still use **clamped**
cell indices. Deformation does not extrapolate past the cube faces. Parent the
cage node under a joint (or a helper under a joint) so posed verts stay inside
the cube.

Normals and tangents: the consumer SHOULD update them for lighting. Method is
implementation-defined (finite difference in lattice space, or a full tangent
frame). Position-only is allowed.

## Extension properties

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `specVersion` | string | yes | — | `"1.0"` |
| `lattices` | object[] | yes | — | Cage list; may be empty |
| `lattices[].name` | string | no | none | Authoring label |
| `lattices[].node` | integer | yes | — | Index into `nodes[]`; unit cube `[0,1]³` local |
| `lattices[].resolution` | integer[3] | yes | — | Handle counts U,V,W; each ≥ 2 |
| `lattices[].interpolation` | string | no | `bSpline` | `linear` / `catmullRom` / `bSpline` |
| `lattices[].handleOffsets` | number[3][] | no | zeros | Lattice-local offset per handle, U-fastest |
| `bindings` | object[] | yes | — | Mesh ↔ cage links; may be empty |
| `bindings[].lattice` | integer | yes | — | Index into `lattices[]` |
| `bindings[].mesh` | integer | yes | — | Index into `meshes[]` |
| `bindings[].strength` | number | no | `1` | Blend in `[0, 1]` |
| `bindings[].weightAttribute` | string | no | none | Vertex attribute; R channel |

One lattice MAY be referenced by many bindings. Node TRS MAY be animated with
ordinary glTF animation channels. Per-handle offset animation is out of v1.

## Attachment example

Non-normative. Node `12` is a helper under the head joint. Its TRS fits the
unit cube around the posed face.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMXT_lattice"
  ],
  "extensions": {
    "VRMXT_lattice": {
      "specVersion": "1.0",
      "lattices": [
        {
          "name": "face_cage",
          "node": 12,
          "resolution": [4, 4, 4],
          "interpolation": "bSpline"
        }
      ],
      "bindings": [
        {
          "lattice": 0,
          "mesh": 3,
          "strength": 1.0,
          "weightAttribute": "COLOR_0"
        }
      ]
    }
  }
}
```

Omitted `handleOffsets` means a rest cube. A 4×4×4 cage with edits stores 64 triples.

## After-skin viability (non-normative)

v1 is written so a consumer only needs a post-skin vertex insert. Approximate
difficulty:

| Runtime | After-skin insert | Notes |
|---------|-------------------|-------|
| Unity SkinnedMeshRenderer | High | GPU skinning output buffer or compute after skin. Mesh Read/Write and GPU skinning are importer/project flags, not file data. Blend-shape Animators may need `Rebind()`. |
| Unity MeshRenderer (no skin) | High | CPU or compute on `MeshFilter` verts after morphs. |
| Unreal skeletal mesh / Control Rig deformers (5.5+) | High | Deformers sit on posed mesh. `FFFDLattice` is CPU DynamicMesh; animation deformers are the live path. |
| Godot 4 | Medium | Skinning is typically in the shader. Append FFD after skeleton in a custom shader, or write `ArrayMesh` after `Skeleton3D` (CPU, heavier). |
| three.js / three-vrm | High | Skinning already in the vertex shader. Add the 4×4×4 sample after `skinning_vertex`. CPU `BufferGeometry` after `skeleton.update()` also works. |
| WebGPU | High | Compute pass on skinned positions, or shader after LBS. |
| WebGL without custom skin shader | Medium | Must own the skinning shader (most VRM loaders do). |
| VRM4U | Medium | Wait for a post-deform hook on the skeletal mesh; do not invent a pre-skin UniVRM-style path. |
| Roblox | Low | No general post-skin vertex hook for imported VRM. Bake or ignore. |
| Stock VRM viewers | n/a | Ignore extension. Correct. |

**Parenting the cage node is part of authoring, not an extra apply stage.** A
helper under the head joint keeps the unit cube on the face while bones move.
A cage under the avatar root stays in place; posed verts slide through the
cube and clamp at the faces.

**Collision, cloth, and spring bones** still see the undeformed (skinned)
mesh unless a consumer also feeds `p_world'` into those systems. v1 does not
require that.

**Pre-skin** remains possible later as a new field or `specVersion`. It would
need an explicit rest-space contract and would fail on GPU-only skin paths
that cannot rewrite bind verts.

## Open questions

1. Per-axis interpolation vs one enum for the whole lattice.
2. Named extras vs `COLOR_n` for weights when the mesh has no spare color.
3. Whether glTF animation of `handleOffsets` lands in v2 or never.
4. Default for normals: require an update, or leave position-only legal.

## References

| Source | URL |
|--------|-----|
| Family rules | [vrmxt-conformance.md](../../core/vrmxt-conformance.md) |
| Lattice vs VFX | [vfx-capability-boundaries.md](../../../decisions/vfx-capability-boundaries.md) |
| Root-extension pattern | [vrmxt-sprite-particle.md](../vfx/vrmxt-sprite-particle.md) |
| Cubic FFD neighborhood (historical DCC reference) | Blender `BKE_lattice_deform_data_eval_co` / `key_curve_position_weights` in blender source; formulas for `catmullRom` (`fc = 0.5`) and `bSpline` match that file |

## Related implementation notes

Profiles not started:

- `implementations/univrm-lattice.md`
- `implementations/three-vrmxt-lattice.md`
- `implementations/vrm4u-lattice.md`
