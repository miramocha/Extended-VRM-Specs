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

This profile is incomplete. Track post-merge work against the known gap below.

## Current behavior

| Stage | Behavior |
|-------|----------|
| Import | Parse `materials[i].extensions.VRMXT_materials_override`; store JSON on the Blender material (`vrmxt_materials_override_settings.raw_json` + custom prop) |
| Export | Re-parse stored JSON; write extension + `extensionsUsed` |
| UI | Stub (raw JSON / authoring only; no Blender engine profile) |

Hooks: `materials_override/import_hook.py`, `materials_override/export_hook.py`,
registered from `hooks/vrm1_hooks.py`.

## Known gap (Unity ↔ Blender round-trip)

UniVRMXT and the base / Unity profiles use `material.idType` / `material.id`
(Unity: `idType: "shaderName"`). The Blender format module still expects
`kind` / `name` (`kind: "shader"`).

Consequence: a `.vrm` written by UniVRMXT fails Blender `parse_materials_override` on
import. Nothing is stored on the material. Re-export omits the extension. Unity
re-import then correctly sees no override.

Unreal side has the same lag (`idType: "materialSet"` vs Blender `kind: "materialSet"`).
`properties[]` is also not modeled in the Blender dataclasses yet.

No production files use the old names — drop them; do not keep a dual-read path.

## Post-merge fix (checklist)

- [ ] Align `format/materials_override.py` with current schema (`idType` / `id`, Unreal
      `idType: "materialSet"`, optional `properties[]`); remove `kind` / `name`
- [ ] Prefer verbatim store of extension JSON on import when typed parse fails (or always
      keep raw bytes alongside typed views) so round-trip does not depend on full parse
- [ ] Update tests/fixtures under `tests/resources/gltf/` to `idType` / `id`
- [ ] Document export rules once behavior matches the base spec open question

## Related

- Spec: [VRMXT_materials_override](../specs/vrmxt-materials-override.md)
- Unity: [UniVRM Materials Override](univrm-materials-override.md)
- Unreal: [VRM4U Materials Override](vrm4u-materials-override.md)
- Host hooks: [Blender Extension Hooks](blender-extension-hooks.md)
