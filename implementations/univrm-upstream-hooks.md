---
title: UniVRM upstream hooks
aliases:
  - UniVRM ScriptedImporter hooks
  - UniVRMXT AssetDatabase workaround
tags:
  - extended-vrm
  - implementation/unity
  - implementation/univrm
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# UniVRM upstream hooks

Working notes from UniVRMXT `VRMXT_vfx` Editor integration. Record what blocked
patching the **original** imported `.vrm` prefab on stock UniVRM, what UniVRMXT does
instead, what [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) already
ships, and remaining hooks for [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM).

## Fork and upstream intent

[Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) is a fork of
[vrm-c/UniVRM](https://github.com/vrm-c/UniVRM). It adds a **generic** `.vrm`
ScriptedImporter extension API (`IVrm10ImportExtension` /
`Vrm10ImportExtensionRegistry`) — not UniVRMXT-specific. The plan is to propose that
hook surface upstream so stock UniVRM hosts can load optional packages without this fork.

Same pattern on Blender:
[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender)
ships generic VRM1 hooks to propose to
[saturday06/VRM-Addon-for-Blender](https://github.com/saturday06/VRM-Addon-for-Blender)
— see [blender-extension-hooks.md](blender-extension-hooks.md).

Related: [univrm-vfx.md](univrm-vfx.md), UniVRMXT
[architecture.md](https://github.com/miramocha/UniVRMXT/blob/main/docs/architecture.md),
[vfx-particle-mapping.md](https://github.com/miramocha/UniVRMXT/blob/main/docs/vfx-particle-mapping.md).

## Symptoms

### 1. Cannot mutate the ScriptedImporter main asset after import

UniVRM builds the avatar in `VrmScriptedImporter` → `VrmScriptedImporterImpl.Import` /
`Process`, via `AssetImportContext` (`AddObjectToAsset`, `SetMainObject`).

After import, `AssetPostprocessor.OnPostprocessAllAssets` can load the `.vrm` with
`AssetDatabase.LoadAssetAtPath<GameObject>`, but:

- `GameObject.AddComponent<T>()` on that main object returns **null** (or otherwise fails).
- Hierarchy edits on that object are not a supported extension point.
- The next reimport **rebuilds** the asset from the file, so any fragile patch would be wiped
  unless applied inside `OnImportAsset`.

So UniVRMXT cannot attach `VrmxtVfxInstance` / `ParticleSystem` children onto the stock
`.vrm` prefab from an optional consumer package alone (without an in-import hook).

Extended-UniVRM solves this with `IVrm10ImportExtension` during `Process` (see
[Current workaround](#current-workaround-univrmxt-mvp)). On stock UniVRM, use the companion
`*.vrmxt.prefab` path.

`Object.Instantiate` of the importer asset was tried and rejected: it broke sub-asset
material references (null `sharedMaterials`), which then NRE’d in
`Vrm10InstanceEditor.OnEnable` when indexing `m.name`. Prefer `PrefabUtility.InstantiatePrefab`.

### 2. Imported prefabs drop `RuntimeGltfInstance`

Runtime loads keep `RuntimeGltfInstance.Nodes` (stable glTF node index → `Transform`).
AssetDatabase imports do **not** (UniVRM treats missing `RuntimeGltfInstance` as “prefab
instance”). Node indices for `VRMXT_vfx` must be resolved another way (UniVRMXT uses
`nodes[].name` matching).

### 3. VFX-only `textures[]` are never imported

`Vrm10TextureDescriptorGenerator` enumerates textures from:

- materials (MToon / PBR / unlit)
- VRM meta thumbnail

It does **not** walk root extensions. A texture referenced only by
`extensions.VRMXT_vfx.emitters[].particle.texture` never becomes a `Texture2D` sub-asset.

Example: `vfx_smoke.vrm` has `materials: []`, one mesh with no material index, and one
`textures[]` / `images[]` entry used solely by a particle emitter. Stock import has no
usable particle albedo.

See [Current workaround](#current-workaround-univrmxt-mvp) (second GLB read / `TryAttachFromGlb`).

### 4. Runtime hosts (Warudo, loaders) never see companion prefabs

Character Source / `LoadGltfDataAsync` paths ignore AssetDatabase companions. They need
the same post-load attach + optional second file read. Companion prefabs are an Editor
convenience only.

## Current workaround (UniVRMXT MVP)

Two Editor paths; runtime unchanged. Attach/decode code is shared in
[UniVRMXT](https://github.com/miramocha/UniVRMXT).

### Editor + Extended-UniVRM (import hooks)

Extended-UniVRM ships `IVrm10ImportExtension` / `Vrm10ImportExtensionRegistry` and invokes
handlers from `VrmScriptedImporterImpl.Process` while `AssetImportContext` is live.

Invocation is gated by **Project Settings → VRM10 → Enable VRM Import Extensions**
(`Vrm10ProjectEditorSettings.EnableImportExtensions`, default on; stored inverted as
`disableImportExtensions` so older ProjectSettings assets missing the field stay enabled).
When that setting is off, `InvokeAll` is a no-op and UniVRMXT treats hooks as unavailable
(companion prefab path).

UniVRMXT soft-detects the registry type (`VRM10.Editor`) and `IsEnabled`, then registers a
handler that runs `TryAttachFromGlb` on the **original** `.vrm` root (node list from
import-time `Nodes`). No companion prefab. Stale `*.vrmxt.prefab` files are deleted on
reimport when hooks are enabled.

### Editor + stock UniVRM or hooks disabled (companion prefab)

When `Vrm10ImportExtensionRegistry` is absent, or Project Settings disable import extensions:

| Step | What |
|------|------|
| 1 | User imports / reimports `Model.vrm` (stock UniVRM ScriptedImporter). |
| 2 | `VrmxtVfxAssetPostprocessor` runs on `.vrm` import. |
| 3 | Read file bytes: `GlbChunks` → JSON; `VrmxtVfx.TryParse` (no-op if extension missing). |
| 4 | `PrefabUtility.InstantiatePrefab` the imported root (keeps material sub-asset links). |
| 5 | Resolve `emitters[].node` by `nodes[].name` → `Transform` (`VrmxtVfxNodeResolver`). |
| 6 | `TryAttachFromGlb` — particles + VFX-only texture decode. |
| 7 | Save sibling **`Model.vrmxt.prefab`**. |
| 8 | Scenes use **`Model.vrmxt.prefab`**. Raw `Model.vrm` stays avatar-only. |

**Do not** place the raw `.vrm` in the scene expecting particles when using stock UniVRM.

### Runtime / Warudo (no companion)

| Step | What |
|------|------|
| 1 | Host loads `.vrm` with stock UniVRM (`Vrm10.LoadGltfDataAsync` / Character Source). |
| 2 | Keep or re-read the same file **bytes**. |
| 3 | `TryAttachFromGlb(root, bytes, RuntimeGltfInstance.Nodes, …)` (or name resolver if no node list). |
| 4 | Dispose `VrmxtVfxGlbTextures` when the avatar is destroyed (or `ReleaseOwnership` if textures were saved into an asset). |

```csharp
var bytes = File.ReadAllBytes(path);
// … stock Vrm10.LoadGltfDataAsync …
var nodes = vrm.GetComponent<RuntimeGltfInstance>().Nodes;
VrmxtVfxRuntime.TryAttachFromGlb(
    vrm.gameObject, bytes, nodes, out var vfx, out var glbTextures);
```

### Shared pieces (UniVRMXT)

| Piece | Role |
|-------|------|
| `VrmxtVfxRuntime.TryAttach` / `TryAttachFromGlb` | Parse + attach + optional `ParticleSystem` build |
| `VrmxtVfxParticleSystemMapper` | Field map, billboard, BIRP/URP unlit material |
| `VrmxtVfxGlbTextures` | Second-read decode of extension-only textures |
| `VrmxtVfxImportHookBootstrap` | Soft-register import handler when Extended-UniVRM hooks exist |
| `VrmxtVfxAssetPostprocessor` | Companion prefab fallback for stock UniVRM |

## What we want from upstream UniVRM (vrm-c)

Hook **A** is implemented in **Extended-UniVRM**. Remaining asks for stock
[vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) (or further Extended work):

### A. Post-import / in-import extension callback — done in Extended-UniVRM

`IVrm10ImportExtension`, `Vrm10ImportExtensionContext`, `Vrm10ImportExtensionRegistry`
(`Register` / `RegisterHandler(Action<object>)` for soft consumers; `IsEnabled` reads
`Vrm10ProjectEditorSettings.EnableImportExtensions`). Invoked from
`VrmScriptedImporterImpl.Process` after ownership transfer, before `RuntimeGltfInstance`
destroy, only when the project setting is on.

Upstream vrm-c adoption would let stock UniVRM hosts use the same path without the fork.

### B. Preserve or expose import-time node index map

Even without a full extension callback:

- Keep a serialized `IReadOnlyList<Transform>` (or instance ID map) on the imported root, or
- Document a stable public API to rebuild index → `Transform` after import.

Today name matching works for unique bone/helper names but is weaker than
`RuntimeGltfInstance.Nodes`.

### C. Texture enumeration hook or “include unused textures”

Either:

1. `ITextureDescriptorGenerator` wrapper already exists for materials — extend the default
   VRM10 generator (or add a second pass) so packages can **register extra texture indices**
   to import; or
2. Optional importer flag / setting: import all `textures[]` / `images[]` even if unreferenced
   by materials (heavier; simple).

**Why:** Removes the second GLB decode for particle (and future extension) images. Sub-assets
would share UniVRM’s normal remap / extract workflow.

### D. Retain glTF JSON (or extension blobs) on the loaded instance (runtime)

Runtime hosts dispose `GltfData` after load; JSON is gone. A retained
`extensions.VRMXT_*` blob (or full JSON) on `Vrm10Instance` / `RuntimeGltfInstance` would
avoid re-opening the file for Warudo-style post-load apply.

Lower priority for AssetDatabase prefab editing; high value for runtime hosts.

## Non-goals / out of scope for upstream asks

- Full Unity VFX authoring/export UI (Blender remains preferred authoring).
- Forcing `VRMXT_vfx` into `extensionsRequired` (must stay optional).
- Changing stock load success when UniVRMXT is absent.

## Decision log (UniVRMXT / Extended-UniVRM)

| Date | Decision |
|------|----------|
| 2026-07 | MVP without fork: companion `*.vrmxt.prefab` + `TryAttachFromGlb`. |
| 2026-07 | Prefer upstream **A + C**; implement **A** in Extended-UniVRM first. |
| 2026-07 | Extended-UniVRM ships import extension registry; UniVRMXT soft-detects and dual-paths. |
| 2026-07 | Project Settings/VRM10 gate for import extensions; off → companion prefab. |

## Links into UniVRM source (0.131.x / Extended-UniVRM)

| Area | Path |
|------|------|
| ScriptedImporter entry | `Packages/VRM10/Editor/ScriptedImporter/VrmScriptedImporter.cs` |
| Import implementation | `Packages/VRM10/Editor/ScriptedImporter/VrmScriptedImporterImpl.cs` |
| Import extension API | `Packages/VRM10/Editor/ScriptedImporter/Vrm10ImportExtension.cs` |
| Import extension project setting | `Packages/VRM10/Editor/Settings/Vrm10ProjectEditorSettings.cs` |
| Texture enumeration | `Packages/VRM10/Runtime/IO/Texture/Vrm10TextureDescriptorGenerator.cs` |
| Runtime node list | `Packages/UniGLTF/Runtime/UniGLTF/RuntimeGltfInstance.cs` |
| Prefab vs runtime detect | `Packages/VRM10/Runtime/Components/Vrm10Instance/Vrm10Instance.cs` (comments on missing `RuntimeGltfInstance`) |
