---
title: MToonXT stencil and lilToon materials override in Warudo
aliases:
  - Example use case
  - UniVRMXT materials overview
  - Unity materials working example
  - MToonXT and lilToon override example
tags:
  - extended-vrm
  - implementation/unity
  - implementation/warudo
  - spec/materials
  - compatibility/vrm1
  - editorial/manual-review
type: guide
status: draft
---

# MToonXT stencil and lilToon materials override in Warudo

A VRM 1.0 Character in Warudo can load stock MToon, MToonXT stencil, or a Unity materials override (`VRMXT_materials_override`: named shader such as lilToon or Poiyomi). This page uses lilToon. UniVRMXT (`com.vrmxt.univrmxt`) reads the extras and swaps shaders on the loaded avatar. The Warudo VRMXT plugin includes that package; shader plugins install lilToon and MToonXT.

## Unity stack

[Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) forks [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM). Extra glTF extensions can import and export through hooks meant for upstream UniVRM. The fork does not define `VRMXT_*` itself.

[UniVRMXT](https://github.com/miramocha/UniVRMXT) (`com.vrmxt.univrmxt`) is a Unity package. It reads `VRMXT_*` from the file and applies them to the avatar. Stock UniVRM still loads VRM 1.0. Writing `VRMXT_*` on export needs those fork hooks.

`VRMXT_*` is listed in `extensionsUsed` only (not `extensionsRequired`). One `.vrm` / `.glb`.

```mermaid
flowchart TB
  upstream["vrm-c/UniVRM"]
  fork["Extended-UniVRM fork"]
  pkg["UniVRMXT UPM"]
  file[".vrm glTF + VRMC_* + optional VRMXT_*"]
  upstream -->|"generic import/export hooks"| fork
  fork --> file
  file --> pkg
  pkg -->|"parse and swap shaders"| override["VRMXT_materials_override"]
  pkg -->|"MToonXT"| mtoonxt["VRMXT_materials_mtoonxt"]
```

[UniVRMXT](../implementations/univrm-vrmxt.md), [UniVRM upstream hooks](../implementations/univrm-upstream-hooks.md), [architecture](../architecture.md).

## Warudo (Unity) stack

After the Character loads, [VRMXT Plugin for Warudo](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) (`mira.vrmxt`) runs. Warudo still loads stock VRM through UniVRM. The plugin includes UniVRMXT. [lilToon](https://steamcommunity.com/sharedfiles/filedetails/?id=3768913139) and [MToonXT](https://steamcommunity.com/sharedfiles/filedetails/?id=3786449905) ship lilToon and `VRMXT/MToonXT10` (Built-in).

```mermaid
flowchart TB
  file[".vrm glTF + VRMC_* + optional VRMXT_*"]
  warudo["Warudo Character load"]
  univrm["UniVRM in Warudo"]
  plugin["VRMXT Plugin for Warudo mira.vrmxt"]
  shaders["Warudo Shader Plugins UMods"]
  file --> warudo
  warudo --> univrm
  warudo --> plugin
  shaders -->|"install shaders"| plugin
  plugin -->|"parse and swap shaders"| override["VRMXT_materials_override"]
  plugin -->|"MToonXT"| mtoonxt["VRMXT_materials_mtoonxt"]
```

[Warudo VRMXT](../implementations/warudo-vrmxt.md), [VRMXT Unity packages](../implementations/vrmxt-unity-packages.md).

## Which shader wins

Per material, same order as [VRMXT_materials_mtoonxt](../specs/extensions/materials/vrmxt-materials-mtoonxt/README.md#load-gate):

```mermaid
flowchart TD
  mat["materials i"]
  mtoon["VRMC_materials_mtoon"]
  xt["VRMXT_materials_mtoonxt"]
  ov["VRMXT_materials_override optional"]
  mat --> mtoon
  mat --> xt
  mat --> ov
  ov -->|"shader found"| engineShader["lilToon / Poiyomi / named shader"]
  ov -->|"no matching shader"| xtGate["MToonXT"]
  xtGate --> xt
  xt -->|"MToonXT shader present"| mtoonxt["MToonXT shader"]
  xt -->|"no MToonXT shader"| stock["stock MToon"]
  mtoon --> stock
```

If the lilToon (or other named) shader is installed, that override is applied. MToonXT and stencil are not applied on that material.

## Images

The following example uses a VRM converted from [SiuSiu (ADPX, Booth)](https://adpx.booth.pm/items/8426340). Mesh and textures belong to that product; this repo does not include the `.vrm`. Left to right: stock MToon, MToonXT stencil, lilToon override.

| Stock MToon | MToonXT stencil | lilToon override |
| :---: | :---: | :---: |
| ![Stock MToon](images/mtoonxt-liltoon-override-warudo/stock-mtoon.png) | ![MToonXT stencil](images/mtoonxt-liltoon-override-warudo/mtoonxt-stencil.png) | ![lilToon override](images/mtoonxt-liltoon-override-warudo/liltoon-override.png) |

Stock: hair occludes eyes, eyebrows, and eyelashes. MToonXT: eyes, eyebrows, and eyelashes write over the hair using stencil. lilToon: `VRMXT_materials_override` swaps the shader to lilToon.

### Stock MToon

Hair draws in front of eyes, eyebrows, and eyelashes. `VRMC_materials_mtoon` and core glTF materials are UniVRM's import. No MToonXT swap and no override shader.

### MToonXT stencil

Shader `VRMXT/MToonXT10` (Built-in). Eyes, eyebrows, and eyelashes write a stencil mask. Hair is clipped where that mask is set (`outside`). Tutorial: [Unity MToonXT stencil](../tutorials/unity-mtoonxt-stencil.md).

Stencil is on two of twelve materials:

| `name` | `stencil` |
| --- | --- |
| `SiuSiu_FaceStencil_MToonXT` | `{ "op": "write" }` |
| `SiuSiu_HairStencil_MToonXT` | `{ "op": "outside", "materials": [1] }` |

`SiuSiu_FaceStencil_MToonXT`:

```json
{
  "extensions": {
    "VRMXT_materials_mtoonxt": {
      "specVersion": "1.0",
      "stencil": { "op": "write" }
    }
  }
}
```

`SiuSiu_HairStencil_MToonXT`:

```json
{
  "extensions": {
    "VRMXT_materials_mtoonxt": {
      "specVersion": "1.0",
      "stencil": { "op": "outside", "materials": [1] }
    }
  }
}
```

Field table: [stencil](../specs/extensions/materials/vrmxt-materials-stencil.md).

### lilToon override

Every material carries `VRMXT_materials_override`: Unity, shader name `lilToon`, Built-in (`builtin`), provider `com.vrmxt.univrmxt`. Transparent clothing uses `Hidden/lilToonTransparent` (`SiuSiu_Alpha_MToonXT`). Each override lists about 470 lilToon properties (including leftover `_DummyProperty` rows). No MToon-to-lilToon `bindings`. Stencil JSON is still on `SiuSiu_FaceStencil_MToonXT` and `SiuSiu_HairStencil_MToonXT`; once lilToon is on the material, MToonXT and stencil are not applied. Hair lighting is lilToon matcap with multiply. Conversion left MToon matcap addition blend unmapped. Tutorial: [Blender materials override](../tutorials/blender-materials-override.md). [VRMXT Editor](../implementations/vrmxt-editor.md#materials-apply-materialize-and-transfer).

On `SiuSiu_Face_MToonXT`. About 470 `properties` follow; three shown:

```json
{
  "extensions": {
    "VRMXT_materials_override": {
      "specVersion": "1.0",
      "overrides": [
        {
          "engine": "unity",
          "material": {
            "id": "lilToon",
            "idType": "shaderName",
            "provider": { "id": "com.vrmxt.univrmxt", "version": "0.1.0" },
            "variant": "builtin"
          },
          "properties": [
            { "name": "_Invisible", "type": "scalar", "value": 0.0 },
            { "name": "_MainTex", "type": "texture", "texture": 0 },
            { "name": "_MatCapTex", "type": "texture", "texture": 8 },
            ...
          ]
        }
      ]
    }
  }
}
```

## Related

- [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
- [VRMXT_materials_mtoonxt](../specs/extensions/materials/vrmxt-materials-mtoonxt/README.md)
- [Warudo VRMXT](../implementations/warudo-vrmxt.md)
- [Unity lilToon catalog](../references/catalogs/unity-liltoon.md) (`shaderName` `lilToon`)
