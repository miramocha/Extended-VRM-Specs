---
title: Warudo Poiyomi Exclusions
aliases:
  - Poiyomi unsupported keywords
  - Poiyomi Warudo excluded features
tags:
  - extended-vrm
  - implementation/warudo
  - reference/unity-shader
  - reference/materials-override
  - compatibility/warudo
type: reference
status: draft
---

# Warudo Poiyomi Exclusions

Inventory of Poiyomi **features, ShaderLab variants, and keywords** excluded from the
Warudo BIRP shipping set (plugin `mira.shaders.poiyomi.birp`, pin **9.3.64**,
`.poiyomi/Poiyomi Toon`).

Non-normative. Cook / keep / warm mechanics:
[Warudo Poiyomi BIRP Variants](warudo-poiyomi-birp-variants.md). Catalog identity:
[Unity Poiyomi Catalog](catalogs/unity-poiyomi.md). Host warm overview:
[Warudo Material Warm-Up](warudo-material-warmup.md).

Source of truth in code: `PoiyomiShaderPluginBirp.cs`
(`MultiCompileGuaranteedKeywords`, `SvcWarmExtraKeywords`, `SvcWarmLightingKeywords`,
`WarmPassTypes`) and BIRP `VENDOR.md`.

## Exclusion kinds

| Kind | Meaning |
|------|---------|
| `unsupported` | Not a Warudo-supported override feature (catalogs / Manager guidance omit). Shader stubs may remain so foreign mats do not pink-error. |
| `deferred-shader` | Alternate ShaderLab not shipped in this UMod; Manager autocomplete filters them. |
| `demoted-mc` | Removed from hitch-safe `multi_compile` keep set; still `shader_feature` (+ usually SVC-warmed). |
| `not-warmed` | Still in Toon.shader as `shader_feature` / `shader_feature_local`, but **not** in BIRP SVC warm lists — first-use hitch or strip risk. |
| `vendor-stripped` | Deleted from the vendored tree for UMod size / asmdef policy. |
| `pass-skipped` | Unity `PassType` omitted from `ShaderVariantCollection` warm. |

“Excluded from supported” ≠ “deleted from the shader.” Most `unsupported` tokens stay as
local stubs.

## Deferred ShaderLab variants

| ShaderLab name | Kind | Notes |
|----------------|------|-------|
| `.poiyomi/Poiyomi Toon + Lil Fur` | `deferred-shader` | Separate plugin later |
| `.poiyomi/Poiyomi Toon + Lil Fur Two Pass` | `deferred-shader` | Same |
| `.poiyomi/Poiyomi Toon World` | `deferred-shader` | Same |

Still shipped (not excluded): Early Outline, Grab Pass, Two Pass, Extras. Dropping those
from warm is still open — see BIRP variants “Remaining prewarm work.”

Pro / commercial URP lines: out of scope until a documented `Shader.Find` name exists.

## Host-dependent / unsupported keywords

These MUST NOT appear as Warudo-supported materials-override features. Normative text
from [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md):

> 27. A supporting implementation that documents, catalogs, or otherwise presents a shader
> or a discrete shader capability (including a `shaderFeature` / keyword) as **supported**
> for this extension MUST ensure that capability works using only:
> - host engine APIs available to that consumer; and
> - shaders, materials, and packages that consumer ships, including first-party VRMXT
>   packages it distributes.
> It MUST NOT present a capability as supported when correct runtime behavior depends on
> an additional third-party plugin, package, world prefab, or equivalent host stack
> outside that shipped set. Non-normative examples: AudioLink (`com.llealloo.audiolink`),
> LTCGI, VRChat Light Volumes, Beat Saber bloomfog hooks.
>
> 28. Files MAY still emit `properties`, `bindings`, or `shaderFeature` entries that name
> host-dependent capabilities under rule 27. Supporting implementations MUST keep
> following rules 11–12 and 24 (ignore unresolvable entries; stock import when required
> assets are missing). They MUST NOT require those third-party stacks to load the file.

