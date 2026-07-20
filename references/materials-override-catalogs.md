---
title: Materials Override Catalogs
aliases:
  - shader catalogs
  - VRMXT materials override catalogs
tags:
  - extended-vrm
  - reference/materials-override
  - compatibility/vrm1
type: reference
status: draft
---

# Materials Override Catalogs

Non-normative authoring catalogs for
[VRMXT_materials_override](../specs/vrmxt-materials-override.md). Tools such as
[Blender Materials Override](../implementations/blender-materials-override.md) and later
[UniVRM Materials Override](../implementations/univrm-materials-override.md) / UniVRMXT
Editor use them for Material-Shader dropdowns, typed property pickers, and **Add Common
Props**.

Catalogs are **not** part of the glTF extension schema. Base-spec rules 18–21 still apply:
open material identifiers, optional catalogs for discovery, unresolved materials fall back
to stock VRM 1.0 import. Absence of a catalog entry MUST NOT block export of a valid
override. A `.vrm` file MUST NOT require catalog membership to be valid.

## Ownership and layout

This repository is the **canonical** home for catalog content:

| Path | Role |
|------|------|
| [materials-override-catalogs.md](materials-override-catalogs.md) (this page) | Schema, distribution, authoring policy |
| [catalogs/unity-liltoon.md](catalogs/unity-liltoon.md), [catalogs/unity-poiyomi.md](catalogs/unity-poiyomi.md), … | Human notes: identity, curated lists, MToon maps, pins |
| [catalogs/data/](catalogs/data/) | Machine JSON (source of truth for tools once files exist) |

Markdown documents rationale and open questions. JSON under `catalogs/data/` is what
loaders parse. Keep them aligned: change JSON and notes in the same PR when practical.

JSON paths:

- `references/catalogs/data/unity-liltoon.json`
- `references/catalogs/data/unity-liltoon-cutout.json`
- `references/catalogs/data/unity-liltoon-transparent.json`
- `references/catalogs/data/unity-liltoon-warudo.json`
- `references/catalogs/data/unity-liltoon-warudo-cutout.json`
- `references/catalogs/data/unity-liltoon-warudo-transparent.json`
- `references/catalogs/data/unity-vrmxt-test-override-builtin.json`
- `references/catalogs/data/unity-vrmxt-test-override-urp.json`
- `references/catalogs/data/unity-poiyomi.json` (planned)

One file per `shaderName` (or per family entry). Do not invent a second parallel schema
inside Blender or UniVRMXT.

## Distribution

### Vendor copy

Consuming packages **copy** the JSON from this repo into their tree at release (or as a
documented sync step). No runtime network fetch. No Specs git submodule required.

