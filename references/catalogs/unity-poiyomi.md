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

Poiyomi ships multiple shaders under `_PoiyomiShaders/Shaders/`. Sibling modes (Pro,
early versions, outline-only, etc.) are **TBD**. First ship target: 9.3 Toon above. Confirm
other `Shader "…"` strings against the pinned revision before adding dropdown rows.

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
