---
title: Unity lilToon Catalog
aliases:
  - lilToon materials override catalog
  - lilToon shader catalog
tags:
  - extended-vrm
  - reference/materials-override
  - reference/unity-shader
  - compatibility/vrm1
type: reference
status: draft
---

# Unity lilToon Catalog

Authoring catalog note for [lilToon](https://github.com/lilxyzw/lilToon) under
[VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md). Index and shared
schema: [Materials Override Catalogs](../materials-override-catalogs.md).

Non-normative. Not a closed allowlist. Property names from opaque
[`lts.shader`](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Shader/lts.shader)
(`Shader "lilToon"`), pin **2.3.4**.

## Identity

| Field | Value |
|-------|-------|
| `engine` | `unity` |
| `idType` | `shaderName` |
| Primary opaque `shaderName` | `lilToon` |
| Source file (opaque) | [`Assets/lilToon/Shader/lts.shader`](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Shader/lts.shader) |
| Upstream `Shader.Find` | `Shader.Find("lilToon")` |
| Catalog JSON | [`catalogs/data/unity-liltoon.json`](data/unity-liltoon.json) |

`material.id` for the opaque default is **`lilToon`**.

### Related shader names (family)

| Mode (informal) | `shaderName` | `displayName` | Catalog JSON |
|-----------------|--------------|---------------|--------------|
| Opaque | `lilToon` | lilToon 2.3.4 | [`unity-liltoon.json`](data/unity-liltoon.json) |
| Cutout | `Hidden/lilToonCutout` | lilToon Cutout 2.3.4 | [`unity-liltoon-cutout.json`](data/unity-liltoon-cutout.json) |
| Transparent | `Hidden/lilToonTransparent` | lilToon Transparent 2.3.4 | [`unity-liltoon-transparent.json`](data/unity-liltoon-transparent.json) |

One JSON file per `shaderName`. Cutout source:
[`lts_cutout.shader`](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Shader/lts_cutout.shader).
Transparent source:
[`lts_trans.shader`](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Shader/lts_trans.shader).
At pin **2.3.4**, curated property declarations (name, ShaderLab type, default) match
opaque for all three; the JSON property lists are copies. Other modes (outline, multi,
lite, fur, …) stay out of scope.

### Provider (advisory)

| Field | Suggested value | Notes |
|-------|-----------------|-------|
| `provider.id` | TBD | Advisory only |
| `provider.version` | Pin when known | Exporter-observed version |

### Render pipeline support

lilToon is **not** Built-in-only. Upstream ships one package that targets Built-in RP,
URP, and HDRP (pipeline detection / templates). The opaque `shaderName` remains
`lilToon` across those pipelines.

| Pipeline | Support (upstream) | Catalog `supportedVariants` | Dropdown when that variant selected |
|----------|--------------------|-----------------------------|--------------------------------------|
| Built-in (`builtin`) | yes | yes | Shows lilToon 2.3.4 |
| URP (`urp`) | yes | yes | Shows lilToon 2.3.4 |
| HDRP (`hdrp`) | yes (upstream) | **no** (not shipped yet) | lilToon **not** listed; Custom only |

Catalog JSON SHOULD set `"supportedVariants": ["builtin", "urp"]` and
`"defaultVariant": "builtin"`. Authors MAY still type `lilToon` under HDRP via Custom,
or we add `hdrp` to `supportedVariants` later after a pinned revision is smoke-tested.

Multi-slot: authors MAY store `(unity, builtin)` and `(unity, urp)` siblings with the
same `shaderName` per
[UniVRMXT materials override](../../implementations/univrm-vrmxt.md#materials-override).

## Type mapping

| ShaderLab | Catalog `type` | Notes |
|-----------|----------------|-------|
| `Color` | `vector` | `vectorSize` 4 |
| `2D` | `texture` | |
| `Float` / `Range` | `scalar` | |
| `[lilToggle]` / `[lilToggleLeft]` Int | `scalar` | Store 0/1 |
| `[lilEnum]` Int | `scalar` | Enum index |

## Curated property subset

Two tiers for Blender authoring ([Blender VRMXT materials override](../../implementations/blender-vrmxt.md#materials-override)):

| Tier | Catalog flag | UI |
|------|--------------|-----|
| Common | `common: true` | **Add Common Props** batch-adds these |
| Extended | listed, `common` omitted/false | **Add** enum only |
| Unlisted | — | **Custom…** (any lilToon name + manual type) |

### Common (`common: true`)

#### Main

| `name` | `type` | `displayName` |
|--------|--------|---------------|
| `_Color` | `vector` | Color |
| `_MainTex` | `texture` | Main Texture |
| `_Cutoff` | `scalar` | Cutoff |

#### Shadow (toon shade)

| `name` | `type` | `displayName` |
|--------|--------|---------------|
| `_UseShadow` | `scalar` | Use Shadow |
| `_ShadowColor` | `vector` | Shadow Color |
| `_ShadowColorTex` | `texture` | Shadow Color Texture |
| `_ShadowBorder` | `scalar` | Shadow Border |
| `_ShadowBlur` | `scalar` | Shadow Blur |
| `_ShadowStrength` | `scalar` | Shadow Strength |
| `_ShadowReceive` | `scalar` | Receive Shadow |
| `_Shadow2ndColor` | `vector` | Shadow 2nd Color |
| `_ShadowEnvStrength` | `scalar` | Shadow Env Strength |

#### Rim

| `name` | `type` | `displayName` |
|--------|--------|---------------|
| `_UseRim` | `scalar` | Use Rim |
| `_RimColor` | `vector` | Rim Color |
| `_RimColorTex` | `texture` | Rim Texture |
| `_RimBorder` | `scalar` | Rim Border |
| `_RimBlur` | `scalar` | Rim Blur |
| `_RimFresnelPower` | `scalar` | Rim Fresnel Power |
| `_RimEnableLighting` | `scalar` | Rim Enable Lighting |

#### Emission

| `name` | `type` | `displayName` |
|--------|--------|---------------|
| `_UseEmission` | `scalar` | Use Emission |
| `_EmissionColor` | `vector` | Emission Color |
| `_EmissionMap` | `texture` | Emission Map |

### Extended (catalog **Add** enum; not in **Add Common Props**)

359 properties total per JSON file at pin **2.3.4** (22 common + 337 extended). Machine
list: [`catalogs/data/unity-liltoon.json`](data/unity-liltoon.json). Regenerate from
ShaderLab sections via
[`generate_liltoon_curated.py`](../../.cursor/skills/unity-shader-catalog/scripts/generate_liltoon_curated.py).

Extended rows include normal/matcap (above) plus lilToon-only and MToon-adjacent extras
not covered by **Add Common Props**. Grouped by upstream inspector section:

| Section | Examples | MToon convert |
|---------|----------|---------------|
| Base / Main | `_MainTex_ScrollRotate`, `_MainTexHSVG`, `_MainGradationTex` | partial / bake |
| Main 2nd / 3rd | `_UseMain2ndTex`, `_Color2nd`, `_Main2ndTex`, dissolve on layer | bake |
| Alpha mask | `_AlphaMask`, `_AlphaMaskMode` | no |
| Normal 2nd | `_UseBump2ndMap`, `_Bump2ndMap` | no |
| Anisotropy | `_UseAnisotropy`, `_AnisotropyScale`, … | no |
| Backlight | `_UseBacklight`, `_BacklightColor`, … | no |
| Shadow (extra) | `_ShadowBorderMask`, `_Shadow3rdColor`, `_ShadowAOShift`, … | partial |
| Rim shade | `_UseRimShade`, `_RimShadeColor`, … | no |
| Reflection | `_UseReflection`, `_Smoothness`, `_Metallic`, … | no |
| MatCap / MatCap 2nd | `_MatCapBlend`, `_UseMatCap2nd`, … | partial (`_SphereAdd`) |
| Rim (extra) | `_RimMainStrength`, `_RimBlendMode`, … | partial |
| **Glitter** | `_UseGlitter`, `_GlitterColor`, `_GlitterParams1`, … | no |
| Emission / 2nd | `_EmissionBlink`, `_UseEmission2nd`, gradation, … | partial |
| **Parallax** | `_UseParallax`, `_UsePOM`, `_ParallaxMap`, `_Parallax` | no |
| Distance fade | `_DistanceFade`, `_DistanceFadeMode`, … | no |
| AudioLink | `_UseAudioLink`, `_AudioLinkMask`, … | no |
| Dissolve | `_DissolveMask`, `_DissolveParams`, … | no |
| ID mask / UDIM | `_IDMask1`…`_IDMask8`, `_UDIMDiscardMode`, … | no |
| VRChat | `_Ramp` | no |
| For Multi | `_UseClippingCanceller`, `_AsOverlay` | no |

**Excluded** from these three catalog files (use **Custom…** or a future outline shader
row): Outline + Outline Advanced, Tessellation, Advanced render state (`_Cull`,
`_SrcBlend`, stencil, …), `_TransparentMode`, `_UseOutline`.

Catalog JSON defaults follow ShaderLab where useful. **Add Common Props** still only
batch-adds `common: true` rows. Feature toggles in `enableToggles` (shadow, rim,
emission, glitter, parallax, main 2nd/3rd, …) default to `1` when added via scaffold
(ShaderLab often ships `0`).

## lilToon ↔ MToon conversion (upstream)

Official lilToon ships **lilToon → MToon** only (optimize / convert in the lilToon
inspector: 「MToon(VRM)に変換」). Implementation:
[`CreateMToonMaterial`](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Editor/lilInspector/lilMaterialConvertUtility.cs)
in `lilMaterialConvertUtility.cs`. Target shader: `VRM/MToon`
(`lilShaderManager.mtoon`). Docs note compatible parameters only; look is not 1:1.

There is **no** first-party **MToon → lilToon** convert in lilToon. Community tools exist
separately. For VRMXT `bindings` (MToon sources → lil targets) use the **inverse** of the
table below.

### Official map (lilToon → MToon)

Non-normative summary of `CreateMToonMaterial` when the matching lil feature is on:

| lilToon | → MToon (`VRM/MToon`) | Notes |
|---------|----------------------|-------|
| `_Color` | `_Color` | Clamped |
| `_MainTex` (often baked) | `_MainTex` | Bake may fold layers / HSVG |
| `_MainTex_ScrollRotate` | `_UvAnimScrollX/Y`, `_UvAnimRotation` | Packing differs |
| `_BumpMap` / `_BumpScale` | `_BumpMap` / `_BumpScale` | If `_UseBumpMap` |
| `_ShadowColor`, `_ShadowStrength`, `_ShadowColorTex` | `_ShadeColor`, `_ShadeTexture` | May bake shadow into tex; else strength-modulated color |
| `_ShadowBorder`, `_ShadowBlur` | `_ShadeShift`, `_ShadeToony` | **Derived** (see formula) |
| `_ShadowBorderMask` | `_ShadingGradeTexture` | With `_ShadingGradeRate` = 1 |
| `_RimColor`, `_RimColorTex`, `_RimEnableLighting` | `_RimColor`, `_RimTexture`, `_RimLightingMix` | |
| `_RimFresnelPower`, `_RimBlur`, `_RimBorder` | `_RimFresnelPower`, `_RimLift` | Derived from border/blur/power |
| `_EmissionColor`, `_EmissionMap` | `_EmissionColor`, `_EmissionMap` | If `_UseEmission` |
| `_MatCapTex` (baked) | `_SphereAdd` | If `_UseMatCap` and blend mode allows |
| Outline width/color/mask | `_OutlineWidth*`, `_OutlineColor` | Outline shader modes only |

**Shade shift / toony formula** (lil → MToon), from upstream:

```text
shadeShift = clamp01(shadowBorder - shadowBlur * 0.5) * 2 - 1
shadeToony = (shadeShift == 1)
  ? 1
  : (2 - clamp01(shadowBorder + shadowBlur * 0.5) * 2) / (1 - shadeShift)
```

Inverse (MToon → lil border/blur) is **TBD**; do not treat `_ShadowBorder` =
`shadingShiftFactor` as exact.

### Suggested VRMXT bindings (MToon → lilToon)

[VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md) `bindings` sources are
the shade set only. Invert the shadow rows above for defaults:

| MToon `source` | lilToon `target` | `targetType` | Notes |
|----------------|------------------|--------------|-------|
| `shadeColorFactor` | `_ShadowColor` | `vector` | Matches convert’s shade ↔ shadow color pairing |
| `shadeMultiplyTexture` | `_ShadowColorTex` | `texture` | Matches `_ShadeTexture` ↔ shadow color tex (bake path aside) |
| `shadingShiftFactor` | `_ShadowBorder` | `scalar` | Approximate until inverse formula ships |
| `shadingToonyFactor` | `_ShadowBlur` | `scalar` | Approximate; coupled with border in convert |
| `shadingShiftTexture` | `_ShadowBorderMask` | `texture` | Aligns with `_ShadingGradeTexture` mapping |
| `shadingShiftTexture.scale` | TBD | `scalar` | No clear single lil twin in convert |
| `giEqualizationFactor` | `_ShadowEnvStrength` | `scalar` | Not in `CreateMToonMaterial`; weak / optional |

When emitting these bindings, also set `_UseShadow` = `1` via `properties` (literal).
Binding alone does not flip `[lilToggle]` enables.

Rim / emission / matcap appear in the **lil → MToon** convert but are **not** in the
current VRMXT MToon binding source list. Keep them as catalog `properties` only unless
the base spec adds sources.

Glitter, parallax, anisotropy, AudioLink, dissolve, and most other extended catalog rows
are **lilToon-only** (not in `CreateMToonMaterial`). Authors add them via catalog
**Add**; values round-trip in `properties[]` without MToon `bindings`.

## Upstream pin

| Item | Value |
|------|-------|
| Repository | https://github.com/lilxyzw/lilToon |
| Tag | `2.3.4` |
| Commit | `252fd8cfc46106d4967e95b3f2c788418502f227` |
| Opaque source | `Assets/lilToon/Shader/lts.shader` |
| Cutout source | `Assets/lilToon/Shader/lts_cutout.shader` |
| Transparent source | `Assets/lilToon/Shader/lts_trans.shader` |
| Convert reference | `Assets/lilToon/Editor/lilInspector/lilMaterialConvertUtility.cs` (`CreateMToonMaterial`) |
| `Shader.Find` table | `Assets/lilToon/Editor/lilShaderManager.cs` |

Release: https://github.com/lilxyzw/lilToon/releases/tag/2.3.4

## Open questions

- [ ] URP smoke check on pin `2.3.4` (Built-in assumed from ShaderLab extract)
- [ ] When to add `hdrp` to lilToon `supportedVariants` (after HDRP smoke test)
- [ ] Whether to ship example multi-slot `builtin` + `urp` fixtures with the same
      `shaderName`
- [ ] Derive inverse border/blur from MToon shift/toony (or document “approx only”)
- [ ] Keep or drop `giEqualizationFactor` → `_ShadowEnvStrength`
- [ ] Whether outline shaders are in scope
- [ ] Whether Blender should offer a “suggested bindings from MToon” preset using this table

## Related

- Index: [Materials Override Catalogs](../materials-override-catalogs.md)
- Sibling (Warudo pin 1.10.3): [Unity lilToon Warudo Catalog](unity-liltoon-warudo.md)
- Sibling: [Unity Poiyomi Catalog](unity-poiyomi.md)
- Blender authoring: [Blender VRMXT materials override](../../implementations/blender-vrmxt.md#materials-override)
- Unity apply: [UniVRMXT materials override](../../implementations/univrm-vrmxt.md#materials-override)
- Upstream convert: [lilMaterialConvertUtility.cs](https://github.com/lilxyzw/lilToon/blob/2.3.4/Assets/lilToon/Editor/lilInspector/lilMaterialConvertUtility.cs)
