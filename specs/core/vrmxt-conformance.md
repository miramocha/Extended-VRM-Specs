---
title: VRMXT Conformance
aliases:
  - Extended VRM conformance
  - VRMXT family rules
tags:
  - extended-vrm
  - spec/conformance
  - compatibility/vrm1
type: specification
status: draft
---

# VRMXT Conformance

Shared requirements for extensions in the `VRMXT_*` family. Concrete capability
specifications cite this document and define their own glTF extension names, attachment
points, schemas, and `specVersion` values.

This document is not a glTF extension. Its name MUST NOT appear in `extensionsUsed` or
`extensionsRequired`, and it adds no serialized object to a glTF asset.

## Scope

| Item | Value |
|------|-------|
| Target | glTF 2.0 assets containing VRM 1.0 (`VRMC_vrm` 1.0) |
| Applies to | Concrete `VRMXT_*` extension specifications that cite this document |
| Serialized fields | none |
| Capability negotiation | Each concrete extension through glTF `extensionsUsed` |

## Normative requirements

1. A conforming capability specification MUST define its glTF extension name,
   attachment point, extension-object schema, and extension `specVersion`.
2. A file that contains a concrete `VRMXT_*` extension MUST list that extension name in
   `extensionsUsed`.
3. A concrete extension object MUST contain the `specVersion` required by its capability
   specification.
4. Consumers MUST ignore properties they do not recognize unless the capability
   specification assigns different handling to that property.
5. A consumer that does not support a concrete `VRMXT_*` extension MUST ignore it and
   continue loading the underlying glTF and VRM 1.0 asset.
6. Files MUST NOT list a `VRMXT_*` extension in `extensionsRequired`. Portable glTF and
   VRM 1.0 data MUST remain usable when every `VRMXT_*` extension is ignored.
7. Invalid `VRMXT_*` data MUST NOT make the underlying glTF or VRM 1.0 asset invalid.
   Each capability specification MUST define the smallest independently skippable unit
   and the fallback behavior for invalid data.
8. Runtime objects and state created or modified from `VRMXT_*` data MUST remain scoped
   to the asset instance that contains the extension. They MUST NOT modify another
   avatar instance, shared environment state, scene-wide rendering, camera-wide
   rendering, or global post-processing.
9. A consumer MUST NOT mutate a shared engine resource when that mutation would change
   another asset instance or the environment. It MUST create instance-owned state or an
   equivalent isolated copy.
10. Numeric data MUST use glTF units and coordinate conventions unless a capability
    specification explicitly defines another representation.

## Extension names

Serialized glTF extension names defined by this family MUST use the `VRMXT_` prefix.
`VRMC_` names are VRM Consortium identifiers (`VRMC_vrm`, `VRMC_materials_mtoon`,
`VRMC_springBone`, `VRMC_springBone_extended_collider`, and other stock extensions).
Capability specifications in this repository MUST NOT invent new `VRMC_*` names.

A sibling extra on the same glTF object as a stock `VRMC_*` extension is still a
`VRMXT_*` name. Family-fork names append `xt` to the stock stem with no extra
underscore: `VRMXT_materials_mtoonxt` on `materials[i].extensions` beside
`VRMC_materials_mtoon`; `VRMXT_springBonext` on root `extensions` beside
`VRMC_springBone`. MToon feature extras use their own names on the same sit-site:
`VRMXT_materials_stencil`, `VRMXT_materials_face_sdf`,
`VRMXT_materials_directional_dissolve`. Third-party replace names
use `_override`: `VRMXT_materials_override`, `VRMXT_springBone_override`. See
[Architecture Naming](../../architecture.md#naming).

Properties inside an extension object are unprefixed camelCase (`specVersion`,
`stencil`, `outlineStencil`, `sdfTexture`). They MUST NOT use a `VRMC_` or `VRMXT_`
property prefix.

Engine override extensions, family-fork `…xt` extensions, and MToon feature extras
are separate `VRMXT_*` names. Family extras MUST NOT be written as unknown fields
inside stock `VRMC_*` objects. When an `_override` Apply succeeds on a material or
spring, a supporting implementation MUST skip the `…xt` fork and the MToon feature
extras for that item.

## Capability support

Support is declared per concrete extension, not for the `VRMXT_*` family as a whole.
A consumer claiming support for a capability MUST implement every normative fragment
cited by that capability specification.

Partial support for a capability MUST be documented by the implementation profile. It
MUST NOT be presented as full support for that capability. Claiming
`VRMXT_materials_mtoonxt` does not claim `VRMXT_materials_stencil`,
`VRMXT_materials_face_sdf`, or `VRMXT_materials_directional_dissolve`.

## Versioning

While these drafts remain experimental, citations to this document and to shared
fragments stay unversioned. Concrete extensions still use their own serialized
`specVersion`.

Pinned conformance or fragment versions, and migration rules when those texts diverge,
are future work. They do not block experimental use of the family rules above.

## Related

- [VRMXT_materials_override](../extensions/materials/vrmxt-materials-override.md)
- [VRMXT_materials_mtoonxt](../extensions/materials/vrmxt-materials-mtoonxt/README.md)
- [VRMXT_materials_stencil](../extensions/materials/vrmxt-materials-stencil.md)
- [VRMXT_materials_face_sdf](../extensions/materials/vrmxt-materials-face-sdf.md)
- [VRMXT_materials_directional_dissolve](../extensions/materials/vrmxt-materials-directional-dissolve.md)
- [VRMXT_springBonext](../extensions/physics/vrmxt-springbonext/README.md)
- [VRMXT_springBone_override](../extensions/physics/vrmxt-spring-bone-override.md)
- [VRMXT_sprite_particle](../extensions/vfx/vrmxt-sprite-particle.md)
- [VRMXT_lattice](../extensions/deformation/vrmxt-lattice.md)
- [VRMXT_AnimationController](../extensions/animation/vrmxt-animation-controller.md)
- [VRMXT_AnimationClip](../extensions/animation/vrmxt-animation-clip.md)
