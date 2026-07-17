---
title: VRMEX_materials_override
aliases:
  - materials override
  - VRM material override
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMEX_materials_override

Per-material glTF extension. Lets an author mark a VRM 1.0 material for optional
consumer-side override. Stock VRM 1.0 importers that ignore the extension MUST still
load the material through normal glTF / MToon / unlit / PBR rules.

The extension stores one or more engine-specific override entries. Each entry MAY name
a target shader and MAY bind MToon shade values to that shader's parameters.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMEX_materials_override` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | `materials[i].extensions.VRMEX_materials_override` |
| Engine entries | `overrides[]` |
| Root `extensions` | not used for this extension |
| UniVRM / stock importer | no required change |
| Consumer package | optional; interprets the extension when present |

## Normative requirements

1. Files that use this extension MUST list `VRMEX_materials_override` in
   `extensionsUsed`.
2. The extension object MUST appear on a glTF `materials[]` entry under
   `extensions.VRMEX_materials_override`.
3. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
4. The extension object MUST contain a non-empty `overrides` array.
5. Each `overrides` entry MUST contain an `engine` string identifying its target engine.
6. A material MUST NOT contain more than one override for the same `engine`.
7. A supporting implementation MUST select only the entry matching its engine. It MUST
   ignore entries for other or unknown engines.
8. Implementations that do not support the extension MUST ignore it and import the
   material using remaining glTF and VRM 1.0 material rules
   (`VRMC_materials_mtoon`, `KHR_materials_unlit`, core PBR, in that existing precedence).
9. Implementations MUST NOT require this extension in `extensionsRequired` unless the
   file is intentionally unusable without a supporting consumer.
10. An override MAY contain a `shader` object. When present, `shader.name` MUST be a
    non-empty string identifying the engine-local shader to resolve.
11. When `shader` is present and the named shader cannot be resolved, a supporting
    implementation MUST fall back to stock VRM 1.0 material import for that material.
12. An override MAY contain `bindings`. Each binding maps one MToon source semantic to
    one engine-specific target material parameter.
13. A supporting implementation MUST resolve MToon source values from the sibling
    `VRMC_materials_mtoon` extension. When a source property is omitted, it MUST use the
    default defined by the supported `VRMC_materials_mtoon` version.
14. A supporting implementation MUST ignore a binding when the material has no
    `VRMC_materials_mtoon` extension or does not recognize the binding's source semantic.
15. Override properties other than `engine`, `shader`, and `bindings` are **TBD** and
    MUST NOT be treated as stable until this specification marks them accepted.

## Extension properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | Version of this extension; currently `"1.0"` |
| `overrides` | object[] | yes | Non-empty list of engine-specific overrides |
| `overrides[].engine` | string | yes | Case-sensitive engine identifier |
| `overrides[].shader` | object | no | Target shader definition |
| `shader.name` | string | yes if `shader` present | Engine-local shader identifier |
| `shader.packageId` | string | no | Optional package or module that provides the shader |
| `shader.packageVersion` | string | no | Exporter-observed package version hint |
| `shader.renderPipeline` | string | no | Optional render-pipeline hint |
| `overrides[].bindings` | object[] | no | MToon semantic-to-target bindings |
| `bindings[].source` | string | yes | MToon source semantic listed below |
| `bindings[].target` | string | yes | Engine-specific material parameter identifier |

Engine identifiers are **TBD**. Examples use `unity` and `unreal` provisionally; this
draft does not register either value.

## Shader definition

`shader` tells a supporting consumer which engine-local shader to use for the material.

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `name` | string | yes | Case-sensitive shader identifier used by the target engine |
| `packageId` | string | no | Package, plugin, or module expected to provide the shader |
| `packageVersion` | string | no | Package version observed by the exporter |
| `renderPipeline` | string | no | Pipeline hint such as `builtin`, `urp`, or `hdrp` |

Rules:

- `name` is engine-local. For Unity examples, it is the string passed to `Shader.Find`.
- `packageId` is a discovery hint only. A supporting implementation MAY use it to detect
  an optional package before resolving `name`. It MUST NOT treat package absence as a
  hard error; it falls back per requirement 11.
