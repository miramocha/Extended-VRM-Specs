---
title: Engine material override — glTF history and PBR-only fallback sketch
aliases:
  - materials override without MToon
  - KHR_techniques_webgl lessons
  - PBR-only materials override fallback
tags:
  - extended-vrm
  - reference/gltf
  - reference/materials-override
  - format/gltf-extension
  - compatibility/vrm1
type: reference
status: draft
---

# Engine material override — glTF history and PBR-only fallback sketch

Non-normative research. Lives under `references/research/` only. Does **not** change
[`VRMXT_materials_override`](../../specs/extensions/materials/vrmxt-materials-override.md)
or propose a Khronos submission.

**Question:** if materials override drops VRM MToon as the designed stock fallback and
aims at a plain glTF extension (portable base = core PBR / unlit), what prior art exists,
and what shape would that draft have?

**Short finding:** Khronos never ratified engine-shader-identity overrides. Closest
attempts either embedded WebGL techniques (archived) or pointed at an external material
language with **core PBR** as the ignore-path (`NV_materials_mdl`). A PBR-only fallback
sketch is workable as research; it leaves the VRM 1.0 product path.

## Sources

| Source | Role |
|--------|------|
| [glTF Extension Registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md) | Ratified / archived / vendor lists; extensionUsed vs Required guidance |
| [KHR_techniques_webgl](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Archived/KHR_techniques_webgl) (archived) | Custom GLSL techniques on materials |
| glTF 1.0 techniques / materials common | Pre-2.0 custom shader model (dropped for PBR-first 2.0) |
| [NV_materials_mdl](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Vendor/NV_materials_mdl) | Vendor MDL material graphs; PBR recommended as fallback |
| [KHR_materials_variants](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_materials_variants) | Portable `materials[]` swaps |
| [KHR / glTF overlap](../khr-gltf-overlap.md) | Registry check vs current `VRMXT_*` (2026-07-20) |
| [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md) | Current VRMXT draft (MToon sibling + stock ignore chain) |

Registry / history claims below checked against public Khronos docs as of **2026-08-06**.
In-progress rows can change after that date.

## VRMXT baseline (for contrast)

Current draft from day one (`VRMEX_materials_override`, 2026-07-17 → `VRMXT_*`):

| Choice | Current draft |
|--------|---------------|
| Namespace | Vendor `VRMXT_` (never proposed as `KHR_` / `EXT_`) |
| Target | VRM 1.0 (`VRMC_vrm`) only |
| Attachment | `materials[i].extensions` |
| Ignore path | `VRMC_materials_mtoon`, `KHR_materials_unlit`, core PBR (existing VRM precedence) |
| MToon role | Sibling JSON; `bindings` read MToon semantics; `properties` independent |
| Shader payload | Not in file; consumer resolves engine material id locally |

No vault ADR proposes submitting materials override to Khronos.

## Prior art: custom / non-PBR materials in glTF

### glTF 1.0 techniques

glTF 1.0 carried materials as techniques bound to GLSL (and related) programs. glTF 2.0
replaced that with a portable metallic-roughness PBR model so loaders could render
without executing author-supplied shaders. Lesson for override design: **embedding
engine shader source in the asset failed as a core/portable story**.

### `KHR_techniques_webgl` (archived)

Intent: restore technique-style materials on glTF 2.0 — root `techniques[]`, material
extension picks a technique index and supplies uniform values; shaders referenced as
external WebGL programs.

| Aspect | What happened |
|--------|----------------|
| Status | Moved to **Archived**; never ratified |
| Fallback model | Core material fields still present; techniques override shading when supported |
| Ecosystem | Partial / niche use (e.g. Cesium lineage, Hilo3d samples). Broad loaders (e.g. three.js) declined shipping support while ratification was unlikely |
| Failure mode | Custom GLSL is API- and engine-specific; hard to map to Unity/Unreal/native material graphs; maintenance cost without Khronos buy-in |

**Lessons for an engine-override proposal:**

1. **In-file shader programs do not survive Khronos process** once PBR is the portable base.
2. Safe ignore still needs a **portable** material on the same `materials[i]` (core PBR /
   unlit). Domain toon (MToon) is optional product glue, not what Khronos expects as the
   common fallback.
3. Ratification pressure favors **one portable shading model**, not per-engine ids.
4. Archived KHR is a weak template for VRMXT: VRMXT stores **engine material identity +
   property bag**, not GLSL technique graphs.

### `NV_materials_mdl` (vendor, live)

NVIDIA vendor extension: material extension points into MDL function-call graphs;
modules may be referenced or embedded. Spec text recommends keeping a representative
**core glTF PBR** material for loaders that skip the extension.

| Aspect | Relation to VRMXT |
|--------|-------------------|
| Rich look language | Yes (MDL): one shared language. Differs from Unity `shader` strings / Unreal parents |
| Fallback | Core PBR (explicit) |
| Khronos path | Stayed **vendor** (`NV_`), not `KHR_` |
| Closest lesson | Richer materials still ship with a **PBR ignore-path**; multi-engine shader ids were never the ask |

### Adjacent KHR (wrong job)