| Token / family | Kind | Why |
|----------------|------|-----|
| `POI_AUDIOLINK`, `POI_AL_DECAL`, `POI_AL_VOLUMECOLOR` | `unsupported` | Needs [AudioLink](https://github.com/llealloo/audiolink) (`com.llealloo.audiolink`) / `_AudioTexture` |
| `POI_LTCGI` | `unsupported` | LTCGI world / light package |
| `POIBS_ENABLE`, `POIBS_BLOOMFOG`, `BSSBLOOMFOGTYPE_HEIGHT` | `unsupported` | Beat Saber / bloomfog; also dropped from warm lists |
| `POI_MIRROR`, `POI_MIRROR_TEXTURE` | `unsupported` | Mirror / camera stack |
| `POI_VIDEO_EFFECTS` | `unsupported` | Video player / RT |
| `POI_VORONOI` | `unsupported` | Self-contained FX; left unsupported for Warudo catalogs |
| VRC Light Volumes (`_UdonLightVolume*`) | `unsupported` | Host float toggle; not a `multi_compile` axis |

Mechanism for the keyword rows: already `shader_feature` / `shader_feature_local` in
upstream Toon — they never multiplied the Base cook product. Exclusion is **policy +
catalog**, not a cook cut.

## Demoted from `multi_compile`

Historical twelve-axis effect product → six keep axes. Demoted tokens:

| Keyword | Kind | Panel / look | SVC warm? |
|---------|------|--------------|-----------|
| `_SUNDISK_HIGH_QUALITY` | `demoted-mc` | Flipbook / HQ glitter path | yes |
| `POI_PATHING` | `demoted-mc` | Pathing | yes |
| `GRAIN` | `demoted-mc` | Depth / touch glow (PP name trap) | yes |
| `EFFECT_BUMP` | `demoted-mc` | Text FX | yes |
| `POI_PARALLAX` | `demoted-mc` | Parallax / POM | yes |
| `POI_SUBSURFACESCATTERING` | `demoted-mc` | SSS | yes |

Keep set (not excluded): `_EMISSION`, `POI_EMISSION_1`, `_SUNDISK_SIMPLE`,
`POI_MATCAP0`, `POI_BACKLIGHT`, `DISTORT`.

## Avatar extras: warmed vs not warmed

### In SVC warm (`SvcWarmExtraKeywords` / lighting)

These are **not** hitch-guaranteed (`shader_feature` only) but are intentionally warmed:

| Keyword | Notes |
|---------|-------|
| `POI_MATCAP1`, `POI_MATCAP2`, `POI_MATCAP3` | Extra matcaps |
| `POI_EMISSION_2`, `POI_EMISSION_3` | Emission slots 3–4 |
| `POI_CLEARCOAT`, `MOCHIE_PBR`, `POI_ANISOTROPICS` | Reflection stack |
| `PROP_DECALMASK`, `GEOM_TYPE_MESH` | Decal / geom helpers |
| `POI_BACKFACE`, `POI_STYLIZED_StylizedSpecular` | QuickCel-style extras |
| `_LIGHTINGMODE_SKIN`, `_LIGHTINGMODE_MULTILAYER_MATH` | Preset lighting modes (mutually exclusive vs FLAT) |

Plus the six `demoted-mc` rows above.

### Explicitly not warmed (representative)

Still present as stubs / features in Toon.shader; **not** listed in BIRP warm arrays.
Treat as `not-warmed` (and often also `unsupported` when host-dependent):

| Token / family | Also |
|----------------|------|
| `POI_AUDIOLINK`, `POI_AL_DECAL`, `POI_AL_VOLUMECOLOR` | `unsupported` |
| `POI_LTCGI` | `unsupported` |
| `POIBS_*`, `BSSBLOOMFOGTYPE_HEIGHT` | `unsupported` |
| `POI_MIRROR`, `POI_MIRROR_TEXTURE` | `unsupported` |
| `POI_VIDEO_EFFECTS`, `POI_VORONOI` | `unsupported` |
| `POI_RIM2` + non-Poiyomi rim styles (`_RIMSTYLE_UTS2`, `_RIMSTYLE_LILTOON`, …) | hitch risk if used |
| `_POI_DEPTH_RIMLIGHT` | hitch risk |
| `POI_UDIMDISCARD`, `POI_GLOBALMASK_TEXTURES` | hitch risk |
| `POI_BLACKLIGHTMASKING` | hitch risk |
| `POI_VERTEX_LOOKAT`, `POI_VERTEX_GLITCHING`, `POI_VERTEX_GLITCHING_TEXTURE` | hitch risk |
| `POI_DEPTHBULGE`, `POI_UZUMORE` | hitch risk |
| `POI_MATCAP*_CUSTOM_NORMAL` | hitch risk |
| `_CUBEMAP`, `GGX_ANISOTROPICS` | hitch risk |
| Other `_LIGHTINGMODE_*` beyond FLAT / SKIN / MULTILAYER_MATH | hitch risk |
| `_STOCHASTICMODE_HEXTILE`, `_STOCHASTICMODE_NONE` | warm mat uses DELIOT_HEITZ only |

This list is not exhaustive of every `PROP_*` / Thry toggle in the megashader. Anything
outside the keep + warm arrays is `not-warmed` by default.

## PassTypes skipped from SVC warm

| PassType | Kind | Reason |
|----------|------|--------|
| Deferred | `pass-skipped` | Warudo cameras Forward |
| Meta | `pass-skipped` | Not drawn |
| Normal / Vertex | `pass-skipped` | Not drawn |
| MotionVectors | `pass-skipped` | Not in this Toon pass set / not drawn |

Warmed: `ForwardBase`, `ForwardAdd`, `ShadowCaster`.

## Vendor tree stripped

| Item | Kind | Notes |
|------|------|-------|
| `Scripts/` (ThryEditor, poi-tools, Editor, `*.asmdef`) | `vendor-stripped` | Warudo mods cannot ship asmdefs |
| Legacy `Shaders/7.3` … `9.2` | `vendor-stripped` | Size |
| `Prefabs/`, `Presets/`, `Translators/` | `vendor-stripped` | Size |
| `Textures/Fur`, `Noise`, `Gifs`, `Fonts` | `vendor-stripped` | Size |
| `Textures/Matcaps/` | `vendor-stripped` | Avatars / overrides supply matcaps; `_Matcap` defaults to `"white"` |
| Lil Fur / World alt `.shader` files | `vendor-stripped` + `deferred-shader` | See above |

## Outline note

Outline is a separate ForwardBase pass (`POI_PASS_OUTLINE`), gated by float
`_EnableOutlines`, **not** a keep-axis keyword. It is not in the exclusion tables;
it works with the current BIRP warm without an extra effect keyword.

## Related

- Mechanics: [Warudo Poiyomi BIRP Variants](warudo-poiyomi-birp-variants.md)
- Catalog: [Unity Poiyomi Catalog](catalogs/unity-poiyomi.md)
- Warm layers: [Warudo Material Warm-Up](warudo-material-warmup.md)
- Plugin: `Warudo Shader Plugins/Assets/PoiyomiShaderPluginBirp/` (`VENDOR.md`)
- Upstream: [Poiyomi](https://www.poiyomi.com/), [alt versions](https://www.poiyomi.com/general/alt-versions)
