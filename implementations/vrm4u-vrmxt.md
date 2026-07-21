---
title: VRM4U VRMXT
aliases:
  - VRM4U Materials Override
  - VRMXT materials override for Unreal
tags:
  - extended-vrm
  - implementation/unreal
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# VRM4U VRMXT

Unreal consumer profile for Extended VRM through VRM4U. Current scope covers
[VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md).
A separate plugin can support wrapped runtime loads and post-processing. VRM4U
currently has no callback for custom material extensions during its normal conversion
flow.

## Supported features

| Extension | Status |
|-----------|--------|
| `VRMXT_materials_override` | Planned |

## Supported entry

The consumer considers all `overrides[]` where `engine` equals `unreal`. Selection uses
`material.variant` as this profile's refinement of the base-spec selection key
(rules 6–7). Sibling `unreal` entries can each name one blend/cull parent; a loader MAY
fold those siblings into a `UVrmImportMaterialSet` when talking to VRM4U's material-set
API.

### Profile properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `material.idType` | string | yes | `"resourcePath"` |
| `material.id` | string | yes | Resource path string for a parent material |
| `material.variant` | string | no (see Selection) | `opaque`, `opaqueTwoSided`, `translucent`, or `translucentTwoSided` |
| `material.provider` | object | no | Unreal plugin hint |
| `material.provider.id` | string | yes if `provider` present | Unreal plugin name |
| `material.provider.version` | string | no | Exporter-observed plugin version |

`material.id` is an engine resource path. In Unreal today that string is a soft object
path resolving to a `UMaterialInterface` parent. `provider` is advisory per base-spec
rules 18–21. This profile MUST NOT require a closed material registry. A consumer MAY
compare `provider` with the installed `.uplugin`; asset resolution determines support.
Catalog absence MUST NOT reject the file.

Authors need only the slots they care about (opaque-only is valid). Missing selected
slot or unresolved `id` → stock import for that material.

### Selection

- **One `unreal` entry:** `material.variant` MAY be omitted or empty. That entry matches
  any blend/cull combination derived from the glTF material.
- **Two or more `unreal` entries:** each MUST have a non-empty `material.variant` from
  the table below. Duplicate `(unreal, variant)` pairs are invalid under base-spec
  rule 6.
- Otherwise pick the entry whose `variant` matches core glTF material state:

| `alphaMode` | `doubleSided` | Select `variant` |
|-------------|---------------|------------------|
| `OPAQUE` | `false` | `opaque` |
| `OPAQUE` | `true` | `opaqueTwoSided` |
| `MASK` | `false` | `opaque` |
| `MASK` | `true` | `opaqueTwoSided` |
| `BLEND` | `false` | `translucent` |
| `BLEND` | `true` | `translucentTwoSided` |

If no entry matches, use stock VRM4U material behavior. The parent determines Unreal
blend and culling. VRM4U's current material-set API has no separate masked parent. A
parent used for `MASK` must preserve alpha cutoff through its own parameter contract;
otherwise the consumer falls back to the stock material.

### Example (single slot)

```json
{
  "engine": "unreal",
  "material": {
    "idType": "resourcePath",
    "id": "/ExampleMaterials/Materials/M_Skin_Opaque.M_Skin_Opaque",
    "variant": "opaque",
    "provider": {
      "id": "ExampleMaterials",
      "version": "1.0.0"
    }
  },
  "bindings": [
    {
      "source": "shadeColorFactor",
      "target": "mtoon_ShadeColor",
      "targetType": "vector"
    },
    {
      "source": "shadeMultiplyTexture",
      "target": "mtoon_tex_ShadeTexture",
      "targetType": "texture"
    },
    {
      "source": "shadingShiftFactor",
      "target": "mtoon_ShadeShift",
      "targetType": "scalar"
    },
    {
      "source": "shadingToonyFactor",
      "target": "mtoon_ShadeToony",
      "targetType": "scalar"
    }
  ],
  "properties": [
    {
      "name": "mtoon_UseRimLight",
      "type": "shaderFeature",
      "value": true
    }
  ]
}
```

### Example (opaque and translucent siblings)

```json
{
  "specVersion": "1.0",
  "overrides": [
    {
      "engine": "unreal",
      "material": {
        "idType": "resourcePath",
        "id": "/Game/Example/M_Skin_Opaque",
        "variant": "opaque"
      }
    },
    {
      "engine": "unreal",
      "material": {
        "idType": "resourcePath",
        "id": "/Game/Example/M_Skin_Translucent",
        "variant": "translucent"
      }
    }
  ]
}
```

`provider.id` is an Unreal plugin name.

## Variant survival

- Re-export and authoring MUST update only the `unreal` slot for the blend/cull state
  being authored (create the slot when missing).
- Sibling `unreal` entries for other variants MUST NOT be deleted or rewritten as a
  side effect.
- An exporter MAY set `variant` from glTF `alphaMode` / `doubleSided` only when creating
  a new slot that has no `variant` yet.

## Current VRM4U integration surface

