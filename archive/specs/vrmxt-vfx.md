---
title: VRMXT_vfx
aliases:
  - VRM VFX
  - VRM particles
tags:
  - extended-vrm
  - spec/vfx
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: superseded
---

# VRMXT_vfx

> Archived experimental draft. Superseded by
> [VRMXT_sprite_particle](../../specs/extensions/vfx/vrmxt-sprite-particle.md). See
> [VFX capability boundaries](../../decisions/vfx-capability-boundaries.md) for the decision.

Root glTF extension for portable avatar VFX. Version `1.0` defines particle
emitters only. Each emitter attaches to one glTF node (any bone or helper).

Stock VRM 1.0 importers that ignore the extension MUST load the model without
VFX. Supporting consumers map the portable fields to their native particle system.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_vfx` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_vfx` |
| v1 effect kinds | `particle` only |
| Stock importer | no required change |
| Consumer package | optional |

## Normative requirements

1. Files that use this extension MUST list `VRMXT_vfx` in `extensionsUsed`.
2. The extension object MUST appear at root `extensions.VRMXT_vfx`.
3. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
4. The extension object MUST contain an `emitters` array. The array MAY be empty.
5. Each emitter MUST contain `type` and `node`.
6. `node` MUST be a valid zero-based index into the glTF `nodes` array.
7. If `node` is missing or out of range, the consumer MUST skip that emitter.
8. Unknown `type` values MUST be ignored.
9. For `type` equal to `"particle"`, the emitter MUST contain a `particle` object.
10. Particle emission is a continuous point source at the emitter transform. Emission
    shapes, gravity, trails, sub-emitters, and collision are out of scope for `1.0`.
11. Particles MUST be treated as camera-facing billboards when the consumer supports
    billboards.
