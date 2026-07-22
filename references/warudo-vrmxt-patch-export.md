---
title: Warudo VRMXT Patch Export
aliases:
  - Warudo VRMXT export plan
  - Warudo source GLB rewrite
  - Warudo Source-Preserving VRMXT Export
tags:
  - extended-vrm
  - implementation/warudo
  - format/glb
  - compatibility/vrm1
type: reference
status: accepted
---

# Warudo VRMXT Patch Export

Reference for the plugin utility that patches VRMXT extension state into a copy of a
Warudo Character's original local VRM file.

Tracking:
[VRMXT Plugin for Warudo #8](https://github.com/miramocha/VRMXT-Plugin-for-Warudo/issues/8).
Consumer profile: [Warudo VRMXT](../implementations/warudo-vrmxt.md).

## Goal

Reuse the source GLB geometry, buffers, images, and stock VRM extensions. The export
changes supported VRMXT JSON objects and `extensionsUsed`, then writes a separate file
under Warudo's data folder.

Warudo UI: manually added scene asset **VRMXT** (`VrmxtCharacterAsset`) — Character
picker (unique claim), per-feature toggles, per-material shader autocomplete, Apply,
then Export VRMXT Patch. Editable output suffix (default `.vrmxt`).

This utility patches source bytes. It does not export the live avatar or general Warudo
scene state.

## Feasibility

The current plugin and Warudo API provide the required UMod-safe primitives:

- `Context.PersistentDataManager.ReadFileBytesAsync` already reads local Character
  sources.
- `Context.PersistentDataManager.WriteFileBytesAsync` writes through Warudo's sandbox.
- `GlbChunks.TryExtract` reads JSON and BIN chunks without UniGLTF.
- Newtonsoft JSON is available in the mod.
- `VrmxtPlugin` already exposes `[Trigger]` actions and status text.

The flow does not need a UniVRM exporter hook or UniVRM assembly reference.

## Initial scope

- Support active Characters whose Source resolves to
  `character://data/Characters/*.vrm` or an equivalent `Characters/*.vrm` path.
- Parse the original GLB JSON with Newtonsoft.
- Write current `VRMXT_materials_override` store JSON onto matched
  `materials[i].extensions` entries.
- Preserve existing root `VRMXT_sprite_particle` JSON.
- Add supported extension names to `extensionsUsed` without duplicates.
- Preserve the original BIN chunk and all unrelated JSON.
- Rebuild a valid GLB with correct little-endian lengths and four-byte padding.
- Write to a separate deterministic Character-relative path by default, such as
  `Characters/<name>.vrmxt.vrm`.
- Report output path, skipped entries, and errors through plugin status and logging.

The initial trigger will not replace the active Character Source.

## Design

### Vendored UniVRMXT

Add a GLB rebuild or JSON-replacement API to authoritative
`UniVRMXT/Runtime/Format/GlbChunks.cs`, then recopy that file into the Warudo plugin.
The helper will:

1. accept rewritten UTF-8 JSON and the existing optional BIN payload;
2. pad JSON with `0x20` and BIN with `0x00` to four-byte alignment;
3. emit the GLB 2 header, JSON chunk, and optional BIN chunk;
4. validate sizes before allocation and reject malformed or oversized input.

The planned vendor surface is one modified file. The copy under
`Assets/Vrmxt/Scripts/UniVRMXT/Format/` remains byte-identical to UniVRMXT.

### Warudo host

Add a Warudo-owned export service outside `Scripts/UniVRMXT/` (`VrmxtPatchExport`). It will:

- resolve source and output paths;
- read and write bytes through `PersistentDataManager`;
- parse and mutate the glTF `JObject`;
- match store entries to glTF materials;
- inject per-material extension objects;
- rebuild the GLB and return a structured result.

Material matching prefers a valid stored `GltfMaterialIndex`. If that index is absent or
invalid, the service may use normalized material-name matching when the result is unique.
Missing or ambiguous entries remain unchanged and appear in the result.

`VrmxtCharacterAsset` exposes an export `[Trigger]`, output naming/configuration, an
in-progress guard, and status reporting.

## Data integrity rules

- Never mutate input bytes in place.
- Keep output separate from the loaded source by default.
- Route writes through `PersistentDataManager` so paths remain inside Warudo's data
  folder.
- Preserve material and texture indices because the original JSON and BIN form the
  baseline.
- Do not call `VrmxtMaterialsOverrideExporter.PrepareTextures`; it targets fresh exporter
  texture registration.
- Leave an unmatched or ambiguous material unchanged.
- Preserve unknown extensions and extras.
- Preserve original BIN bytes exactly in the initial implementation.

## Verification

### UniVRMXT format tests

- Rebuild JSON-only and JSON-plus-BIN GLBs.
- Verify JSON-space and BIN-zero padding for lengths zero through three modulo four.
- Verify chunk lengths and total GLB length.
- Verify extract, rebuild, and extract preserves BIN bytes.
- Reject malformed or oversized input without partial output.

### Warudo host tests

- Inject one or several per-material extensions.
- Replace an existing `VRMXT_materials_override` object.
- Preserve unrelated material and root extensions and extras.
- Deduplicate `extensionsUsed`.
- Prefer valid `GltfMaterialIndex` and use name fallback only when unique.
- Report ambiguous or missing materials without changing them.
- Preserve the original BIN hash.
- Reject non-local Character sources.
- Write only to the configured new relative path.

### Manual verification

1. Load a local VRMXT Character in Warudo.
2. Apply or edit supported materials override state.
3. Trigger Export VRMXT Patch.
4. Confirm that the new file appears under Warudo's persistent `Characters/` data.
5. Compare source and output GLBs. Stock JSON and BIN should differ only where this plan
   permits.
6. Load the output in Warudo and Blender and confirm extension survival.

## Deferred work

- Capture live VFX and ParticleSystem values through `VrmxtVfxExporter`.
- Append newly authored textures, images, and buffer views to the GLB BIN chunk.
- Offer source overwrite only with explicit confirmation and backup behavior.
- Add other VRMXT extension stores as their Warudo runtime representations become
  available.

## Out of scope

- General live-avatar VRM export.
- Export of live mesh, skeleton, pose, blend shape, spring bone, or stock VRM changes.
- Workshop Characters whose source bytes are unavailable.
- Automatic Character Source replacement.
- UniVRM exporter dependencies, reflection, `System.IO`, DLLs, or new UPM packages.
- New GLB image payloads in the initial implementation.
- Live ParticleSystem capture in the initial implementation.