VRM4U exposes material templates:

- `UVrmImportMaterialSet` stores opaque, opaque two-sided, translucent, and translucent
  two-sided parents.
- `UVrmAssetListObject` stores standard sets, `CustomSet`, and generated materials.
- `EVRMImportMaterialType::VRMIMT_Custom` selects the custom set.

These APIs configure a load globally. They do not inspect
`VRMXT_materials_override` or select a different set per glTF material.

VRM4U parses the complete GLB JSON into `VRMConverter::jsonData`, but the normal loader
keeps the converter on the stack and exposes no material-extension delegate. An optional
plugin using the stock loader must parse the GLB JSON independently.

## No-core-change implementation

A separate plugin can support the extension when it owns the VRM loading entry point:

1. Parse the GLB JSON and retain each material's `unreal` override entries.
2. Run the normal VRM4U load.
3. For each source material, select the matching sibling entry (Selection) and resolve
   `material.id`. A loader MAY also assemble sibling paths into a
   `UVrmImportMaterialSet` when that API is useful.
4. Create a material instance from that parent, then apply `properties`, then
   `bindings`.
5. Replace generated material references in `UVrmAssetListObject::Materials` and the
   skeletal mesh material slots.
6. Leave the original VRM4U material untouched when any step fails.

Editor integration can listen for post-import events and perform the same replacement.
This is post-processing; VRM4U already created its stock materials. Applications that
call VRM4U directly without the wrapper do not receive override support.

Editor imports normally create `UMaterialInstanceConstant` assets. Runtime wrappers
normally create `UMaterialInstanceDynamic` instances. A consumer must update the same
mesh slots and asset-list references that held the stock material.

Transparent integration into every existing VRM4U load path would require a future
VRM4U callback or material-factory hook. That hook is outside this specification.

## Bindings

VRM4U parent materials conventionally expose `mtoon_*` and `gltf_*` parameters.

| Source | Typical VRM4U target | `targetType` |
|--------|----------------------|--------------|
| `shadeColorFactor` | `mtoon_ShadeColor` | `vector` |
| `shadeMultiplyTexture` | `mtoon_tex_ShadeTexture` | `texture` |
| `shadingShiftFactor` | `mtoon_ShadeShift` | `scalar` |
| `shadingToonyFactor` | `mtoon_ShadeToony` | `scalar` |

`scalar`, `vector`, and `texture` use material-instance parameter setters. A
`shaderFeature` (an Unreal Material **Static Switch** parameter) may require a
material-instance-constant permutation rebuild and is not equivalent to a runtime
scalar parameter.

Current VRM4U conversion does not populate every MToon 1.0 field listed by the base
spec. The optional plugin must read those values from raw JSON when it supports them.

## Properties

`overrides[].properties` sets literal values on the resolved parent material instance
with no `VRMC_materials_mtoon` dependency (base-spec rules 22–26). `properties[].name`
is a parent material parameter name (conventionally `mtoon_*` or `gltf_*`, matching the
bindings table above); `type` selects the matching instance-parameter setter, reading
`value` (or `texture`) directly instead of a resolved MToon source.

The plugin applies `properties` before `bindings` per rule 23, so a `bindings` entry
wins if an authoring error targets the same parameter name. `shaderFeature` properties
carry the same `UMaterialInstanceConstant` permutation-rebuild caveat as `shaderFeature`
bindings.

## Packaging

- The plugin descriptor declares a dependency on `VRM4U` and can contain content.
- Runtime code depends on `VRM4U` and `VRM4ULoader`, not `VRM4UImporter`.
- Parent materials must be referenced so Unreal cooking retains them.
- Provider resolution may use `IPluginManager` and soft object paths.
- Runtime material loading needs validation for each packaged platform and VRM4U build.

The VRM file stores resource paths in `material.id` (`idType: "resourcePath"`); it does
not embed Unreal material assets. A supporting consumer MUST cook or otherwise include
any parent materials it intends to honor. Resolve the selected path at load time; on
miss, leave the stock VRM4U material (see Fallback). Remote download of material source
is out of scope for this profile.

## Fallback

Package absence requires no action: VRM4U ignores the unknown extension. With the package
installed, unknown providers, unresolved assets, missing selected variants, and invalid
bindings leave the stock generated material and mesh slot in place.

## Open questions

- [ ] Outline parent override and parameter inheritance
- [ ] Masked-parent support beyond VRM4U's current material-set API
- [ ] Shader-feature (Static Switch) behavior for editor constants and runtime dynamic
      instances
- [ ] Stable mapping between source material indices and post-import mesh slots

## Source references

- `Source/VRM4U/Public/VrmImportMaterialSet.h`
- `Source/VRM4U/Public/VrmAssetListObject.h`
- `Source/VRM4U/Public/VrmUtil.h`
- `Source/VRM4ULoader/Public/VrmConvert.h`
- `Source/VRM4ULoader/Private/VrmConvertTexture.cpp`
- `Source/VRM4ULoader/Private/LoaderBPFunctionLibrary.cpp`
