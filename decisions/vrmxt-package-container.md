---
title: VRMXT Package container format
aliases:
  - VRMXTPKG decision
  - compiled avatar distribution
tags:
  - extended-vrm
  - decision/package
  - format/vrmxtpkg
  - compatibility/vrm1
type: decision
status: draft
---

# VRMXT Package container format

## Status

Draft. Experimental specifications under `specs/packages/vrmxt-package/`.

## Context

VRM 1.0 is glTF. A static `.vrm` on a website is a complete, Blender-openable file.
`VRMXT_*` extensions stay on that glTF and MUST remain ignorable
([VRMXT Conformance](../specs/core/vrmxt-conformance.md)). They cannot hide the mesh.

Web delivery still needs humanoid, expressions, MToon, and optional `VRMXT_*` behavior
after load.

## Decision

1. Add a **sibling** compiled format, VRMXT Package (`.vrmxtpkg`), not a glTF
   extension and not a second authoring format.
2. Authoring remains `.vrm` (`VRMC_*` + optional `VRMXT_*`). Distribution MAY be
   `.vrmxtpkg`.
3. Version 1 packages VRM avatars only. `.vrma` stays a separate fetch.
4. Runtime MUST NOT reconstruct a full VRM/GLB buffer. Stock three-vrm
   `VRMLoaderPlugin` is not the load path.
5. Protected web delivery uses anonymous gateway sessions, AES-GCM chunks, and
   server-time expiry. Keys are not derived from clocks on the client.
6. Live objects use a facade so stock GLTF/VRM exporters do not round-trip a usable
   VRM. This is deterrence, not DRM.
7. Specs live in this repository. The first SDK MAY live in another repo as
   `@vrmxt/package`.

## Rationale

glTF extensions cannot both stay ignorable and prevent opening the file as VRM.
A container can drop GLB magic, split resources, and attach a key broker without
changing stock VRM tools.

## Alternatives considered

| Alternative | Reason rejected |
|-------------|-----------------|
| Encrypt whole `.vrm`, decrypt to `GLTFLoader.parse` | Full VRM exists in RAM; trivial dump |
| Zip + password in the JS bundle | Key is public |
| Timestamp-derived keys | Client can recompute or change the clock |
| Remote rendering only | Correct max protection; out of scope for this format |
| Fork three-vrm | Avoid unless public runtime classes cannot build the facade |

## Related

- [VRMXT Package Format](../specs/packages/vrmxt-package/README.md)
- [Extended VRM Architecture](../architecture.md#vrmxt-package)
