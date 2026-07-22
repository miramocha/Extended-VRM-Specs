---
title: Warudo VRMXT
aliases:
  - VRMXT plugin for Warudo
  - Warudo VTubing VRMXT host
  - VRMXT materials override for Warudo
  - Warudo Materials Override
tags:
  - extended-vrm
  - implementation/warudo
  - implementation/unity
  - spec/vfx
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Warudo VRMXT

Host integration for [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md) and
[VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md) on
[Warudo](https://warudo.app/) Characters. Implementation:
[VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo)
(`Assets/Vrmxt/`), exported as a UMod plugin to `StreamingAssets/Plugins`.

Warudo remains a runtime consumer: the plugin applies VRMXT data after Character load.
A planned export utility will rewrite VRMXT JSON into a copy of the original local VRM.
It will not export live geometry or other Warudo scene state.

Related: [UniVRMXT](univrm-vrmxt.md).
Planned Hub WebGL viewer uses the same Unity `2021.3.45f2` pin:
[Unity WebGL VRMXT viewer](unity-webgl-vrmxt-viewer.md),
[VRoid Hub browser viewer architecture](../decisions/vroid-hub-browser-viewer-architecture.md).

## Goal

After Character **Source** loads a VRM 1.0 `.vrm`, attach:

1. `VRMXT_sprite_particle` → ParticleSystem children
2. `VRMXT_materials_override` → unity-slot shader/properties/bindings on matching mats

| Item | Value |
|------|-------|
| Plugin id | `mira.vrmxt` |
| Mod folder | `Assets/Vrmxt` |
| Export | `Warudo_Data/StreamingAssets/Plugins` |
| Extensions | `VRMXT_sprite_particle`, `VRMXT_materials_override` |
| Plugin version (shipped) | `0.1.1` (see `VrmxtPlugin`) |
| Steam Workshop | [VRMXT](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) |
| Warudo Mod Tool | `0.14.5.1` (`app.warudo.modtool` `#upm/0.14.5.1`) |
| UniVRM (Warudo runtime) | `0.130.1` (`UniGLTF.PackageVersion` / `UniGLTFVersion` `2.66.1` in `Warudo_Data/Managed/UniGLTF.dll`) |
| UniVRM (Mod Tool editor) | `0.129.1` (`com.vrmc.*@96a7b03851` embedded in Mod Tool `0.14.5.1`) |
| Source-preserving export | Planned in [VRMXT Plugin for Warudo #8](https://github.com/miramocha/VRMXT-Plugin-for-Warudo/issues/8) |

## Package split

| Piece | Where |
|-------|-------|
| Extension JSON | `.vrm` glTF |
| Parse + VFX map + materials apply | Vendored UniVRMXT Format/Vfx/MaterialsOverride `.cs` under the mod (no UPM/DLL/`.asmdef`) |
| Packaged shaders / mats | Particles Unlit + sample `TestOverrideBuiltin` / `TestOverrideURP` under `Assets/Vrmxt/` |
| Character watch + byte re-read | `VrmxtPlugin` / `VrmxtCharacterApply` |
| Emit-axis correction | `VrmxtWarudoBoneAxisCorrection` (VRM 1.0 **ReverseX**) |
| Stock VRM load | Warudo Character asset |
| Planned export | Original GLB bytes + rewritten VRMXT JSON; sandboxed `PersistentDataManager` output |

## Flow

**Status: shipped** (plugin `0.1.1`). Warudo owns stock VRM load; the plugin attaches
after the Character is active.

```text
Character Source load (Warudo + UniVRM)
        → Character becomes active (plugin polls; no OnActiveStateChange)
VrmxtPlugin (if Enable VRMXT)
        → PersistentDataManager.ReadFileBytesAsync
VrmxtCharacterApply
        → resolve Character root (name / hierarchy; not CharacterAsset.GameObject)
        → VrmxtVfxRuntime.TryAttachFromGlb …
        → VrmxtWarudoBoneAxisCorrection
        → materials: TryAttachFromGltfJson → RememberTexturesFromPairs(json)
          → ReleaseOwnership → Apply (pipeline + ShaderResolveProvider)
```

## VFX

### Node resolve

`emitters[].node` by GLB `nodes[].name` (`VrmxtVfxNodeResolver`). VFX-only textures
via second GLB read (`VrmxtVfxGlbTextures`); plugin owns them until unbind/reload.

## Materials override

After Character **Source** loads a VRM 1.0 `.vrm`, the plugin applies `engine: "unity"`
override slots whose `material.variant` matches the active pipeline. Shaders and sample
materials ship in the plugin mod.

### Why post-load re-read

Warudo owns Character Source loading. Mod Tool stubs do not expose
`IMaterialDescriptorGenerator`, retained `GltfData`, or a post-parse extension callback.
UniVRM disposes the `GltfData` that held the source JSON. The plugin reads the Character
bytes through `PersistentDataManager`, parses the glTF JSON, and applies the override to
live materials.

Materials apply after VFX while GLB texture ownership is live:

```text
Character Source load (stock materials)
        → Character active
Plugin reads bytes → glTF JSON
TryAttachFromGltfJson → RememberTexturesFromPairs(resolver, json)
        → ReleaseOwnership
Apply(root, store, json, pipeline, resolveTexture)
```

### Character material catalog

Apply mutates live renderer materials in place. The plugin does not write
`CharacterAsset.Materials`; accessing Warudo members typed with
`UnityEngine.Material` causes UMod compiler error CS0012 because Warudo and the mod
reference different `UnityEngine` assemblies.

After apply, the plugin rebuilds `CharacterAsset.MaterialProperties` for overridden
keys. It matches store and live material names using the same `(Instance)` suffix
normalization as apply, enumerates each live shader locally, and writes the resulting
`List<ShaderProperty>` into the existing catalog. This changes the Character material UI
catalog from MToon to the active override shader.

Warudo's `Shader.GetShaderProperties()` extension cannot be called from the mod because
its CoreModule `Shader` parameter also triggers CS0012.

### Pipeline and shaders

| Concern | Behavior |
|---------|----------|
| Active RP | `DetectActivePipelineForWarudo`: `currentRenderPipeline == null` → Builtin, else Urp |
| Slot select | UniVRMXT `UnityOverrideSelector` (`variant` match among `unity` siblings) |
| Shader resolve | ModHost-warmed name-to-Shader map → `ShaderResolveProvider` (`Shader.Find` returns null for mod shaders) |
| Sample URP shader | CG + `SRPDefaultUnlit`; no URP package includes |

The Mod Tool must ship a drawable sample URP pass without `PackageRequirements`.

### Material matching

Store keys retain glTF `materials[].name`, including a trailing ` (Instance)` when
present. Live `sharedMaterials` names are matched after stripping ` (Instance)` from
both sides. Duplicate names use `Name#N` keys. `GltfMaterialIndex` on pairs drives
sibling MToon and binding texture resolution.

### Textures

`RememberTexturesFromPairs` collects indices from override `properties[]` and
texture-targeting MToon `bindings` before GLB release. Apply resolves textures from
`ImportedTextures` after ownership release.

An unresolved shader or unmatched variant leaves the stock material in place for that
entry. Stock MToon or PBR may appear briefly before the override is applied.

## Plugin setting

`Enable VRMXT` (default on) lives on the plugin entity and persists across scenes.
Disabling it unbinds Characters and clears VFX. Material overrides remain on mutated
host materials until the scene reloads. Enabling it again rebinds and reapplies.

## Planned source-preserving export

**Status: planned.** See the
[export plan](../references/warudo-source-preserving-vrmxt-export.md) and
[VRMXT Plugin for Warudo #8](https://github.com/miramocha/VRMXT-Plugin-for-Warudo/issues/8).

The trigger will read the original local Character VRM, replace supported VRMXT objects
in its glTF JSON, rebuild the GLB around the unchanged BIN payload, and write a separate
file through `PersistentDataManager`.

Initial support covers `VRMXT_materials_override`. Existing root
`VRMXT_sprite_particle` JSON and unrelated extensions pass through unchanged. The
utility does not export live geometry, pose, spring-bone state, or other Warudo scene
changes.

Implementation adds one generic GLB rebuild helper to authoritative UniVRMXT
`GlbChunks.cs`; Warudo-specific injection and file handling stay in host code.

## UMod compile constraints

These constraints describe the current Warudo Mod Tool and are non-normative:

- Do **not** read `CharacterAsset.GameObject` or `OnActiveStateChange` / `UnityEvent`
  (CS0012 under UMod).
- Do **not** use `System.Reflection` (includes `GetType().Name`).
- Do **not** use `System.IO`; file reads and writes use `PersistentDataManager`.
- `referencePaths` is for other mods, not UnityEngine DLLs.
- Load shaders and materials with `ModHost.Assets.Load`, not `Resources.Load`.
- `Shader.Find` returns null for mod-shipped shaders. `VrmxtPlugin` warms assets into
  `VrmxtMaterialsOverrideApplier.ShaderResolveProvider`.
- Pipeline detection uses `DetectActivePipelineForWarudo`: null means Builtin; any
  active render pipeline means Urp.

## Local Source URIs only

Apply and planned export accept `character://data/Characters/….vrm` (and bare
`Characters/….vrm`). Workshop and other schemes are skipped with a log line.

## Out of scope

- General live-avatar VRM export
- Automatic overwrite or replacement of the loaded Character source
- New GLB image payloads in the first source-preserving export
- Scene AssetTypes / Blueprint nodes for overrides
- Workshop Character byte access
- Hiding the Character until apply finishes (first-frame stock flash possible)
- `IMaterialDescriptorGenerator` inject on Character load (Warudo does not expose it)
- Assigning into `CharacterAsset.Materials` (UMod CS0012)
- Rewriting expression or blend-shape `MaterialPropertyEntry` lists after apply

## Build

1. Unity `2021.3.45f2` + Warudo Mod Tool; Api Compatibility Level **.NET Framework**;
   Assembly Version Validation **off**.
2. Local Mod Settings: copy `umod/ExportSettings.example.asset` →
   `Assets/ExportSettings.asset` (gitignored). Backup/restore:
   `umod/export-settings.ps1 -Backup` / `-Restore`. Restore **after** script recompile
   settles (UMod wipes profiles on code change).
3. Editor project may use URP (`Assets/Settings/VrmxtUniversalRP`, outside the mod
   folder) so sample URP shaders compile; that does not change Warudo’s runtime RP.
4. **Warudo → Build Mod** profile **VRMXT**.
5. Enable plugin in Warudo; load a Character whose `.vrm` contains the extensions.

Repo: https://github.com/miramocha/VRMXT-Plugin-for-Warudo  
Steam Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210
