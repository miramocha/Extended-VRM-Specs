---
title: VRMXT Package implementation
aliases:
  - @vrmxt/package
  - VRMXTPKG SDK
tags:
  - extended-vrm
  - implementation/optional-consumer
  - format/vrmxtpkg
type: guide
status: draft
---

# VRMXT Package implementation

Non-normative profile for the compiled container
[VRMXT Package Format](../specs/packages/vrmxt-package/README.md).

This is **not** [three-vrmxt](three-vrmxt.md). `three-vrmxt` is a `GLTFLoaderPlugin` for
`VRMXT_*` on ordinary `.vrm` files. VRMXT Package is a separate binary and loader.

## Planned packages

| Package | Role |
|---------|------|
| `@vrmxt/package` | Container parse, protection, delivery client, Three.js facade |
| `@vrmxt/package/compiler` | `.vrm` → `.vrmxtpkg` |
| `@vrmxt/package/gateway` | Session/chunk handler (Node-agnostic) |

First in-tree consumer MAY be a website workspace that depends on `@vrmxt/package`
and does not parse package bytes itself.

## Three.js

- `VRMXTPackageLoader.load(packageId | indexUrl, { signal, onProgress })`
- Returns a facade: `scene`, `humanoid`, `expressionManager`, `lookAt`, `update(delta)`
- Decode Worker for AES-GCM + meshopt/KTX2
- Vite or Node mounts `@vrmxt/package/gateway` for local sessions

## Unity / Blender

Not started. Same Payload JSON; native geometry APIs. No requirement to produce GLB.

## Conformance tests (package, not site)

- Header/magic reject GLB
- Encrypt/decrypt round-trip
- Signature tamper
- Expired **session** → 410
- Static package loads without gateway; keys in index
- No assembled GLB in tests that hook the loader
- `GLTFExporter` / known VRM exporters fail or yield non-loadable output
- Expression presets `blink` / `aa` / `oh` when present in source
- Humanoid bone parity

## Related

- [Runtime](../specs/packages/vrmxt-package/runtime.md)
- [Delivery](../specs/packages/vrmxt-package/delivery.md)
- [three-vrmxt](three-vrmxt.md)
