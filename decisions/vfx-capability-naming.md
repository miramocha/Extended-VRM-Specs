---
title: VFX capability naming
aliases:
  - VRMXT VFX extension names
  - sprite particle naming
tags:
  - extended-vrm
  - decision/vfx
  - format/gltf-extension
  - compatibility/vrm1
type: decision
status: accepted
---

# VFX capability naming

## Status

Accepted for the current experimental specifications. Future capability names below are
candidates until their specifications exist.

## Context

[VFX capability boundaries](vfx-capability-boundaries.md) chose one glTF extension per
capability and kept `vfx` out of serialized identifiers. After the Billboard Sprite
fragment was removed, particle naming needed to distinguish sprite particles from future
mesh particles and persistent camera-facing quads.

Trail and ribbon terminology overlap across engines. Unreal Niagara uses one ribbon
renderer for both history strips and ordered chains. Godot names trail meshes after
ribbons. Shipping two extensions that differ only by engine vocabulary would be premature.

## Decision

1. Extension names identify portable capabilities. They do not encode engine classes,
   rendering resources, or repository folder names.
2. Keep `vfx` out of serialized identifiers. Folder placement under
   `specs/extensions/vfx/` supplies taxonomy.
3. Use singular snake-case names after `VRMXT_`.
4. Current particle capability is `VRMXT_sprite_particle` (formerly `VRMXT_particle` and
   earlier `VRMXT_vfx`).
5. Candidate future names:
   - `VRMXT_mesh_particle` — particles that reference one glTF mesh
   - `VRMXT_billboard` — persistent node-attached camera-facing quad
6. Do not use `VRMXT_texture_particle`. Texture is optional appearance, not the
   capability.
7. Do not reserve both `VRMXT_trail` and `VRMXT_ribbon` yet. Choose one strip capability
   name only after ordering and topology semantics are defined:
   - moving-point history / age ordering → trail behavior
   - ordered point or particle chains → ribbon behavior
8. If one schema covers both strip behaviors, use one extension with explicit ordering
   semantics.
9. Use `VRMXT_billboard` only when the capability is always camera-facing.
   Fixed or world-oriented quads need another name.

## Rationale

`sprite_particle` matches Unreal's sprite-versus-mesh particle split and leaves
`VRMXT_billboard` free for persistent icons. Flat names continue the boundary decision
against `VRMXT_vfx_*` prefixes.

## Alternatives considered

| Alternative | Reason rejected |
|-------------|-----------------|
| Keep `VRMXT_particle` | Too broad once mesh particles exist |
| `VRMXT_vfx_sprite_particle` | `vfx` segment duplicates folder taxonomy |
| `VRMXT_texture_particle` | Texture is optional; solid-color sprites remain valid |
| `VRMXT_billboard_particle` | Less common capability name across engines |
| `VRMXT_sprite` for persistent icons | Collides with sprite-particle vocabulary |
| Separate trail and ribbon names now | Engines often implement one strip renderer with two ordering modes |

## Consequences

- Specs, implementation profiles, and fixtures rename `VRMXT_particle` to
  `VRMXT_sprite_particle`.
- Persistent billboard and mesh-particle remain naming-only until drafted.
- Spec and consumer migration tracked in
  [issue #13](https://github.com/miramocha/Extended-VRM-Specs/issues/13) and
  [issue #14](https://github.com/miramocha/Extended-VRM-Specs/issues/14).

## Related

- [VFX capability boundaries](vfx-capability-boundaries.md)
- [Billboard sprite ownership](billboard-sprite-ownership.md)
- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VRMXT Conformance](../specs/core/vrmxt-conformance.md)
