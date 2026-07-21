---
title: Blender VFX
aliases:
  - VRMXT_sprite_particle for Blender
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

Blender add-on implementation profile for [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md).
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
| Attachment pointer | `emitters[].node` | Pose bone **or** Empty/object helper; see mapping |
| `texture` (`PointerProperty` to `Image`) | `texture` | Resolved through glTF textures/images |
| `size` | `size` | Width and height in meters |
| `color` | `color` | Linear RGBA |
| `emission_rate` | `emissionRate` | |
| `max_particles` | `maxParticles` | |
| `lifetime` | `lifetime` | |
| `start_speed` | `startSpeed` | |

Offsets live on the glTF / Blender node the emitter points at. Prefer an Empty (or
other Object) parented under the bone when a non-zero local offset is needed. Do not
store duplicate `localPosition` / `localRotation` on the emitter property group.

## VRM 1 import seam

Preferred path for a **separate** Blender add-on: register a callback with
`io_scene_vrm.extension_hooks` (see [Blender Extension Hooks](blender-extension-hooks.md)).
The callback runs at the end of `Vrm1Importer.load_gltf_extensions()` with frozen node
and image maps.

In-tree path: same timing, code lives beside the existing
`extensions.VRMC_springBone` load:

1. Read root `extensions.VRMXT_sprite_particle`.
2. Require `specVersion` `"1.0"` for this draft; unknown versions: **TBD** (skip or
   best-effort).
3. Iterate `emitters[]`. Skip invalid entries per the base spec.
4. Resolve `node` with `get_object_or_bone_by_node_index()` or hook maps:
   - Returns `PoseBone` when the node mapped to a bone (`_bone_names`).
   - Returns `Object` when the node mapped to an object (`_object_names`).
   - Returns `None` → skip emitter.
5. Resolve `texture` when present:
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
3. Ensure particle images exist in the glTF using existing exporter helpers
   (`find_or_create_image` and texture/sampler append paths used by meta and MToon).
4. Set `texture` to the resulting `textures[]` index.
5. Write root `extensions.VRMXT_sprite_particle` and add `VRMXT_sprite_particle` to
   `extensionsUsed`.
6. Do **not** add `VRMXT_sprite_particle` to `extensionsRequired`.

Offset helpers authored as Empties under bones export as ordinary glTF nodes with
`translation` / `rotation`. The emitter `node` index points at that helper.

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

- `node` missing, out of range, or unresolved
- `size` present but not two finite numbers greater than `0`
- `color` present but not four finite numbers, RGB `>= 0`, alpha in `[0,1]`
- Non-finite or negative `emissionRate` / `lifetime` / `startSpeed`
- `maxParticles` not an integer `>= 1`
- Attachment cleared or unmapped on export

Stock VRM 1.0 load without the VFX feature: avatar imports; no emitters. Missing
optional package behavior does not apply here (this lives inside the VRM add-on),
but absent `VRMXT_sprite_particle` in the file MUST leave the collection empty.

## UI

Follow existing editor patterns (`editor/spring_bone1` panels, lists, operators):

- Panel under the armature VRM 1 UI
- UIList of emitters with add / remove / reorder
- Per-emitter fields: name, attach node (bone or Empty/object), sprite appearance
  (texture, size, color), particle scalars
- Operators to create an offset Empty under a selected bone when needed
- Rebuild / Clear VFX Preview operators (GeoNodes helpers; see Preview policy)
- No simulation authoring controls beyond portable particle fields

## Preview policy

After VRM 1 import (and via **Rebuild VFX Preview**), VRMXT spawns Geometry Nodes
helpers so portable particle emitters can be checked in the viewport. The shared
node group is ``VRMXT_SpriteParticle`` (Simulation Zone emit, local **+Y** velocity,
lifetime cull, max-particle cap, fixed **XZ** quads in emitter node local space).

| Spec / Unity field | GeoNodes / helper |
|--------------------|-------------------|
| `emissionRate` | Modifier **Emission Rate** (particles/sec) |
| `maxParticles` | Modifier **Max Particles** |
| `lifetime` | Modifier **Lifetime** |
| `size` | Modifier **Start Size** (instance width / height) |
| `startSpeed` | Modifier **Start Speed** along emitter node local **+Y** |
| `color` | Preview material emission tint |
| `texture` | Preview material image (tint-only when missing) |
| Attach node transform | Preview parented to resolved bone / Empty |
| Quad orientation | Fixed Mesh Grid rotated to **XZ** (normal +Y); no camera/viewport billboarding |

