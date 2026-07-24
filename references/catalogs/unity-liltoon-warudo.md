---
title: Unity lilToon Warudo Catalog
aliases:
  - lilToon Warudo materials override catalog
  - lilToon 1.10.3 Warudo catalog
tags:
  - extended-vrm
  - reference/materials-override
  - reference/unity-shader
  - compatibility/vrm1
  - compatibility/warudo
type: reference
status: draft
---

# Unity lilToon Warudo Catalog

Authoring catalog for the lilToon pin Warudo hosts: **1.10.3**. Same `shaderName`
values as [Unity lilToon Catalog](unity-liltoon.md) (pin **2.3.4**), separate JSON so
Blender can offer both without mixing property sets.

Non-normative. Extracted from the vendored ShaderLab in
[Warudo Shader Plugins](https://github.com/miramocha/Warudo-Shader-Plugins)
`LilToonShaderPluginBirp` (Upstream release
[1.10.3](https://github.com/lilxyzw/lilToon/releases/tag/1.10.3)).

## Identity

| Field | Value |
|-------|-------|
| `engine` | `unity` |
| `idType` | `shaderName` |
| Primary opaque `shaderName` | `lilToon` |
| Upstream pin | lilToon **1.10.3** |
| Warudo host RP | Built-in (`builtin`) |
| Catalog JSON | [`catalogs/data/unity-liltoon-warudo.json`](data/unity-liltoon-warudo.json) |

### Related shader names (family)

| Mode (informal) | `shaderName` | `displayName` | Catalog JSON |
|-----------------|--------------|---------------|--------------|
| Opaque | `lilToon` | lilToon Warudo 1.10.3 | [`unity-liltoon-warudo.json`](data/unity-liltoon-warudo.json) |
| Cutout | `Hidden/lilToonCutout` | lilToon Cutout Warudo 1.10.3 | [`unity-liltoon-warudo-cutout.json`](data/unity-liltoon-warudo-cutout.json) |
| Transparent | `Hidden/lilToonTransparent` | lilToon Transparent Warudo 1.10.3 | [`unity-liltoon-warudo-transparent.json`](data/unity-liltoon-warudo-transparent.json) |

Curated property declarations match across all three at this pin (356 props each).
Outline / multi / lite / fur stay out of scope (same as the 2.3.4 family).

### Render pipeline support

| Pipeline | Catalog `supportedVariants` | Notes |
|----------|-----------------------------|-------|
| Built-in (`builtin`) | yes | Warudo + BIRP shader plugin |
| URP (`urp`) | **no** | Not listed; use Custom or the 2.3.4 family if needed |
| HDRP (`hdrp`) | **no** | — |

`"defaultVariant": "builtin"`, `"supportedVariants": ["builtin"]`.

## vs pin 2.3.4

Same common-prop policy and section include/exclude rules as
[Unity lilToon Catalog](unity-liltoon.md). Count differs:

| Pin | Props | Not in the other pin (curated names) |
|-----|-------|--------------------------------------|
| Warudo **1.10.3** | 356 | — |
| Current **2.3.4** | 359 | `_Ramp`, `_EnvRimBorder`, `_EnvRimBlur` |

Use this family when the target runtime is Warudo’s lilToon 1.10.3 mod. Use the 2.3.4
family for newer UniVRMXT / general Unity authoring.

## Curated property subset

Common / extended tiers and `enableToggles` match the 2.3.4 note (22 common). Full
machine list: [`unity-liltoon-warudo.json`](data/unity-liltoon-warudo.json). Pin bump /
regen: [Maintaining catalogs](maintaining-catalogs.md).

MToon convert / suggested bindings: reuse
[Unity lilToon Catalog — lilToon ↔ MToon](unity-liltoon.md#liltoon--mtoon-conversion-upstream).
Names that exist only on 2.3.4 are absent here.

## Upstream pin

| Item | Value |
|------|-------|
| Repository | https://github.com/lilxyzw/lilToon |
| Tag | `1.10.3` |
| Warudo vendor tree | `Assets/LilToonShaderPluginBirp/lilToon/` in Warudo Shader Plugins |
| Opaque source | `Shader/lts.shader` |
| Cutout source | `Shader/lts_cutout.shader` |
| Transparent source | `Shader/lts_trans.shader` |

Release: https://github.com/lilxyzw/lilToon/releases/tag/1.10.3

## Related

- Sibling (newer pin): [Unity lilToon Catalog](unity-liltoon.md)
- Index: [Materials Override Catalogs](../materials-override-catalogs.md)
- Maintainer regen: [Maintaining catalogs](maintaining-catalogs.md)
- Warudo plugin: [LilToonShaderPluginBirp](https://github.com/miramocha/Warudo-Shader-Plugins)
- Blender authoring: [Blender VRMXT materials override](../../implementations/blender-vrmxt.md#materials-override)
