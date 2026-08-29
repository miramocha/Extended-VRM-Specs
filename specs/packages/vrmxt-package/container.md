---
title: VRMXT Package Container
aliases:
  - VRMXTPKG container
  - VRMXT Package binary layout
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
type: specification
status: draft
---

# VRMXT Package Container

Binary layout of `.vrmxtpkg` and optional split chunks. Conforms to
[VRMXT Package Format](README.md).

## Scope

| Item | Value |
|------|-------|
| Media type (proposed) | `application/vnd.vrmxt.package` |
| Extension | `.vrmxtpkg` |
| Endianness | little-endian |
| Integer widths | unsigned unless noted |

## Header

Fixed 48-byte prefix. Offset 0.

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0 | 8 | `magic` | ASCII `VRMXTPKG` (`56 52 4D 58 54 50 4B 47`) |
| 8 | 4 | `formatVersion` | `1` for this draft |
| 12 | 4 | `flags` | Bit field below |
| 16 | 8 | `indexOffset` | Byte offset of signed index blob |
| 24 | 8 | `indexLength` | Length of signed index blob |
| 32 | 16 | `indexDigest` | SHA-256 of the **unsigned** index JSON bytes |

A consumer MUST reject the file if `magic` is not `VRMXTPKG`.
A consumer MUST reject `formatVersion` it does not implement.
`indexOffset` MUST be `48` or greater. Bytes between header and index, if any, MUST be
ignored by version-1 consumers (reserved padding).

### Flags

| Bit | Name | Meaning |
|-----|------|---------|
| 0 | `SPLIT` | Resource chunks are **not** embedded; fetch via Delivery URLs |
| 1 | `ENCRYPTED` | Resource chunks are AES-GCM sealed (see [Protection](protection.md)) |
| 2–31 | reserved | MUST be 0 in this draft; consumers MUST reject unknown set bits |

`ENCRYPTED` without a Protection-capable consumer MUST fail closed.
Embedded unencrypted packages MAY set both bits to 0 for compiler tests only.

## Signed index blob

Bytes `[indexOffset, indexOffset + indexLength)`:

| Offset in blob | Size | Field |
|----------------|------|-------|
| 0 | 64 | Ed25519 signature over `indexDigest` (or over canonical index UTF-8; see Protection) |
| 64 | 32 | `signingKeyId` (SHA-256 of public key, truncated policy in Protection) |
| 96 | remainder | UTF-8 JSON index, no BOM, no trailing garbage |

This draft signs the SHA-256 of the JSON. The header `indexDigest` MUST equal that hash.
A consumer MUST verify the signature before parsing JSON.

## Index JSON

Root object. Additional properties MUST be ignored unless marked forbidden.

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | `"1.0"` |
| `packageId` | string | yes | Stable id (UUID or reverse-DNS). Not a secret |
| `payloadKind` | string | yes | `"vrm1"` in this draft |
| `payload` | object | yes | Descriptor ids; schema in [Payload](payload.md) |
| `chunks` | object[] | yes | Non-empty list |
| `watermark` | object | no | See [Watermark](watermark.md) |
| `protection` | object | if `ENCRYPTED` | Algorithm ids only; **no keys** |

### `chunks[]`

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `id` | string | yes | Unique within package |
| `kind` | string | yes | Kind enum below |
| `codec` | string | yes | `identity`, `meshopt`, `ktx2`, `zstd` |
| `byteLength` | integer | yes | Ciphertext length if encrypted, else plaintext |
| `digest` | string | yes | `sha256:` plus 64 hex of **plaintext** after decrypt+decompress |
| `offset` | integer | if not `SPLIT` | Offset from start of `.vrmxtpkg` |
| `variantGroup` | string | no | Watermark carrier group |
| `variant` | integer | no | `0` or `1` when grouped |

Kind values for `payloadKind` `"vrm1"`:

`graph`, `mesh`, `morph`, `skin`, `image`, `material`, `humanoid`, `expression`,
`lookAt`, `firstPerson`, `springBone`, `nodeConstraint`, `meta`, `vrmxt`.

A consumer MUST fail if a required kind for the payload is missing
(see [Payload](payload.md) required set).

## Embedded chunks

When `SPLIT` is 0, each chunk occupies `[offset, offset + byteLength)` in the same file.
Regions MUST NOT overlap the header or the index blob. Regions MAY be sparse (unused
gaps MUST be ignored).

## Split chunks

When `SPLIT` is 1, the `.vrmxtpkg` file contains only header + signed index.
Chunk bytes are fetched per [Delivery](delivery.md). `offset` MUST be omitted.

## Codecs

| `codec` | Input after decrypt | Output |
|---------|---------------------|--------|
| `identity` | raw bytes | same |
| `zstd` | zstd frame | raw |
| `meshopt` | EXT_meshopt-style buffer | decoded vertex/index bytes defined by Payload |
| `ktx2` | KTX2 file | GPU-ready image as defined by Payload |

A consumer MUST decode `codec` before hashing against `digest`.

## Normative requirements

1. A file MUST NOT contain GLB magic at offset 0.
2. A consumer MUST NOT concatenate chunks into a GLB / VRM byte stream.
3. Chunk `id` values MUST match `payload` references.
4. Production distributions that set `ENCRYPTED` MUST NOT embed content keys in the
   index or package file.

## Open questions

- [ ] CBOR index instead of JSON
- [ ] Exact Ed25519 payload (raw hash vs detached canonical JSON)
- [ ] Maximum chunk count (suggested 4–12 coarse chunks)
- [ ] `signingKeyId` length (full SHA-256 vs 16-byte prefix)

## Related

- [Protection](protection.md)
- [Delivery](delivery.md)
- [Payload](payload.md)
