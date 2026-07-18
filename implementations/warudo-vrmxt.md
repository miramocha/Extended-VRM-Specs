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

Host integration for [VRMXT](../specs/vrmxt-vfx.md) extensions on [Warudo](https://warudo.app/)
Characters. Implementation lives in the **VRMXT Plugin for Warudo** Unity project
(`Assets/Vrmxt/`), exported as a plugin mod to `StreamingAssets/Plugins`.

Related: [Warudo Materials Override](warudo-materials-override.md) (planned on the same
host path), [UniVRM VFX](univrm-vfx.md), [UniVRM upstream hooks](univrm-upstream-hooks.md).

## Goal

After Character **Source** loads a VRM 1.0 `.vrm`, apply VRMXT extensions onto that
Character’s GameObject. No extra scene Asset. No authoring from Warudo in v1.

| Item | Value |
|------|-------|
| Plugin id | `mira.vrmxt` |
| Mod folder | `Assets/Vrmxt` |
| Export | `Warudo_Data/StreamingAssets/Plugins` |
| v1 extension | `VRMXT_vfx` |

## Package split

| Piece | Where |
|-------|-------|
| Extension JSON | `.vrm` glTF |
| Parse + ParticleSystem map | Vendored UniVRMXT Format/Vfx `.cs` under the mod (no UPM/DLL/`.asmdef`) |
| Character watch + byte re-read | `VrmxtPlugin` |
| Stock VRM load | Warudo Character asset |

## Flow (v1)

```
Character Source load (Warudo + UniVRM)
        → Character Active = true
VrmxtPlugin watches Source / Active
        → PersistentDataManager.ReadFileBytesAsync (character://data/… → relative path)
VrmxtCharacterApply
        → VrmxtVfxRuntime.TryAttachFromGlb(Character.GameObject, bytes, nodes)
ParticleSystem children under emitter nodes
```

Node resolve prefers `RuntimeGltfInstance.Nodes`. Fallback: `VrmxtVfxNodeResolver` by
`nodes[].name`.

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

1. Unity 2021.3 + Warudo Mod Tool; Api Compatibility Level **.NET Framework**.
2. **Warudo → Build Mod** with ExportSettings profile `Vrmxt`.
3. Enable plugin in Warudo; load a Character whose `.vrm` contains `VRMXT_vfx`.
