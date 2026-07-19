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

How [VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo)
applies [VRMXT_materials_override](../specs/vrmxt-materials-override.md) on Characters.
Normative fields stay in the base spec and
[UniVRM Materials Override](univrm-materials-override.md).

Warudo is a **consumer only**. Overrides are authored elsewhere (e.g. Blender / UniVRMXT
Editor) and applied after Character load. No Warudo authoring UI.

Host overview: [Warudo VRMXT](warudo-vrmxt.md).

## Goal

After Character **Source** loads a VRM 1.0 `.vrm`, apply `engine: "unity"` override
slots whose `material.variant` matches the active pipeline (Built-in vs URP / Warudo
Pro). Shaders and sample materials ship in the plugin mod.

**Status: shipped** with plugin `0.1.1` (same mod as VFX).

## Package split

| Piece | Where |
|-------|-------|
| Override JSON | `.vrm` glTF |
| Parse + Applier + Instance | Vendored UniVRMXT MaterialsOverride under `Assets/Vrmxt/` |
| Sample shaders / mats | `VRMXT/Samples/TestOverrideBuiltin`, `VRMXT/Samples/TestOverrideURP` |
| Watch + GLB re-read + apply | `VrmxtPlugin` / `VrmxtCharacterApply` |
| Stock VRM load | Warudo Character asset |

## Why post-load re-read

Warudo owns Character Source loading. Mod Tool stubs do not expose
`IMaterialDescriptorGenerator`, retained `GltfData`, or a post-parse extension callback.
UniVRM’s `GltfData.Json` is gone after the host dispose. The plugin re-reads Character
bytes via `PersistentDataManager`, parses JSON, then applies onto live materials.

```
Character Source load (stock materials)
        → Character active
Plugin reads bytes → glTF JSON
TryAttachFromGltfJson → RememberTexturesFromPairs(resolver, json)
        → ReleaseOwnership
Apply(root, store, json, pipeline, resolveTexture)
```

Apply order relative to VFX: VFX first (while GLB texture ownership is live), then
materials Remember + Release + Apply.

## Pipeline and shaders

| Concern | Behavior |
|---------|----------|
| Active RP | `DetectActivePipelineForWarudo`: `currentRenderPipeline == null` → Builtin, else Urp |
| Slot select | UniVRMXT `UnityOverrideSelector` (`variant` match among `unity` siblings) |
| Shader resolve | ModHost-warmed name→Shader map → `ShaderResolveProvider` (`Shader.Find` is null for mod shaders) |
| Sample URP shader | CG + `SRPDefaultUnlit`; no URP package includes (Mod Tool must ship a drawable pass without `PackageRequirements`) |

## Material name match

Store keys keep glTF `materials[].name` (including a trailing ` (Instance)` when present).
Live `sharedMaterials` names are matched after stripping ` (Instance)` on both sides so
clone-export keys hit Warudo’s live names. Duplicate names use `Name#N` keys;
`GltfMaterialIndex` on pairs drives sibling MToon / binding texture resolve.

## Textures

`RememberTexturesFromPairs` collects indices from override `properties[]` and from MToon
`bindings` that target textures (needs glTF JSON before GLB release). Apply resolves
textures from `ImportedTextures` after ownership release.

## Missing shader / variant

Unresolved shader or non-matching variant: leave stock material for that entry (JSON
may still sit on the Instance).

## First-frame flash

Stock MToon/PBR may show briefly before apply. No hide-until-ready in current plugin.

## Enable toggle

Plugin `Enable VRMXT` gates bind/apply. Disable clears VFX immediately. Material
overrides stay on mutated host mats until the **scene is reloaded**.

## Out of scope

- Authoring or export of overrides from Warudo
- Load-time `IMaterialDescriptorGenerator` inject
- Workshop Character byte access (local `character://` / `Characters/…` only)

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Host: [Warudo VRMXT](warudo-vrmxt.md)
- Unity profile: [UniVRM Materials Override](univrm-materials-override.md)
- UniVRMXT samples: Test Materials for Overrides (`TestOverrideBuiltin` / `TestOverrideURP`)