- `packageVersion` is advisory metadata, not an installation request or compatibility
  range. A consumer MAY warn when its installed version differs.
- `renderPipeline` values are **TBD**. Examples are provisional.
- When `shader` is omitted, a supporting implementation MAY still use `bindings` against
  a locally chosen override material, or ignore the override entirely.

## MToon shading source semantics

The following `source` identifiers refer to resolved values from
`VRMC_materials_mtoon`. They do not name engine shader properties.

| Source | Value |
|--------|-------|
| `shadeColorFactor` | RGB shade color factor |
| `shadeMultiplyTexture` | Shade multiply texture and its texture-info metadata |
| `shadingShiftFactor` | Base shading shift scalar |
| `shadingShiftTexture` | Shading shift texture and its texture-info metadata |
| `shadingShiftTexture.scale` | Scalar applied to the shading shift texture |
| `shadingToonyFactor` | Shading boundary toony scalar |
| `giEqualizationFactor` | Global illumination equalization scalar |

Bindings transfer the resolved source value to `target`. Conversion, texture-coordinate
handling, and target type compatibility are **TBD**.

## Attachment example

Non-normative. Engine identifiers, shader names, and target parameter names are
provisional.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMC_materials_mtoon",
    "VRMEX_materials_override"
  ],
  "materials": [
    {
      "name": "Face",
      "pbrMetallicRoughness": {
        "baseColorFactor": [1.0, 1.0, 1.0, 1.0]
      },
      "extensions": {
        "VRMC_materials_mtoon": {
          "specVersion": "1.0"
        },
        "VRMEX_materials_override": {
          "specVersion": "1.0",
          "overrides": [
            {
              "engine": "unity",
              "shader": {
                "name": "Example/SkinToon",
                "packageId": "com.example.vrmex-materials",
                "packageVersion": "1.0.0",
                "renderPipeline": "urp"
              },
              "bindings": [
                {
                  "source": "shadeColorFactor",
                  "target": "_ShadeColor"
                },
                {
                  "source": "shadeMultiplyTexture",
                  "target": "_ShadeTexture"
                },
                {
                  "source": "shadingShiftFactor",
                  "target": "_ShadingShift"
                },
                {
                  "source": "shadingToonyFactor",
                  "target": "_ShadingToony"
                },
                {
                  "source": "giEqualizationFactor",
                  "target": "_GiEqualization"
                }
              ]
            },
            {
              "engine": "unreal",
              "shader": {
                "name": "/Game/Materials/SkinToon"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## Relationship to other material extensions

- Core glTF material fields remain the portable base (base color, alpha, normals,
  emissive, double-sided).
- `VRMC_materials_mtoon` remains the VRM 1.0 toon material extension when present.
- `VRMEX_materials_override` is a sibling under `materials[i].extensions`. It does not
  replace MToon JSON.
- `bindings` describe how a supporting engine adapter transfers existing MToon shade
  values to target shader parameters. They do not redefine MToon values.
- Precedence when a supporting consumer is present: **TBD** (override vs MToon vs
  coexistence).

## Optional consumer interpretation

Supporting tools MAY read the matching engine entry, resolve `shader`, apply `bindings`,
and construct a local override material. Missing package, unresolved shader, or unknown
engine leaves stock VRM 1.0 import intact.

Unity consumers MAY implement support in a separate package by supplying
`IMaterialDescriptorGenerator` / `MaterialDescriptorGeneratorFactory` without modifying
UniVRM. When that package is absent, load behavior stays stock VRM 1.0.

## Open questions

- [ ] Stable engine identifier registry and naming rules
- [ ] Stable `renderPipeline` values
- [ ] Binding conversions, texture transforms, and target type compatibility
- [ ] Precedence vs `VRMC_materials_mtoon` and `KHR_materials_unlit`
- [ ] Whether `extensionsRequired` is ever appropriate
- [ ] Export rules for Blender / other authoring tools
- [ ] Stable `specVersion` policy after first accepted property set

## Related

- Upstream MToon: `VRMC_materials_mtoon` in the VRM 1.0 specification
- Core materials: glTF 2.0 `materials` schema