12. Initial particle velocity direction MUST follow the emitter local +Y axis after
    `localPosition` and `localRotation` are applied (see
    [Emitter transform](#emitter-transform)). Magnitude is `startSpeed` in meters
    per second.
13. Consumers MUST ignore unknown properties.
14. Files using this optional design MUST NOT list `VRMXT_vfx` in `extensionsRequired`.
15. Engine-specific override entries are **TBD** and MUST NOT be treated as stable.

## Extension properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | Extension version; currently `"1.0"` |
| `emitters` | object[] | yes | Emitter list; may be empty |
| `emitters[].name` | string | no | Authoring label |
| `emitters[].type` | string | yes | Effect kind; v1 defines `"particle"` |
| `emitters[].node` | integer | yes | Attach node index |
| `emitters[].localPosition` | number[3] | no | Offset in node local space, meters; default `[0,0,0]` |
| `emitters[].localRotation` | number[4] | no | Orientation in node local space as quaternion **xyzw**; default identity `[0,0,0,1]` |
| `emitters[].particle` | object | yes if `type` is `"particle"` | Portable particle parameters |

### Emitter transform

All vectors and quaternions below are in the same right-handed Y-up space as glTF
node transforms.

1. When `localPosition` is omitted, use `[0,0,0]`.
2. When `localRotation` is omitted, use identity `[0,0,0,1]` (x, y, z, w).
3. `localRotation` MUST be four finite numbers in **xyzw** order, matching glTF
   `nodes[].rotation`.
4. Build the emitter local matrix as translation by `localPosition` composed with
   rotation by `localRotation`:

   `emitterLocal = T(localPosition) * R(localRotation)`

   Column-vector convention: apply rotation first, then translation, in node local
   space.
5. Emitter world matrix:

   `emitterWorld = nodeWorld * emitterLocal`

   where `nodeWorld` is the evaluated world matrix of `nodes[node]`.
6. Emission origin is the translation of `emitterWorld`.
7. Initial velocity direction is the unit +Y axis of the emitter local frame,
   transformed by `emitterWorld` (equivalently: the world-space direction of
   `emitterLocal`'s +Y axis under `nodeWorld`). Magnitude is `startSpeed`.
8. When both locals are defaults, emission origin equals the node origin and
   velocity follows the node local +Y axis.

Invalid `localPosition` or `localRotation` (wrong length, non-finite components, or
a zero-length quaternion) MUST cause the consumer to skip that emitter.
Normalization of near-unit quaternions is **TBD**.

## Particle properties

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `texture` | integer | no | none | Index into glTF `textures[]` |
| `emissionRate` | number | no | `10` | Particles spawned per second |
| `maxParticles` | integer | no | `64` | Active particle cap |
| `lifetime` | number | no | `1` | Particle lifetime in seconds |
| `startSize` | number | no | `0.05` | Billboard size in meters |
| `startSpeed` | number | no | `0.1` | Initial speed along emitter local +Y, m/s |
| `startColor` | number[4] | no | `[1,1,1,1]` | Linear RGBA |

When `texture` is omitted or unresolved, the consumer MAY use a solid quad tinted by
`startColor`.

`emissionRate`, `lifetime`, `startSize`, and `startSpeed` MUST be finite and
non-negative. `maxParticles` MUST be an integer greater than or equal to `1`. Invalid
values MUST cause the emitter to be skipped.

## Attachment example

Non-normative.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMXT_vfx"
  ],
  "extensions": {
    "VRMXT_vfx": {
      "specVersion": "1.0",
      "emitters": [
        {
          "name": "HandSpark",
          "type": "particle",
          "node": 42,
          "localPosition": [0.0, 0.05, 0.0],
          "localRotation": [0.0, 0.0, 0.0, 1.0],
          "particle": {
            "texture": 3,
            "emissionRate": 20.0,
            "maxParticles": 64,
            "lifetime": 0.8,
            "startSize": 0.04,
            "startSpeed": 0.2,
            "startColor": [1.0, 0.85, 0.4, 1.0]
          }
        }
      ]
    }
  }
}
```

## Compatibility

| Consumer | Expected behavior |
|----------|-------------------|
| Stock VRM 1.0 importer | Ignore extension; avatar loads without VFX |
| Supporting UniVRM / Godot / three-vrm / VRM4U / Blender package | Build native particles from portable fields |
| Unknown `type` or bad `node` | Skip that emitter only |

Exact visual parity across engines is not required. Field meaning and units are.

The glTF Extension Registry has no particle-emitter `KHR_` / `EXT_` extension.
`EXT_mesh_gpu_instancing` covers static instance batches, not live emitters. Research:
[KHR / glTF overlap](../../references/khr-gltf-overlap.md).

## Extensibility

Later drafts MAY:

- Add emitter `type` values other than `"particle"`.
- Add optional particle fields with defaults (shapes, gravity).
- Add per-emitter engine `overrides[]` in the same style as
  [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md) and
  [VRMXT_springBone_override](../../specs/extensions/physics/vrmxt-spring-bone-override.md).

Adding optional fields with defaults does not by itself require a `specVersion` bump.
Removing or redefining an existing field does.

## Related

- [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md)
- [VRMXT_springBone_override](../../specs/extensions/physics/vrmxt-spring-bone-override.md)
- [VRMXT_lattice](../../specs/extensions/deformation/vrmxt-lattice.md) (research draft)
- [KHR / glTF overlap](../../references/khr-gltf-overlap.md) (non-normative)
- [Blender VFX](../../implementations/blender-vfx.md)
- [UniVRM VFX](../../implementations/univrm-vfx.md)
- [Godot VFX](../../implementations/godot-vfx.md)
- [three-vrm VFX](../../implementations/three-vrm-vfx.md)

## Open questions

| Topic | Status |
|-------|--------|
| Expression / state triggers (`playOn`) | TBD |
| Color / size over lifetime curves | TBD |
| Blend mode / render queue | TBD |
| Engine override profile schema | TBD |
| Whether `name` must be unique | TBD |
| Near-unit quaternion normalization | TBD |
