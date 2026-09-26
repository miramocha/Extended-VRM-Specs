---
title: VRMXT Package Security
aliases:
  - VRMXTPKG threat model
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
type: specification
status: draft
---

# VRMXT Package Security

Threat model for `.vrmxtpkg`. Non-secret. Conforms to
[VRMXT Package Format](README.md).

## In scope

- Casual download of a raw `.vrm` from static hosting
- Opening the network file in Blender / UniVRM as VRM
- Stock `GLTFExporter` / community VRM exporters on the live scene
- Bulk scrape of guessable URLs
- Replay of expired gateway sessions
- Client clock rollback to mint keys

## Out of scope (will not be solved by this format)

- Determined attacker with a working browser session who hooks decode, copies GPU
  buffers, or writes a custom exporter
- Users who screenshot or record the canvas
- Remote attestation that the official loader ran unmodified

True non-delivery of mesh data requires **remote rendering**. That is a different
product.

## Properties we claim (when Protection + **session** Delivery are used)

| Claim | Mechanism |
|-------|-----------|
| No public VRM/GLB | Container magic, split encrypted chunks |
| Cannot newly decrypt after expiry | Gateway clock, wrap TTL |
| Keys not in the static file | Private key metadata |
| Stock re-export fails | [Runtime](runtime.md) facade + attribute swizzle |
| Leaks may be cohort-traceable | [Watermark](watermark.md) |

## Properties we claim (when Protection + **static** Delivery are used)

| Claim | Mechanism |
|-------|-----------|
| No public VRM/GLB header | Container magic, encrypted chunks |
| File does not expire | No session; keys live in the signed index |
| Stock re-export fails | Same runtime facade |

Static packages do **not** claim that keys are absent from the download. Anyone with
the `.vrmxtpkg` can decrypt.

## Properties we do not claim

| Non-claim |
|-----------|
| Unextractable mesh while rendered |
| Per-person legal identity from anonymous sessions |
| WASM hiding equals key secrecy |
| Revoking a key already observed in RAM |

## Residual attacks

1. Hook Worker post-decrypt, dump chunks, write a custom GLB builder.
2. Read `BufferGeometry` after a buggy consumer skipped swizzle.
3. `readPixels` / `getBufferSubData` from GPU.
4. Instrument the official loader and disable swizzle.
5. Valid session + save wrapped keys if extractable.

## Operational notes

- Rotate Ed25519 signing keys; publish `signingKeyId`.
- Rotate content keys by recompiling or re-wrapping; old packages stay decryptable if
  old keys leak.
- Log watermark selection with session id and coarse request metadata.
- Production builds MUST fail if a `.vrm` or GLB magic ships next to the site bundle.

## Related

- [Protection](protection.md)
- [Delivery](delivery.md)
- [Runtime](runtime.md)
