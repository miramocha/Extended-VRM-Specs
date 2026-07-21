---
title: Blender VRMXT
aliases:
  - Blender VFX
  - Blender Materials Override
  - VRMXT_sprite_particle for Blender
  - VRMXT_materials_override for Blender
  - Blender particle emitters
tags:
  - extended-vrm
  - implementation/blender
  - spec/vfx
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Blender VRMXT

Blender add-on implementation profile for
[VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md) and
[VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md).
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


## VFX

### Canonical data model

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

### VRM 1 import seam

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

### VRM 1 export seam

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

### Node, bone, and object mapping

| glTF | Import | Export |
|------|--------|--------|
| Bone node | `PoseBone` via `_bone_names` | Bone name → `bone_name_to_index_dict` |
| Object / mesh / empty node | `Object` via `_object_names` | Object name → `object_name_to_index_dict` |
| Missing index | Skip emitter | N/A |
| Cleared UI pointer | N/A | Skip emitter |

Attachment UI should accept either a pose bone or an object, matching node-constraint
and spring-bone patterns that already resolve both kinds.

### Texture mapping

| Direction | Path |
|-----------|------|
| Import | `textures[i]` → `source` (image index) → `_images[source]` → `Image` pointer |
| Export | `Image` pointer → `find_or_create_image` → texture dict with `source` → `textures[]` index |

Sampler settings for VFX textures are **TBD**; MVP MAY reuse a default sampler or
share an existing texture entry when `source` matches.

### Validation and fallback

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

### UI

Follow existing editor patterns (`editor/spring_bone1` panels, lists, operators):

- Panel under the armature VRM 1 UI
- UIList of emitters with add / remove / reorder
- Per-emitter fields: name, attach node (bone or Empty/object), sprite appearance
  (texture, size, color), particle scalars
- Operators to create an offset Empty under a selected bone when needed
- Rebuild / Clear VFX Preview operators (GeoNodes helpers; see Preview policy)
- No simulation authoring controls beyond portable particle fields

### Preview policy

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

#### Legacy particle systems

Do not use Blender legacy particle systems for VRMXT preview. Risks that motivated
GeoNodes instead: pose bones cannot own particle systems (Empty + child mesh
required for the same reason), rate/frame timing mismatch, and long-term
deprecation risk inside the 4.2–&lt;5.3 window.

### Tests

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

### Likely code touch points

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

### Open questions

| Topic | Status |
|-------|--------|
| `specVersion` other than `1.0` on import | TBD |
| Omit vs write default `localPosition` / `localRotation` | Removed — offsets live on helper glTF nodes |
| Warn on skipped export emitters | TBD |
| VFX texture sampler defaults | TBD |
| Axis conversion if preview gizmos are added | Open; attach-node transform is source of truth |
| UniVRM / Godot / three-vrm / VRM4U consumer packages | See [UniVRMXT VFX](univrm-vrmxt.md#vfx), [Godot VRMXT](godot-vrmxt.md), [three-vrmxt](three-vrmxt.md), and [VRM4U VRMXT](vrm4u-vrmxt.md); backend notes in [Engine particle capability](../references/engine-particle-capability.md) |

## Materials override

### Current behavior

| Stage | Behavior |
|-------|----------|
| Import | Read extension JSON; store on material; populate authored PropertyGroups when Unity parse succeeds. |
| Export | Serialize authored groups (preferred) or stored raw JSON; remap texture Images into `textures[]` when export context provides buffer helpers. |
| UI | Editable Material PROPERTIES panel: Add/Remove override slots, Engine / Variant / Material-Shader (catalog + Custom), Add Common Props / Add / Remove properties. Bindings still deferred. Unreal / unparsed payloads stay readonly via raw JSON. |

Hooks: `materials_override/import_hook.py`, `materials_override/export_hook.py`,
registered from `hooks/vrm1_hooks.py`. Format module:
`format/materials_override.py` (Unity multi-slot selection key = `engine` + `variant`).
Catalogs: `materials_override/catalogs/*.json` + `catalog.py`. Panel / ops:
`materials_override/panel.py`, `materials_override/ops.py`, `sync.py`.

### Authoring UI plan

Goal: let authors create and edit `VRMXT_materials_override` on a Blender material
without hand-editing JSON. Catalog JSON drives known shaders (lilToon JSON shipped in
Specs; Poiyomi next). Catalogs are authoring aids only. Base-spec rules 18–21 still
apply (open identifiers; unresolved materials fall back on import).

#### Target authoring flow

Non-normative. Unity Built-in + Liltoon example:

1. Open Material Properties → **Materials Override**.
2. Click **Add Override**. Creates one `overrides[]` entry on the active material.
3. Set **Engine** → `Unity` (`engine: "unity"`).
4. Set **Variant** → e.g. `Built-In` (`material.variant: "builtin"`).
5. Set **Material / Shader** from the catalog dropdown **filtered by that variant**
   (see [Materials Override Catalogs](../references/materials-override-catalogs.md)
   Material/Shader dropdown filter). Built-In → lilToon family + Poiyomi (when
   shipped); URP → lilToon family; HDRP → no catalog entries yet (**Custom…** only).
   lilToon ships as **three** catalog rows (opaque `lilToon`, cutout
   `Hidden/lilToonCutout`, transparent `Hidden/lilToonTransparent`). Writes
   `material.idType: "shaderName"` and `material.id` to the chosen catalog’s Unity
   shader name.
6. Under **Properties**:
   - **Add Common Props** — one click appends the catalog's common subset (names not
     already on this slot), with catalog defaults.
   - **Add** — enum of remaining catalog properties (common + extended), then
     **Custom…** for any name/type not in the catalog.
   - **Remove** on each row — drops that entry from `properties[]` (consumer then uses
     the shader default for that parameter again).