| Extension | Why it does not replace override |
|-----------|----------------------------------|
| `KHR_materials_*` PBR pack | Extends portable PBR (clearcoat, sheen, …). No external engine shader id |
| `KHR_materials_variants` | Primitive → another portable `materials[]` index. No engine profile |
| `KHR_materials_unlit` | Alternate portable shading; already in stock chains |

Detail and VRMXT comparison tables: [KHR / glTF overlap](../khr-gltf-overlap.md).

## Sketch: PBR-only fallback (no MToon as designed sibling)

Research-only shape. Names below are placeholders (`EXT_` / `VRMXT_` undecided).

### Intent

Per-material optional override for engine-specific material identity and literal
parameters. Loaders that ignore the extension render with **core glTF material** (and
`KHR_materials_unlit` when present). No dependency on `VRMC_materials_mtoon`.

### Scope sketch

| Item | Sketch value |
|------|----------------|
| Attachment | `materials[i].extensions.<name>` |
| Target asset | Any glTF 2.0 (VRM optional host) |
| Required sibling | None beyond core `materials[i]` fields the author already wrote |
| Ignore path | Core PBR (+ unlit if used). No MToon in the normative fallback list |
| `bindings` | Drop, or redefine sources from core/`KHR_materials_*` semantics only |
| `properties` | Keep: literal engine parameter bag (closest to today’s independent path) |
| Shader programs | Still out of file (avoid techniques trap) |
| `extensionsRequired` | Same Khronos guidance: material extensions usually stay out of Required when the portable material remains valid |

### Example (non-normative)

```json
{
  "extensionsUsed": [
    "KHR_materials_unlit",
    "EXT_materials_engine_override"
  ],
  "materials": [
    {
      "name": "Face",
      "pbrMetallicRoughness": {
        "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
        "baseColorTexture": { "index": 0 }
      },
      "extensions": {
        "EXT_materials_engine_override": {
          "specVersion": "0.0-research",
          "overrides": [
            {
              "engine": "unity",
              "material": {
                "idType": "shader",
                "id": "lilToon",
                "variant": "builtin"
              },
              "properties": [
                {
                  "name": "_Color",
                  "type": "color",
                  "value": [1.0, 1.0, 1.0, 1.0]
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

No `VRMC_materials_mtoon`, no `bindings`. Shade params that today ride MToon semantics
must be duplicated into `properties` or into portable PBR fields the consumer maps
itself.

### Diff vs current `VRMXT_materials_override`

| Topic | Current VRMXT draft | PBR-only research sketch |
|-------|---------------------|---------------------------|
| Product target | VRM 1.0 avatars | Generic glTF (+ optional VRM host) |
| Stock ignore | Includes MToon | Core PBR / unlit only |
| `bindings` | MToon source semantics | Absent or rebased onto core/KHR portable fields |
| Hub / VRM tools | Keeps VRM1 look when override ignored | Author must author portable PBR that looks acceptable alone |
| Khronos fit | Still engine ids → weak KHR candidate | Same engine-id problem; PBR fallback only removes the MToon-specific objection |
| Implementation reuse | Shipping UniVRMXT / Warudo / Blender path | Would need profile + binding redesign; VRM product may keep today’s extension |

### What PBR-only does **not** fix for a Khronos pitch

Engine-local shader / parent material ids (`lilToon`, `.poiyomi/…`, Unreal parent path)
remain non-portable. History says Khronos either:

- extends **one** portable material model (`KHR_materials_*`), or
- leaves richer languages as **vendor** (`NV_materials_mdl`), or
- archives in-file custom shading (`KHR_techniques_webgl`).

So “drop MToon, keep engine overrides, propose as glTF standard” still faces the same
identity-portability wall. PBR-only mainly aligns the **ignore-path** with Khronos
material-extension norms.

## Implications if this research ever graduates

Non-binding. Possible futures (pick later; do not invent a decision here):

1. **Stay VRMXT as-is** — MToon sibling + `bindings`; document Khronos cousins in
   [khr-gltf-overlap](../khr-gltf-overlap.md) only.
2. **Dual profile** — VRMXT keeps MToon bindings for VRM1; a separate generic-glTF
   profile documents PBR-only ignore + `properties`-only.
3. **Vendor `EXT_` experiment** — same payload as (2), outside VRM namespace; still not
   a KHR submission until engine ids have a portable story (unlikely without a shared
   material language like MDL/MaterialX).

## Open questions

- [ ] Whether any portable source semantics replace MToon `bindings` (baseColor only?
      full `KHR_materials_*` pointer set?)
- [ ] Whether a research `EXT_` name is worth minting vs keeping `VRMXT_` with a
      “no MToon required” profile flag
- [ ] Authoring UX when portable PBR must look good without toon (VRM creators today
      often treat MToon as the authored look)
- [ ] Relationship to MaterialX / MDL as a *shared* override language (different product
      from Unity/Unreal shader catalogs)

## Related

- [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md)
- [KHR / glTF overlap](../khr-gltf-overlap.md)
- [Materials Override Catalogs](../materials-override-catalogs.md)
