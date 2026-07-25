---
title: Warudo Poiyomi BIRP Variants
aliases:
  - Poiyomi Warudo keyword warm
  - Poiyomi BIRP multi_compile cut
tags:
  - extended-vrm
  - implementation/warudo
  - reference/unity-shader
  - reference/materials-override
  - compatibility/warudo
type: reference
status: draft
---

# Warudo Poiyomi BIRP Variants

Reference for shader variant cost, SVC prewarm, and BIRP `multi_compile` cuts on the
Warudo Poiyomi Shader VRMXT Plugin (Built-in RP).

Non-normative. Companion to [Unity Poiyomi Catalog](catalogs/unity-poiyomi.md) and
the cross-plugin warm overview [Warudo Material Warm-Up](warudo-material-warmup.md).
Upstream pin: Poiyomi Toon **9.3.64**, ShaderLab name `.poiyomi/Poiyomi Toon`.

This note covers the BIRP plugin:

| Plugin id | Mod folder |
|-----------|------------|
| `mira.shaders.poiyomi.birp` | `Warudo Shader Plugins/Assets/PoiyomiShaderPluginBirp/` |

## Scope

- Record Warudo host rendering facts that bound prewarm `PassType` lists.
- Quantify effect-keyword product and observed / expected Base compile size.
- Compare MToon10 / lilToon / Poiyomi keyword strategies for Warudo.
- Document the `multi_compile` keep set sized for lilToon-class avatar looks.
- Document vendor cuts already applied (matcaps, Lil Fur / World alts).
- State that supported features must not require third-party host plugins (e.g. AudioLink).
- Confirm rule 27 does not cut effect `multi_compile` axes (third-party tokens already `shader_feature`).
- Apply lil-parity `multi_compile` cut (6 keep axes) and re-export guidance.

This note does not change normative materials-override schema. Pragma edits apply only
after patching vendored `Poiyomi Toon.shader` and re-exporting the UMod.

## Warudo host observations

Probe: Playground `PoiyomiPassProbeAsset` (2026-07-24). Compile-check copy:
`VRMXT Plugin for Warudo/Assets/TestPlugin/PoiyomiPassProbeAsset.cs`.

| Setting | Observed |
|---------|----------|
| Render pipeline | Built-in (`GraphicsSettings.currentRenderPipeline` null) |
| Camera `actualRenderingPath` | Forward (three cameras) |
| Shadows | `All` |
| `pixelLightCount` | 8 |
| Realtime reflection probes | true |

`Shader.Find(".poiyomi/…")` returns null after UMod load. Materials still bind the
loaded ShaderLab name.

## ShaderLab passes

On an applied `.poiyomi/Poiyomi Toon` material:

| Index | Name | LightMode |
|------:|------|-----------|
| 0 | EarlyZ | ForwardBase |
| 1 | Base | ForwardBase |
| 2 | Add | ForwardAdd |
| 3 | Outline | ForwardBase |
| 4 | ShadowCaster | ShadowCaster |

Warudo Forward draws these five when enabled. This Toon file has no Deferred, Meta, or
MotionVectors passes.

## Prewarm PassTypes (applied)

`WarmPassTypes` are limited to:

| PassType | Rationale |
|----------|-----------|
| `ForwardBase` | EarlyZ, Base, Outline |
| `ForwardAdd` | Pixel lights (`pixelLightCount=8`) |
| `ShadowCaster` | `shadows=All` |

Removed from SVC warm: Deferred, Meta, Normal, Vertex, MotionVectors.

Expected effect: about two-thirds fewer SVC warm entries. This does not change the
shader’s `#pragma multi_compile` product at UMod or editor cook time.

## Pragma scale

Approximate counts on `Poiyomi Toon.shader` (feature / multi_compile pragmas):

| Metric | Approx |
|--------|--------|
| Unique keyword tokens | 113 |
| Unique pragma line strings | 102 |
| Pragma lines across passes (duplicated) | 401 |

### Effect `multi_compile` product