Rules:

- Property groups remain the export source of truth. Do not read GeoNodes state
  back into emitters.
- Each preview helper is an **Empty** named `VRMXT_sprite_particle_{name}`, parented to
  the attach node, tagged `vrmxt_vfx_preview=1` (VRMXT lifecycle) and
  `vrm_exclude_from_export=1` (host export filter). Preview helpers are viewport-only;
  they MUST NOT become the serialized attach node. Empties cannot host Geometry Nodes,
  so a child mesh `VRMXT_sprite_particle_{name}_geo` (also tagged, `hide_select`) carries
  the `VRMXT_SpriteParticle` modifier.
- Helpers use `hide_render=True`. Extended VRM `export_objects` skips any object
  with `vrm_exclude_from_export` so they do not become avatar meshes in the GLB.
- Simulation Nodes require Blender 4.2+ (already the VRMXT add-on window).

### Legacy particle systems

Do not use Blender legacy particle systems for VRMXT preview. Risks that motivated
GeoNodes instead: pose bones cannot own particle systems (Empty + child mesh
required for the same reason), rate/frame timing mismatch, and long-term
deprecation risk inside the 4.2–&lt;5.3 window.

## Tests

Minimum coverage (mirror existing importer/exporter and spring-bone editor tests):

| Case | Expectation |
|------|-------------|
| Import valid emitter on bone node | Property group filled; bone attachment set; GeoNodes helper spawned |
| Import emitter on object node | Object attachment set; helper parented to object |
| Import bad `node` / invalid scalars | Emitter skipped; VRM otherwise loads |
| Import texture index | Image pointer set via `textures` → `source` → `_images` |
| Export round-trip | Same portable fields and node attachment after re-import |
| Export with texture | `textures[]` / `images[]` present; `extensionsUsed` contains `VRMXT_sprite_particle` |
| Empty `emitters` | Valid file; no required extension entry |
| UI operators | Add / remove / reorder update the collection; preview rebuilds |
| Preview clear | Tagged helpers removed; property groups unchanged |
| Preview export isolation | Objects with `vrm_exclude_from_export` omitted from host `export_objects` |

Exact test module paths: `tests/test_format_vfx.py`, `tests/test_vfx_property_adapters.py`,
`tests/test_vfx_geonodes_preview.py`, and hook tests in the VRMXT repo.

## Likely code touch points

Non-normative; [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender):

- `src/io_scene_vrmxt/vfx/` (property groups, import/export hooks, GeoNodes preview)
- `src/io_scene_vrmxt/hooks/vrm1_hooks.py`
- `src/io_scene_vrmxt/format/vfx.py`
- Tests: `tests/test_format_vfx.py`, `tests/test_vfx_property_adapters.py`,
  `tests/test_vfx_geonodes_preview.py`, `tests/test_hooks_registration.py`

Host hooks remain in Extended-VRM-Addon-for-Blender (`extension_hooks.py`).
Host `export_objects` skips objects tagged `vrm_exclude_from_export`
(`EXCLUDE_FROM_EXPORT_CUSTOM_PROP` in `extension_hooks.py`). VRMXT sets that
prop on preview helpers alongside its own `vrmxt_vfx_preview` lifecycle tag.

## Open questions

| Topic | Status |
|-------|--------|
| `specVersion` other than `1.0` on import | TBD |
| Omit vs write default `localPosition` / `localRotation` | Removed — offsets live on helper glTF nodes |
| Warn on skipped export emitters | TBD |
| VFX texture sampler defaults | TBD |
| Axis conversion if preview gizmos are added | Open; attach-node transform is source of truth |
| UniVRM / Godot / three-vrm / VRM4U consumer packages | See [UniVRM VFX](univrm-vfx.md), [Godot VFX](godot-vfx.md), [three-vrm VFX](three-vrm-vfx.md); VRM4U TBD — backend notes in [Engine particle capability](../references/engine-particle-capability.md) |
