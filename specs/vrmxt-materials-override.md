---
title: VRMXT_materials_override
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

# VRMXT_materials_override

Per-material glTF extension. Lets an author mark a VRM 1.0 material for optional
consumer-side override. Stock VRM 1.0 importers that ignore the extension MUST still
load the material through normal glTF / MToon / unlit / PBR rules.

The extension stores engine-specific override entries. Each entry names a target
material definition and MAY bind MToon shade values to its parameters.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_materials_override` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | `materials[i].extensions.VRMXT_materials_override` |
| Engine entries | `overrides[]` |
| Root `extensions` | not used for this extension |
| Stock importer | no required change |
| Consumer package | optional; interprets the extension when present |

## Normative requirements

1. Files that use this extension MUST list `VRMXT_materials_override` in
   `extensionsUsed`.
2. The extension object MUST appear on a glTF `materials[]` entry under
   `extensions.VRMXT_materials_override`.
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
10. An override MUST contain a `material` object valid for its engine profile.
11. A supporting implementation MUST ignore material definitions it does not recognize.
12. If the material definition or any required asset cannot be resolved, a supporting
    implementation MUST use stock VRM 1.0 material import for that material.
13. An override MAY contain `bindings`. Each binding maps one MToon source semantic to
    one engine-specific target material parameter.
14. Each binding MUST contain `source`, `target`, and `targetType`.
15. A supporting implementation MUST resolve MToon source values from the sibling
    `VRMC_materials_mtoon` extension. When a source property is omitted, it MUST use the
    default defined by the supported `VRMC_materials_mtoon` version.
16. A supporting implementation MUST ignore a binding when the material has no
    `VRMC_materials_mtoon` extension or does not recognize the binding's source semantic.
17. Override properties other than `engine`, `material`, and `bindings` are **TBD** and
    MUST NOT be treated as stable until this specification marks them accepted.

## Extension properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | Version of this extension; currently `"1.0"` |
| `overrides` | object[] | yes | Non-empty list of engine-specific overrides |
| `overrides[].engine` | string | yes | Case-sensitive engine identifier |
| `overrides[].material` | object | yes | Definition specified by the engine profile |
| `overrides[].bindings` | object[] | no | MToon semantic-to-target bindings |
| `bindings[].source` | string | yes | MToon source semantic listed below |
| `bindings[].target` | string | yes | Engine-specific material parameter identifier |
| `bindings[].targetType` | string | yes | `scalar`, `vector`, `texture`, or `staticSwitch` |

Engine profiles define the contents of `material`, provider identifiers, supported
`targetType` operations, and engine-specific fallback constraints.

## Engine profiles

This draft defines two case-sensitive engine identifiers:

| Engine | Profile |
|--------|---------|
| `unity` | [UniVRM Materials Override](../implementations/univrm-materials-override.md) |
| `unreal` | [VRM4U Materials Override](../implementations/vrm4u-materials-override.md) |

New engines require a separate profile. Adding a profile does not change this base
extension version unless it changes common fields or behavior.

## MToon shading source semantics

The following `source` identifiers refer to resolved values from
`VRMC_materials_mtoon`. They do not name engine material parameters.

| Source | Value |
|--------|-------|
| `shadeColorFactor` | RGB shade color factor |
| `shadeMultiplyTexture` | Shade multiply texture and its texture-info metadata |
| `shadingShiftFactor` | Base shading shift scalar |
| `shadingShiftTexture` | Shading shift texture and its texture-info metadata |
| `shadingShiftTexture.scale` | Scalar applied to the shading shift texture |
| `shadingToonyFactor` | Shading boundary toony scalar |
| `giEqualizationFactor` | Global illumination equalization scalar |

Bindings transfer the resolved source value to `target` using `targetType`. Consumers
MUST ignore incompatible source/target combinations. Color-vector conversion,
texture-coordinate handling, and static-switch rebuild behavior are **TBD**.

## Attachment example

Non-normative. The placeholder engine and material kind are not registered profiles.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMC_materials_mtoon",
    "VRMXT_materials_override"
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
        "VRMXT_materials_override": {
          "specVersion": "1.0",
          "overrides": [
            {
              "engine": "example-engine",
              "material": {
                "kind": "example-material"
              },
              "bindings": [
                {
                  "source": "shadeColorFactor",
                  "target": "exampleShadeColor",
                  "targetType": "vector"
                },
                {
                  "source": "shadingToonyFactor",
                  "target": "exampleShadingToony",
                  "targetType": "scalar"
                }
              ]
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
- `VRMXT_materials_override` is a sibling under `materials[i].extensions`. It does not
  replace MToon JSON.
- `bindings` transfer existing MToon shade values to target material parameters. They do
  not redefine MToon values.
- Precedence when a supporting consumer is present: **TBD** (override vs MToon vs
  coexistence).

## Optional consumer interpretation

Supporting tools MAY read the matching engine entry, resolve `material`, apply
`bindings`, and create a local material instance. Missing providers, unresolved assets,
unsupported kinds, or unknown engines leave stock VRM 1.0 import intact.

Engine integration details are documented in
[UniVRM Materials Override](../implementations/univrm-materials-override.md) and
[VRM4U Materials Override](../implementations/vrm4u-materials-override.md).

## Open questions

- [ ] Binding color conversions and texture transforms
- [ ] Static-switch rebuild behavior
- [ ] Precedence vs `VRMC_materials_mtoon` and `KHR_materials_unlit`
- [ ] Whether `extensionsRequired` is ever appropriate
- [ ] Export rules for Blender / other authoring tools
- [ ] Stable `specVersion` policy after first accepted property set

## Related

- Upstream MToon: `VRMC_materials_mtoon` in the VRM 1.0 specification
- Core materials: glTF 2.0 `materials` schema
- [UniVRM Materials Override](../implementations/univrm-materials-override.md)
- [VRM4U Materials Override](../implementations/vrm4u-materials-override.md)
- [VRMXT_vfx](vrmxt-vfx.md)
- [VRMXT_springBone_override](vrmxt-spring-bone-override.md)
- [VRMXT_lattice](vrmxt-lattice.md) (research draft)
