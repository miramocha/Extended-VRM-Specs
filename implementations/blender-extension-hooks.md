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

API and implementation notes for the public VRM 1.0 import/export hooks in
[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender).
Third-party Blender add-ons use this surface to read or write root glTF extensions
(for example `VRMXT_*`) after stock VRM node maps exist.

Primary consumer today:
[VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender)
(`io_scene_vrmxt`). Spec examples: [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md),
[VRMXT_lattice](../specs/extensions/deformation/vrmxt-lattice.md).

Module: `io_scene_vrm.extension_hooks` (source:
`src/io_scene_vrm/extension_hooks.py`).

## Fork and upstream intent

[Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender)
is a fork of [saturday06/VRM-Addon-for-Blender](https://github.com/saturday06/VRM-Addon-for-Blender).
The hook API is **generic** (not VRMXT-specific). Intent: propose the same surface
upstream so stock Blender VRM hosts can load optional packages without the fork.

Unity parallel: [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM)
generic hooks. See [univrm-upstream-hooks.md](univrm-upstream-hooks.md).

## Why hooks exist

Stock VRM import builds temporary `node index → Object/PoseBone` maps and then
discards them. Stock VRM export builds final `bone/object name → node index` maps
only inside `add_vrm_extension_to_glb()`. Without hooks, a third-party add-on cannot
reliably attach bone-referenced extensions.

glTF2 user extensions run too early on import, and too early on export (before VRM
postprocessing). They do not receive those maps.

## Host requirements (operators)

| Requirement | Detail |
|-------------|--------|
| Host | Extended-VRM-Addon-for-Blender with `extension_hooks` |
| VRM version | VRM 1.0 only. VRM 0.0 is out of scope |
| Preferences | Import and export hooks are **opt-in**, default **off** |

### Preferences

Edit → Preferences → Add-ons → VRM (Extended):

| Property | Default | Effect |
|----------|---------|--------|
| `enable_vrm1_import_extension_hooks` | `False` | When off, registered import hooks are never invoked |
| `enable_vrm1_export_extension_hooks` | `False` | When off, registered export hooks are never invoked |

Registration still succeeds when prefs are off. Consumers that need round-trip
MUST document that operators enable both toggles (or automate setting them).

Prefs live on `VrmAddonPreferences` only (not per-file import/export operator
properties).

## Module discovery

Development installs often expose `io_scene_vrm.extension_hooks`. Blender 4.2+
extensions may load as `bl_ext.<repo>.vrm.extension_hooks`.

Third parties SHOULD soft-import:

1. Try `importlib.import_module("io_scene_vrm.extension_hooks")`.
2. Else scan `sys.modules` for names starting with `bl_ext.` and ending with
   `.vrm.extension_hooks`.
3. If neither loads, log and skip registration (host without hooks).

Reference pattern:
[VRMXT `hooks/vrm1_hooks.py`](https://github.com/miramocha/VRMXT-Extension-for-Blender/blob/main/src/io_scene_vrmxt/hooks/vrm1_hooks.py).

## API reference

### Registration

| Symbol | Role |
|--------|------|
| `register_vrm1_import_extension_hook(hook)` | Append import callback |
| `unregister_vrm1_import_extension_hook(hook)` | Remove import callback (missing = no-op) |
| `register_vrm1_export_extension_hook(hook)` | Append export callback |
| `unregister_vrm1_export_extension_hook(hook)` | Remove export callback (missing = no-op) |
| `clear_vrm1_extension_hooks()` | Clear all hooks; **tests only** |

Callback type (protocols are positional-only):

```python
def hook(context: Vrm1ImportExtensionContext, /) -> None: ...
def hook(context: Vrm1ExportExtensionContext, /) -> None: ...
```

### Lifetime and order

- Hooks are process-global lists. Append order = invoke order (FIFO).
- Duplicate `register_*` of the same callable is ignored.
- Dispatch copies the list (`tuple(...)`) so a hook MAY unregister itself mid-run.
- Hooks are **not** cleared when the VRM add-on is disabled. Third parties MUST
  `unregister_*` from their own `unregister()`.
- Exceptions propagate and abort the host import/export.

No priority API. Across add-ons, earlier Blender enable / `register()` wins the
earlier slot. Within one add-on, combine work in one registered callable if order
between features must be fixed.

### Constants

| Symbol | Value | Role |
|--------|-------|------|
| `EXCLUDE_FROM_EXPORT_CUSTOM_PROP` | `"vrm_exclude_from_export"` | Custom property name; truthy → object omitted from `export_objects` |

Host filter is in `editor/search.py` `export_objects`. Product-specific tags (e.g.
VRMXT’s `vrmxt_vfx_preview`) are for that add-on’s lifecycle only; they do not
drive the host skip.

### Invoke sites (host)

| Direction | When | Gate |
|-----------|------|------|
| Import | End of `Vrm1Importer.load_gltf_extensions()`, after spring bone, node constraint, heavy migration | `enable_vrm1_import_extension_hooks` |
| Export | In `Vrm1Exporter.add_vrm_extension_to_glb()`, after stock `VRMC_vrm` / `VRMC_springBone` / constraints, before generator string and GLB pack | `enable_vrm1_export_extension_hooks` |

`invoke_vrm1_*_extension_hooks` and `create_vrm1_import_extension_context` are host
internals. Third parties register only; they do not call invoke.

## Import context

`Vrm1ImportExtensionContext` (frozen dataclass). `json_dict` and index maps are
read-only snapshots (`Mapping` / `MappingProxyType`).

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

Import callbacks SHOULD write results onto Blender data (property groups, objects).
They MUST NOT rely on mutating `json_dict`.

## Export context

`Vrm1ExportExtensionContext` (frozen dataclass; several fields are mutable
containers).

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

Export callbacks MAY:

- Append root extensions and `extensionsUsed` entries.
- Append buffer bytes when they also create valid buffer views / update
  `byteLength`.

Export callbacks MUST NOT:

- Insert, remove, or reorder existing indexed `nodes`, `meshes`, `materials`, or
  `images` already referenced by stock VRM extensions in a way that invalidates
  those references.

`image_name_to_index` starts empty and fills as the VRM postprocessor creates or
reuses images. It is not a full dump of every image emitted by glTF-Blender-IO.

## Viewport-only helpers

Late export hooks cannot strip meshes already gathered by `export_objects`. For
viewport preview empties/meshes that must not enter the GLB:

1. Set `obj[EXCLUDE_FROM_EXPORT_CUSTOM_PROP] = 1` (or soft-import the constant).
2. Keep any product-specific tag for clear/rebuild ownership separately.

Soft-import the constant with a string fallback so the consumer still works if
an older host lacks the symbol:

```python
EXCLUDE_FROM_EXPORT_CUSTOM_PROP = "vrm_exclude_from_export"
try:
    from io_scene_vrm.extension_hooks import (
        EXCLUDE_FROM_EXPORT_CUSTOM_PROP as _HOST,
    )
    EXCLUDE_FROM_EXPORT_CUSTOM_PROP = _HOST
except ImportError:
    pass
```

## Example usage

Non-normative. Soft-detect and prefs are omitted for brevity; production add-ons
SHOULD soft-import and document the preference toggles.

```python
from io_scene_vrm.extension_hooks import (
    Vrm1ExportExtensionContext,
    Vrm1ImportExtensionContext,
    register_vrm1_export_extension_hook,
    register_vrm1_import_extension_hook,
    unregister_vrm1_export_extension_hook,
    unregister_vrm1_import_extension_hook,
)

def on_vrm1_import(ctx: Vrm1ImportExtensionContext, /) -> None:
    extensions = ctx.json_dict.get("extensions")
    if not isinstance(extensions, dict):
        return
    payload = extensions.get("VRMXT_example")
    # Resolve nodes via ctx.node_index_to_bone_name / object maps.
    # Store on ctx.armature (property groups).

def on_vrm1_export(ctx: Vrm1ExportExtensionContext, /) -> None:
    extensions = ctx.json_dict.setdefault("extensions", {})
    assert isinstance(extensions, dict)
    extensions["VRMXT_example"] = {"specVersion": "1.0"}
    used = ctx.json_dict.setdefault("extensionsUsed", [])
    assert isinstance(used, list)
    if "VRMXT_example" not in used:
        used.append("VRMXT_example")

def register() -> None:
    register_vrm1_import_extension_hook(on_vrm1_import)
    register_vrm1_export_extension_hook(on_vrm1_export)

def unregister() -> None:
    unregister_vrm1_import_extension_hook(on_vrm1_import)
    unregister_vrm1_export_extension_hook(on_vrm1_export)
```

## Relation to VRMXT features

[Blender VRMXT](blender-vrmxt.md) implements VFX and materials override through
these hooks. Preview helpers set `vrm_exclude_from_export` plus a VRMXT lifecycle
tag. Property groups remain the export source of truth.

## Open questions

| Topic | Status |
|-------|--------|
| Stable helper to append textures/images from hooks | TBD |
| Deduplicate `extensionsUsed` in core exporter | TBD |
| Early export filter hook (UniVRM PreHierarchy-style) | Out of scope; use `vrm_exclude_from_export` |
| VRM0 hooks | Out of scope unless separately requested |
| Default prefs on (match UniVRM project settings) | TBD |
