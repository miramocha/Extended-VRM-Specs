---
title: Blender Materials Override
aliases:
  - VRMXT_materials_override for Blender
tags:
  - extended-vrm
  - implementation/blender
  - spec/materials-override
  - compatibility/vrm1
type: guide
status: draft
---

# Blender Materials Override

Blender add-on notes for [VRMXT_materials_override](../specs/vrmxt-materials-override.md).
Support belongs in
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender)
(VRM1 hooks on
[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender);
see [Blender Extension Hooks](blender-extension-hooks.md)).

## Current behavior

| Stage | Behavior |
|-------|----------|
| Import | Read `materials[i].extensions.VRMXT_materials_override`; store extension JSON on the Blender material (`vrmxt_materials_override_settings.raw_json` + custom prop). |
| Export | Write stored JSON back onto the material extension + `extensionsUsed`. |
| UI | Readonly Material PROPERTIES panel. Shows parsed engine / identity / bindings / properties. Multiple `unity` or `unreal` variant slots MAY appear as separate rows. No authoring. |

Hooks: `materials_override/import_hook.py`, `materials_override/export_hook.py`,
registered from `hooks/vrm1_hooks.py`. Format module:
`format/materials_override.py` (`idType` / `id` / `variant`; Unity `shaderName`;
optional `properties[]`; Unreal `resourcePath` still open). Panel:
`materials_override/panel.py`.

## Authoring UI plan

Goal: let authors create and edit `VRMXT_materials_override` on a Blender material
without hand-editing JSON. Catalog JSON drives known shaders (ship Liltoon and
Poiyomi first). Catalogs are authoring aids only. Base-spec rules 18–21 still apply
(open identifiers; unresolved materials fall back on import).

### Target authoring flow

Non-normative. Unity Built-in + Liltoon example:

1. Open Material Properties → **Materials Override**.
2. Click **Add Override**. Creates one `overrides[]` entry on the active material.
3. Set **Engine** → `Unity` (`engine: "unity"`).
4. Set **Variant** → e.g. `Built-In` (`material.variant: "builtin"`).
5. Set **Material / Shader** from the catalog dropdown **filtered by that variant**
   (see [Materials Override Catalogs](../references/materials-override-catalogs.md)
   Material/Shader dropdown filter). Built-In → lilToon and Poiyomi; URP → lilToon;
   HDRP → no catalog entries yet (**Custom…** only). Writes `material.idType:
   "shaderName"` and `material.id` to the chosen catalog’s Unity shader name.
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

### UI layout (Material Properties panel)

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
  (common and non-common alike).
- Always include **Custom…** → free-text `name` + manual `type`.
- Reject `properties[].name` that equals any `bindings[].target` on the same slot
  (base-spec rule 23); warn in UI.

**Remove** (per property row):

- Deletes that `properties[]` entry from the active slot only.
- Does not change sibling override slots or `bindings[]`.
- After remove, **Add** / **Add Common Props** MAY offer that name again.
- Export omits the removed name; UniVRMXT leave that parameter at shader default.

Multi-slot rules follow the Unity profile
([UniVRM Materials Override](univrm-materials-override.md) Selection / Variant survival):

- Multiple `unity` slots on one material are allowed when each has a distinct non-empty
  `variant` (`builtin` / `urp` / `hdrp`).
- Editing one slot MUST NOT rewrite sibling slots.
- UI SHOULD warn on duplicate `(engine, variant)` before write.

### Engine, Variant, and Material/Shader controls

Three separate controls per override slot (not one combined enum).

#### Engine

Writes `overrides[].engine`.

| UI label | Stored value | Notes |
|----------|--------------|-------|
| Unity | `unity` | Spec engine id |
| Unreal | `unreal` | Spec engine id; UI MAY disable until Unreal authoring lands |

#### Variant (Unity)

Writes `material.variant`. Shown when Engine is Unity.

| UI label | Stored value |
|----------|--------------|
| Built-In | `builtin` |
| URP | `urp` |
| HDRP | `hdrp` |

