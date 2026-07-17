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

Extension object properties beyond `specVersion` are **TBD**. This note locks the
extension name, attachment point, and optional-consumer rule.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMEX_materials_override` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | `materials[i].extensions.VRMEX_materials_override` |
| Root `extensions` | not used for this extension |
| UniVRM / stock importer | no required change |
| Consumer package | optional; interprets the extension when present |

## Normative requirements

1. Files that use this extension MUST list `VRMEX_materials_override` in
   `extensionsUsed`.
2. The extension object MUST appear on a glTF `materials[]` entry under
   `extensions.VRMEX_materials_override`.
3. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
4. Implementations that do not support the extension MUST ignore it and import the
   material using remaining glTF and VRM 1.0 material rules
   (`VRMC_materials_mtoon`, `KHR_materials_unlit`, core PBR, in that existing precedence).
5. Implementations MUST NOT require this extension in `extensionsRequired` unless the
   file is intentionally unusable without a supporting consumer.
6. Additional properties of the extension object are **TBD** and MUST NOT be treated as
   stable until this specification marks them accepted.

## Attachment example

Non-normative. Properties other than `specVersion` are placeholders for later design.

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
          "specVersion": "1.0"
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
- Precedence when a supporting consumer is present: **TBD** (override vs MToon vs
  coexistence).

## Optional consumer interpretation

Supporting tools MAY read `VRMEX_materials_override` and apply a local override
(material remap, custom generator, project mapping, and so on). How that override is
resolved is outside this draft until properties are defined.

Unity consumers MAY implement support in a separate package by supplying
`IMaterialDescriptorGenerator` / `MaterialDescriptorGeneratorFactory` without modifying
UniVRM. When that package is absent, load behavior stays stock VRM 1.0.

## Open questions

- [ ] Extension properties (override id, profile, property bag, other)
- [ ] Precedence vs `VRMC_materials_mtoon` and `KHR_materials_unlit`
- [ ] Whether `extensionsRequired` is ever appropriate
- [ ] Export rules for Blender / other authoring tools
- [ ] Stable `specVersion` policy after first accepted property set

## Related

- Upstream MToon: `VRMC_materials_mtoon` in the VRM 1.0 specification
- Core materials: glTF 2.0 `materials` schema
