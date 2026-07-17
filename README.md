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

Specifications and design notes for Extended VRM. Implementations target UniVRM,
VRM4U, and the [Blender add-on](https://github.com/miramocha/Extended-VRM-Addon-for-Blender);
this vault defines portable file behavior.

Optional `VRMXT_*` consumers:

| Repo | Role |
|------|------|
| [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender) | Blender authoring / I/O via VRM1 hooks |
| [UniVRMXT](https://github.com/miramocha/UniVRMXT) | Unity UPM package on UniVRM |

## Drafts

| Note | Extension / topic | Status |
|------|-------------------|--------|
| [VRMXT_materials_override](specs/vrmxt-materials-override.md) | `VRMXT_materials_override` | draft |
| [VRMXT_springBone_override](specs/vrmxt-spring-bone-override.md) | `VRMXT_springBone_override` | draft |
| [VRMXT_vfx](specs/vrmxt-vfx.md) | `VRMXT_vfx` (particles) | draft |

## Implementation profiles

| Note | Target | Status |
|------|--------|--------|
| [UniVRM Materials Override](implementations/univrm-materials-override.md) | Unity / UniVRMXT | draft |
| [UniVRM VFX](implementations/univrm-vfx.md) | Unity / UniVRMXT / `VRMXT_vfx` | draft |
| [VRM4U Materials Override](implementations/vrm4u-materials-override.md) | Unreal / VRM4U | draft |
| [Blender Extension Hooks](implementations/blender-extension-hooks.md) | Blender add-on third-party VRM1 hooks | draft |
| [Blender VFX](implementations/blender-vfx.md) | Blender VRMXT extension / `VRMXT_vfx` | draft |
