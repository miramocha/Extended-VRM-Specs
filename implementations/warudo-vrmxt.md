---
title: Warudo VRMXT
aliases:
  - VRMXT plugin for Warudo
  - Warudo VTubing VRMXT host
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

Host integration for [VRMXT_vfx](../specs/vrmxt-vfx.md) and
[VRMXT_materials_override](../specs/vrmxt-materials-override.md) on
[Warudo](https://warudo.app/) Characters. Implementation:
[VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo)
(`Assets/Vrmxt/`), exported as a UMod plugin to `StreamingAssets/Plugins`.

Warudo is a **consumer only**: post-load apply onto Characters. No authoring UI and no
re-export of VRMXT extensions from Warudo.

Related: [Warudo Materials Override](warudo-materials-override.md) (apply details),
[UniVRM VFX](univrm-vfx.md), [UniVRM Materials Override](univrm-materials-override.md).

## Goal

After Character **Source** loads a VRM 1.0 `.vrm`, attach:

1. `VRMXT_vfx` → ParticleSystem children
2. `VRMXT_materials_override` → unity-slot shader/properties/bindings on matching mats

| Item | Value |
|------|-------|
| Plugin id | `mira.vrmxt` |
| Mod folder | `Assets/Vrmxt` |
| Export | `Warudo_Data/StreamingAssets/Plugins` |
| Extensions | `VRMXT_vfx`, `VRMXT_materials_override` |
| Plugin version (shipped) | `0.1.1` (see `VrmxtPlugin`) |
| Steam Workshop | [VRMXT](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) |

## Package split

| Piece | Where |
|-------|-------|
| Extension JSON | `.vrm` glTF |
| Parse + VFX map + materials apply | Vendored UniVRMXT Format/Vfx/MaterialsOverride `.cs` under the mod (no UPM/DLL/`.asmdef`) |
| Packaged shaders / mats | Particles Unlit + sample `TestOverrideBuiltin` / `TestOverrideURP` under `Assets/Vrmxt/` |
| Character watch + byte re-read | `VrmxtPlugin` / `VrmxtCharacterApply` |
| Emit-axis correction | `VrmxtWarudoBoneAxisCorrection` (VRM 1.0 **ReverseX**) |
| Stock VRM load | Warudo Character asset |

## Flow

**Status: shipped** (plugin `0.1.1`). Warudo owns stock VRM load; the plugin attaches
after the Character is active.

```
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

### Plugin setting

`Enable VRMXT` (default on) lives on the plugin entity and persists across scenes.
Off: unbind Characters (VFX cleared). Material overrides mutate host materials in
place; reload the scene to restore stock look. On again: re-bind and re-apply.

### UMod compile constraints (non-normative)

- Do **not** read `CharacterAsset.GameObject` or `OnActiveStateChange` / `UnityEvent`
  (CS0012 under UMod).
- Do **not** use `System.Reflection` (includes `GetType().Name`).
- `referencePaths` is for other **mods**, not UnityEngine DLLs.
- Load shaders/materials with **`ModHost.Assets.Load`**, not `Resources.Load`.
- `Shader.Find` returns null for mod-shipped shaders; `VrmxtPlugin` warms assets into
  `VrmxtMaterialsOverrideApplier.ShaderResolveProvider`.
- Materials pipeline detect: host uses `DetectActivePipelineForWarudo` (null → Builtin,
  else Urp). UniVRMXT `DetectActivePipeline` uses `Object.ToString()` for URP/HDRP labels.

### Node resolve (VFX)

`emitters[].node` by GLB `nodes[].name` (`VrmxtVfxNodeResolver`). VFX-only textures
via second GLB read (`VrmxtVfxGlbTextures`); plugin owns them until unbind/reload.

## Local Source URIs only

Accepts `character://data/Characters/….vrm` (and bare `Characters/….vrm`). Workshop and
other schemes are skipped with a log line.

## Out of scope

- Authoring UI or export of VRMXT extensions from Warudo (permanent; consumer host)
- Scene AssetTypes / Blueprint nodes for overrides
- Workshop Character byte access
- Hiding the Character until apply finishes (first-frame stock flash possible)
- `IMaterialDescriptorGenerator` inject on Character load (Warudo does not expose it)

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
