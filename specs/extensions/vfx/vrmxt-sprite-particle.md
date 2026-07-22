---
title: VRMXT_sprite_particle
aliases:
  - VRM particles
  - Extended VRM particle systems
tags:
  - extended-vrm
  - spec/vfx
  - spec/particle
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_sprite_particle

Root glTF extension for portable point-source particle systems attached to a VRM 1.0
avatar. Particles render as camera-facing rectangular sprites. The consumer owns
runtime sprite geometry.

Stock VRM 1.0 importers that ignore the extension MUST load the model without particles.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_sprite_particle` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_sprite_particle` |
| Entries | `emitters[]` |
| Attach point | glTF `nodes[]` index |
| Emission shape | point |
| Renderer | camera-facing rectangular sprite (consumer-owned geometry) |
| Stock importer | no required change |
| Consumer package | optional |

## Conformance

This specification conforms to [VRMXT Conformance](../../core/vrmxt-conformance.md).

Ownership and naming decisions:

- [Billboard sprite ownership](../../../decisions/billboard-sprite-ownership.md)
- [VFX capability naming](../../../decisions/vfx-capability-naming.md)

## Normative requirements

1. Files that use this extension MUST list `VRMXT_sprite_particle` in `extensionsUsed`.
2. The extension object MUST appear at root `extensions.VRMXT_sprite_particle`.
3. The extension object MUST contain `specVersion` with value `"1.0"`.
4. The extension object MUST contain an `emitters` array. The array MAY be empty.
5. Each emitter MUST contain `node`.
6. `node` MUST be a valid zero-based index into the glTF `nodes` array. If `node` is
   missing or out of range, the consumer MUST skip that emitter.
7. Emission origin is the translation of the evaluated world matrix of `nodes[node]`.
8. Each emitter is a continuous point source at that origin.
9. Initial particle velocity direction MUST follow the emitter node's local +Y axis,
   transformed by the linear part of that node's world matrix and then normalized.
   Magnitude is `startSpeed` in meters per second.
10. Each spawned particle MUST render as a camera-facing rectangular sprite. The
    consumer MUST create or select the runtime geometry required by its particle
    system or equivalent renderer. The sprite MUST NOT require a glTF `meshes[]`
    entry. Exporters MUST NOT serialize preview or runtime sprite geometry as avatar
    meshes solely to satisfy this extension.
11. Sprite right and up axes MUST align with the active camera's right and up axes
    (camera-plane facing). Exact pixel parity across rasterizers is not required.
12. `texture`, when present, MUST be a valid zero-based index into glTF `textures[]`.
13. `size` MUST contain two finite numbers greater than `0` when present. Dimensions
    are world-space meters and MUST NOT inherit scale from the emitter's referenced
    glTF node.
14. `color` MUST contain four finite numbers when present. RGB components MUST be
    greater than or equal to `0`; alpha MUST be in the inclusive range `[0,1]`. Color
    is linear RGBA. The consumer MUST multiply sampled texture RGBA by `color`.
15. When `texture` is omitted, the consumer MUST render a solid white quad multiplied
    by `color`. If a valid referenced texture cannot be loaded at runtime, it MUST use
    the same fallback.
16. The consumer MUST skip only the invalid emitter when its node or particle
    properties are invalid.

Offsets relative to a bone or mesh use ordinary glTF hierarchy: add a helper node under
the parent, set that node's `translation` / `rotation` / `scale`, and point `node` at
the helper. This extension does not define local offset fields.

Emission shapes, gravity, trails, ribbons, sub-emitters, collision, and mesh particles
are outside this draft. Those capabilities use separate extensions when standardized.

