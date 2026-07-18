---
title: Warudo Materials Override
aliases:
  - VRMXT materials override for Warudo
  - Warudo VTubing VRMXT
tags:
  - extended-vrm
  - implementation/warudo
  - implementation/unity
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Warudo Materials Override

Host integration notes for applying
[VRMXT_materials_override](../specs/vrmxt-materials-override.md) when a VRM 1.0 avatar
loads in [Warudo](https://warudo.app/) (VTubing). Normative override fields stay in the
base spec and the [UniVRM Materials Override](univrm-materials-override.md) profile.
This note records what Warudo’s public docs and Mod SDK expose today, and a workable
plugin path.

Sources reviewed (2026-07):

- [Warudo Handbook](https://docs.warudo.app/) / [HakuyaLabs/warudo-docs](https://github.com/HakuyaLabs/warudo-docs)
- [HakuyaLabs/Warudo-Mod-Tool](https://github.com/HakuyaLabs/Warudo-Mod-Tool) (`app.warudo.modtool` 0.14.5)
- UniVRM `GltfData` / `Vrm10.LoadGltfDataAsync` lifetime (JSON on parse object only)

## Goal

After the user selects a `.vrm` as Character **Source**, honor
`materials[i].extensions.VRMXT_materials_override` entries with `engine: "unity"`,
using shaders and materials shipped in a **Warudo plugin mod** (not the base Warudo
player build).

## Package split

| Piece | Where it lives |
|-------|----------------|
| Override JSON in the avatar | `.vrm` glTF (`VRMXT_materials_override`) |
| Unity shaders / material assets | Warudo **plugin mod** (`ModHost` load) |
| Parse + apply logic | Plugin C# (loose `.cs`; Format layer from [UniVRMXT](https://github.com/miramocha/UniVRMXT) or equivalent) |
| Stock VRM load | Warudo Character asset (UniVRM inside the app) |

Warudo plugin mods MAY include Unity assets (prefabs, materials, shaders). They MUST
NOT rely on third-party DLLs or `.asmdef` packages. Ship parse helpers as source under
the mod folder. See Warudo [Plugin Mod](https://docs.warudo.app/docs/scripting/plugin-mod)
limitations.

## Ideal UniVRM path (not available in Warudo today)

The UniVRM profile wraps `IMaterialDescriptorGenerator` and passes it into
`Vrm10.LoadPathAsync` / `LoadBytesAsync` / `LoadGltfDataAsync` so materials are built
correctly on first import. Warudo owns Character Source loading. Public docs and Mod
Tool API stubs do **not** expose:

- A `materialGenerator` inject point on Character load
- A retained `GltfData` or glTF JSON string on the loaded character
- A documented `OnVRMLoaded` / post-parse extension callback

## UniVRM JSON lifetime

UniVRM exposes JSON on **`GltfData.Json`** while the parse object is alive. Typical
callers dispose `GltfData` when the `using` ends after `LoadGltfDataAsync`. Loaded
components (`Vrm10Instance`, `RuntimeGltfInstance`) keep nodes, materials, textures,
and meshes. They do **not** keep the glTF JSON string.

So: once Warudo’s Character is active in the scene, the parse-time JSON is gone unless
the host kept `GltfData` (undocumented; Mod Tool `CharacterAsset` stubs show no such
field).

## Practical Warudo path: post-load re-read

Re-open the same `.vrm` after Character becomes active, parse override JSON, then swap
or rebuild materials on the live avatar.

```
Character Source load (Warudo + UniVRM, stock materials)
        → WatchAsset / active = true
Plugin resolves Source → file bytes
        → parse GLB JSON chunk
materials[i].extensions.VRMXT_materials_override
        → Shader.Find / materials from plugin mod
apply to Character renderers / Materials map
```

### Load hook

Use [Data Input Watchers](https://docs.warudo.app/docs/scripting/api/watchers)
`WatchAsset` on a `CharacterAsset` reference. When `Source` changes, Warudo sets active
`false`, then `true` after a successful load. Guard with `IsNonNullAndActive()` before
touching the GameObject.

`OnSceneLoaded` on a `Plugin` runs after deserialize. Prefer `WatchAsset` for avatar
reload within a scene.

### Reading bytes

Plugin mods cannot use `System.IO`. Use
[PersistentDataManager](https://docs.warudo.app/docs/scripting/api/io)
(`ReadFileBytesAsync`) against paths under Warudo’s data folder.

`CharacterAsset` inherits `FromSourceGameObjectAsset.Source` (resource URI such as
`character://data/Characters/MyModel.vrm`). Resolve URI → sandbox-relative path before
read. Workshop or non-file URIs need explicit handling; TBD if PersistentDataManager
covers every provider.

### Parsing

- Prefer Newtonsoft.Json (available in Warudo scripting / Mod Tool deps).
- UniVRMXT Format `VrmxtMaterialsOverride` can parse per-material extension objects;
  walk `materials[]` from the full glTF JSON.
- Optional: if the plugin can call UniGLTF types already loaded in Warudo, parse with
  `GlbLowLevelParser` / `GltfData.Json` on a **new** parse of the re-read bytes, then
  dispose. Do not expect Warudo’s first-load `GltfData` to still exist.

### Applying overrides

Post-load apply (approximate):

1. Select `engine: "unity"` (and matching `variant` for Built-in vs URP / Warudo Pro).
2. Resolve `material.name` via `Shader.Find` (shader must be in the plugin mod / player).
3. Map glTF material index → Unity materials on the Character (`CharacterAsset.Materials`,
   renderers, or `Vrm10Instance` / `RuntimeGltfInstance` when present).
4. Apply `bindings` (`scalar` / `vector` / `texture` / `staticSwitch`). Reuse textures
   already imported on the avatar where possible.
5. On missing shader or failed resolve, leave Warudo’s stock material for that index.

This is weaker than load-time `MaterialDescriptor` generation: first frames may show
stock MToon/PBR, then swap. Document that flash or hide the character until apply
finishes if needed.

### What CharacterAsset keeps (Mod Tool stubs)

Public surface useful after load (implementations are stubs in Mod Tool; runtime is in
the Warudo app):

| Member | Role |
|--------|------|
| `Source` | Resource URI for the avatar file |
| `Vrm10Instance` | VRM 1.0 instance when used |
| `VRMBlendShapeProxy` | VRM 0.x blend shapes |
| `Animator`, `MainTransform` | Hierarchy access |
| `Materials`, `SkinnedMeshRenderers` | Material / mesh maps for swap |

No `GltfData` / `Json` on that surface.

## Alternate paths

| Path | Fit |
|------|-----|
| Character expression **Target Material Properties** | Property tweaks only; not full shader override |
| Character **`.warudo` mod** with baked materials | Offline bake; no runtime `VRMXT_materials_override` parse unless you also store JSON |
| Custom Character `IResourceUriResolver` | Would replace Character load; high risk vs expressions / mocap |
| NiloToon Character Controller (Pro) | Precedent for a material controller asset; NiloToon-specific |

## Mod Tool notes

[Warudo-Mod-Tool](https://github.com/HakuyaLabs/Warudo-Mod-Tool) ships:

- `Warudo.Core` / `Warudo.Plugins.Core` API stubs for compiling plugins
- UniVRM **0.129.1** (`com.vrmc.gltf`, `com.vrmc.univrm`, `com.vrmc.vrm`) for editor
  character-mod authoring
- UMod export (`Warudo → Build Mod`), Setup Character window

Use it to build the plugin mod that carries shaders and apply scripts. It does not add
a Character load-time generator hook.

## Compatibility

| Item | Notes |
|------|-------|
| VRM version | VRM 1.0 `.vrm` with `VRMXT_materials_override` |
| `.warudo` character mods | Prefab pipeline; extension JSON not present unless separately authored |
| Warudo Pro URP | Match override `variant` to active pipeline; ship URP-compatible shaders in the plugin |
| UniVRMXT UPM | Cannot drop as DLL/asmdef into a plugin mod; copy needed Format `.cs` or reimplement |

## Open questions

- Exact mapping from `character://` URI to `PersistentDataManager` path for local and
  Workshop Characters.
- Whether Warudo ever retains `GltfData` or raw JSON (none on Mod Tool stubs).
- Stable material-index ↔ renderer slot mapping after Warudo’s own material setup.
- Upstream feature request: expose post-load glTF JSON and/or `materialGenerator` on
  Character Source load.

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Unity profile: [UniVRM Materials Override](univrm-materials-override.md)
- Warudo scripting: [Watchers](https://docs.warudo.app/docs/scripting/api/watchers),
  [IO](https://docs.warudo.app/docs/scripting/api/io),
  [Plugin Mod](https://docs.warudo.app/docs/scripting/plugin-mod)
- Mod SDK: [Warudo-Mod-Tool](https://github.com/HakuyaLabs/Warudo-Mod-Tool)
