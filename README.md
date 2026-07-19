---
title: Extended VRM Specs
aliases: []
tags:
  - extended-vrm
  - type/index
type: index
status: draft
---

# Extended VRM Specs

Specifications and design notes for Extended VRM. Implementations target
[UniVRM](https://github.com/vrm-c/UniVRM), VRM4U, Godot (godot-vrm), Three.js
(three-vrm), and the
[Blender add-on](https://github.com/miramocha/Extended-VRM-Addon-for-Blender);
this repository defines portable file behavior.

Host forks that carry **generic** extension hooks (to propose upstream; not VRMXT-specific):

| Fork | Upstream | Hooks doc |
|------|----------|-----------|
| [Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender) | [saturday06/VRM-Addon-for-Blender](https://github.com/saturday06/VRM-Addon-for-Blender) | [Blender Extension Hooks](implementations/blender-extension-hooks.md) |
| [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) | [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) | [UniVRM upstream hooks](implementations/univrm-upstream-hooks.md) |

Optional `VRMXT_*` consumers:

| Repo | Role |
|------|------|
| [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender) | Blender authoring / I/O via VRM1 hooks |
| [UniVRMXT](https://github.com/miramocha/UniVRMXT) | Unity UPM package on [UniVRM](https://github.com/vrm-c/UniVRM) |
| [VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo) | Warudo consumer plugin (vendored UniVRMXT VFX + materials override; UMod). Install: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) |
| Godot VRMXT addon (planned) | Optional Godot addon beside [godot-vrm](https://github.com/V-Sekai/godot-vrm) |
| three-vrmxt (planned) | Optional npm package beside [@pixiv/three-vrm](https://github.com/pixiv/three-vrm) |

## Architecture

| Note | Topic | Status |
|------|-------|--------|
| [Extended VRM Architecture](architecture.md) | Multi-engine authoring + runtime consumers; stock VRM stays as-is; Extended optional per engine | draft |

## Drafts

| Note | Extension / topic | Status |
|------|-------------------|--------|
| [VRMXT_materials_override](specs/vrmxt-materials-override.md) | `VRMXT_materials_override` | draft |
| [VRMXT_springBone_override](specs/vrmxt-spring-bone-override.md) | `VRMXT_springBone_override` | draft |
| [VRMXT_vfx](specs/vrmxt-vfx.md) | `VRMXT_vfx` (particles) | draft |
| [VRMXT_lattice](specs/vrmxt-lattice.md) | `VRMXT_lattice` (FFD / cage) | draft |

## Implementation profiles

| Note | Target | Status |
|------|--------|--------|
| [UniVRM Materials Override](implementations/univrm-materials-override.md) | Unity / UniVRMXT | draft |
| [Warudo VRMXT](implementations/warudo-vrmxt.md) | Warudo plugin / `VRMXT_vfx` + materials override consumer | draft |
| [Warudo Materials Override](implementations/warudo-materials-override.md) | Warudo plugin / post-load materials apply (shipped) | draft |
| [UniVRM VFX](implementations/univrm-vfx.md) | Unity / UniVRMXT / `VRMXT_vfx` | draft |
| [Godot VFX](implementations/godot-vfx.md) | Godot / godot-vrm / `VRMXT_vfx` | draft |
| [three-vrm VFX](implementations/three-vrm-vfx.md) | Three.js / three-vrm / `VRMXT_vfx` | draft |
| [VRM4U Materials Override](implementations/vrm4u-materials-override.md) | Unreal / VRM4U | draft |
| [UniVRM upstream hooks](implementations/univrm-upstream-hooks.md) | UniVRM / Extended-UniVRM ScriptedImporter hooks (upstream propose) | draft |
| [Blender Extension Hooks](implementations/blender-extension-hooks.md) | Blender / Extended-VRM-Addon-for-Blender VRM1 hook API (prefs, exclude prop, upstream propose) | draft |
| [Blender VFX](implementations/blender-vfx.md) | Blender VRMXT extension / `VRMXT_vfx` | draft |
| [Blender Materials Override](implementations/blender-materials-override.md) | Blender VRMXT extension / `VRMXT_materials_override` (Unreal `resourcePath` + multi-variant format/UI pending) | draft |