| SKU | Effect axes | Product per Base (before Unity megas) |
|-----|-------------|----------------------------------------|
| Pre-cut (historical) | twelve: keep six below plus `_SUNDISK_HIGH_QUALITY`, `POI_PATHING`, `GRAIN`, `EFFECT_BUMP`, `POI_PARALLAX`, `POI_SUBSURFACESCATTERING` | \(2^{12}\) = 4096 |
| Current (lil-parity) | `_EMISSION`, `POI_EMISSION_1`, `_SUNDISK_SIMPLE`, `POI_MATCAP0`, `POI_BACKLIGHT`, `DISTORT` | \(2^{6}\) = 64 |

Demoted from guaranteed set to `shader_feature` (+ SVC warm):
`_SUNDISK_HIGH_QUALITY`, `POI_PATHING`, `GRAIN`, `EFFECT_BUMP`, `POI_PARALLAX`,
`POI_SUBSURFACESCATTERING`.

Unity also expands `multi_compile_fwdbase`, `fwdadd_fullshadows`, fog,
`VERTEXLIGHT_ON`, and instancing. Pre-cut Base cook was **65536** fragment
programs (\(2^{16}\) ≈ 4096 × 16). After the lil-parity cut, expect order **~1024** fp
with the same mega factor (64 × 16). Re-measure after BIRP UMod re-export.

### Guaranteed vs SVC

| Class | Mechanism | Examples |
|-------|-----------|----------|
| Guaranteed | `multi_compile` / `multi_compile_local` | Six lil-parity axes above |
| SVC extras | `shader_feature` (warm subsets) | Demoted six + `POI_MATCAP1–3`, `POI_EMISSION_2/3`, `POI_CLEARCOAT`, `MOCHIE_PBR`, `POI_ANISOTROPICS`, `PROP_DECALMASK`, `GEOM_TYPE_MESH` |
| Out of Warudo v1 intent | leave as `shader_feature` or omit | AudioLink, mirror, LTCGI, video, voronoi, real post stack |

Runtime plugin settings adjust warm lists and material keywords only. Cook size follows
the Toon.shader pragma set; re-export the BIRP UMod after pragma edits.

## Axis audit vs host dependency (rule 27)

**Verdict:** rule 27 does **not** remove any of the twelve historical effect
`multi_compile` axes. Every third-party / world-stack integration below is already
`#pragma shader_feature` / `shader_feature_local` only — stubs that do not multiply
the Base cook product.

| Token | Mechanism | Host dep? | Axis impact |
|-------|-----------|-----------|-------------|
| `POI_AUDIOLINK`, `POI_AL_DECAL`, `POI_AL_VOLUMECOLOR` | `shader_feature_local` | AudioLink package | none on cook |
| `POI_LTCGI` | `shader_feature_local` | LTCGI | none |
| `POIBS_ENABLE`, `POIBS_BLOOMFOG`, `BSSBLOOMFOGTYPE_HEIGHT` | `shader_feature_local` | Beat Saber | none |
| `POI_MIRROR`, `POI_MIRROR_TEXTURE` | `shader_feature_local` | mirror / camera stack | none |
| `POI_VIDEO_EFFECTS` | `shader_feature_local` | video player / RT | none |
| `POI_VORONOI` | `shader_feature_local` | self-contained FX; leave unsupported for Warudo catalogs | none |
| VRC Light Volumes (`_UdonLightVolume*`) | float toggle + always-linked SH helpers when enabled | VRC Light Volumes | **not** a `multi_compile` axis |

Twelve historical axes (pre-cut); lil-parity keep applied on Toon.shader:

| Axis | Self-contained? | lil-parity cut |
|------|-----------------|----------------|
| `_EMISSION` | yes | **keep** (`multi_compile`) |
| `POI_EMISSION_1` | yes | **keep** |
| `_SUNDISK_SIMPLE` | yes | **keep** |
| `POI_MATCAP0` | yes | **keep** |
| `POI_BACKLIGHT` | yes | **keep** |
| `DISTORT` (dissolve) | yes | **keep** (6th axis) |
| `_SUNDISK_HIGH_QUALITY` (flipbook) | yes | demoted → `shader_feature` + SVC |
| `POI_PATHING` | yes | demoted |
| `GRAIN` (depth / touch FX) | uses `_CameraDepthTexture` (Unity API, not a package) | demoted — weak without depth on Warudo cams |
| `EFFECT_BUMP` (text) | yes | demoted |
| `POI_PARALLAX` | yes | demoted |
| `POI_SUBSURFACESCATTERING` | yes | demoted |

