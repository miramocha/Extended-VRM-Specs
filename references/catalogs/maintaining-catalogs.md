---
title: Maintaining Materials Override Catalogs
aliases:
  - catalog regen
  - shader catalog maintenance
tags:
  - extended-vrm
  - reference/materials-override
  - type/guide
type: guide
status: draft
---

# Maintaining Materials Override Catalogs

Maintainer workflow for non-normative shader catalogs under
[Materials Override Catalogs](../materials-override-catalogs.md). Implementers vendor
JSON; they do not need this page for runtime behavior.

## Layout

| Path | Role |
|------|------|
| Family notes (`unity-liltoon.md`, …) | Pins, identity, curated common/extended lists, MToon maps |
| `data/*.json` | Machine source of truth for tools |
| This page | Pin bumps, regen, vendor sync |
| `.cursor/skills/unity-shader-catalog/` | Agent skill + Python scripts |

Change JSON and matching family notes in the same PR when practical. Update
`data/README.md` and the catalogs index Status row.

## Pin bump / regen

1. Record the new upstream tag or commit on the family page.
2. Curate property names / `common` / `displayName` (family tables or curated JSON under
   the skill `examples/`).
3. Scaffold types and defaults from ShaderLab with the skill scripts (repo root):

```powershell
python .cursor/skills/unity-shader-catalog/scripts/scaffold_catalog_json.py `
  --curated .cursor/skills/unity-shader-catalog/examples/liltoon-opaque.curated.json `
  --github "lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader" `
  -o references/catalogs/data/unity-liltoon.json
```

lilToon section extract → curated list:
`scripts/generate_liltoon_curated.py`. Variant parity:
`scripts/diff_shader_props.py`. Explore:
`scripts/parse_shaderlab_props.py`.

4. Copy scaffold output per `shaderName` (opaque / cutout / transparent). Keep curated
   property decls aligned across those modes when upstream matches.
5. Deslop edited prose. Do not edit normative
   `specs/extensions/materials/vrmxt-materials-override.md` for catalog-only work.

Warudo lilToon: point `--file` at the BIRP plugin Shader folder in Warudo Shader Plugins
(see [Unity lilToon Warudo](unity-liltoon-warudo.md) pin table).

Full agent checklist: skill **unity-shader-catalog**.

## Vendor sync

Consumers copy `data/*.json` at release (or a documented sync step). Record Specs commit
or tag next to the copies (`CATALOG_PIN.txt` or changelog). See **Distribution** on the
catalogs index.

## Do not

- Dump full ShaderLab `Properties` into JSON without curation
- Auto-mark `common: true` (read family markdown)
- Add `hdrp` to `supportedVariants` without smoke test + family note update
- Fork catalog schema per consumer (Blender and UniVRMXT share one shape)

## Related

- Index: [Materials Override Catalogs](../materials-override-catalogs.md)
- Data folder: [catalogs/data/](data/README.md)
- Spec: [VRMXT_materials_override](../../specs/extensions/materials/vrmxt-materials-override.md)
