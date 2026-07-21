---
title: UniVRMXT
aliases:
  - UniVRM VFX
  - UniVRM Materials Override
  - VRMXT_sprite_particle for UniVRM
  - VRMXT materials override for Unity
  - UniVRMXT particles
tags:
  - extended-vrm
  - implementation/unity
  - spec/vfx
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# UniVRMXT

Unity implementation profile for
[VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md) and
[VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md).
Support belongs in [UniVRMXT](https://github.com/miramocha/UniVRMXT)
(`com.miramocha.univrmxt`), an optional UPM package that depends on stock
[UniVRM](https://github.com/vrm-c/UniVRM). UniVRM source changes are not required.

VRM 1.0 only. Extensions are optional: stock UniVRM load MUST succeed when UniVRMXT
is absent or when either extension is missing from the file.

## Package

| Item | Value |
|------|-------|
| UPM id | `com.miramocha.univrmxt` |
| Stock VRM I/O | [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) (`0.131.1`+) |
| Optional host fork | [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) |
| Unity | `2022.3` |
| Extensions | `VRMXT_sprite_particle`, `VRMXT_materials_override` |

## VFX

### Import seam

UniVRM has no general root-extension registry. UniVRMXT foundation:

1. Parse root `extensions.VRMXT_sprite_particle` from glTF JSON (`specVersion` `"1.0"`) via
   `VrmxtVfx.TryParse`.
2. Skip invalid emitters per the base spec.
3. After `Vrm10.LoadGltfDataAsync` (or equivalent), map `emitters[].node` through
   `RuntimeGltfInstance.Nodes`.
4. Call `VrmxtVfxRuntime.TryAttach(root, gltfJson, nodes, out instance)` to store
   resolved emitters on `VrmxtVfxInstance` (avatar root). `VrmxtVfxData` remains
   available as a ScriptableObject mirror for asset workflows.

Unresolved nodes skip that emitter only. UniVRMXT Runtime does not hard-reference
UniGLTF/VRM10 asmdefs; the load caller supplies JSON and the node Transform list.

### Runtime behavior (foundation)

MVP stores parsed emitter data on `VrmxtVfxInstance` (node index, `Transform`,
particle scalars, sprite texture). `VrmxtVfxParticleSystemMapper` maps portable
fields onto Unity `ParticleSystem` (camera-facing billboard render mode, node-local +Y
velocity, optional texture).
Offsets live on the resolved node (helper Empty / Transform), not on emitter fields.
See UniVRMXT [vfx-particle-mapping.md](https://github.com/miramocha/UniVRMXT/blob/main/docs/vfx-particle-mapping.md).

### Export

Unity → VRM re-export of portable emitters requires Extended-UniVRM export hooks
(`Vrm10ExportExtensionRegistry`), Project Settings → VRM10 → **Enable VRM Export
Extensions** (default on), and UniVRMXT (`VrmxtVfxExportHookBootstrap`).

Source of truth is `VrmxtVfxInstance.Emitters`, with live preview `ParticleSystem`
values (color, rate, size, etc.) folded back at export time. Preview systems are
cleared on a throwaway export copy so they do not become glTF nodes or materials.
Particle albedo is re-registered into `textures[]` when
`VrmxtVfxParticleData.Texture` or the live material is available. UniGLTF rebuilds
`extensionsUsed` from written extensions (includes `VRMXT_sprite_particle`).

Stock UniVRM without the Extended export registry does not write `VRMXT_sprite_particle`.

### AssetDatabase limits (UniVRMXT findings)

Optional consumer packages cannot patch the stock imported `.vrm` prefab after
`VrmScriptedImporter` finishes (`AddComponent` on the main asset fails; reimport rebuilds
the hierarchy).

**Current UniVRMXT workaround** (dual path):

- **Extended-UniVRM:** import hooks (Project Settings/VRM10 enable) → VFX on original `.vrm`
- **Stock UniVRM / hooks disabled:** sibling companion prefab `*.vrmxt.prefab`
- Runtime / Warudo: stock load, then `TryAttachFromGlb` — [Warudo VRMXT](warudo-vrmxt.md)
- VFX-only textures: second GLB image decode (texture enum hook still open)

Full write-up: [univrm-upstream-hooks.md](univrm-upstream-hooks.md).

### Open questions (VFX)

| Topic | Status |
|-------|--------|
| Editor `.vrm` ScriptedImporter integration | Done in Extended-UniVRM (Project Settings/VRM10 gate); stock UniVRM still needs companion prefab or upstream adoption of hook A — [univrm-upstream-hooks.md](univrm-upstream-hooks.md) |
| VFX-only `textures[]` import | Workaround: re-read GLB; prefer texture enumeration hook |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |

## Materials override

### Supported entry

The consumer considers all `overrides[]` where `engine` equals `unity`. Selection uses
`material.variant` as this profile's refinement of the base-spec selection key
(rules 6–7).

#### Profile properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `material.idType` | string | yes | `"shaderName"` |
| `material.id` | string | yes | Exact Unity shader name |
| `material.variant` | string | no (see Selection) | `builtin`, `urp`, or `hdrp` |
| `material.provider` | object | no | Unity package hint |
| `material.provider.id` | string | yes if `provider` present | Unity package name |
| `material.provider.version` | string | no | Exporter-observed package version |

`provider` is advisory per base-spec rules 18–21. This profile MUST NOT require a closed
shader registry. A consumer MAY warn about package/version mismatch. It MUST use stock
import when the shader or requested pipeline variant cannot be resolved.

#### Selection

- **One `unity` entry:** `material.variant` MAY be omitted or empty. That entry matches
  any active pipeline.
- **Two or more `unity` entries:** each MUST have a non-empty `material.variant` of
  `builtin`, `urp`, or `hdrp`. Duplicate `(unity, variant)` pairs are invalid under
  base-spec rule 6.
- Selection order:
  1. Prefer the entry whose `variant` equals the active pipeline.
  2. Else, if exactly one `unity` entry has omitted or empty `variant`, use that.
  3. Else use stock import for that material (do not apply a mismatched pipeline entry).

Authors MAY store several pipeline slots (for example `builtin` and `urp`) on one
material. Only the slot selected above is applied.

#### Example (single pipeline)

```json
{
  "engine": "unity",
  "material": {
    "idType": "shaderName",
    "id": "Example/SkinToon",
    "variant": "urp",
    "provider": {
      "id": "com.example.vrmxt-materials",
      "version": "1.2.0"
    }
  },
  "bindings": [
    {
      "source": "shadeColorFactor",
      "target": "_ShadeColor",
      "targetType": "vector"
    },
    {
      "source": "shadeMultiplyTexture",
      "target": "_ShadeTex",
      "targetType": "texture"
    },
    {
      "source": "shadingShiftFactor",
      "target": "_ShadingShiftFactor",
      "targetType": "scalar"
    },
    {
      "source": "shadingToonyFactor",
      "target": "_ShadingToonyFactor",
      "targetType": "scalar"
    }
  ],
  "properties": [
    {
      "name": "_UseRimLight",
      "type": "shaderFeature",
      "value": true
    }
  ]
}
```

#### Example (builtin and urp siblings)

```json
{
  "specVersion": "1.0",
  "overrides": [
    {
      "engine": "unity",
      "material": {
        "idType": "shaderName",
        "id": "VRMXT/Samples/TestOverrideBuiltin",
        "variant": "builtin"
      },
      "properties": [
        { "name": "_Color", "type": "vector", "value": [0, 1, 0, 1] }
      ]
    },
    {
      "engine": "unity",
      "material": {
        "idType": "shaderName",
        "id": "VRMXT/Samples/TestOverrideURP",
        "variant": "urp"
      },
      "properties": [
        { "name": "_Color", "type": "vector", "value": [1, 1, 0, 1] }
      ]
    }
  ]
}
```

`material.idType` names the identity scheme; `"shaderName"` is the only value this
profile defines today. `material.id` is the exact string passed to `Shader.Find` — no
GUID. `provider.id` is a Unity package name. `variant` identifies the intended render
pipeline:

| Value | Unity pipeline |
|-------|----------------|
| `builtin` | Built-in Render Pipeline |
| `urp` | Universal Render Pipeline |
| `hdrp` | High Definition Render Pipeline |

The optional package MUST reject a variant that does not match the active pipeline and
use stock import for that material.

### UniVRM integration

UniVRM exposes `IMaterialDescriptorGenerator`. A supporting package wraps the stock
VRM 1.0 generator:

1. Read `materials[i].extensions.VRMXT_materials_override`.
2. Select the `unity` entry for the active pipeline per Selection.
3. Resolve `material.id` via `Shader.Find` (per `material.idType: "shaderName"`).
4. Return a `MaterialDescriptor` using the resolved shader, declared `properties`, and
   declared `bindings`.
5. Delegate to the stock generator when any step fails.

Runtime callers pass the wrapper through the `materialGenerator` argument on
`Vrm10.LoadPathAsync`, `LoadBytesAsync`, or `LoadGltfDataAsync`.

Editor import uses a `MaterialDescriptorGeneratorFactory` assigned in UniVRM project
settings. The factory returns the same wrapper. With no factory assigned, UniVRM keeps
its built-in MToon, unlit, and PBR selection.

### Package and shader resolution

The VRM file names a Unity shader (`material.id`); it does not contain shader source.
UniVRMXT and the host app MUST include any shaders they intend to honor, and MUST keep
those shaders in player builds (referenced materials, shader variant collections,
Resources, or Always Included Shaders). `provider` is an advisory package hint only.

Runtime resolve order for a supporting consumer:

1. Select the `unity` override for the active pipeline (Selection) and read `material.id`.
2. Resolve the shader (typically `Shader.Find`).
3. If the shader is present and the selected entry is compatible, build the override
   material and apply `properties`, then `bindings`.
4. If the shader is missing, stripped, or incompatible, use stock VRM 1.0 import for
   that material.

A drag-and-drop or other runtime VRM viewer therefore loads every valid VRM with stock
materials by default. Overrides appear only for shaders the app (or an optional shader
pack it depends on) already ships. Remote git fetch and runtime shader compilation are
out of scope for this profile.

### Bindings

The generator reads resolved values from `VRMC_materials_mtoon` and writes them through
`MaterialDescriptor` actions.

| `targetType` | Unity operation |
|--------------|-----------------|
| `scalar` | `Material.SetFloat` |
| `vector` | `Material.SetVector` or `SetColor`, according to the target shader |
| `texture` | Imported glTF texture assigned with `Material.SetTexture` |
| `shaderFeature` | `Material.EnableKeyword` / `DisableKeyword` for a `#pragma shader_feature` or ShaderLab `[Toggle]` keyword |

The example Unity targets in the base spec follow UniVRM MToon10 naming where applicable:
`_ShadeTex`, `_ShadingShiftFactor`, `_ShadingToonyFactor`, and
`_GiEqualizationFactor`. Custom shaders may use different targets.

### Properties

`overrides[].properties` sets literal values on the resolved shader with no
`VRMC_materials_mtoon` dependency (base-spec rules 22–26). `properties[].name` is a Unity
material property name (for example `_UseRimLight`); `type` selects the same Unity
operation as the matching row in the bindings table above, reading `value` (or
`texture`) directly instead of a resolved MToon source.

A wrapper applies `properties` before `bindings` per rule 23, so a `bindings` entry wins
if an authoring error targets the same parameter name.

Exporters that emit a `properties[].texture` reference MUST register the source image
during the `Vrm10ExportExtensionPhase.PrepareTextures` phase (see
`IVrm10ExportExtension` / `Vrm10ExportExtensionContext.RegisterSRgbTexture` and
equivalents) so the texture lands in the file's `textures[]` before export finishes, per
base-spec rule 26.

### Variant survival

`material.variant` names the render-pipeline slot for that entry. Re-export and
authoring treat it as stored intent for that slot.

- Re-export MUST NOT delete or rewrite sibling `unity` entries for other variants.
- Authoring or sync for the active pipeline MUST update only the matching
  `(unity, variant)` slot, creating that slot when missing.
- An exporter MAY set `variant` from the active render pipeline only when creating a
  new slot that has no `variant` yet.
- Existing non-empty `variant` values MUST NOT be overwritten with the active pipeline
  (an entry authored `hdrp` stays `hdrp` when re-exported from URP).

### Fallback

Failure is local to one glTF material. The wrapper delegates that material index to the
stock `BuiltInVrm10MaterialDescriptorGenerator` or
`UrpVrm10MaterialDescriptorGenerator`. Unsupported files therefore load as normal
VRM 1.0 assets when the optional package is missing, disabled, or incomplete.

### Authoring catalogs

Shared shader catalog JSON (lilToon, Poiyomi, …) is owned by Specs and vendored into
consumers. UniVRMXT MAY load the same files for Editor authoring later. See
[Materials Override Catalogs](../references/materials-override-catalogs.md) (Ownership /
Distribution). Runtime apply does not require catalogs.

### Known constraints

- Built-in UniVRM generator selection covers Built-in RP and URP. HDRP support requires
  the optional package to provide its own stock-equivalent fallback.
- Runtime support requires the application to pass the generator at its VRM load sites.
- Editor support requires one-time project settings configuration.
- Shader property type validation and texture transforms remain implementation work.

### Host note: Warudo

Warudo does not expose `materialGenerator` on Character Source load. A workable plugin
path is post-load re-read of the `.vrm` plus material swap. See
[Warudo VRMXT materials override](warudo-vrmxt.md#materials-override).

### Source references

- `Packages/UniGLTF/Runtime/UniGLTF/IO/MaterialIO/Import/IMaterialDescriptorGenerator.cs`
- `Packages/UniGLTF/Runtime/UniGLTF/IO/MaterialIO/Import/MaterialDescriptor.cs`
- `Packages/VRM10/Runtime/IO/Vrm10.cs`
- `Packages/VRM10/Runtime/IO/Vrm10Exporter.cs`
- `Packages/VRM10/Runtime/IO/Export/Vrm10ExportExtension.cs`
- `Packages/VRM10/Editor/Settings/MaterialDescriptorGeneratorFactory.cs`
- `Packages/VRM10/Editor/ScriptedImporter/VrmScriptedImporterImpl.cs`

## Related

- Specs: [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md),
  [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
- Backend research: [Engine particle capability](../references/engine-particle-capability.md)
  (`ParticleSystem` required; VFX Graph optional)
- Upstream hooks / AssetDatabase workaround: [univrm-upstream-hooks.md](univrm-upstream-hooks.md)
- UniVRMXT: https://github.com/miramocha/UniVRMXT
- [Blender VRMXT](blender-vrmxt.md)
- [Warudo VRMXT](warudo-vrmxt.md)
