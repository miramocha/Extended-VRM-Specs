---
title: Blender Extension Hooks
aliases:
  - VRM1 extension hooks
  - third-party VRMXT hooks
  - Blender VRM1 hook API
tags:
  - extended-vrm
  - implementation/blender
  - format/gltf-extension
  - compatibility/vrm1
type: guide
status: draft
---

# Blender Extension Hooks

VRM 1.0 third-party import/export hooks shipped in stock
[VRM Add-on for Blender](https://github.com/saturday06/VRM-Addon-for-Blender)
**4.6.0** ([changelog](https://github.com/saturday06/VRM-Addon-for-Blender/blob/v4.6.0/CHANGELOG.md),
commit [2c4b073](https://github.com/saturday06/VRM-Addon-for-Blender/commit/2c4b07336a536aafa2dd206c6a22290da7da03b7)).
The host copies the glTF-Blender-IO user-extension pattern: enabled add-ons expose
classes on their **root module**. After stock VRM node maps exist, the host calls
those methods with glTF JSON, BIN, and index → Blender ID maps.

Primary consumer:
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender)
(`io_scene_vrmxt`). Spec examples: [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md),
[VRMXT_lattice](../specs/extensions/deformation/vrmxt-lattice.md).

Host sources:

- `src/io_scene_vrm/common/third_party_user_extension.py`
- `Vrm1Importer.on_post_import` / `trigger_post_import_hook`
- `Vrm1Exporter.trigger_pre_save_hook`
- Examples: `examples/vrm1_import_hook/`, `examples/vrm1_export_hook/`

Unity parallel (still a fork propose): [univrm-upstream-hooks.md](univrm-upstream-hooks.md).

## Why hooks exist

Stock VRM import builds `node index → Object/Bone` maps and then discards them.
Stock VRM export builds the final maps only inside `add_vrm_extension_to_glb()`.
Bone-referenced `VRMXT_*` needs those maps.

Ordinary glTF2 user extensions run before VRM postprocess and miss those maps.
Import `post_import_hook` is after the file is loaded and stock VRM is on Blender IDs; export `pre_save_hook` is after stock `VRMC_*` is written in `add_vrm_extension_to_glb()`.

## Host requirements

| Requirement | Detail |
|-------------|--------|
| Host | [VRM format 4.6.0](https://github.com/saturday06/VRM-Addon-for-Blender/releases/tag/v4.6.0) or later |
| VRM version | VRM 1.0 only. VRM 0.0 `on_post_import` is a no-op |
| Preferences | None. If the class exists on an enabled add-on, the host instantiates it |

The add-on name in `blender_manifest.toml` (`name` + `version`) is appended to
`asset.generator`.

## Discovery

On VRM 1.0 import/export, the host walks `context.preferences.addons`, loads each
enabled add-on's root module (`sys.modules[addon_name]`), and looks for:

| Class on add-on root | Method |
|----------------------|--------|
| `Vrm1ImportUserExtension` | `post_import_hook` |
| `Vrm1ExportUserExtension` | `pre_save_hook` |

Blender 4.2+ extensions use keys like `bl_ext.<repo>.vrmxt`. Put the classes on
that package's `__init__.py` (re-export is enough). Nested modules are ignored.

The host instantiates the class with no arguments. Keyword-only parameters without
defaults cause the callback to be skipped (logged). Extra positional parameters
are truncated. Exceptions in the callback are logged and **swallowed**; stock I/O
continues.

Reference:
[VRMXT `hooks/vrm1_hooks.py`](https://github.com/miramocha/VRMXT-Extension-for-Blender/blob/main/src/io_scene_vrmxt/hooks/vrm1_hooks.py)
and `io_scene_vrmxt/__init__.py`.

## Invoke sites

| Direction | When |
|-----------|------|
| Import | `AbstractBaseVrmImporter.import_vrm()` finally: `on_post_import()` after glTF load, VRM extensions, selection setup |
| Export | End of `Vrm1Exporter.add_vrm_extension_to_glb()`, after stock `VRMC_*`. Host then `make_json()`-copies the dict, rewrites `asset.generator`, sets `buffers[0].byteLength`, packs GLB |

Export JSON mutations must be JSON-safe. Host `byteLength` follows `len(bin_chunk)`
after the hook.

## Method arguments

Positional. Official example signatures:

```python
class Vrm1ImportUserExtension:
    def post_import_hook(
        self,
        json_chunk,  # Mapping[str, JsonView]; recursively frozen
        bin_chunk,  # bytes
        armature,  # Object
        node_index_to_object,  # Mapping[int, Object]
        node_index_to_bone,  # Mapping[int, Bone]
        image_index_to_image,  # Mapping[int, Image]
        material_index_to_material,  # Mapping[int, Material]
        mesh_index_to_mesh,  # Mapping[int, Mesh]
    ) -> None: ...

class Vrm1ExportUserExtension:
    def pre_save_hook(
        self,
        json_chunk,  # mutable dict[str, object]
        bin_chunk,  # bytearray
        armature,
        node_index_to_object,
        node_index_to_bone,
        image_index_to_image,
        material_index_to_material,
        mesh_index_to_mesh,
    ) -> None: ...
```

Export maps are `MappingProxyType` (index → ID). Invert `.name` when a consumer
walks name → index. Build a **local** mutable `{image.name: index}` if the hook
appends images via `Vrm1Exporter.find_or_create_image`. The host does not pass
`bpy.Context`; use `bpy.context` during the operator.

Import callbacks write Blender data (property groups, pointers). Do not mutate
frozen `json_chunk`.

Export callbacks MAY append root extensions, `extensionsUsed`, buffer bytes, and
new `images` / `textures` / `bufferViews` that stay consistent with `byteLength`.

Export callbacks MUST NOT insert, remove, or reorder existing indexed `nodes`,
`meshes`, `materials`, or `images` already referenced by stock `VRMC_*`.

## Viewport-only helpers

`pre_save_hook` runs **after** `export_objects` gather. Stock 4.6.0 does not skip
a `vrm_exclude_from_export` custom property. Viewport `hide_set` still exports
when `export_invisibles` is on.

Consumers that spawn preview meshes MUST keep them out of gather themselves
(unlink from collections, or exclude from the view layer, for the duration of
`EXPORT_SCENE_OT_vrm.execute`). Do not delete nodes from `json_chunk` (index
invalidation).

VRMXT: tag `vrmxt_vfx_preview`, unlink in `vfx/export_preview_omit.py`. Property
groups stay the export source of truth.

## Example

Non-normative. Classes live on the add-on root module.

```python
from collections.abc import Mapping

from bpy.types import Bone, Image, Material, Mesh, Object


class Vrm1ImportUserExtension:
    def post_import_hook(
        self,
        json_chunk: Mapping[str, object],
        _bin_chunk: bytes,
        armature: Object,
        _node_index_to_object: Mapping[int, Object],
        node_index_to_bone: Mapping[int, Bone],
        _image_index_to_image: Mapping[int, Image],
        _material_index_to_material: Mapping[int, Material],
        _mesh_index_to_mesh: Mapping[int, Mesh],
    ) -> None:
        extensions = json_chunk.get("extensions")
        if not isinstance(extensions, dict):
            return
        payload = extensions.get("VRMXT_example")
        # Resolve nodes via node_index_to_bone[i].name
        # Store on armature.data property groups.


class Vrm1ExportUserExtension:
    def pre_save_hook(
        self,
        json_chunk: dict[str, object],
        _bin_chunk: bytearray,
        _armature: Object,
        _node_index_to_object: Mapping[int, Object],
        _node_index_to_bone: Mapping[int, Bone],
        _image_index_to_image: Mapping[int, Image],
        _material_index_to_material: Mapping[int, Material],
        _mesh_index_to_mesh: Mapping[int, Mesh],
    ) -> None:
        extensions = json_chunk.setdefault("extensions", {})
        assert isinstance(extensions, dict)
        extensions["VRMXT_example"] = {"specVersion": "1.0"}
        used = json_chunk.setdefault("extensionsUsed", [])
        assert isinstance(used, list)
        if "VRMXT_example" not in used:
            used.append("VRMXT_example")
```

## Relation to VRMXT

[Blender VRMXT](blender-vrmxt.md) implements VFX, materials override, and MToonXT
stencil through these methods. A shim inverts maps for existing `apply_*`
functions.

## Open questions

| Topic | Status |
|-------|--------|
| Stable helper to append textures/images from hooks | TBD (today: `find_or_create_image` on `Vrm1Exporter`) |
| Deduplicate `extensionsUsed` in core exporter | TBD |
| Host-side skip for viewport helpers | Out of scope; consumer unlinks before gather |
| VRM0 hooks | Out of scope |
