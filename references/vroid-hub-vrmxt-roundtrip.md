---
title: VRoid Hub VRMXT round-trip
aliases:
  - VRoid Hub materials override survival
  - VRMXT Hub download test
tags:
  - extended-vrm
  - reference/compatibility
  - compatibility/vrm1
  - spec/materials
  - implementation/warudo
type: reference
status: draft
---

# VRoid Hub VRMXT round-trip

Non-normative empirical note. Records whether `VRMXT_*` metadata survives upload to
[VRoid Hub](https://hub.vroid.com/) and download of the **original** model file.

Hub also builds a separate optimized preview for the browser viewer. This note covers
the downloaded original only. Preview GLB was not inspected in this pass.

## Finding (2026-07-21)

`VRMXT_materials_override` survived a Hub upload → download round trip.

| Check | Result |
|-------|--------|
| File | Warudo `StreamingAssets/Characters/vrmxt_vroid_hub_roundtrip.vrm` (GLB 2, ~14.5 MB) |
| VRM | `VRMC_vrm` 1.0, meta name `Mira GD Base` |
| `extensionsUsed` | Includes `VRMXT_materials_override` |
| Root `extensions` | No VRMXT key (expected; override attaches on materials) |
| Material attachments | `materials[10]` and `materials[11]` both carry the extension |

Override payload on both hair materials:

| Field | Value |
|-------|-------|
| `engine` | `unity` |
| `material.id` | `Hidden/lilToonOutline` |
| `material.idType` | `shaderName` |
| `material.variant` | `builtin` |
| Property count | 462 (390 scalar, 71 vector, 1 texture) |
| Texture props | `_MainTex` present with `value: null` |

Null `_MainTex` may be authored that way or lost earlier in the pipeline. No pre-upload
byte comparison in this pass.

## Related Hub behavior (public)

- Hub FAQ: downloadable VRM for own / redistributable models is the **original** upload;
  browser display uses a separately optimized model
  ([FAQ](https://vroid.pixiv.help/hc/en-us/articles/900001196326-The-VRoid-Studio-model-looks-different-from-the-VRoid-Hub-model)).
- Model processing / optimize / on-demand serve (historically VRMIO, VRMFLUX, now Rust)
  is closed-source. Pixiv open-sourced VRM schema crates as
  [vrm-utils-rs](https://github.com/pixiv/vrm-utils-rs), not the optimizer.
- `@pixiv/three-vrm` is the Hub **viewer** stack (load/render). It does not export VRM
  and is not the upload optimize path.

## Open checks

- [ ] Diff pre-upload vs post-download for texture indices and full property equality
- [ ] Inspect Hub **preview** / optimized GLB for the same extension
- [ ] Round-trip other `VRMXT_*` roots (`VRMXT_sprite_particle`, etc.)

## Related

- Spec: [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
- Warudo apply: [Warudo Materials Override](../implementations/warudo-materials-override.md)
