---
title: Billboard sprite ownership
aliases:
  - Billboard Sprite removal
  - particle appearance ownership
tags:
  - extended-vrm
  - decision/vfx
  - format/gltf-extension
  - compatibility/vrm1
type: decision
status: accepted
---

# Billboard sprite ownership

## Status

Accepted for the current experimental specifications.

## Context

An early draft introduced a reusable Billboard Sprite fragment and nested a `billboard`
object under each particle emitter. Only `VRMXT_sprite_particle` consumed that fragment.
Future trails, ribbons, and mesh particles use different geometry. Persistent icon or
emote sprites remain hypothetical.

Engine research showed:

- Unity and Unreal sprite particles generate billboard geometry at runtime.
- Godot and Three.js also create or share procedural quads at runtime.
- Mesh particles are the opposite case: they must reference real mesh assets.

## Decision

1. Remove the standalone Billboard Sprite fragment and the nested `billboard` object.
2. Keep `texture`, `size`, and `color` as fields on `VRMXT_sprite_particle` emitters.
3. Consumers create or select runtime sprite geometry. Exporters MUST NOT serialize that
   geometry as glTF meshes solely for this capability.
4. Define one camera-plane facing behavior in normative particle prose. Do not serialize
   facing mode, renderer type, or engine class names.
5. A future persistent icon/emote capability owns its own attachment and appearance data.
   Particles do not depend on it.
6. Introduce a shared appearance fragment only after multiple concrete capabilities
   require identical semantics.

## Rationale

Khronos `textureInfo` became a shared schema only after several material maps needed the
same `{ index, texCoord }` binding. Billboard Sprite had one consumer, so extraction was
premature.

Flattening keeps particle appearance with the particle capability. Runtime geometry stays
engine-owned, matching Unity `ParticleSystem` billboard mode, Niagara Sprite Renderer,
Godot draw-pass meshes, and Three.js sprites or instanced quads.

## Alternatives considered

| Alternative | Reason rejected |
|-------------|-----------------|
| Keep Billboard Sprite fragment | Only one concrete consumer; speculative reuse |
| Serialize a glTF mesh for the sprite | Stock avatar mesh data polluted by runtime helpers |
| Add renderer-type metadata | Engine-specific; not portable author data |
| Move particle appearance under a persistent-billboard extension | Couples unrelated emission and attachment capabilities |
| Keep selectable `facing` metadata | Author intent may return later; current draft uses one camera-plane behavior |

## Consequences

- `VRMXT_sprite_particle` schema is flatter.
- Implementation profiles map `texture` / `size` / `color` directly.
- Trail, ribbon, and mesh-particle drafts will redefine appearance fields if needed.
- Spec and consumer migration tracked in
  [issue #13](https://github.com/miramocha/Extended-VRM-Specs/issues/13) and
  [issue #14](https://github.com/miramocha/Extended-VRM-Specs/issues/14).

## Related

- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VFX capability boundaries](vfx-capability-boundaries.md)
- [VFX capability naming](vfx-capability-naming.md)
- [VRMXT Conformance](../specs/core/vrmxt-conformance.md)
