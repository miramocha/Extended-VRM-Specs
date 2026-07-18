---
title: Blender VFX
aliases:
  - VRMXT_vfx for Blender
  - Blender particle emitters
tags:
  - extended-vrm
  - implementation/blender
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# Blender VFX

Blender add-on implementation profile for [VRMXT_vfx](../specs/vrmxt-vfx.md).
Support belongs in
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender),
which registers on VRM1 hooks from
[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender)
(see [Blender Extension Hooks](blender-extension-hooks.md)). VRM 1.0 only.

## Supported Blender versions

VRMXT extension declares the same window as Extended VRM:

| Manifest field | Value | Meaning |
|----------------|-------|---------|
| `blender_version_min` | `4.2.0` | Inclusive lower bound |
| `blender_version_max` | `5.3.0` | Exclusive upper bound |

Source: `src/io_scene_vrmxt/blender_manifest.toml`. Blender **4.2** inclusive through
**&lt;5.3**.

## Canonical data model

Store emitters on the armature via VRMXT-owned property groups in
`io_scene_vrmxt` (not the stock VRM armature extension). Same CollectionProperty
pattern as spring bone lists.

Import and export read and write those groups. Blender particle systems are not the
source of truth.

Proposed layout (implementation identifiers MAY be adjusted; keep semantics):

| Blender property | Spec field | Notes |
|------------------|------------|-------|
| Collection of emitter items | `emitters[]` | Order preserved on export |
| `name` | `emitters[].name` | Authoring label |
| Attachment pointer | `emitters[].node` | Pose bone **or** object; see mapping |
| `local_position` | `localPosition` | Spec-space meters; default `(0,0,0)` |
| `local_rotation` | `localRotation` | Spec-space quaternion **xyzw**; default identity |
| `texture` (`PointerProperty` to `Image`) | `particle.texture` | Resolved through glTF textures/images |
| `emission_rate` | `emissionRate` | |
| `max_particles` | `maxParticles` | |
| `lifetime` | `lifetime` | |
| `start_size` | `startSize` | |
| `start_speed` | `startSpeed` | |
| `start_color` | `startColor` | Linear RGBA |

MVP stores `local_position` and `local_rotation` as **spec / glTF node-local** values
so round-trip matches file bytes. Bone `axis_translation` remapping used for spring
colliders and look-at offsets is **not** applied to these fields in MVP.

Whether a later preview UI should convert values for Blender bone axes is **TBD**.

## VRM 1 import seam

Preferred path for a **separate** Blender add-on: register a callback with
`io_scene_vrm.extension_hooks` (see [Blender Extension Hooks](blender-extension-hooks.md)).
The callback runs at the end of `Vrm1Importer.load_gltf_extensions()` with frozen node
and image maps.

In-tree path: same timing, code lives beside the existing
`extensions.VRMC_springBone` load:

1. Read root `extensions.VRMXT_vfx`.
2. Require `specVersion` `"1.0"` for this draft; unknown versions: **TBD** (skip or
   best-effort).
3. Iterate `emitters[]`. Skip invalid entries per the base spec.
4. Resolve `node` with `get_object_or_bone_by_node_index()` or hook maps:
   - Returns `PoseBone` when the node mapped to a bone (`_bone_names`).
   - Returns `Object` when the node mapped to an object (`_object_names`).
   - Returns `None` → skip emitter.
5. Resolve `particle.texture` when present:
   - Index into glTF `textures[]`.
   - Read `textures[i].source` as an image index.
   - Assign `self._images.get(source)` to the emitter image pointer.
   - Unresolved texture → leave empty; still import other particle fields.
6. Copy portable scalars and color; apply defaults when properties are omitted.

Unknown root extensions are **not** round-tripped today: import writes `vrm.json`,
but the exporter does not rebuild arbitrary extensions from that text. Explicit VFX
load/save (in-tree or via hooks) is required.

## VRM 1 export seam

Preferred separate-add-on path: register an export hook after stock `VRMC_*` writing
(see [Blender Extension Hooks](blender-extension-hooks.md)).

In-tree path: same timing inside `Vrm1Exporter.add_vrm_extension_to_glb()` after bone
and object index maps exist:

1. Build `emitters[]` from the armature VFX collection.
2. Map attachment back to a node index:
   - Pose bone → `bone_name_to_index_dict`.
   - Object → `object_name_to_index_dict`.
   - Unmapped attachment → skip that emitter (or omit export; **TBD** whether to warn).
3. Write `localPosition` / `localRotation` from property groups. Whether to omit
   identity/zero defaults or write them explicitly is **TBD**; either is valid.
4. Ensure particle images exist in the glTF using existing exporter helpers
   (`find_or_create_image` and texture/sampler append paths used by meta and MToon).
