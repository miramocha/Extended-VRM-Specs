---
title: Engine particle capability
aliases:
  - Unity Particle System vs VFX Graph
  - VRM4U Niagara particle research
  - Portable sprite particle backends
tags:
  - extended-vrm
  - reference/engine
  - spec/vfx
  - spec/particle
  - implementation/unity
  - implementation/unreal
  - compatibility/vrm1
type: reference
status: draft
---

# Engine particle capability

Non-normative research note (as of 2026-07-21). Compares native particle backends
against [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md) and
records Unity deprecation status plus VRM4U / Unreal integration constraints.

**Findings:**

1. Unity deprecates the **Built-in Render Pipeline (BIRP)**, not the Built-in
   **Particle System** (Shuriken). Keep one required Unity mapper on `ParticleSystem`.
   Treat VFX Graph as optional later.
2. Unreal (UE5) uses **Niagara** only. Cascade is deprecated. VRM4U has no particle
   code today; a VRMXT consumer would own Niagara mapping.
3. Current `VRMXT_sprite_particle` fields map to Unity Particle System, Niagara, Godot
   `GPUParticles3D` / `CPUParticles3D`, and a Three.js custom drawable. Exact visual
   parity is not required.

## Sources

| Source | Role |
|--------|------|
| [Choosing your particle system solution](https://docs.unity3d.com/6000.6/Documentation/Manual/ChoosingYourParticleSystem.html) | Unity 6.6: Particle System vs VFX Graph |
| [VFX Graph requirements](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.6/manual/System-Requirements.html) | URP/HDRP only; compute + SSBO |
| [Render Pipelines strategy for 2026](https://unity.com/topics/render-pipelines-strategy-for-2026) | BIRP deprecated in 6.5; available through 6.7 LTS |
| [Niagara overview (UE 5.8)](https://dev.epicgames.com/documentation/unreal-engine/creating-visual-effects-in-niagara-for-unreal-engine) | Niagara = UE5 primary VFX |
| [UE5 migration guide](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-migration-guide) | Cascade deprecated in UE 5.0 |
| [UNiagaraFunctionLibrary](https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/Niagara/UNiagaraFunctionLibrary) | `SpawnSystemAttached` for runtime attach |
| Local Extended-VRM4U tree (upstream [ruyo/VRM4U](https://github.com/ruyo/VRM4U); UE 5.8 notes 2026-06-22) | Loader / skeleton / JSON lifetime |

## Unity: Particle System vs VFX Graph

Shared name “Built-in” confuses two different things:

| Term | Status (2026-07) |
|------|------------------|
| Built-in **Render Pipeline** (BIRP) | Deprecated from Unity 6.5. Supported through Unity 6.7 LTS. Final removal version undecided. New projects: URP. |
| Built-in **Particle System** (Shuriken) | Still a first-class solution on BIRP, URP, and HDRP. No current deprecation notice. |

### Comparison (Unity docs)

| | Particle System | VFX Graph |
|--|-----------------|-----------|
| Pipelines | BIRP, URP, HDRP | URP, HDRP only |
| Simulation | CPU | GPU (compute) |
| Feasible count | Thousands | Millions |
| Authoring | Component modules | Graph asset |
| C# particle access | Full read/write | Events / exposed params / limited scripting |
| Hardware | Broad | Compute shaders + SSBOs |

Unity’s current guidance: use both when needed. VFX Graph does not replace Particle
System for BIRP hosts, non-compute devices, or small script-driven emitters.

Older forum guidance said Shuriken would not be deprecated before VFX Graph reached
feature and platform parity. That is not a permanent product promise; current manuals
still document both systems.

### Implication for UniVRMXT

Do not ship two required Unity backends for `VRMXT_sprite_particle`.

| Backend | Role |
|---------|------|
| `ParticleSystem` | Required mapper. Works BIRP / URP / HDRP. Dynamic setup from imported JSON. Matches current defaults (`maxParticles` 64). |
| VFX Graph | Optional later path for large-scale or URP/HDRP-only profiles. Needs pre-authored assets, compute-capable hardware, and a second API surface. |

BIRP removal forces material / shader migration toward URP; it does not force a particle
simulation rewrite. Current UniVRM VFX profile already targets `ParticleSystem`
([UniVRMXT VFX](../implementations/univrm-vrmxt.md#vfx)).

## Cross-engine capability (summary)

| Capability | Unity Particle System | Unity VFX Graph | Unreal Niagara | Godot 4 | Three.js |
|------------|----------------------|-----------------|----------------|---------|----------|
| Point emitter + camera-facing sprite | Yes | Yes | Sprite renderer | Draw-pass billboard | Custom (`Points`, `Sprite`, or instanced quads) |
| `emissionRate` (particles/sec) | Rate over time | Spawn rate | Spawn rate | Derive from `amount` × `lifetime` | App spawner |
| `maxParticles` / `lifetime` / velocity | Yes | Yes | Yes | Yes | App |
| World-meter sprite size | Start size (world) | Sprite size | Sprite size | Mesh / process scale | Prefer instanced quads; `Points` size is weak for meters |
| Trails / ribbons / collision / sub-emitters | Yes | Yes | Yes | Partial / yes | Community libs |
| GPU millions | No | Yes | Yes | `GPUParticles3D` | Instancing + custom |

Godot has no direct particles-per-second API. Lock
`amount = ceil(emissionRate * lifetime)` (or equivalent) in a conformance sample.
Three.js has no engine particle system; the consumer owns simulation and drawable choice.

Deferred VRMXT fields (bursts, color/size over life, gravity, simulation space, shapes,
flipbook) remain outside the current sprite-particle draft. See open questions on the
base spec.

## Unreal / VRM4U

### Engine target

| Item | Choice |
|------|--------|
| VFX backend | Niagara only |
| Cascade | Do not implement (deprecated since UE 5.0) |
| VRM host | [VRM4U](https://github.com/ruyo/VRM4U) / local Extended-VRM4U |
| Documented engine window | UE 5.0–5.8 in recent release notes (README “動作環境” lags; code has UE 5.8 paths) |
| Particle code in VRM4U | None. No Niagara module dependency in `VRM4U.uplugin` |

A VRMXT Unreal package should depend on VRM4U + VRM4ULoader + Niagara and attach after
stock load—same optional-consumer pattern as
[VRM4U VRMXT](../implementations/vrm4u-vrmxt.md).

### Integration surface

| Piece | Observation |
|-------|-------------|
| glTF JSON | `VRMConverter::jsonData` exists during convert only. Not stored on `UVrmAssetListObject`. |
| Textures | Retained on `UVrmAssetListObject::Textures`. |
| Node → bone | `VRMSkeleton::readVrmBone` walks Assimp nodes into `FReferenceSkeleton`, including nodes without mesh weights. Helper Empties can become bones. |
| Index map | No durable `glTF nodes[]` index → Unreal bone name map. Duplicate names are rewritten (`_vrm4uNN`). |
| Load APIs | `ULoaderBPFunctionLibrary::LoadVRMFile` / `FromMemory`; `UVrmLoaderComponent`. |

Practical attach path: wrap load (read GLB JSON first), then post-process the returned
`UVrmAssetListObject` / skeletal mesh—same shape as materials override. Transparent
integration into every VRM4U load path needs an upstream callback (out of scope for the
portable spec).

### Axis / velocity conflict

`VRMXT_sprite_particle` requires initial velocity along the referenced node’s local **+Y**
after world-transform evaluation.

VRM4U defaults for VRM 1.0:

| Option | Default | Effect |
|--------|---------|--------|
| `bVrm10RemoveLocalRotation` | `true` | Local bone rotations set to identity on import |
| `bVrm10UseBindToRestPose` | `true` | Rest-pose handling |

So imported bone axes may not match glTF node local +Y. The Unreal mapper must keep an
original-node basis (or correction transform) when resolving emitters. Disabling rotation
stripping globally may break normal VRM animation expectations; treat it as a VRMXT-only
or per-load concern.

Also convert meters → centimeters (`size * 100`, `startSpeed * 100`).

### Proposed Niagara mapping

Prefer one bundled `UNiagaraSystem` template with exposed user parameters. Spawn with
`UNiagaraFunctionLibrary::SpawnSystemAttached` on the resolved bone / helper.

| Spec field | Niagara direction |
|------------|-------------------|
| Attach `node` | Socket / bone attach |
| `emissionRate` | Spawn rate |
| `maxParticles` | Emitter allocation / cap |
| `lifetime` | Particle lifetime |
| `startSpeed` + local +Y | Init velocity (after basis fix) |
| `size` | Sprite size (cm) |
| `color` | Linear user color |
| `texture` | User texture / material |
| Facing | Sprite renderer camera-plane alignment |

## Spec field portability

Current draft fields and backends:

| Spec field | Unity Particle System | Niagara | Godot | Three.js |
|------------|----------------------|---------|-------|----------|
| Point emitter | Shape point / tiny sphere | Point location | Emission point | Spawn origin |
| Camera-facing sprite | Billboard render mode | Sprite renderer | Default draw-pass billboard | Instanced quad preferred |
| `emissionRate` | Emission rate | Spawn rate | Derive `amount` | Spawner rate |
| `maxParticles` | Max particles | Cap | `amount` | Pool size |
| `lifetime` | Start lifetime | Lifetime | `lifetime` | Per-particle |
| `startSpeed` +Y | Start speed + direction | Init velocity | Direction + velocity | Velocity |
| `size` (m) | Start size | Sprite size | Scale | Quad scale |
| `color` | Start color | Color | Color | Vertex / material |
| `texture` | Material albedo | Material / user tex | Albedo | Material map |

## Implications for VRMXT

1. Unity: one required `ParticleSystem` mapper. Optional VFX Graph later. Do not couple
   the portable schema to VFX Graph assets.
2. Unreal: one Niagara mapper. Never Cascade. Own a VRMXT plugin; do not expect stock
   VRM4U to grow particles.
3. Conformance: add a **rotated** helper-node sample (not translation-only) so Unreal
   local-+Y stripping is covered. Godot: lock rate↔`amount` formula. Three.js: prefer
   instanced quads for world-meter size.
4. Implementation profile for VRM4U VFX remains TBD
   ([Blender VRMXT VFX](../implementations/blender-vrmxt.md#vfx) open questions).

## Related

- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VFX capability boundaries](../decisions/vfx-capability-boundaries.md)
- [VFX capability naming](../decisions/vfx-capability-naming.md)
- [Billboard sprite ownership](../decisions/billboard-sprite-ownership.md)
- [UniVRMXT VFX](../implementations/univrm-vrmxt.md#vfx)
- [Godot VRMXT](../implementations/godot-vrmxt.md)
- [three-vrmxt](../implementations/three-vrmxt.md)
- [VRM4U VRMXT](../implementations/vrm4u-vrmxt.md)
- [KHR / glTF overlap](khr-gltf-overlap.md)
