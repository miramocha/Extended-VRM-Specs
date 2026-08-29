---
title: VRMXT Package Watermark
aliases:
  - VRMXTPKG forensic watermark
  - VRMXT Package variants
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
type: specification
status: draft
---

# VRMXT Package Watermark

Optional forensic fingerprinting. Conforms to [VRMXT Package Format](README.md).

## Goal

Identify **which session class** a leaked mesh likely came from, without baking a unique
full mesh per viewer.

## Carrier model

The compiler emits `N` carrier groups. Each group has two imperceptible variants
(`variant` 0 and 1) of the same logical mesh or texture (tiny position or texel delta).

The session's `watermarkSelection` is an `N`-bit string (or list of `{ group, bit }`).
Gateway serves only the selected variant chunks ([Delivery](delivery.md)).

Index field `watermark`:

| Property | Type | Required |
|----------|------|----------|
| `groups` | object[] | yes |
| `groups[].id` | string | yes |
| `groups[].chunkIds` | string[2] | yes | Variant 0 and variant 1 chunk ids |

Amplitude MUST stay below a documented visual threshold and above quantization /
meshopt loss so recovery still works after common mesh export.

## Recovery (non-normative)

Compare leaked geometry or textures to both carriers; read bits; map to session
cohort or logged selection. Not a legal identity. Anonymous sessions only bind to
gateway logs (IP, time, selection).

## Normative requirements

1. Watermark MUST NOT be the only access-control mechanism.
2. Both variants MUST remain valid Payload (bounds, skinning, expressions).
3. A consumer MUST NOT fetch the non-selected variant for a group in a protected
   session.
4. Unwatermarked packages omit `watermark`.

## Open questions

- [ ] `N` default (suggested 8–16)
- [ ] Texture vs vertex carriers
- [ ] Survival through glTF re-export and Blender import

## Related

- [Delivery](delivery.md)
- [Security](security.md)