Rule 27 still does not change this list; cook reduction came from the lil-parity demote.

**Warm-list cleanup (applied):** `RequiredWarmKeywords` and
`PoiyomiWarmGlitterEmission.mat` no longer enable `BSSBLOOMFOGTYPE_HEIGHT` (Beat Saber).
Shader stubs remain `shader_feature_local`; SVC warm no longer keeps that variant.

## Host dependency policy

Supported Warudo / VRMXT materials-override features for this plugin family MUST run
with only:

- Unity Built-in RP APIs available in the Warudo player;
- the shipped Poiyomi (or lilToon) shader UMod;
- UniVRMXT / VRMXT Plugin for Warudo first-party code.

They MUST NOT require a separate third-party Unity package, world prefab, or Udon
stack at runtime for the feature to be considered supported.

| Integration | Third-party? | Notes |
|-------------|--------------|-------|
| **AudioLink** (`POI_AUDIOLINK`, lil `AUDIOLINK*`) | **Yes** | Community package [llealloo/audiolink](https://github.com/llealloo/audiolink) (`com.llealloo.audiolink`). Not a Unity module. Needs AudioLink CRT / `_AudioTexture` (typically VRChat curated VPM). Out of supported set. |
| LTCGI | Yes | World/light baking package; not Warudo stock. |
| VRC Light Volumes | Yes | VRChat ecosystem; lil defines optional without package, still host-dependent. |
| Beat Saber / bloomfog (`POIBS_*`, `BSSBLOOMFOGTYPE_HEIGHT`) | Yes | Game-specific; not Warudo. |
| Mirror / video / voronoi stacks as world hooks | Often yes | Treat as unsupported unless self-contained in the shader UMod alone. |

ShaderLab may keep `#pragma shader_feature` stubs for these tokens so foreign mats do
not pink-error. Catalogs, Manager autocomplete guidance, `multi_compile` keep
lists, and “supported” override docs MUST NOT list them as Warudo-supported features.
Normative: [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
rules 27–28.

## Comparison: MToon10, lilToon, Poiyomi BIRP

| | MToon10 (`VRM10/MToon10`) | lilToon 1.10.3 (Warudo BIRP) | Poiyomi BIRP (current) |
|--|--------------------------|------------------------------|-------------------------|
| Role | VRM stock toon | Rich avatar toon | Rich avatar toon + FX |
| Main sources | ~8 KB shader | ~55 KB `lts.shader` shell + hidden `ltspass_*`; ~65 files / ~3 MB | ~2.7 MB `Poiyomi Toon.shader` |
| Feature enable | Few map keywords; mostly floats/textures | `#define LIL_FEATURE_*` plus material `_Use…` toggles | Many `#pragma` keywords |
| Effect `multi_compile` axes | ~5 (maps / alpha / outline modes) | 0 for features | **6** (lil-parity) |
| Observed Base cook | Small | Lighting megas only | pre-cut ~65536 fp; post-cut ~1024 expected |

lilToon and Poiyomi both expose matcap, dual emission, glitter, backlight, rim,
reflection, and related avatar FX. lilToon does not build a \(2^{N}\) effect-keyword
matrix; Poiyomi BIRP does when those FX are promoted to `multi_compile`.

“lilToon parity” here means covering the same class of Warudo avatar looks. It does not
require adopting lilToon’s `#define` pipeline.

### Feature coverage

| Look / FX | MToon10 | lilToon | Poiyomi |
|-----------|---------|---------|---------|
| Base shade / toony | floats | `SHADOW`, rimshade | lighting modes / `VIGNETTE_MASKED` (`shader_feature`) |
| Normal map | `_NORMALMAP` | `NORMAL_1ST` / `2ND` | properties / features |
| Emission 1 | `_MTOON_EMISSIVEMAP` | `EMISSION_1ST` | `_EMISSION` |
| Emission 2 | — | `EMISSION_2ND` | `POI_EMISSION_1` (slots 2–3: SVC) |
| Matcap 1 | matcap factor/tex | `MATCAP` | `POI_MATCAP0` |
| Matcap 2 | — | `MATCAP_2ND` | `POI_MATCAP1` (`shader_feature` / SVC) |
| Glitter | — | `GLITTER` | `_SUNDISK_SIMPLE` (HQ separate) |
| Backlight | — | `BACKLIGHT` | `POI_BACKLIGHT` |
| Rim | rim maps/factors | `RIMLIGHT` | rim styles (`shader_feature`) |
| Reflection / aniso | — | `REFLECTION`, `ANISOTROPY` | `MOCHIE_PBR`, `POI_ANISOTROPICS` (SVC) |
| Clear coat | — | via reflection stack | `POI_CLEARCOAT` (SVC) |
| Parallax / POM | — | `PARALLAX`, `POM` | `POI_PARALLAX` |
| Dissolve / decals / layers | — | `DISSOLVE`, `DECAL`, main 2nd/3rd | mostly `shader_feature` / properties |
| UV distortion | UV anim floats | animate main UV | `DISTORT` |
| Subsurface | — | no strong match | `POI_SUBSURFACESCATTERING` |
| Pathing | — | — | `POI_PATHING` |
| Depth / touch FX | — | — | `GRAIN`, `EFFECT_BUMP` |
| AudioLink | — | `AUDIOLINK*` | unsupported (third-party host; see policy) |
| Fur | — | separate fur shaders | deferred separate plugin |

## `multi_compile` cut (lilToon parity)

**Status:** Applied on BIRP `Poiyomi Toon.shader` (plugin **1.0.1**). Re-export BIRP UMod
to pick up cook-size change.

Keep as `multi_compile` / `multi_compile_local` (lil-class, hitch-sensitive):

| Keyword | lilToon counterpart |
|---------|---------------------|
| `_EMISSION` | `EMISSION_1ST` |
| `POI_EMISSION_1` | `EMISSION_2ND` |
| `_SUNDISK_SIMPLE` | `GLITTER` |
| `POI_MATCAP0` | `MATCAP` |
| `POI_BACKLIGHT` | `BACKLIGHT` |
| `DISTORT` | dissolve (lil `DISSOLVE`) |

| Axes | Effect product / Base | Order with ×16 Unity megas |
|------|------------------------|----------------------------|
| 6 | 64 | ~1024 |

Demoted to `shader_feature` (SVC-warmed in BIRP plugin):

| Keyword | Notes |
|---------|-------|
| `_SUNDISK_HIGH_QUALITY` | Flipbook / HQ glitter path; lil uses one glitter path |
| `POI_PATHING` | No lil counterpart |
| `GRAIN` | Depth / touch glow; weak on Warudo |
| `EFFECT_BUMP` | Text FX; drop from guaranteed set |
| `POI_PARALLAX` | lil has parallax/POM; available without guaranteeing |
| `POI_SUBSURFACESCATTERING` | Weak lil map |

Do not promote to `multi_compile`: matcap 1–3, emission 2–3, clear coat, Mochie PBR,
anisotropy, decal mask, AudioLink (third-party host), and related `shader_feature`
tokens.

Relative to twelve-axis historical: effect product 4096 → 64 (64× before megas).
Observed Base ~65536 fp → order ~1024 with the same mega factor.

Upstream docs grouping (emission, glitter, matcap, backlight, UV modifiers, pathing,
depth FX): [Poiyomi home](https://www.poiyomi.com/),
[sitemap](https://www.poiyomi.com/sitemap.xml),
[9.3 modular system](https://www.poiyomi.com/9.3/modular-shader-system/).

## Unity PP keyword name traps

Poiyomi reuses Unity post-processing keyword strings for avatar feature toggles:

| Keyword | Meaning in Poiyomi |
|---------|-------------------|
| `POSTPROCESS` | Post Processing panel |
| `POIBS_*` / `BSSBLOOMFOGTYPE_HEIGHT` | Beat Saber / bloomfog |
| `GRAIN` | Depth FX / touch glow |
| `VIGNETTE` | RGB Mask |
| `VIGNETTE_MASKED` | Shading enable |
| `COLOR_GRADING_HDR` | Main color adjust |
| `COLOR_GRADING_HDR_3D` | Matcap 2 |
| `USER_LUT` | Distortion |
| `AUTO_EXPOSURE` | Vertex manipulations |
| `FINALPASS` | Detail maps |
| `DEPTH_OF_FIELD_COC_VIEW` | Decal 3 |

Material dumps that list `GRAIN`, `VIGNETTE_MASKED`, or `BSSBLOOMFOGTYPE_HEIGHT` are
reporting those toggles, not Warudo camera post-processing.

## Vendor tree cuts (applied)

### Textures

BIRP plugin vendored `_PoiyomiShaders/Textures/` under the BIRP mod folder.

`_Matcap` defaults to Unity `"white"`. UniVRMXT / avatar overrides supply matcap textures
when needed.

Removed `Textures/Matcaps/` (~6.1 MB). Remaining texture images ~3.7 MB. See BIRP
`VENDOR.md`.

### Alternate shaders

Primary: `.poiyomi/Poiyomi Toon`.

Still shipped: Early Outline, Grab Pass, Two Pass, Extras.

Deferred to a later plugin (removed from trees and `KnownShaderFiles`; excluded from
VRMXT Manager autocomplete in `VrmxtShaderInventory`):

| File | ShaderLab name |
|------|----------------|
| Lil Fur | `.poiyomi/Poiyomi Toon + Lil Fur` |
| Lil Fur Two Pass | `.poiyomi/Poiyomi Toon + Lil Fur Two Pass` |
| World | `.poiyomi/Poiyomi Toon World` |

Shader sources: ~22.7 MB → ~12.2 MB. Alternate removal does not reduce the main Toon
`multi_compile` product.

## Remaining prewarm work

| Item | Status |
|------|--------|
| `WarmPassTypes` → ForwardBase / ForwardAdd / ShadowCaster | Applied |
| Drop `BSSBLOOMFOGTYPE_HEIGHT` from warm keywords / warm `.mat` | Applied |
| Demote effect `multi_compile` to lil-parity 6 axes | Applied (re-export BIRP UMod) |
| Trim `BuildWarmKeywordSets` from live keyword census | Open |
| Drop Early Outline / Grab / Two Pass if unused | Open |
| Measure and possibly drop Blit/SetPass after SVC `WarmUp` | Open |
| Re-measure Base cook after lil-parity cut | Open |

## Debug tooling

| Location | Role |
|----------|------|
| `Warudo_Data/StreamingAssets/Playground/PoiyomiProbe/PoiyomiPassProbeAsset.cs` | Live Warudo probe |
| `VRMXT Plugin for Warudo/Assets/TestPlugin/PoiyomiPassProbeAsset.cs` | UMod compile check (Test Hello World plugin) |

Same asset type id on both copies: do not enable Playground and an exported TestPlugin
build together.

Useful follow-up measurements: union of live material `shaderKeywords`; Frame Debugger
or RenderDoc counts for EarlyZ / Outline / Add.

## Related apply notes (shipped)

- `ApplyUnityRenderStateFromMode`: `_Mode` → `renderQueue` / `RenderType` (Additive = 3000).
- Vector pans: `SetVector` rather than `SetColor` for scroll direction.
- BIRP: lil-parity `multi_compile` plus expanded SVC subsets.

## Related

- Exclusion inventory: [Warudo Poiyomi Exclusions](warudo-poiyomi-exclusions.md)
- Catalog: [Unity Poiyomi Catalog](catalogs/unity-poiyomi.md)
- lilToon Warudo pin: [Unity lilToon Warudo Catalog](catalogs/unity-liltoon-warudo.md)
- Upstream: [Poiyomi](https://www.poiyomi.com/), [Alternate versions](https://www.poiyomi.com/general/alt-versions)
- Plugin tree: `Warudo Shader Plugins/Assets/PoiyomiShaderPluginBirp/`