7. Edit each row's value widget (type-driven):
   - `scalar` → float
   - `vector` → 2–4 floats (UI length from catalog; export as `number[]`)
   - `texture` → Blender `Image` pointer (export resolves to glTF `textures[]` index)
   - `shaderFeature` → bool
8. Optional: **Custom…** on the shader picker for `material.id` absent from the catalog.

Unreal authoring stays out of the first ship set (format/UI for `resourcePath` still open).

#### UI layout (Material Properties panel)

Replace the readonly dump with editable controls. Keep one panel under the VRM material
parent (`VRM_PT_vrm_material_property`).

| Region | Controls |
|--------|----------|
| Header | Empty state label, or **Add Override** / list of existing slots |
| Per-slot box | Engine enum; Variant enum (Unity); Material/Shader enum (+ Custom); optional Provider fields; Remove slot |
| Properties list | Rows: name (readonly if from catalog), type, dynamic value, Remove |
| Property actions | **Add Common Props**; **Add** (catalog enum + Custom…); per-row Remove |
| Bindings | Deferred; readonly or hidden until bindings authoring lands |

**Add Common Props** behavior:

- Enabled when the active slot has a catalog entry with at least one `common` property.
- Appends every catalog property with `common: true` whose `name` is not already on the
  slot. Skips duplicates; does not overwrite existing rows.
- Applies catalog `default` values when present; otherwise leave Blender property defaults.
- No-op (or disabled) for Custom shader with no catalog.

**Add** behavior:

- Enum = all catalog `properties[]` for this shader minus names already on the slot
  (common and non-common alike). lilToon @ pin `2.3.4` has ~337 extended rows
  (glitter, parallax, … as literal `properties[]`, not MToon `bindings`); UI MAY
  add search or section grouping later if the flat enum is hard to use.
- Always include **Custom…** → free-text `name` + manual `type`.
- Reject `properties[].name` that equals any `bindings[].target` on the same slot
  (base-spec rule 23); warn in UI.

**Remove** (per property row):

- Deletes that `properties[]` entry from the active slot only.
- Does not change sibling override slots or `bindings[]`.
- After remove, **Add** / **Add Common Props** MAY offer that name again.
- Export omits the removed name; UniVRMXT leave that parameter at shader default.

