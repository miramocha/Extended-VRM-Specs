---
title: VRMXT Package Format
aliases:
  - VRMXTPKG
  - .vrmxtpkg
  - VRMXT Package
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
  - compatibility/vrm1
type: specification
status: draft
---

# VRMXT Package Format

Portable compiled avatar container. File extension `.vrmxtpkg`. Magic `VRMXTPKG`.

This specification is **not** a glTF extension. The name MUST NOT appear in
`extensionsUsed` or `extensionsRequired`. A `.vrmxtpkg` file is not a `.vrm` / `.glb`
and MUST NOT begin with glTF / GLB magic (`glTF` / `glTF` binary header).

A supporting runtime reconstructs avatar **behavior** (humanoid, expressions, look-at,
spring bones, MToon, optional `VRMXT_*` capabilities) from typed descriptors and resource
chunks. It MUST NOT assemble a complete VRM or GLB byte stream in memory.

VRM Animation (`.vrma`) is out of scope for format version 1.

## Documents

| Document | Role |
|----------|------|
| [Container](container.md) | Header, index, chunks, codecs |
| [Payload](payload.md) | Scene graph, mesh, material, VRM 1.0 semantics |
| [Protection](protection.md) | Signatures, encryption, key wrapping |
| [Delivery](delivery.md) | Anonymous session, expiry, chunk fetch |
| [Runtime](runtime.md) | Incremental load, facade, anti-reexport |
| [Watermark](watermark.md) | Forensic carrier variants |
| [Security](security.md) | Threat model and residual attacks |
| [Decision](../../../decisions/vrmxt-package-container.md) | Why a sibling format exists |

## Profiles

Consumers claim support per profile. A Three.js site loader MAY implement all of them.
A native engine MAY implement Container + Payload only.

| Profile | Document | Required for |
|---------|----------|--------------|
| Container | [container.md](container.md) | Parse `.vrmxtpkg` |
| Payload | [payload.md](payload.md) | Avatar semantics without reconstructing VRM bytes |
| Protection | [protection.md](protection.md) | Encrypted distribution |
| Delivery | [delivery.md](delivery.md) | Time-limited keys and private chunks |
| Runtime | [runtime.md](runtime.md) | Engine-specific construction rules |
| Watermark | [watermark.md](watermark.md) | Optional forensic variants |

Protection and Delivery MAY be omitted for local compiler tests. A production web
distribution that claims protection MUST implement both.

## Relationship to VRM and VRMXT

| Artifact | Role |
|----------|------|
| `.vrm` (glTF + `VRMC_*`) | Authoring and stock interchange |
| `VRMXT_*` glTF extensions | Optional extras on that `.vrm` |
| `.vrmxtpkg` | Compiled, optionally protected **distribution** of one avatar |

A compiler reads VRM 1.0 (and optional `VRMXT_*`) and emits `.vrmxtpkg`. Stock VRM
importers MUST NOT be expected to open `.vrmxtpkg`.

## Versioning

| Field | Value in this draft |
|-------|---------------------|
| Container `formatVersion` | `1` |
| Index `specVersion` | `"1.0"` |
| Payload `payloadKind` | `"vrm1"` |

`formatVersion` is an unsigned integer in the binary header. `specVersion` is a string
in the signed index. Breaking binary layout increments `formatVersion`. Additive index
fields MAY keep `formatVersion` 1 and bump `specVersion` only when this specification
says so.

## Related

- [VRMXT Conformance](../../core/vrmxt-conformance.md) (glTF `VRMXT_*` family; does not govern this container)
- [Extended VRM Architecture](../../../architecture.md#vrmxt-package)
- [Implementation profile](../../../implementations/vrmxt-package.md)
