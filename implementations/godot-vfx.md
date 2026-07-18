---
title: Godot VFX
aliases:
  - VRMXT_vfx for Godot
  - godot-vrmxt particles
tags:
  - extended-vrm
  - implementation/godot
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# Godot VFX

Godot implementation profile for [VRMXT_vfx](../specs/vrmxt-vfx.md). Support belongs in
a **separate** optional addon (working name `godot-vrmxt`), registered beside
[godot-vrm](https://github.com/V-Sekai/godot-vrm). Do not fork or replace the stock
VRM importer.

VRM 1.0 only. The extension is optional: stock godot-vrm load MUST succeed when the
VRMXT addon is absent or when `VRMXT_vfx` is missing.

## Package

| Item | Value |
|------|-------|
| Host VRM importer | [V-Sekai/godot-vrm](https://github.com/V-Sekai/godot-vrm) (Asset Library / `addons/vrm`) |
| Extended package | Separate Godot addon under `addons/` (path TBD; MUST NOT be nested inside `addons/vrm`) |
| Engine | Godot 4.x matching the project's godot-vrm version window |
| Integration API | `GLTFDocumentExtension` via `GLTFDocument.register_gltf_document_extension` |

godot-vrm already registers per-`VRMC_*` document extensions the same way. `VRMXT_vfx`
uses that registry as a peer plugin.

## Architecture fit

See [Extended VRM Architecture](../architecture.md). Godot maps to the optional
consumer package row:

| Architecture rule | Godot approach |
|-------------------|----------------|
| Stock VRM load unchanged | Keep godot-vrm; enable VRMXT addon separately |
| Do not replace stock import | Own `EditorPlugin`; do not replace `import_vrm.gd` |
| Parse + attach | `_import_post` (editor) and/or explicit runtime attach helper |
| No `extensionsRequired` | Never list `VRMXT_vfx` there |
| Missing package / missing ext | Avatar loads; no emitters |

Rejected: shipping Extended VFX only by forking V-Sekai/godot-vrm or patching
`addons/vrm` as the sole path.

## Import seam (editor)

Preferred path: an `EditorPlugin` registers a `GLTFDocumentExtension` in `_enter_tree`
and unregisters it in `_exit_tree`, parallel to godot-vrm's `plugin.gd`.

1. `_import_preflight(state, extensions)`: if `extensions` lacks `VRMXT_vfx`, return
   `ERR_SKIP`. Otherwise return `OK`.
2. `_import_post(state, root)`:
   - Read `state.json["extensions"]["VRMXT_vfx"]`.
   - Require `specVersion` `"1.0"` for this draft; other versions: **TBD** (skip or
     best-effort).
   - Iterate `emitters[]`. Skip invalid entries per the base spec.
   - Resolve `node` with `state.get_scene_node(node_index)`. Null / missing → skip
     that emitter.
   - Resolve `particle.texture` when present via `state` textures/images (same
     direction as MToon). Unresolved → leave empty; still apply other particle fields.
   - Spawn a particle node under the resolved scene node using
     `localPosition` / `localRotation` (see [Emitter transform](../specs/vrmxt-vfx.md#emitter-transform)).
3. Do not fail the whole VRM import when individual emitters are skipped.

godot-vrm's `*.vrm` `EditorSceneFormatImporter` builds a `GLTFDocument` and calls
`append_from_file`. Globally registered document extensions participate in that
import. VRMXT MUST register without `first_priority` so stock `VRMC_*` preflight and
skin fixes still run first.

## Runtime seam

`EditorPlugin` does not run in exported games. Apps that load `.vrm` / `.glb` at
runtime (see godot-vrm `vrm_samples/load_at_runtime_scene.gd`) MUST either:

1. Call `GLTFDocument.register_gltf_document_extension` for the VRMXT extension before
   `append_from_file` / `generate_scene` (autoload or load helper), or
2. After stock generate, call an explicit attach API with glTF JSON and a
   node-index → `Node3D` resolver (same shape as UniVRMXT
   `VrmxtVfxRuntime.TryAttach`).

Missing extension → no-op. Unresolved nodes skip that emitter only.

## Layering (proposed)

Non-normative package layout:

| Layer | Role |
|-------|------|
| Format | Parse / validate `VRMXT_vfx` JSON only |
| Importer | Resolve nodes and textures from `GLTFState` or caller maps |
| Runtime attach | Store resolved emitters on the avatar root |
| Particle mapper | Map portable fields onto `GPUParticles3D` (or `CPUParticles3D`) |

Keep format parsing free of godot-vrm script paths (`addons/vrm/...`). Soft dependency
on godot-vrm is enough: VFX attaches to any glTF scene with valid node indices.

## Particle mapping (proposed)

Exact visual parity with Unity is not required. Field meaning and units follow the
base spec. Proposed Godot targets:

| Spec field | Godot target | Notes |
|------------|--------------|-------|
| `localPosition` / `localRotation` | Child `Node3D` under resolved node | Spec / glTF node-local; xyzw quat |
| emitter | `GPUParticles3D` (preferred) or `CPUParticles3D` | Continuous point source |
| `emissionRate` | Derived from `amount` and `lifetime` | Godot has no exact particles/sec API; document the formula when locked |
| `maxParticles` | `amount` | Cap ≥ 1 |
| `lifetime` | `lifetime` | Seconds |
| `startSize` | Process / mesh scale | Billboard size in meters |
| `startSpeed` | Initial velocity along local +Y | `ParticleProcessMaterial.direction` / velocity |
| `startColor` | Particle color | Linear RGBA |
| `texture` | Albedo on particle material | Omitted / unresolved → solid tint |
| billboard | Camera-facing draw pass | When the renderer supports it |

`emissionRate` ↔ `amount` mapping is **TBD** until a conformance sample exists.

## Export

Export of authored VFX from Godot is **TBD**. Prefer Blender
([Blender VFX](blender-vfx.md)) as the authoring path until a Godot exporter lands.

If export is added later: write root `extensions.VRMXT_vfx`, add `VRMXT_vfx` to
`extensionsUsed`, and do **not** add it to `extensionsRequired`.

## Validation and fallback

Per emitter, skip (do not fail the whole load) when:

- `type` missing or unknown
- `node` missing, out of range, or `get_scene_node` returns null
- `type` is `"particle"` but `particle` is missing
- Non-finite or negative `emissionRate` / `lifetime` / `startSize` / `startSpeed`
- `maxParticles` not an integer `>= 1`
- Invalid `localPosition` / `localRotation` per the base spec

Stock godot-vrm without the VRMXT addon: avatar imports; no emitters.

## Tests

Minimum coverage (mirror UniVRMXT / Blender VFX intent):

| Case | Expectation |
|------|-------------|
| Import valid emitter on bone / object node | Particle child under resolved node |
| Import bad `node` / invalid scalars | Emitter skipped; VRM otherwise loads |
| Import texture index | Material albedo set when texture resolves |
| Missing `VRMXT_vfx` with addon enabled | No-op; avatar valid |
| Runtime load without EditorPlugin | Autoload register or explicit attach works |
| Empty `emitters` | Valid file; no required extension entry |

## Related

- [VRMXT_vfx](../specs/vrmxt-vfx.md)
- [Extended VRM Architecture](../architecture.md)
- [UniVRM VFX](univrm-vfx.md)
- [three-vrm VFX](three-vrm-vfx.md)
- [Blender VFX](blender-vfx.md)
- [godot-vrm](https://github.com/V-Sekai/godot-vrm)

## Open questions

| Topic | Status |
|-------|--------|
| Final addon id / Asset Library listing | TBD |
| `GPUParticles3D` vs `CPUParticles3D` default | TBD |
| `emissionRate` → `amount` formula | TBD |
| glTF node-local TR vs Godot import basis on bones | TBD (verify on sample) |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |
| Godot export | TBD |