| Consumer | Vendored location (proposed) | Use |
|----------|------------------------------|-----|
| [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender) | `io_scene_vrmxt/materials_override/catalogs/*.json` | Authoring UI |
| [UniVRMXT](https://github.com/miramocha/UniVRMXT) | e.g. `Runtime/MaterialsOverride/Catalogs/` or `Editor/.../Catalogs/` | Editor authoring / validation / common-props helper |

Warudo applies overrides at runtime with its own inspector; it does **not** vendor these
catalogs.

Each consumer release SHOULD record which Specs commit or tag the vendored JSON came from
(changelog or a small `CATALOG_PIN.txt` next to the copies).

### Later options

- Shared UPM/npm package (e.g. `vrmxt-shader-catalogs`) if many consumers and frequent
  catalog churn make vendor copies painful.
- Avoid: Specs as a Unity package submodule; Blender as sole owner of the JSON; remote
  download during VRM import.

### Versioning

| Knob | Meaning |
|------|---------|
| `catalogVersion` inside each JSON | Catalog **file format** (schema of this JSON). Start `"1.0"`. Bump when field meaning breaks loaders. |
| Specs git tag / commit | **Content** pin (which properties / shader names). Consumers vendor that revision. |
| Upstream shader pin | Documented on family markdown pages (lilToon / Poiyomi revision used when extracting names). |

Breaking `catalogVersion`: update loaders, then re-vendor. Additive property rows with the
same `catalogVersion` are fine; consumers SHOULD tolerate unknown fields.

## Shipped / planned families

| Note | Engine | Data JSON | `supportedVariants` | Status |
|------|--------|-----------|---------------------|--------|
| [Unity lilToon](catalogs/unity-liltoon.md) | `unity` | `unity-liltoon.json`, `unity-liltoon-cutout.json`, `unity-liltoon-transparent.json` | `builtin`, `urp` (not `hdrp` yet) | shipped (pin lilToon `2.3.4`, 359 props each) |
| [Unity lilToon Warudo](catalogs/unity-liltoon-warudo.md) | `unity` | `unity-liltoon-warudo.json`, `unity-liltoon-warudo-cutout.json`, `unity-liltoon-warudo-transparent.json` | `builtin` only | shipped (pin lilToon `1.10.3` Warudo, 356 props each) |
| [Unity VRMXT Test Override](catalogs/unity-vrmxt-test-override.md) | `unity` | `unity-vrmxt-test-override-builtin.json`, `unity-vrmxt-test-override-urp.json` | `builtin` / `urp` (one each) | shipped (UniVRMXT sample, 11 props each) |
| [Unity Poiyomi](catalogs/unity-poiyomi.md) | `unity` | `catalogs/data/unity-poiyomi.json` (planned) | `builtin` only | stub |

### Material/Shader dropdown filter

UI filters catalog entries by the slot’s selected **Variant** (`material.variant`):

| Selected variant | Catalog entries shown |
|------------------|------------------------|
| Built-In (`builtin`) | lilToon, VRMXT Test Override (Built-in), Poiyomi |
| URP (`urp`) | lilToon, VRMXT Test Override (URP) |
| HDRP (`hdrp`) | *(none)* — **Custom…** only until a catalog lists `hdrp` |

**Custom…** always remains available for any variant. Empty catalog list for HDRP is
intentional (lilToon can run on HDRP upstream; we are not shipping an HDRP catalog row
yet).

## Catalog JSON schema

Proposed shape for tool-side JSON (field names MAY change; keep semantics):

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `catalogVersion` | string | yes | Catalog file format version (start `"1.0"`) |
| `engine` | string | yes | `"unity"` for Unity families |
| `displayName` | string | yes | Dropdown label (e.g. `"lilToon 2.3.4"`) |
| `shaderName` | string | yes | Exact Unity shader name → `material.id` |
| `idType` | string | yes | `"shaderName"` for Unity |
| `defaultVariant` | string | no | Suggested variant when creating a slot; MUST be in `supportedVariants` when that field is set |
| `supportedVariants` | string[] | yes (for shipped catalogs) | Which Unity `material.variant` values show this entry in the Material/Shader dropdown: `builtin`, `urp`, `hdrp`. Catalog-only; not a glTF field. |
| `provider` | object | no | Advisory `provider.id` / `version` defaults |
| `properties` | object[] | yes | Definitions for **Add** enum (common + extended) |
| `properties[].name` | string | yes | Engine material parameter name |
| `properties[].type` | string | yes | `scalar`, `vector`, `texture`, or `shaderFeature` |
| `properties[].displayName` | string | no | UI label; default to `name` |
| `properties[].common` | boolean | no | If `true`, included by **Add Common Props**; default `false` |
| `properties[].vectorSize` | integer | no | 2, 3, or 4 when `type` is `vector`; default 4 |
| `properties[].default` | number, number[], or boolean | no | Initial value when adding the row |
| `properties[].keyword` | string | no | Keyword hint when `type` is `shaderFeature` |

Shipped catalogs SHOULD always set `supportedVariants`. If a loader sees it omitted,
show the entry for every variant (`builtin`, `urp`, `hdrp`) as a soft fallback so the
UI still works — not a migration path and not part of `VRMXT_materials_override`.

One JSON file MAY describe a single `shaderName`, or a tool MAY load several files that
share a `displayName` family (opaque / cutout / transparent). Family notes document which
approach they use.

## Authoring policy

1. Catalog JSON MAY list many properties. Mark the VRM-useful subset with
   `common: true` for **Add Common Props**.
2. Authors MAY add any other catalog property via **Add**, or any name via **Custom…**.
3. Omitted properties stay at the target shader's defaults after consumer apply (UniVRMXT
   only writes listed `properties[]` / `bindings[]`).
4. Pin the upstream package or commit used when extracting property names (family page).
5. A UI toggle that stores an Int is usually `scalar` 0/1, not `shaderFeature`, unless a
   real Unity keyword is documented.
6. Do not fork schema per consumer. Blender and UniVRMXT load the same JSON shape.

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Unity profile: [UniVRM Materials Override](../implementations/univrm-materials-override.md)
- Blender authoring: [Blender Materials Override](../implementations/blender-materials-override.md)
- Architecture: [Extended VRM Architecture](../architecture.md)
