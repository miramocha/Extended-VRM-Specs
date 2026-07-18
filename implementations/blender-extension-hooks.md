---
title: Blender Extension Hooks
aliases:
  - VRM1 extension hooks
  - third-party VRMXT hooks
tags:
  - extended-vrm
  - implementation/blender
  - format/gltf-extension
  - compatibility/vrm1
type: guide
status: draft
---

# Blender Extension Hooks

Public VRM 1.0 import/export hooks in
[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender).
They let a separate Blender add-on handle `VRMXT_*` (and similar) root extensions
after stock VRM maps exist. Examples: [VRMXT_vfx](../specs/vrmxt-vfx.md),
[VRMXT_lattice](../specs/vrmxt-lattice.md).

## Fork and upstream intent

[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender)
is a fork of [saturday06/VRM-Addon-for-Blender](https://github.com/saturday06/VRM-Addon-for-Blender).
It adds a **generic** VRM1 extension hook API (`io_scene_vrm.extension_hooks`) — not
VRMXT-specific. The plan is to propose that hook surface upstream so stock Blender VRM
hosts can load optional packages (e.g.
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender))
without requiring this fork.

Same pattern on Unity: [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM)
ships generic import hooks to propose to [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM)
— see [univrm-upstream-hooks.md](univrm-upstream-hooks.md).

Primary consumer today:
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender)
(`io_scene_vrmxt`).

Module: `io_scene_vrm.extension_hooks`.

## Why hooks exist

Stock VRM import builds temporary `node index → Object/PoseBone` maps and then
discards them. Stock VRM export builds final `bone/object name → node index` maps
only inside `add_vrm_extension_to_glb()`. Without hooks, a third-party add-on cannot
reliably attach bone-referenced extensions.

glTF2 user extensions run too early (import) or too early (export, before VRM
postprocessing) and do not receive those maps.

## API

| Function | Role |
|----------|------|
| `register_vrm1_import_extension_hook` | Append import callback |
| `unregister_vrm1_import_extension_hook` | Remove import callback |
| `register_vrm1_export_extension_hook` | Append export callback |
| `unregister_vrm1_export_extension_hook` | Remove export callback |

Callbacks are process-global and ordered by registration. Duplicate registration is
ignored. Missing unregister is harmless. Dispatch copies the hook list so a callback
may unregister itself. Exceptions propagate and abort import/export.

Hooks are **not** cleared when the VRM add-on is disabled. Third parties MUST
unregister from their own `unregister()`.

VRM 0.0 is out of scope for this API.

## Import context

Invoked at the end of `Vrm1Importer.load_gltf_extensions()`, after spring bone, node
constraint, and heavy migration.

| Field | Meaning |
|-------|---------|
| `context` | Blender context |
| `armature` | Imported armature object |
| `json_dict` | Frozen snapshot of the parsed glTF JSON |
| `node_index_to_object_name` | glTF node → object name |
| `node_index_to_bone_name` | glTF node → bone name |
| `image_index_to_image` | glTF image index → Blender `Image` |
| `material_index_to_material` | glTF material index → Blender `Material` |
| `mesh_index_to_object` | glTF mesh index → mesh object |
| `mesh_node_index_to_object_name` | Mesh-bearing node → object name |

Import callbacks SHOULD store results on Blender data (property groups). They MUST
NOT rely on mutating `json_dict`.

## Export context

Invoked in `Vrm1Exporter.add_vrm_extension_to_glb()` after stock `VRMC_vrm` /
`VRMC_springBone` / node constraints are written, before generator / buffer length
finalization and GLB packing.

| Field | Meaning |
|-------|---------|
| `context` | Blender context |
| `armature` | Exported armature |
| `json_dict` | Mutable glTF root dict |
| `buffer0` | Mutable primary binary buffer |
| `bone_name_to_node_index` | Final bone → node index |
| `object_name_to_node_index` | Final object → node index |
| `image_name_to_index` | Mutable image name → image index map used by the exporter |
| `material_name_to_index` | Material name → material index |
| `mesh_object_name_to_node_index` | Mesh object → node index |
| `mesh_object_name_to_morph_target_names` | Morph target names per mesh object |

Export callbacks MAY append root extensions and `extensionsUsed` entries. They MAY
append buffer data when they also create valid buffer views. They MUST NOT reindex
existing `nodes`, `meshes`, `materials`, or `images` already referenced by stock VRM
extensions.

`image_name_to_index` starts empty and is populated as the VRM postprocessor creates
or reuses images. It is not a full dump of every image emitted by glTF-Blender-IO.

## Example usage

Non-normative.

```python
from io_scene_vrm.extension_hooks import (
    Vrm1ExportExtensionContext,
    Vrm1ImportExtensionContext,
    register_vrm1_export_extension_hook,
    register_vrm1_import_extension_hook,
    unregister_vrm1_export_extension_hook,
    unregister_vrm1_import_extension_hook,
)

def on_vrm1_import(ctx: Vrm1ImportExtensionContext) -> None:
    extensions = ctx.json_dict.get("extensions")
    if not isinstance(extensions, dict):
        return
    vfx = extensions.get("VRMXT_vfx")
    # resolve emitters via ctx.node_index_to_bone_name / object maps

def on_vrm1_export(ctx: Vrm1ExportExtensionContext) -> None:
    extensions = ctx.json_dict.setdefault("extensions", {})
    assert isinstance(extensions, dict)
    extensions["VRMXT_vfx"] = {"specVersion": "1.0", "emitters": []}
    used = ctx.json_dict.setdefault("extensionsUsed", [])
    assert isinstance(used, list)
    if "VRMXT_vfx" not in used:
        used.append("VRMXT_vfx")

def register() -> None:
    register_vrm1_import_extension_hook(on_vrm1_import)
    register_vrm1_export_extension_hook(on_vrm1_export)

def unregister() -> None:
    unregister_vrm1_import_extension_hook(on_vrm1_import)
    unregister_vrm1_export_extension_hook(on_vrm1_export)
```

## Relation to VFX

[Blender VFX](blender-vfx.md) is implemented by
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender)
through these hooks. Hooks are the prerequisite for a clean separate add-on with
bone-attached emitters.

## Open questions

| Topic | Status |
|-------|--------|
| Stable helper to append textures/images from hooks | TBD |
| Deduplicate `extensionsUsed` in core exporter | TBD |
| VRM0 hooks | Out of scope unless separately requested |
