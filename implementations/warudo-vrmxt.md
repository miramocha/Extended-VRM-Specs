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
  - compatibility/vrm1
type: guide
status: draft
---

# Warudo VRMXT

Host integration for [VRMXT_vfx](../specs/vrmxt-vfx.md) on [Warudo](https://warudo.app/)
Characters. Implementation: [VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo)
(`Assets/Vrmxt/`), exported as a UMod plugin to `StreamingAssets/Plugins`.

Related: [Warudo Materials Override](warudo-materials-override.md) (planned on the same
host path), [UniVRM VFX](univrm-vfx.md), [UniVRM upstream hooks](univrm-upstream-hooks.md).

## Goal

After Character **Source** loads a VRM 1.0 `.vrm`, apply `VRMXT_vfx` onto that
Character’s GameObject. No extra scene Asset. No authoring from Warudo in v1.

| Item | Value |
|------|-------|
| Plugin id | `mira.vrmxt` |
| Mod folder | `Assets/Vrmxt` |
| Export | `Warudo_Data/StreamingAssets/Plugins` |
| v1 extension | `VRMXT_vfx` |
| Plugin version (shipped) | `0.0.4` (see `VrmxtPlugin`) |

## Package split

| Piece | Where |
|-------|-------|
| Extension JSON | `.vrm` glTF |
| Parse + ParticleSystem map | Vendored UniVRMXT Format/Vfx `.cs` under the mod (no UPM/DLL/`.asmdef`) |
| Packaged particle shader / mat | `Assets/Vrmxt/Shaders/VrmxtParticlesUnlit.shader` (`VRMXT/Particles Unlit`), `Resources/UniVRMXT/ParticlesUnlit.mat` |
| Character watch + byte re-read | `VrmxtPlugin` / `VrmxtCharacterApply` |
| Emit-axis correction | `VrmxtWarudoBoneAxisCorrection` (VRM 1.0 **ReverseX**; Warudo humanoid normalize zeros bone local rotations) |
| Stock VRM load | Warudo Character asset |

## Flow (v1)

**Status: shipped** on plugin `main` (plugin version `0.0.4`). Warudo owns stock VRM
load; the plugin attaches after the Character is active.

```
Character Source load (Warudo + UniVRM)
        → Character becomes active (plugin polls; does not use OnActiveStateChange)
VrmxtPlugin
        → PersistentDataManager.ReadFileBytesAsync (character://data/… → relative path)
VrmxtCharacterApply
        → resolve Character root via name / hierarchy walk (not CharacterAsset.GameObject)
        → VrmxtVfxRuntime.TryAttachFromGlb(root, bytes, …)
        → VrmxtWarudoBoneAxisCorrection on emitter parents
ParticleSystem children under emitter nodes
```

### UMod compile constraints (non-normative)

UMod cannot see CoreModule-typed Warudo API surfaces the same way as Editor play mode:

- Do **not** read `CharacterAsset.GameObject` or `OnActiveStateChange` / `UnityEvent`
  (CS0012 under UMod).
- Do **not** use `System.Reflection` (UMod code security).
- `referencePaths` is for other **mods**, not UnityEngine DLLs.
- Load shaders/materials with **`ModHost.Assets.Load`**, not `Resources.Load` (Unity
  Resources cannot see uMod assets). `VrmxtPlugin` binds the packaged particle mat and
  sets UniVRMXT `PreferPackagedParticleMaterial` / `PackagedMaterialProvider`.

### Node resolve

v1 resolves `emitters[].node` by GLB `nodes[].name` lookup (`VrmxtVfxNodeResolver`)
against the Character hierarchy. Preferring `RuntimeGltfInstance.Nodes` is optional
when UniGLTF types are available to the mod; not required for v1.

VFX-only textures are decoded on the second GLB read (`VrmxtVfxGlbTextures`). The plugin
owns those textures until the Character reloads or is unbound.

## Local Source URIs only

v1 accepts `character://data/Characters/….vrm` (and bare `Characters/….vrm` paths).
Workshop and other schemes are skipped with a log line.

## Later: materials override

Same watch + byte re-read. Extend `VrmxtCharacterApply` to honor
`VRMXT_materials_override` after VFX (or in parallel). See
[warudo-materials-override.md](warudo-materials-override.md). Vendor
`VrmxtMaterialsOverride.cs` when that lands.

## Out of scope (v1)

- Scene AssetTypes / Blueprint nodes
- Authoring or export of `VRMXT_vfx` from Warudo
- Workshop Character byte access
- Hiding the Character until apply finishes (first-frame stock flash possible)

## Build

1. Unity `2021.3.45f2` + Warudo Mod Tool; Api Compatibility Level **.NET Framework**;
   Assembly Version Validation **off**.
2. Local Mod Settings: copy `umod/ExportSettings.example.asset` →
   `Assets/ExportSettings.asset` (gitignored; machine paths). Optional backup:
   `umod/export-settings.ps1 -Backup` / `-Restore` (`.old` twin UMod does not wipe).
3. **Warudo → Build Mod** with profile **VRMXT** (mod folder `Assets/Vrmxt`).
4. Enable plugin in Warudo; load a Character whose `.vrm` contains `VRMXT_vfx`.
5. Rebuild after pulling shader/Resources under `Assets/Vrmxt/`.

Repo README: https://github.com/miramocha/VRMXT-Plugin-for-Warudo
