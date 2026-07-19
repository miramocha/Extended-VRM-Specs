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
| Import | Read `materials[i].extensions.VRMXT_materials_override`; store **verbatim** JSON on the Blender material (`vrmxt_materials_override_settings.raw_json` + custom prop). Typed parse is not required to store. |
| Export | Write stored JSON back onto the material extension + `extensionsUsed`. Typed parse is not required to export. |
| UI | Readonly Material PROPERTIES panel. Shows parsed engine / identity / bindings / properties. Multiple `unity` or `unreal` variant slots MAY appear as separate rows. If JSON is stored but unparsed, shows `Stored (unparsed)`. No authoring. |

Hooks: `materials_override/import_hook.py`, `materials_override/export_hook.py`,
registered from `hooks/vrm1_hooks.py`. Format module:
`format/materials_override.py` (`idType` / `id` / `variant`; Unity `shaderName`, Unreal
`resourcePath`; optional `properties[]`). Panel: `materials_override/panel.py`.

## Checklist

- [x] Align `format/materials_override.py` with current schema (`idType` / `id`, Unreal
      `idType: "materialSet"`, optional `properties[]`); remove `kind` / `name`
- [ ] Update format/UI for Unreal `idType: "resourcePath"` + per-entry `variant` (and
      optional expand of deprecated `materialSet` / `variants` maps on read)
- [x] Prefer verbatim store of extension JSON on import (always keep raw) so round-trip
      does not depend on full parse
- [x] Update tests/fixtures under `tests/resources/gltf/` to `idType` / `id`
- [x] Readonly Material PROPERTIES panel for display
- [ ] Document export rules once behavior matches the base spec open question
- [ ] Authoring UI (edit / create overrides in Blender; multi-variant slots)

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Unity: [UniVRM Materials Override](univrm-materials-override.md)
- Unreal: [VRM4U Materials Override](vrm4u-materials-override.md)
- Host hooks: [Blender Extension Hooks](blender-extension-hooks.md)
