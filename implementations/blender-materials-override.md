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

## Checklist

- [x] Format layer on `idType` / `id` / `variant` (Unity `shaderName`; optional `properties[]`)
- [ ] Format/UI for Unreal `idType: "resourcePath"` + per-entry `variant`
- [x] Store extension JSON on import; write it back on export
- [x] Tests/fixtures under `tests/resources/gltf/` use `idType` / `id`
- [x] Readonly Material PROPERTIES panel for display
- [ ] Document export rules once behavior matches the base spec open question
- [ ] Authoring UI (edit / create overrides in Blender; multi-variant slots)

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Unity: [UniVRM Materials Override](univrm-materials-override.md)
- Unreal: [VRM4U Materials Override](vrm4u-materials-override.md)
- Host hooks: [Blender Extension Hooks](blender-extension-hooks.md)