5. Set `particle.texture` to the resulting `textures[]` index.
6. Write root `extensions.VRMXT_vfx` and add `VRMXT_vfx` to `extensionsUsed`.
7. Do **not** add `VRMXT_vfx` to `extensionsRequired`.

## Node, bone, and object mapping

| glTF | Import | Export |
|------|--------|--------|
| Bone node | `PoseBone` via `_bone_names` | Bone name → `bone_name_to_index_dict` |
| Object / mesh / empty node | `Object` via `_object_names` | Object name → `object_name_to_index_dict` |
| Missing index | Skip emitter | N/A |
| Cleared UI pointer | N/A | Skip emitter |

Attachment UI should accept either a pose bone or an object, matching node-constraint
and spring-bone patterns that already resolve both kinds.

## Texture mapping

| Direction | Path |
|-----------|------|
| Import | `textures[i]` → `source` (image index) → `_images[source]` → `Image` pointer |
| Export | `Image` pointer → `find_or_create_image` → texture dict with `source` → `textures[]` index |

Sampler settings for VFX textures are **TBD**; MVP MAY reuse a default sampler or
share an existing texture entry when `source` matches.

## Validation and fallback

Per emitter, skip (do not fail the whole VRM load/export) when:

- `type` missing or unknown
- `node` missing, out of range, or unresolved
- `type` is `"particle"` but `particle` is missing
- Non-finite or negative `emissionRate` / `lifetime` / `startSize` / `startSpeed`
- `maxParticles` not an integer `>= 1`
- `localPosition` or `localRotation` wrong length, non-finite, or zero-length quaternion
- Attachment cleared or unmapped on export

Stock VRM 1.0 load without the VFX feature: avatar imports; no emitters. Missing
optional package behavior does not apply here (this lives inside the VRM add-on),
but absent `VRMXT_vfx` in the file MUST leave the collection empty.

## UI

Follow existing editor patterns (`editor/spring_bone1` panels, lists, operators):

- Panel under the armature VRM 1 UI
- UIList of emitters with add / remove / reorder
- Per-emitter fields: name, attachment, local position, local rotation, texture,
  particle scalars and color
- No simulation controls in MVP

## Preview policy

MVP deliberately has **no** viewport particle preview and does **not** create Blender
particle systems from VFX data.

### Future optional legacy particle preview (risks)

A later adapter MAY spawn legacy Blender particles for authoring feedback. Known
risks:

| Risk | Detail |
|------|--------|
| Owner object | Pose bones and empties cannot own a particle system; needs a hidden helper mesh |
| Export exclusion | Helper must stay out of GLB output (same class of problem as internal link objects) |
| Rate model | Blender particle count / frame timing does not match `emissionRate` particles/second exactly |
| Billboard / texture | Camera-facing textured quads differ by render engine (EEVEE / Cycles) |
| Version window | Legacy particles exist in the supported 4.2–&lt;5.3 range but remain a long-term risk if Blender removes or replaces them |

Do not infer export data from any preview particle system if preview is added later.

## Tests

Minimum coverage (mirror existing importer/exporter and spring-bone editor tests):

| Case | Expectation |
|------|-------------|
| Import valid emitter on bone node | Property group filled; bone attachment set |
| Import emitter on object node | Object attachment set |
| Import bad `node` / invalid scalars | Emitter skipped; VRM otherwise loads |
| Import texture index | Image pointer set via `textures` → `source` → `_images` |
| Export round-trip | Same portable fields and node attachment after re-import |
| Export with texture | `textures[]` / `images[]` present; `extensionsUsed` contains `VRMXT_vfx` |
| Empty `emitters` | Valid file; no required extension entry |
| UI operators | Add / remove / reorder update the collection |

Exact test module paths: `tests/test_format_vfx.py` and hook tests in the VRMXT repo.
UI operator coverage is **TBD** until panels land.

## Likely code touch points

Non-normative; [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender):

- `src/io_scene_vrmxt/vfx/` (property groups, import/export hooks)
- `src/io_scene_vrmxt/hooks/vrm1_hooks.py`
- `src/io_scene_vrmxt/format/vfx.py`
- Tests: `tests/test_format_vfx.py`, `tests/test_hooks_registration.py`

Host hooks remain in Extended-VRM-Addon-for-Blender (`extension_hooks.py`).

## Open questions

| Topic | Status |
|-------|--------|
| `specVersion` other than `1.0` on import | TBD |
| Omit vs write default `localPosition` / `localRotation` | TBD |
| Warn on skipped export emitters | TBD |
| VFX texture sampler defaults | TBD |
| Axis conversion if preview gizmos are added | TBD |
| UniVRM / VRM4U consumer packages | See [UniVRM VFX](univrm-vfx.md); VRM4U TBD |
