---
title: Unity VRMXT Test Override Catalog
aliases:
  - VRMXT TestOverride catalog
  - Test Materials for Overrides catalog
tags:
  - extended-vrm
  - reference/materials-override
  - reference/unity-shader
  - compatibility/vrm1
type: reference
status: draft
---

# Unity VRMXT Test Override Catalog

Authoring catalog for UniVRMXT **Test Materials for Overrides** under
[VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md). Index and shared
schema: [Materials Override Catalogs](materials-override-catalogs.md).

Non-normative. Small fixture for Blender / UniVRMXT authoring UI — not a production
shader family.

## Identity

| Field | Built-in | URP |
|-------|----------|-----|
| `engine` | `unity` | `unity` |
| `idType` | `shaderName` | `shaderName` |
| `shaderName` | `VRMXT/Samples/TestOverrideBuiltin` | `VRMXT/Samples/TestOverrideURP` |
| Catalog JSON | [`data/unity-vrmxt-test-override-builtin.json`](data/unity-vrmxt-test-override-builtin.json) | [`data/unity-vrmxt-test-override-urp.json`](data/unity-vrmxt-test-override-urp.json) |
| `supportedVariants` | `builtin` | `urp` |
| Default `_Color` | green `(0,1,0,1)` | yellow `(1,1,0,1)` |

Source (UniVRMXT sample package):

- `Samples~/TestMaterialsForOverrides/Shaders/VrmxtTestOverrideBuiltin.shader`
- `Samples~/TestMaterialsForOverrides/Shaders/VrmxtTestOverrideURP.shader`

Property lists match. Only `shaderName`, `displayName`, `defaultVariant`,
`supportedVariants`, and `_Color` default differ.

### Provider (advisory)

| Field | Value |
|-------|-------|
| `provider.id` | `com.miramocha.univrmxt` |
| `provider.version` | `0.1.0` (sample examples) |

### Render pipeline support

| Pipeline | Catalog entry shown |
|----------|---------------------|
| Built-in (`builtin`) | VRMXT Test Override (Built-in) |
| URP (`urp`) | VRMXT Test Override (URP) |
| HDRP (`hdrp`) | none (Custom only) |

One catalog file per `shaderName`. Multi-slot: store `(unity, builtin)` and
`(unity, urp)` siblings with the matching sample shader per
[UniVRM Materials Override](../../implementations/univrm-materials-override.md).

## Curated properties

All 11 ShaderLab slots are `common: true` so **Add Common Props** fills a full test
override in one click.

| Name | Catalog `type` | Notes |
|------|----------------|-------|
| `_MainTex` | `texture` | Albedo sample |
| `_Color` | `vector` | Tint × `_MainTex` |
| `_ShadeColor` | `vector` | Binding target (`shadeColorFactor`) |
| `_ShadeTex` | `texture` | Binding target (`shadeMultiplyTexture`) |
| `_ShadingShiftFactor` | `scalar` | Binding target |
| `_ShadingShiftTex` | `texture` | Binding target |
| `_ShadingShiftTexScale` | `scalar` | Binding target (`shadingShiftTexture.scale`) |
| `_ShadingToonyFactor` | `scalar` | Binding target |
| `_GiEqualizationFactor` | `scalar` | Binding target |
| `_OutlineWidth` | `scalar` | Unbound sample property |
| `_USE_RIM_LIGHT` | `shaderFeature` | Keyword from `[Toggle(_USE_RIM_LIGHT)] _UseRimLight`; export name is the keyword, not `_UseRimLight` |

Texture rows omit `default` (same as lilToon catalogs).

Binding pairs live in authoring UI / example JSON
(`Samples~/TestMaterialsForOverrides/example-override-*.json`), not in catalog JSON.

## Upstream pin

| Item | Value |
|------|-------|
| Package | UniVRMXT `Samples~/TestMaterialsForOverrides` |
| Pin | track UniVRMXT sample revision when re-vendoring |

## Related

- Index: [Materials Override Catalogs](materials-override-catalogs.md)
- Sample README: UniVRMXT `Samples~/TestMaterialsForOverrides/README.md`
- Blender authoring: [Blender Materials Override](../../implementations/blender-materials-override.md)
- Unity apply: [UniVRM Materials Override](../../implementations/univrm-materials-override.md)