#### Material / Shader

Writes `material.idType` + `material.id`. Options depend on Engine + Variant.

| UI entry | Stored value | Source |
|----------|--------------|--------|
| Catalog row (e.g. lilToon, Poiyomi) | `idType: "shaderName"`, `id` = catalog `shaderName` | Catalog JSON entries whose `supportedVariants` contains the selected Variant |
| Custom… | `idType: "shaderName"`, `id` = free-text | Author (always listed) |

When the filtered catalog list is empty (e.g. **HDRP**), this control still offers
**Custom…** only. Changing Variant SHOULD refresh the Material/Shader enum; if the
current catalog selection is invalid for the new variant, clear it or switch to Custom
(pick one; document in UI impl).

Display names are UI-only. File bytes use the stored ids above.

### Shader catalog JSON

Canonical JSON and distribution rules:
[Materials Override Catalogs](../references/materials-override-catalogs.md)
(`references/catalogs/data/*.json`). Blender vendors a copy under
`io_scene_vrmxt/materials_override/catalogs/` (path MAY adjust). Same files are intended
for UniVRMXT Editor later.

Family notes: [Unity lilToon](../references/catalogs/unity-liltoon.md),
[Unity Poiyomi](../references/catalogs/unity-poiyomi.md).

Authors MAY still type any `material.id`. Catalog coverage is convenience, not a
whitelist.

### Blender data model

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
[UniVRM Materials Override](univrm-materials-override.md).

### Dynamic value widgets

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

### Implementation phases

| Phase | Deliverable |
|-------|-------------|
| 0 | Catalog schema + Liltoon + Poiyomi JSON stubs (names/types only; fill real shader strings later) |
| 1 | PropertyGroups for overrides + properties; import fills groups; export serializes groups |
| 2 | Panel rewrite: Add/Remove slot; Engine / Variant / Shader enums; Custom shader |
| 3 | Add/edit/remove properties with type-driven value widgets + texture pointers |
| 4 | Texture registration on VRM export path; round-trip tests |
| 5 | Bindings authoring (MToon source → target); multi-variant UX polish |
| 6 | Unreal `resourcePath` + variant authoring |

First ship target = phases 0–4. Readonly panel remains until phase 2 replaces it.

### Tests

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

### Open questions (authoring)

- [ ] One catalog file per shader vs bundled multi-shader catalogs (see catalog index)
- [ ] Whether changing Material/Shader clears existing `properties[]` or remaps by name
- [ ] Whether `provider` is editable in the first ship set or catalog-only
- [ ] Bindings UI timing relative to properties authoring
- [ ] HDRP catalog entries in first ship set, or Built-in + URP only
- [ ] String-typed literal properties (needs base-spec change if required)
- [ ] Curated lilToon / Poiyomi property lists (tracked on catalog family pages)

## Checklist

- [x] Format layer on `idType` / `id` / `variant` (Unity `shaderName`; optional `properties[]`)
- [ ] Format/UI for Unreal `idType: "resourcePath"` + per-entry `variant`
- [x] Store extension JSON on import; write it back on export
- [x] Tests/fixtures under `tests/resources/gltf/` use `idType` / `id`
- [x] Readonly Material PROPERTIES panel for display
- [ ] Document export rules once behavior matches the base spec open question
- [ ] Authoring UI (edit / create overrides in Blender; multi-variant slots)
- [ ] Shader catalogs (Liltoon, Poiyomi) + catalog loader — docs:
      [Materials Override Catalogs](../references/materials-override-catalogs.md)
- [ ] PropertyGroups as source of truth; sync/export from groups
- [ ] Type-driven property value widgets + texture export registration

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Catalogs: [Materials Override Catalogs](../references/materials-override-catalogs.md)
- Unity: [UniVRM Materials Override](univrm-materials-override.md)
- Unreal: [VRM4U Materials Override](vrm4u-materials-override.md)
- Host hooks: [Blender Extension Hooks](blender-extension-hooks.md)