## Extension properties

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `specVersion` | string | yes | — | Extension version; `"1.0"` |
| `emitters` | object[] | yes | — | Particle emitter list; may be empty |
| `emitters[].name` | string | no | none | Authoring label |
| `emitters[].node` | integer | yes | — | Index into glTF `nodes[]` |
| `emitters[].texture` | integer | no | none | Index into glTF `textures[]` |
| `emitters[].size` | number[2] | no | `[0.05,0.05]` | Sprite width and height in meters |
| `emitters[].color` | number[4] | no | `[1,1,1,1]` | Linear RGBA multiplier |
| `emitters[].emissionRate` | number | no | `10` | Particles spawned per second |
| `emitters[].maxParticles` | integer | no | `64` | Active particle cap |
| `emitters[].lifetime` | number | no | `1` | Particle lifetime in seconds |
| `emitters[].startSpeed` | number | no | `0.1` | Initial speed along node local +Y, m/s |

`emissionRate`, `lifetime`, and `startSpeed` MUST be finite and non-negative.
`maxParticles` MUST be an integer greater than or equal to `1`. An out-of-range
`texture` index or other invalid property makes the emitter invalid.

## Attachment example

Non-normative. Node `42` is a helper child of a hand bone; its glTF `translation` /
`rotation` supply the offset.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMXT_sprite_particle"
  ],
  "nodes": [
    {
      "name": "RightHand",
      "children": [42]
    },
    {
      "name": "HandSparkAnchor",
      "translation": [0.0, 0.05, 0.0]
    }
  ],
  "extensions": {
    "VRMXT_sprite_particle": {
      "specVersion": "1.0",
      "emitters": [
        {
          "name": "HandSpark",
          "node": 42,
          "texture": 3,
          "size": [0.04, 0.04],
          "color": [1.0, 0.85, 0.4, 1.0],
          "emissionRate": 20.0,
          "maxParticles": 64,
          "lifetime": 0.8,
          "startSpeed": 0.2
        }
      ]
    }
  }
}
```

## Compatibility

| Consumer | Expected behavior |
|----------|-------------------|
| Stock VRM 1.0 importer | Ignore extension; avatar loads without particles |
| Supporting consumer | Build a native point-source sprite particle system for each valid emitter |
| Invalid emitter | Skip that emitter only |

Exact visual parity across engines is not required. Emission rate, lifetime, active cap,
initial velocity, node transform, sprite size, texture selection, and linear color
meaning are portable. Runtime geometry may use Unity `ParticleSystem` billboard mode,
Niagara Sprite Renderer, Godot draw-pass `QuadMesh`, Three.js `Sprite` or instanced
quads, or an equivalent renderer.

The glTF Extension Registry has no particle-emitter `KHR_` or `EXT_` extension.
Research: [KHR / glTF overlap](../../../references/khr-gltf-overlap.md).
Native backends and Unity / VRM4U constraints:
[Engine particle capability](../../../references/engine-particle-capability.md).

## Extensibility

Later drafts MAY add particle-specific fields such as emission shapes, gravity, or
color and size over lifetime. A different simulation or rendering capability uses a
separate `VRMXT_*` extension.

Adding optional fields with defaults does not by itself require a `specVersion` bump.
Removing or redefining an existing field does.

## Open questions

| Topic | Status |
|-------|--------|
| Emission burst schedules | TBD |
| Color / size over lifetime curves | TBD |
| Initial velocity spread | TBD |
| Particle simulation space | TBD |
| Whether `name` must be unique | TBD |
| Singular / zero-scale node world transform | TBD |
| Blend / depth / order / sidedness / UV / alpha cutoff | TBD |

## Related

- [VRMXT Conformance](../../core/vrmxt-conformance.md)
- [Billboard sprite ownership](../../../decisions/billboard-sprite-ownership.md)
- [VFX capability naming](../../../decisions/vfx-capability-naming.md)
- [VFX capability boundaries](../../../decisions/vfx-capability-boundaries.md)
- [VRMXT_lattice](../deformation/vrmxt-lattice.md)
- [KHR / glTF overlap](../../../references/khr-gltf-overlap.md)
- [Engine particle capability](../../../references/engine-particle-capability.md)
