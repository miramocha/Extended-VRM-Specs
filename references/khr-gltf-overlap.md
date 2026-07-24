---
title: KHR / glTF overlap with VRMXT
aliases:
  - KHR materials variants vs VRMXT
  - glTF particle extension research
  - KHR animation vs VRMXT AnimationController
  - KHR_animation_pointer vs VRMXT
tags:
  - extended-vrm
  - reference/gltf
  - format/gltf-extension
  - compatibility/vrm1
  - decision/animation
type: reference
status: draft
---

# KHR / glTF overlap with VRMXT

Non-normative research note. Checked ratified and in-progress entries in the
[glTF 2.0 Extension Registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md)
(as of 2026-07-20) against VRMXT materials, particle, and animation drafts.

**Finding:** no Khronos (`KHR_`) or multi-vendor (`EXT_`) extension replaces
`VRMXT_materials_override`, `VRMXT_sprite_particle`, `VRMXT_AnimationController`, or
`VRMXT_AnimationClip`. Closest materials naming collision is
`KHR_materials_variants`. No particle-emitter extension exists on the registry. No
ratified FSM or clip-metadata catalog exists for animation.

## Sources

| Source | Role |
|--------|------|
| [glTF Extension Registry](https://github.com/KhronosGroup/glTF/blob/main/extensions/README.md) | Ratified, in-progress, vendor lists |
| [KHR_materials_variants](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_materials_variants) | Material variant switching |
| [EXT_mesh_gpu_instancing](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Vendor/EXT_mesh_gpu_instancing) | GPU instance batches |
| [glTF#1521](https://github.com/KhronosGroup/glTF/issues/1521) | Particle systems out of core glTF |
| [KHR_animation_pointer](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_animation_pointer) | Channel targets beyond node TRS |
| [glTF#1730](https://github.com/KhronosGroup/glTF/issues/1730) | Playback / blending = application concern |
| [KHR_animation_controller PR #2079](https://github.com/KhronosGroup/glTF/pull/2079) | Closed draft (2021); renamed toward clip |
| [KHR_animation_clip PR #2080](https://github.com/KhronosGroup/glTF/pull/2080) | Closed draft (2022); deferred to interactivity |
| [KHR_interactivity](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_interactivity/Specification.adoc) | Behavior graph (submitted for ratification) |
| [VRMC_vrm_animation](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0) | Upstream VRMA retarget mapping |

## `VRMXT_materials_override`

VRMXT stores optional engine-specific material identities and parameter maps on
`materials[i]`. Stock VRM 1.0 import (core PBR, `KHR_materials_unlit`,
`VRMC_materials_mtoon`) stays valid when the extension is ignored. Engine shader
programs are not embedded in the file.

### Candidates

| Extension | Overlap | Notes |
|-----------|---------|-------|
| `KHR_materials_variants` | Naming / weak concept | Root named variants; mesh primitives map variant → `materials[]` index. Payload stays portable glTF materials inside the file. Designed for finite premade skins (e.g. product SKUs). |
| `KHR_materials_*` PBR pack (clearcoat, transmission, volume, sheen, emissive_strength, …) | Adjacent domain | Extends the portable material model. No external engine shader id, no override profile. |
| `KHR_materials_unlit` | Precedence only | Already in the VRMXT stock fallback chain. Not an override mechanism. |
| `KHR_texture_transform` | Narrow | UV offset / rotation / scale on `textureInfo`. May matter for binding TBD work; not an override. |
| Archived `KHR_techniques_webgl` | Historical cousin | Custom WebGL techniques in-file. Archived; not a template for VRMXT. |
| `NV_materials_mdl` (vendor) | Weak cousin | References NVIDIA Material Definition Language. Different ecosystem from Unity / Unreal profiles. |

### `KHR_materials_variants` vs VRMXT

| | `KHR_materials_variants` | `VRMXT_materials_override` |
|--|--------------------------|----------------------------|
| Attachment | Root `variants[]` + **mesh primitive** mappings | `materials[i].extensions` |
| Payload | Index into another `materials[]` entry | Engine `material` identity + `bindings` / `properties` |
| Fallback | Default primitive material | Ignore extension → MToon / unlit / PBR |
| Word `variant` | User-facing skin name (e.g. Yellow Sneaker) | Engine selection key (`builtin` / `urp`, `opaque` / `translucent`) |

Do not implement materials override by emitting `KHR_materials_variants`. Wrong
attachment point and wrong payload (loses engine ids and MToon bindings).

UI and tool authors SHOULD keep the two `variant` meanings distinct in labels and
cross-links.

## `VRMXT_sprite_particle`

VRMXT root emitters attach to glTF nodes and describe continuous point-source sprite
particles for mapping onto native particle systems.

### Candidates

| Extension | Overlap | Notes |
|-----------|---------|-------|
| Particle / FX `KHR_` or `EXT_` | None | Registry has no particle-emitter extension. [glTF#1521](https://github.com/KhronosGroup/glTF/issues/1521) confirms particles are outside core glTF. |
| `EXT_mesh_gpu_instancing` | Wrong layer | Static per-instance transforms for draw batching (trees, grass). Tools may bake a particle **snapshot** into instances; that is not live emission rate, lifetime, or billboard sim. |
| `KHR_lights_punctual` | None | Punctual lights only. |
| In-progress (`KHR_interactivity`, physics, audio_graph, gaussian_splatting, …) | None meaningful | Different domains. No particle-emitter row on the 2026-07-20 in-progress table. |

## Animation: `VRMXT_AnimationController` / `VRMXT_AnimationClip`

Decision:
[animation-controller-standardization](../decisions/animation-controller-standardization.md).

Root controller owns a flat FSM and float/bool/int params. Per-clip extension owns
playback / role metadata and is **required** on every `animations[i]` the controller
binds (VRM expression → morph pattern). Core glTF `animations[]` holds keyframes
(packaging A).

### Survey

| Spec / attempt | Status | Relation to the VRMXT split |
|----------------|--------|------------------------------|
| Core glTF `animations[]` | Ratified | Keyframe clips only (channels/samplers). Which clip plays, blending, and FSM policy are application concerns ([glTF#1730](https://github.com/KhronosGroup/glTF/issues/1730)). |
| [`KHR_animation_pointer`](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_animation_pointer) | Ratified | Extends *what* a channel can target (JSON pointers to materials, etc.). Not a controller or clip library metadata. |
| [`KHR_animation_controller` PR #2079](https://github.com/KhronosGroup/glTF/pull/2079) | Closed (2021) | Draft closer to a clip brick; renamed toward the clip PR. |
| [`KHR_animation_clip` PR #2080](https://github.com/KhronosGroup/glTF/pull/2080) | Closed (2022) | Clip playback metadata (loop / speed / offset-style). Closed with: solve via interactivity and a behavior node graph. |
| [`KHR_interactivity`](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_interactivity/Specification.adoc) | Submitted for ratification (2026); includes `animation/start` etc. | Khronos deferred dedicated clip/controller KHRs to this behavior graph. Too heavy for a small avatar FSM; VRMXT does not take a dependency. |
| `animations[i].extensions` / `extras` | Core | Allowed (same pattern as materials). `VRMXT_AnimationClip` attaches here. |
| [`VRMC_vrm_animation`](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0) (VRMA) | Upstream VRM | Maps humanoid / expressions / lookAt onto clips — retarget file, not an FSM. |

**Implication:** no collision with ratified KHR. Keep both VRMXT animation extensions.
`KHR_animation_pointer` stays out of the FSM. `KHR_interactivity` is not a base for the
avatar graph.

### VRChat-like: use vs skip

VRChat-like hosts need avatar-shipped clips, param-driven locomotion, triggerable emotes,
and clip swap. That maps to the VRMXT controller + clip split + bridge.

| Source | Use for VRChat-like? | How |
|--------|----------------------|-----|
| Core `animations[]` | Yes — required | Packaging A; bake clips in `.vrm` |
| Closed `KHR_animation_clip` ideas | Field ideas only | Loop / speed / offset / reverse-style metadata → shape `VRMXT_AnimationClip`. Dead KHR is neither implemented nor required. |
| Closed `KHR_animation_controller` | No code | Validates clip-vs-controller split; no usable ratified schema. |
| `KHR_animation_pointer` | Optional later, not core FSM | Useful if clips must drive materials / extras. Not needed for bone locomotion / emotes. Do not block the controller on pointer support. |
| `KHR_interactivity` | Skip as foundation | Full behavior graphs; wrong shape for Mecanim-like avatar params; not a dependency. Hosts that already run interactivity MAY also call the VRMXT bridge (peer, not base). |
| `VRMC_vrm_animation` (VRMA) | Complementary | Cross-avatar retarget packs. Separate from in-avatar controller; keep packaging A for the avatar file. |

Ship `VRMXT_AnimationController` + `VRMXT_AnimationClip` + flagged UniVRM clip I/O +
bridge. Reuse loop / speed / offset *concepts* from the abandoned KHR clip draft for
clip metadata only. Skip interactivity and pointer as foundations.

## Implications for VRMXT

1. Keep materials override, VFX, and the two animation extensions as vendor extensions;
   Khronos does not already own these jobs.
2. Specs and profiles SHOULD link here rather than invent a KHR-variants mapping layer.
   Do not wrap `KHR_interactivity` as the avatar animation brain.

Registry snapshot date: **2026-07-20** (see intro). In-progress Khronos rows can change
after that date.

## Related

- [VRMXT_materials_override](../specs/extensions/materials/vrmxt-materials-override.md)
- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VRMXT_AnimationController](../specs/extensions/animation/vrmxt-animation-controller.md)
- [VRMXT_AnimationClip](../specs/extensions/animation/vrmxt-animation-clip.md)
- [Animation controller standardization](../decisions/animation-controller-standardization.md)
- [Materials Override Catalogs](materials-override-catalogs.md)