Multi-slot rules follow the Unity profile
([UniVRMXT materials override](univrm-vrmxt.md#materials-override) Selection / Variant survival):

- Multiple `unity` slots on one material are allowed when each has a distinct non-empty
  `variant` (`builtin` / `urp` / `hdrp`).
- Editing one slot MUST NOT rewrite sibling slots.
- UI SHOULD warn on duplicate `(engine, variant)` before write.

#### Engine, Variant, and Material/Shader controls

Three separate controls per override slot (not one combined enum).

##### Engine

Writes `overrides[].engine`.

| UI label | Stored value | Notes |
|----------|--------------|-------|
| Unity | `unity` | Spec engine id |
| Unreal | `unreal` | Spec engine id; UI MAY disable until Unreal authoring lands |

##### Variant (Unity)

Writes `material.variant`. Shown when Engine is Unity.

| UI label | Stored value |
|----------|--------------|
| Built-In | `builtin` |
| URP | `urp` |
| HDRP | `hdrp` |

##### Material / Shader

Writes `material.idType` + `material.id`. Options depend on Engine + Variant.

| UI entry | Stored value | Source |
|----------|--------------|--------|
| Catalog row (e.g. lilToon / Cutout / Transparent, Poiyomi) | `idType: "shaderName"`, `id` = catalog `shaderName` | One JSON file per `shaderName`; show entries whose `supportedVariants` contains the selected Variant |
| Custom… | `idType: "shaderName"`, `id` = free-text | Author (always listed) |

When the filtered catalog list is empty (e.g. **HDRP**), this control still offers
**Custom…** only. Changing Variant SHOULD refresh the Material/Shader enum; if the
current catalog selection is invalid for the new variant, clear it or switch to Custom
(pick one; document in UI impl).

Display names are UI-only. File bytes use the stored ids above.

#### Shader catalog JSON

Canonical JSON and distribution rules:
[Materials Override Catalogs](../references/materials-override-catalogs.md)
(`references/catalogs/data/*.json`). Blender vendors a copy under
`io_scene_vrmxt/materials_override/catalogs/` (path MAY adjust). Same files are intended
for UniVRMXT Editor later.

Family notes: [Unity lilToon](../references/catalogs/unity-liltoon.md),
[Unity Poiyomi](../references/catalogs/unity-poiyomi.md).

Authors MAY still type any `material.id`. Catalog coverage is convenience, not a
whitelist.

#### Blender data model

Today: opaque `raw_json` string round-trip.

Authoring needs structured `PropertyGroup`s that rebuild the extension dict on change
(or on export). Proposed layout (identifiers MAY change; keep semantics):

| Blender | Spec |
|---------|------|
| `Material.vrmxt_materials_override_settings` | Extension root |
| `spec_version` | `specVersion` (`"1.0"`) |
| `overrides` (`CollectionProperty`) | `overrides[]` |
| `overrides[].engine` | `engine` |
| `overrides[].id_type` | `material.idType` |
| `overrides[].material_id` | `material.id` |
| `overrides[].variant` | `material.variant` |
| `overrides[].catalog_key` | UI-only: which catalog entry filled the slot (empty = custom) |
| `overrides[].properties` | `properties[]` |
| `properties[].name` | `name` |
| `properties[].type` | `type` |
| `properties[].value_float` / `value_vector` / `value_bool` | `value` by type |
| `properties[].image` (`PointerProperty` → `Image`) | export → `texture` index |

Keep `raw_json` as:

- import cache / fallback for unparsed payloads, and
- serialized snapshot written by a sync operator before export,

or drop it once PropertyGroups are the sole source of truth and import always parses into
them. Prefer one source of truth after authoring lands; dual-write during migration is
acceptable if tests cover both paths.

Texture export MUST register images through the host glTF/VRM texture path so indices
resolve (base-spec rule 26). Mirror the UniVRM prepare-textures expectation described in
[UniVRMXT materials override](univrm-vrmxt.md#materials-override).

#### Dynamic value widgets

| `type` | Widget | Export |
|--------|--------|--------|
| `scalar` | `FloatProperty` | `value` number |
| `vector` | `FloatVectorProperty` size 2–4 | `value` number[] |
| `texture` | `PointerProperty` to `Image` (+ optional colorspace note) | `texture` int index; omit `value` |
| `shaderFeature` | `BoolProperty` | `value` boolean |

User phrasing "string or texture": treat **string** as free-text for custom `name` /
custom `material.id`, not a new `properties[].type`. The base spec has no string value
type today. If a future Unity string property is needed, mark it TBD in the base spec
before the UI invents one.

Add-property operators:

1. **Add Common Props** — see UI layout above (`common: true` only).
2. **Add** — enum from active slot's full catalog `properties[]`, minus names already
   present; always include **Custom…**.
3. Reject `properties[].name` that equals any `bindings[].target` on the same slot
   (base-spec rule 23); warn in UI.

#### Implementation phases

| Phase | Deliverable |
|-------|-------------|
| 0 | Catalog schema + lilToon JSON (opaque / cutout / transparent @ pin `2.3.4`) — **done in Specs**; Poiyomi JSON still TBD |
| 1 | PropertyGroups for overrides + properties; import fills groups; export serializes groups |
| 2 | Panel rewrite: Add/Remove slot; Engine / Variant / Shader enums; Custom shader |
| 3 | Add/edit/remove properties with type-driven value widgets + texture pointers |
| 4 | Texture registration on VRM export path; round-trip tests |
| 5 | Bindings authoring (MToon source → target); multi-variant UX polish |
| 6 | Unreal `resourcePath` + variant authoring |

First ship target = phases 0–4 (Specs phase 0 content for lilToon is available to vendor).
Readonly panel remains until phase 2 replaces it.

#### Tests

- Catalog load: valid file → enum entries; broken JSON → skip + log, do not crash.
- Authoring → export: Unity `builtin` + catalog shader + **Add Common Props** then one
  custom property; fixture includes common names + the custom row.
- **Add Common Props** twice does not duplicate rows.
- Remove property → export omits that name; re-Add can restore it.
- Import → edit → export preserves sibling `unity` slots for other variants.
- Custom shader name with no catalog entry still exports; **Add Common Props** disabled.
- Duplicate `(unity, variant)` rejected or blocked in UI.
- Texture property without an image: omit entry or fail soft per rule 24 (pick one;
  document in export rules).

#### Open questions (authoring)

- [x] One catalog file per shader vs bundled — **one JSON file per `shaderName`**
      (catalog index)
- [ ] Whether changing Material/Shader clears existing `properties[]` or remaps by name
- [ ] Whether `provider` is editable in the first ship set or catalog-only
- [ ] Bindings UI timing relative to properties authoring (properties first; bindings
      phase 5)
- [x] HDRP in first ship — **no**; catalog `supportedVariants` = `builtin` + `urp`;
      HDRP = **Custom…** only until smoke-tested
- [ ] String-typed literal properties (needs base-spec change if required)
- [x] lilToon curated property list — **shipped** (359 props @ `2.3.4`; common +
      extended including glitter/parallax as `properties[]`)
- [ ] Poiyomi curated property list (family page still stub)

### Checklist

- [x] Format layer on `idType` / `id` / `variant` (Unity `shaderName`; optional `properties[]`)
- [ ] Format/UI for Unreal `idType: "resourcePath"` + per-entry `variant`
- [x] Store extension JSON on import; write it back on export
- [x] Tests/fixtures under `tests/resources/gltf/` use `idType` / `id`
- [x] Readonly Material PROPERTIES panel for display
- [ ] Document export rules once behavior matches the base spec open question
- [x] Authoring UI (edit / create overrides in Blender; multi-variant slots) — first ship in VRMXT-Extension-for-Blender
- [x] Specs catalogs (lilToon opaque/cutout/transparent JSON + index) — docs:
      [Materials Override Catalogs](../references/materials-override-catalogs.md)
- [x] Vendor catalog JSON into `io_scene_vrmxt/materials_override/catalogs/` + catalog
      loader (Poiyomi still TBD on Specs side)
- [x] PropertyGroups as source of truth; sync/export from groups
- [x] Type-driven property value widgets + texture export registration (Image remap on export when helpers available)


## Related

- Specs: [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md),
  [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
- Catalogs: [Materials Override Catalogs](../references/materials-override-catalogs.md)
- Unity: [UniVRMXT](univrm-vrmxt.md)
- Unreal: [VRM4U VRMXT](vrm4u-vrmxt.md)
- Host hooks: [Blender Extension Hooks](blender-extension-hooks.md)
- Consumers: [Godot VRMXT](godot-vrmxt.md), [three-vrmxt](three-vrmxt.md);
  VRM4U VFX TBD — [Engine particle capability](../references/engine-particle-capability.md)
