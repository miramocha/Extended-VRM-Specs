---
title: Unity Poiyomi Catalog
aliases:
  - Poiyomi materials override catalog
  - Poiyomi Toon shader catalog
tags:
  - extended-vrm
  - reference/materials-override
  - reference/unity-shader
  - compatibility/vrm1
type: reference
status: draft
---

# Unity Poiyomi Catalog

Authoring catalog note for [Poiyomi Toon Shader](https://github.com/poiyomi/PoiyomiToonShader)
under [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md). Index and shared
schema: [Materials Override Catalogs](../materials-override-catalogs.md).

Non-normative. Not a closed allowlist.

## Identity

| Field | Value |
|-------|-------|
| `engine` | `unity` |
| `idType` | `shaderName` |
| Primary Toon `shaderName` | `.poiyomi/Poiyomi Toon` |
| Source file (9.3 Toon) | [`_PoiyomiShaders/Shaders/9.3/Toon/Poiyomi Toon.shader`](https://github.com/poiyomi/PoiyomiToonShader/blob/master/_PoiyomiShaders/Shaders/9.3/Toon/Poiyomi%20Toon.shader) |
| Upstream `Shader.Find` | `Shader.Find(".poiyomi/Poiyomi Toon")` |
| Observed package line | `Poiyomi 9.3.64` (pin TBD) |

`material.id` MUST be the exact ShaderLab name **`.poiyomi/Poiyomi Toon`** (leading dot,
space before `Toon`).

### Related shader names (family)

First ship / Warudo Poiyomi Shader VRMXT Plugin SKU ships primary Toon plus kept alts:
Early Outline, Grab Pass, Two Pass (and Extras).

**Deferred** to a separate plugin (omit from Manager shader autocomplete):

| ShaderLab name |
|----------------|
| `.poiyomi/Poiyomi Toon + Lil Fur` |
| `.poiyomi/Poiyomi Toon + Lil Fur Two Pass` |
| `.poiyomi/Poiyomi Toon World` |

Other siblings (Pro, etc.) remain **TBD**. Confirm `Shader "…"` strings against the pinned
revision before adding dropdown rows.

### Provider (advisory)

| Field | Suggested value | Notes |
|-------|-----------------|-------|
| `provider.id` | TBD | Advisory only |
| `provider.version` | Pin when known (e.g. 9.3.x) | Exporter-observed version |

### Render pipeline support

Official **Poiyomi Toon** (this GitHub free/open line) targets **Built-in RP (BIRP)** only.
Upstream README: not compatible with URP, HDRP, or other SRPs (DX11 / VRChat-oriented).

| Pipeline | Support (upstream) | Catalog `supportedVariants` | Dropdown when that variant selected |
|----------|--------------------|-----------------------------|--------------------------------------|
| Built-in (`builtin`) | yes | yes | Shows Poiyomi |
| URP (`urp`) | no (official Toon) | no | Poiyomi **not** listed |
| HDRP (`hdrp`) | no (official Toon) | no | Poiyomi **not** listed |

Catalog JSON SHOULD set `"supportedVariants": ["builtin"]` and
`"defaultVariant": "builtin"`.

Separate commercial / Pro URP builds are out of scope until they have a documented
`Shader.Find` name and a distinct catalog entry (with their own `supportedVariants`).

URP/HDRP hosts that cannot resolve `.poiyomi/Poiyomi Toon` keep stock VRM import.

### Warudo BIRP plugins (non-normative)

Warudo Poiyomi Shader VRMXT Plugin (same ShaderLab name `.poiyomi/Poiyomi Toon` — enable one SKU):

| SKU | Plugin id | Notes |
|-----|-----------|--------|
| Lite | `mira.shaders.poiyomi.birp` | Smaller; glitter/emission warm |
| Full | `mira.shaders.poiyomi.birp.full` | Avatar-common `multi_compile` + expanded SVC |

Variant / warm / cut notes: [Warudo Poiyomi BIRP Variants](../warudo-poiyomi-birp-variants.md).

Supported override features for Warudo MUST NOT depend on third-party Unity packages
or world stacks (example: **AudioLink** / `com.llealloo.audiolink`). See that note’s
host dependency policy. Shader stubs may remain; catalogs and “supported” lists omit them.

## Type mapping

TBD. Same coarse map as other Unity catalogs: `Color` → `vector`, `2D` → `texture`,
floats/ranges → `scalar`.

## Curated property subset

Empty. Fill later; keep curated, not a full property mirror.

## Upstream pin

| Item | Value |
|------|-------|
| Repository | https://github.com/poiyomi/PoiyomiToonShader |
| Source path | `_PoiyomiShaders/Shaders/9.3/Toon/Poiyomi Toon.shader` |
| Pin (tag or commit) | TBD |

## Open questions

- [ ] Pin Poiyomi 9.3.x tag/commit for first shipped JSON
- [ ] Which sibling shaders belong in the first ship set (Toon-only vs Pro / other)
- [ ] Whether a separate catalog entry is ever needed for Pro URP (different `shaderName`)
- [ ] Curated property list for common VRM override workflows
- [ ] Which toggles / keywords map to `scalar` vs `shaderFeature`

## Related

- Index: [Materials Override Catalogs](../materials-override-catalogs.md)
- Sibling: [Unity lilToon Catalog](unity-liltoon.md)
- Blender authoring: [Blender VRMXT materials override](../../implementations/blender-vrmxt.md#materials-override)
- Unity apply: [UniVRMXT materials override](../../implementations/univrm-vrmxt.md#materials-override)
