---
title: VFX capability boundaries
aliases:
  - VRMXT particle standardization
  - VRMXT VFX extension split
tags:
  - extended-vrm
  - decision/vfx
  - format/gltf-extension
  - compatibility/vrm1
type: decision
status: accepted
---

# VFX capability boundaries

## Status

Accepted for the current experimental specifications. The extension identifiers and
schemas remain drafts until their specifications are accepted.

## Context

The first particle draft used one root extension, `VRMXT_vfx`, with a polymorphic entry
list. Future effect kinds would have added `type` values for particles, trails, ribbons,
and other rendering systems.

glTF advertises support through extension names in `extensionsUsed`. A consumer that
implements particles alone cannot express precise support for one type inside a
`VRMXT_vfx` union. Changes to any effect type would also share the umbrella extension's
`specVersion`.

The draft also stored `localPosition` and `localRotation` on each effect entry. These
fields duplicated glTF node transforms. They also required custom transform composition
and prevented ordinary glTF animation channels from driving the attachment offset.

Lattice deformation was considered alongside VFX because both can add visible behavior
to an avatar. Its data and runtime stage differ: lattice binds cages to meshes and
modifies vertices, while particles render transient geometry from a scene-graph node.

## Decision

1. Each portable capability uses its own glTF extension. Sprite particles use
   `VRMXT_sprite_particle`. Trails, ribbons, mesh particles, or other capabilities
   receive separate extension names if standardized. See
   [VFX capability naming](vfx-capability-naming.md).
2. Extension identifiers stay flat. The repository groups rendering effects under
   `specs/extensions/vfx/`; that folder does not add `vfx` to the serialized identifier.
3. `VRMXT_vfx` and its polymorphic `effects[].type` design are removed.
4. Lattice remains the separate `VRMXT_lattice` deformation capability.
5. Shared family behavior belongs in
   [VRMXT Conformance](../specs/core/vrmxt-conformance.md). Speculative shared rendering
   fragments are deferred until multiple concrete capabilities need identical semantics.
   See [Billboard sprite ownership](billboard-sprite-ownership.md).
6. A particle emitter attaches through `emitters[].node`, a zero-based index into glTF
   `nodes[]`. The referenced node supplies origin and orientation.
7. An authoring tool that needs an offset creates an ordinary helper node under the
   bone or object and points the emitter at that helper. The helper does not need to be
   listed in `skin.joints`.
8. Particle entries do not define `localPosition`, `localRotation`, or another
   attachment-transform layer. Initial velocity follows the referenced node's local +Y
   axis after evaluation of its world transform.

## Rationale

Separate extension names provide capability-level negotiation. A consumer can support
`VRMXT_sprite_particle` without claiming support for trails or ribbons, and each
capability can change its schema independently.

Using glTF nodes for offsets preserves one scene graph. Existing node TRS, hierarchy,
and animation rules apply without a VRMXT transform model. An ordinary helper node also
avoids adding an unweighted joint to the skin and keeps attachment anchors usable by
capabilities outside particle rendering.

The flat identifier keeps the capability name concise. Folder placement provides the
VFX taxonomy needed by documentation and tooling.

## Alternatives considered

| Alternative | Reason rejected |
|-------------|-----------------|
| Keep `VRMXT_vfx` with `effects[].type` | Capability support and schema evolution remain coupled under one extension identifier |
| Use `VRMXT_vfx_particle`, `VRMXT_vfx_trail`, and similar names | The `vfx` segment adds taxonomy already represented by repository structure and tags |
| Fold lattice into the VFX family | Lattice runs in the mesh-deformation pipeline and requires cage-to-mesh bindings |
| Keep the Node Attachment fragment | `localPosition` and `localRotation` duplicate core glTF node TRS |
| Require attachment bones | A bone is a node listed in `skin.joints`; offset anchors do not need skin membership |

## Consequences

- Each new capability requires a new extension specification and `extensionsUsed`
  identifier.
- Particle files may contain extra helper nodes. Stock glTF and VRM importers can load
  those nodes as ordinary transforms while ignoring `VRMXT_sprite_particle`.
- Core glTF animation can target helper-node TRS.
- Exporters must preserve helper nodes referenced by VRMXT extensions even when they
  have no mesh, skin, or camera.
- Existing experimental implementations and fixtures need the schema refactor tracked
  in [issue #14](https://github.com/miramocha/Extended-VRM-Specs/issues/14).
- Remaining specification work is tracked in
  [issue #13](https://github.com/miramocha/Extended-VRM-Specs/issues/13).

## Related

- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VFX capability naming](vfx-capability-naming.md)
- [Billboard sprite ownership](billboard-sprite-ownership.md)
- [VRMXT_lattice](../specs/extensions/deformation/vrmxt-lattice.md)
- [VRMXT Conformance](../specs/core/vrmxt-conformance.md)
