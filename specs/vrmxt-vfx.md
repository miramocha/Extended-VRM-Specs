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
status: draft
---

# VRMXT_vfx

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
12. Initial particle velocity direction MUST follow the emitter node's local +Y axis
    after `localPosition` is applied. Magnitude is `startSpeed` in meters per second.
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
| `emitters[].particle` | object | yes if `type` is `"particle"` | Portable particle parameters |

Emitter world transform = node world transform with `localPosition` applied in node
local space. Local rotation is identity for `1.0`.

## Particle properties

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `texture` | integer | no | none | Index into glTF `textures[]` |
| `emissionRate` | number | no | `10` | Particles spawned per second |
| `maxParticles` | integer | no | `64` | Active particle cap |
| `lifetime` | number | no | `1` | Particle lifetime in seconds |
| `startSize` | number | no | `0.05` | Billboard size in meters |
| `startSpeed` | number | no | `0.1` | Initial speed along local +Y, m/s |
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
| Supporting UniVRM / VRM4U / Blender package | Build native particles from portable fields |
| Unknown `type` or bad `node` | Skip that emitter only |

Exact visual parity across engines is not required. Field meaning and units are.

## Extensibility

Later drafts MAY:

- Add emitter `type` values other than `"particle"`.
- Add optional particle fields with defaults (shapes, gravity, local rotation).
- Add per-emitter engine `overrides[]` in the same style as
  [[VRMXT_materials_override]] and [[VRMXT_springBone_override]].

Adding optional fields with defaults does not by itself require a `specVersion` bump.
Removing or redefining an existing field does.

## Open questions

| Topic | Status |
|-------|--------|
| Expression / state triggers (`playOn`) | TBD |
| Color / size over lifetime curves | TBD |
| Blend mode / render queue | TBD |
| Engine override profile schema | TBD |
| Whether `name` must be unique | TBD |
