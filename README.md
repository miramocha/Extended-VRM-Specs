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
| [VRMXT-Unity-Shader-Plugins](https://github.com/miramocha/VRMXT-Unity-Shader-Plugins) | Unity UPM `com.miramocha.vrmxt.unity.shader-plugins` — deprecated transitional Player warm/inventory; supersede with AB packs + in-pack config |
| [VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo) | Warudo consumer plugin (vendored UniVRMXT VFX + materials override; UMod). Install: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) |
| VRMXT Unity Player (planned) | Separate Unity `2021.3.45f2` desktop app: drag-drop view/edit/export; Warudo-aligned megashaders. Today UniVRMXT + shader-plugins; planned StreamingAssets packs. See [player profile](implementations/vrmxt-unity-player.md), [Unity packages map](implementations/vrmxt-unity-packages.md), [desktop Player primary](decisions/vrmxt-desktop-player-primary.md) |
| VRM Posing Desktop consumer (planned) | Post-load VRMXT on [VRM Posing Desktop](https://store.steampowered.com/app/1895630/VRM_Posing_Desktop/); host UniVRM `0.129.3` (measured). See [profile](implementations/vrm-posing-desktop-vrmxt.md) |
| Godot VRMXT addon (planned) | Optional Godot addon beside [godot-vrm](https://github.com/V-Sekai/godot-vrm) |
| three-vrmxt (planned) | Optional npm package beside [@pixiv/three-vrm](https://github.com/pixiv/three-vrm) |
| VRMXT → VRChat converter (planned) | Separate product. Offline Unity conversion of `.vrm` (`VRMC_*` + `VRMXT_*`) into a VRChat-ready avatar. Consumes the portable contract; does not put VRChat SDK types in the file schema. See [Animation controller standardization](decisions/animation-controller-standardization.md) |

## Architecture

| Note | Topic | Status |
|------|-------|--------|
| [Extended VRM Architecture](architecture.md) | Multi-engine authoring + runtime consumers; stock VRM stays as-is; Extended optional per engine | draft |

## Decisions

| Note | Topic | Status |
|------|-------|--------|
| [Animation controller standardization](decisions/animation-controller-standardization.md) | Durable final scope: `VRMXT_AnimationController` + `VRMXT_AnimationClip`; bridge one-shots; packaging A | draft |
| [VFX capability boundaries](decisions/vfx-capability-boundaries.md) | One extension per capability; node-based particle attachment; lattice stays separate | accepted |
| [Billboard sprite ownership](decisions/billboard-sprite-ownership.md) | Flatten particle appearance; no Billboard Sprite fragment; runtime geometry is consumer-owned | accepted |
| [VFX capability naming](decisions/vfx-capability-naming.md) | `VRMXT_sprite_particle` and candidate VFX family names | accepted |
| [VRMXT desktop Player primary](decisions/vrmxt-desktop-player-primary.md) | Desktop Unity Player for preview/edit; drop Hub extension + WebGL product path | accepted |
| [VRoid Hub browser viewer architecture](decisions/vroid-hub-browser-viewer-architecture.md) | Historical Hub extension + Player WebGL; superseded by desktop Player primary | superseded |

## Drafts

| Note | Extension / topic | Status |
|------|-------------------|--------|
| [VRMXT Conformance](specs/core/vrmxt-conformance.md) | Shared `VRMXT_*` family requirements | draft |
| [VRMXT_materials_override](specs/extensions/materials/vrmxt-materials-override.md) | `VRMXT_materials_override` | draft |
| [VRMXT_springBone_override](specs/extensions/physics/vrmxt-spring-bone-override.md) | `VRMXT_springBone_override` | draft |
| [VRMXT_sprite_particle](specs/extensions/vfx/vrmxt-sprite-particle.md) | Portable sprite particle emitters | draft |
| [VRMXT_lattice](specs/extensions/deformation/vrmxt-lattice.md) | `VRMXT_lattice` (FFD / cage) | draft |
| [VRMXT_AnimationController](specs/extensions/animation/vrmxt-animation-controller.md) | Root flat FSM; bridge one-shots; packaging A | draft |
| [VRMXT_AnimationClip](specs/extensions/animation/vrmxt-animation-clip.md) | Per-`animations[i]` metadata; required on controller-bound clips | draft |

## Implementation profiles

| Note | Target | Status |
|------|--------|--------|
| [VRMXT Editor](implementations/vrmxt-editor.md) | Cross-host editor contract + capability matrix (Blender / UniVRMXT / Unity Player / Warudo) | draft |
| [VRMXT Unity packages](implementations/vrmxt-unity-packages.md) | Unity-space UPM / app / Warudo dependency map | draft |
| [VRMXT Unity Player](implementations/vrmxt-unity-player.md) | Desktop Unity app (`2021.3.45f2`); Warudo-aligned; depends on UniVRMXT | draft |
| [VRMXT Unity Shader Plugins](implementations/vrmxt-unity-shader-plugins.md) | Deprecated host megashader ship note; pack/UMod config owns supported names | deprecated |
| [UniVRMXT](implementations/univrm-vrmxt.md) | Unity / UniVRMXT (`VRMXT_sprite_particle` + `VRMXT_materials_override`) | draft |
| [Warudo VRMXT](implementations/warudo-vrmxt.md) | Warudo plugin / particle + materials override consumer | draft |
| [VRM Posing Desktop VRMXT](implementations/vrm-posing-desktop-vrmxt.md) | Posing Desktop consumer; UniVRM `0.129.3` host pin (measured) | draft |
| [VRoid Hub browser extension](implementations/vroid-hub-browser-extension.md) | Historical Hub extension profile | superseded |
| [Unity WebGL VRMXT viewer](implementations/unity-webgl-vrmxt-viewer.md) | Historical Player WebGL / Hub notes | superseded |
| [Godot VRMXT](implementations/godot-vrmxt.md) | Godot / godot-vrm consumer (`VRMXT_sprite_particle` planned) | draft |
| [three-vrmxt](implementations/three-vrmxt.md) | Three.js / three-vrm consumer (`VRMXT_sprite_particle` planned) | draft |
| [VRM4U VRMXT](implementations/vrm4u-vrmxt.md) | Unreal / VRM4U consumer (`VRMXT_materials_override` planned) | draft |
| [UniVRM upstream hooks](implementations/univrm-upstream-hooks.md) | UniVRM / Extended-UniVRM ScriptedImporter hooks (upstream propose) | draft |
| [Blender Extension Hooks](implementations/blender-extension-hooks.md) | Blender / Extended-VRM-Addon-for-Blender VRM1 hook API (prefs, exclude prop, upstream propose) | draft |
| [Blender VRMXT](implementations/blender-vrmxt.md) | Blender VRMXT extension (`VRMXT_sprite_particle` + `VRMXT_materials_override`) | draft |

## References

| Note | Topic | Status |
|------|-------|--------|
| [Face / expression systems](references/face-expression-systems.md) | Non-normative: VRM presets, ARKit 52, VRC/Oculus 15 visemes + maps | draft |
| [glTF morph targets](references/gltf-morph-targets.md) | Non-normative: morph geometry vs animation `weights`; research closed on keyframes (stock glTF anim); Blender + UniVRM notes | draft |
| [Spring bone / secondary physics](references/spring-bone-physics-systems.md) | Non-normative: `VRMC_springBone`, MagicaCloth2, VRC PhysBones + concept maps | draft |
| [KHR / glTF overlap](references/khr-gltf-overlap.md) | Non-normative: Khronos/EXT registry vs materials, VFX, and animation (`VRMXT_AnimationController` / `VRMXT_AnimationClip`) | draft |
| [Engine particle capability](references/engine-particle-capability.md) | Non-normative: Unity Particle System vs VFX Graph / BIRP; Niagara vs Cascade; VRM4U attach constraints (2026-07-21) | draft |
| [VRoid Hub VRMXT round-trip](references/vroid-hub-vrmxt-roundtrip.md) | Non-normative: `VRMXT_materials_override` survives Hub upload → original download (2026-07-21); not an in-browser preview product | draft |
| [Warudo VRMXT Patch Export](references/warudo-vrmxt-patch-export.md) | Plan for patching VRMXT JSON into a copy of a local Warudo Character VRM | accepted |
| [Materials Override Catalogs](references/materials-override-catalogs.md) | Non-normative shader catalogs (schema, distribution, index); JSON under `references/catalogs/data/` | draft |
| [Maintaining catalogs](references/catalogs/maintaining-catalogs.md) | Maintainer pin bump, regen scripts, vendor sync | draft |
| [Unity lilToon Catalog](references/catalogs/unity-liltoon.md) | lilToon opaque/cutout/transparent JSON @ pin `2.3.4` (359 props) | draft |
| [Unity VRMXT Test Override Catalog](references/catalogs/unity-vrmxt-test-override.md) | UniVRMXT TestOverrideBuiltin / TestOverrideURP (11 props) | draft |
| [Unity Poiyomi Catalog](references/catalogs/unity-poiyomi.md) | Poiyomi Toon catalog stub (`.poiyomi/Poiyomi Toon`) | draft |
| [Warudo Poiyomi BIRP Variants](references/warudo-poiyomi-birp-variants.md) | Non-normative: BIRP cook / `multi_compile` keep set / SVC warm | draft |
| [Warudo Poiyomi Exclusions](references/warudo-poiyomi-exclusions.md) | Non-normative: excluded keywords, alts, PassTypes, vendor strips | draft |
| [Warudo Material Warm-Up](references/warudo-material-warmup.md) | Non-normative: ModHost asset warm + Poiyomi SVC | draft |
| [VRMXT Player Shader AssetBundles](references/vrmxt-player-shader-assetbundles.md) | Non-normative: desktop Player runtime AssetBundle packs for lil / Poiyomi | draft |

## Archive

| Note | Superseded by |
|------|---------------|
| [VRMXT_vfx](archive/specs/vrmxt-vfx.md) | [VRMXT_sprite_particle](specs/extensions/vfx/vrmxt-sprite-particle.md) and [VFX capability boundaries](decisions/vfx-capability-boundaries.md) |
