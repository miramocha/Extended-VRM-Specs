---
title: Extended VRM Architecture
aliases:
  - VRMXT architecture
  - authoring and consumers
tags:
  - extended-vrm
  - compatibility/vrm1
  - implementation/optional-consumer
type: guide
status: draft
---

# Extended VRM Architecture

Layering of Extended VRM (`VRMXT_*` glTF extensions) for **authoring** and
**runtime consumers** relative to stock VRM 1.0. Normative field rules live in
[specs/](specs/); this note covers compatibility and integration seams only.

## Claims

1. A valid VRM 1.0 file without `VRMXT_*` extensions loads and runs under stock
   VRM tools unchanged.
2. A VRM 1.0 file that also carries `VRMXT_*` data MUST remain loadable by stock
   importers that ignore unknown extensions (see each extension's
   `extensionsRequired` rules).
3. Extended behavior is optional. Consumers MAY ignore every `VRMXT_*` extension
   and still treat the file as ordinary VRM 1.0.
4. Unity Extended support ships as an add-on package (for example
   [UniVRMXT](https://github.com/miramocha/UniVRMXT)). Baseline avatar import
   keeps [UniVRM](https://github.com/vrm-c/UniVRM); replacing UniVRM or forking
   its load path is not required.

## Layers

```text
┌─────────────────────────────────────────────────────────┐
│  Authoring                                              │
│  Blender VRM add-on (stock VRM 1.0 I/O)                 │
│       └─ optional VRM1 extension hooks                  │
│            └─ VRMXT Blender extension (VRMXT_* write)   │
├─────────────────────────────────────────────────────────┤
│  File                                                   │
│  .vrm / .glb  =  glTF 2.0 + VRMC_*  (+ optional VRMXT_*)│
├─────────────────────────────────────────────────────────┤
│  Consumers                                              │
│  Stock UniVRM / VRM4U / other VRM1 loaders              │
│       └─ optional Extended package (parse + attach)     │
└─────────────────────────────────────────────────────────┘
```

| Layer | Owns | Does not own |
|-------|------|--------------|
| Stock VRM 1.0 (`VRMC_vrm`, spring bone, …) | Humanoid, look-at, expressions, materials baseline | `VRMXT_*` semantics |
| Extended VRM specs (this repo) | Portable `VRMXT_*` schemas and compatibility rules | Engine-specific APIs |
| Authoring hooks | Call sites after stock VRM maps exist | Replacing stock VRM export |
| Optional consumer package | Parse `VRMXT_*`, map to engine runtime | Replacing stock VRM import |

## File model

Extended VRM is ordinary glTF 2.0 / VRM 1.0 plus optional root or per-object
extensions named `VRMXT_*`.

| Rule | Requirement |
|------|-------------|
| Presence | `VRMXT_*` MAY be absent. Absence = stock VRM only. |
| `extensionsUsed` | Files that write a `VRMXT_*` extension MUST list that name in `extensionsUsed`. |
| `extensionsRequired` | Optional Extended designs MUST NOT put their `VRMXT_*` name in `extensionsRequired` (see each spec). |
| Unknown extensions | Stock importers ignore unknown extension objects per glTF rules. |
| Target | Current drafts target VRM 1.0 (`VRMC_vrm` 1.0). VRM 0.0 is out of scope unless a spec says otherwise. |

Stock tools that never heard of Extended VRM still open the avatar. Extended data
is skipped.

## Authoring

Authoring splits into stock VRM I/O and an optional Extended writer.

| Piece | Repo | Role |
|-------|------|------|
| Stock Blender VRM add-on | [Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender) (fork/lineage of VRM Add-on for Blender) | Import/export `VRMC_*`, build node/bone maps |
| VRM1 extension hooks | Same add-on: `io_scene_vrm.extension_hooks` | After stock maps exist, call registered third-party callbacks |
| VRMXT Blender extension | [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender) | Registers hooks; authors and serializes `VRMXT_*` |

Hooks exist because glTF2 user extensions run too early to receive final VRM bone
and object index maps. Details:
[Blender Extension Hooks](implementations/blender-extension-hooks.md).

Authoring flow (non-normative):

1. User builds a VRM 1.0 avatar with the stock VRM add-on.
2. Optional: enable the VRMXT Blender extension and author Extended data (emitters,
   overrides, …).
3. Export writes stock `VRMC_*` first, then hook callbacks append `VRMXT_*` and
   `extensionsUsed` entries.
4. Result is one `.vrm` / `.glb`. No second file format.

Without the VRMXT Blender extension, export stays stock VRM. Hooks stay idle.

## Consumers

A **consumer** reads `VRMXT_*` after (or beside) a stock VRM load and maps portable
fields onto engine types.

| Consumer | Host | Integration style |
|----------|------|-------------------|
| [UniVRMXT](https://github.com/miramocha/UniVRMXT) | Unity + UniVRM | Optional UPM package. Parse extension JSON; attach after `Vrm10` load. Runtime does not replace UniVRM. |
| VRM4U path | Unreal + VRM4U | Optional profile docs under `implementations/`; stock VRM4U load remains baseline. |
| Other engines | Any VRM 1.0 loader | Implement the specs; ignore unknown `VRMXT_*` if unsupported. |

### Unity / UniVRM

UniVRM remains the VRM 1.0 importer. UniVRMXT is additive:

1. Project keeps UniVRM (`com.vrmc.gltf`, `com.vrmc.vrm`).
2. Project MAY add UniVRMXT (`com.miramocha.univrmxt`).
3. After stock load (`Vrm10.LoadGltfDataAsync` or equivalent), the app calls UniVRMXT
   helpers (for example `VrmxtVfxRuntime.TryAttach`) with glTF JSON and node
   transforms.
4. Missing extension or missing package → no Extended runtime objects; avatar still
   valid.

UniVRMXT Runtime avoids hard UniGLTF/VRM10 asmdef references where possible so
format parsing stays testable without replacing UniVRM assemblies. Full material
descriptor wrapping still runs inside a project that already has UniVRM.

Implementation notes:
[UniVRM VFX](implementations/univrm-vfx.md),
[UniVRM Materials Override](implementations/univrm-materials-override.md),
package [architecture](https://github.com/miramocha/UniVRMXT/blob/main/docs/architecture.md).

### Compatibility matrix

| Scenario | Stock VRM load | Extended features |
|----------|----------------|-------------------|
| No `VRMXT_*` in file; no Extended package | Works | N/A |
| `VRMXT_*` in file; no Extended package | Works (extensions ignored) | Off |
| No `VRMXT_*` in file; Extended package present | Works | No-op attach / empty parse |
| `VRMXT_*` in file; Extended package present | Works | Features apply per consumer profile |

## What this architecture rejects

| Approach | Why rejected |
|----------|--------------|
| Fork UniVRM as the only way to get Extended features | Breaks drop-in use; forces replace of a maintained upstream |
| Put `VRMXT_*` in `extensionsRequired` for optional extras | Stock loaders would refuse the file |
| Separate binary format instead of glTF extensions | Splits the ecosystem; breaks “one avatar file” |
| Require Blender VRMXT extension for all VRM export | Stock authoring must stay available |

## Document map

| Need | Doc |
|------|-----|
| Extension schemas | [specs/](specs/) |
| Blender hook API | [implementations/blender-extension-hooks.md](implementations/blender-extension-hooks.md) |
| Unity VFX profile | [implementations/univrm-vfx.md](implementations/univrm-vfx.md) |
| Repo index | [README.md](README.md) |

## Open questions

| Topic | Status |
|-------|--------|
| Shared post-load registry inside upstream UniVRM | TBD (UniVRMXT uses explicit attach today) |
| Editor `.vrm` import callback for UniVRM `VrmScriptedImporter` | Tracked in UniVRMXT (issue #4) |
| Cross-engine conformance tests for each `VRMXT_*` | TBD |
