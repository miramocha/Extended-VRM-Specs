---
title: UniVRM Materials Override
aliases:
  - VRMXT materials override for Unity
tags:
  - extended-vrm
  - implementation/unity
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# UniVRM Materials Override

Unity implementation profile for
[VRMXT_materials_override](../specs/vrmxt-materials-override.md). Support belongs in
[UniVRMXT](https://github.com/miramocha/UniVRMXT) (`com.miramocha.univrmxt`), an optional
UPM package that depends on stock [UniVRM](https://github.com/vrm-c/UniVRM). UniVRM
source changes are not required.

## Supported entry

The consumer selects `overrides[]` where `engine` equals `unity`.

### Profile properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `material.idType` | string | yes | `"shaderName"` |
| `material.id` | string | yes | Exact Unity shader name |
| `material.variant` | string | no | `builtin`, `urp`, or `hdrp` |
| `material.provider` | object | no | Unity package hint |
| `material.provider.id` | string | yes if `provider` present | Unity package name |
| `material.provider.version` | string | no | Exporter-observed package version |

`provider` is advisory per base-spec rules 18–21. This profile MUST NOT require a closed
shader registry. A consumer MAY warn about package/version mismatch. It MUST use stock
import when the shader or requested pipeline variant cannot be resolved.

### Example

```json
{
  "engine": "unity",
  "material": {
    "idType": "shaderName",
    "id": "Example/SkinToon",
    "variant": "urp",
    "provider": {
      "id": "com.example.vrmxt-materials",
      "version": "1.2.0"
    }
  },
  "bindings": [
    {
      "source": "shadeColorFactor",
      "target": "_ShadeColor",
      "targetType": "vector"
    },
    {
      "source": "shadeMultiplyTexture",
      "target": "_ShadeTex",
      "targetType": "texture"
    },
    {
      "source": "shadingShiftFactor",
      "target": "_ShadingShiftFactor",
      "targetType": "scalar"
    },
    {
      "source": "shadingToonyFactor",
      "target": "_ShadingToonyFactor",
      "targetType": "scalar"
    }
  ],
  "properties": [
    {
      "name": "_UseRimLight",
      "type": "shaderFeature",
      "value": true
    }
  ]
}
```

`material.idType` names the identity scheme; `"shaderName"` is the only value this
profile defines today. `material.id` is the exact string passed to `Shader.Find` — no
GUID. `provider.id` is a Unity package name. `variant` identifies the intended render
pipeline:

| Value | Unity pipeline |
|-------|----------------|
| `builtin` | Built-in Render Pipeline |
| `urp` | Universal Render Pipeline |
| `hdrp` | High Definition Render Pipeline |

The optional package MUST reject a variant that does not match the active pipeline and
use stock import for that material.

## UniVRM integration

UniVRM exposes `IMaterialDescriptorGenerator`. A supporting package wraps the stock
VRM 1.0 generator:

1. Read `materials[i].extensions.VRMXT_materials_override`.
2. Select the `unity` entry.
3. Resolve `material.id` via `Shader.Find` (per `material.idType: "shaderName"`).
4. Return a `MaterialDescriptor` using the resolved shader, declared `properties`, and
   declared `bindings`.
5. Delegate to the stock generator when any step fails.

Runtime callers pass the wrapper through the `materialGenerator` argument on
`Vrm10.LoadPathAsync`, `LoadBytesAsync`, or `LoadGltfDataAsync`.

Editor import uses a `MaterialDescriptorGeneratorFactory` assigned in UniVRM project
settings. The factory returns the same wrapper. With no factory assigned, UniVRM keeps
its built-in MToon, unlit, and PBR selection.

## Package and shader resolution

The VRM file names a Unity shader (`material.id`); it does not contain shader source.
UniVRMXT and the host app MUST include any shaders they intend to honor, and MUST keep
those shaders in player builds (referenced materials, shader variant collections,
Resources, or Always Included Shaders). `provider` is an advisory package hint only.

Runtime resolve order for a supporting consumer:

1. Read the `unity` override and `material.id`.
2. Resolve the shader (typically `Shader.Find`).
3. If the shader is present and the `variant` matches the active pipeline, build the
   override material and apply `properties`, then `bindings`.
4. If the shader is missing, stripped, or incompatible, use stock VRM 1.0 import for
   that material.

A drag-and-drop or other runtime VRM viewer therefore loads every valid VRM with stock
materials by default. Overrides appear only for shaders the app (or an optional shader
pack it depends on) already ships. Remote git fetch and runtime shader compilation are
out of scope for this profile.

## Bindings

The generator reads resolved values from `VRMC_materials_mtoon` and writes them through
`MaterialDescriptor` actions.

| `targetType` | Unity operation |
|--------------|-----------------|
| `scalar` | `Material.SetFloat` |
| `vector` | `Material.SetVector` or `SetColor`, according to the target shader |
| `texture` | Imported glTF texture assigned with `Material.SetTexture` |
| `shaderFeature` | `Material.EnableKeyword` / `DisableKeyword` for a `#pragma shader_feature` or ShaderLab `[Toggle]` keyword |

The example Unity targets in the base spec follow UniVRM MToon10 naming where applicable:
`_ShadeTex`, `_ShadingShiftFactor`, `_ShadingToonyFactor`, and
`_GiEqualizationFactor`. Custom shaders may use different targets.

## Properties

`overrides[].properties` sets literal values on the resolved shader with no
`VRMC_materials_mtoon` dependency (base-spec rules 22–26). `properties[].name` is a Unity
material property name (for example `_UseRimLight`); `type` selects the same Unity
operation as the matching row in the bindings table above, reading `value` (or
`texture`) directly instead of a resolved MToon source.

A wrapper applies `properties` before `bindings` per rule 23, so a `bindings` entry wins
if an authoring error targets the same parameter name.

Exporters that emit a `properties[].texture` reference MUST register the source image
during the `Vrm10ExportExtensionPhase.PrepareTextures` phase (see
`IVrm10ExportExtension` / `Vrm10ExportExtensionContext.RegisterSRgbTexture` and
equivalents) so the texture lands in the file's `textures[]` before export finishes, per
base-spec rule 26.

## Variant survival

`material.variant` records shader authoring intent, not the active Unity render
pipeline. A supporting exporter MUST NOT overwrite an existing `variant` value with the
active editor render pipeline on re-export: an entry authored `hdrp` stays `hdrp` even
when re-exported from a URP project, or when the file is re-imported and re-exported
elsewhere. An exporter MAY fill `variant` from the active render pipeline only when it
creates a brand-new `unity` entry that has no `variant` yet.

## Fallback

Failure is local to one glTF material. The wrapper delegates that material index to the
stock `BuiltInVrm10MaterialDescriptorGenerator` or
`UrpVrm10MaterialDescriptorGenerator`. Unsupported files therefore load as normal
VRM 1.0 assets when the optional package is missing, disabled, or incomplete.

## Known constraints

- Built-in UniVRM generator selection covers Built-in RP and URP. HDRP support requires
  the optional package to provide its own stock-equivalent fallback.
- Runtime support requires the application to pass the generator at its VRM load sites.
- Editor support requires one-time project settings configuration.
- Shader property type validation and texture transforms remain implementation work.

## Host note: Warudo

Warudo does not expose `materialGenerator` on Character Source load. A workable plugin
path is post-load re-read of the `.vrm` plus material swap. See
[Warudo Materials Override](warudo-materials-override.md).

## Source references

- `Packages/UniGLTF/Runtime/UniGLTF/IO/MaterialIO/Import/IMaterialDescriptorGenerator.cs`
- `Packages/UniGLTF/Runtime/UniGLTF/IO/MaterialIO/Import/MaterialDescriptor.cs`
- `Packages/VRM10/Runtime/IO/Vrm10.cs`
- `Packages/VRM10/Runtime/IO/Vrm10Exporter.cs`
- `Packages/VRM10/Runtime/IO/Export/Vrm10ExportExtension.cs`
- `Packages/VRM10/Editor/Settings/MaterialDescriptorGeneratorFactory.cs`
- `Packages/VRM10/Editor/ScriptedImporter/VrmScriptedImporterImpl.cs`
