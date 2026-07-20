---
title: Animation controller standardization
aliases:
  - Animator Controller across platforms
  - VRMXT Mecanim-like decision
tags:
  - extended-vrm
  - decision/animation
  - compatibility/vrm1
  - format/gltf-extension
type: decision
status: draft
---

# Animation controller standardization

## Status

**Conditional / narrow.** Reject a full Unity Animator Controller (Mecanim) dump as a
cross-platform VRMXT contract. Accept pursuing a **small portable controller profile**
(parameters, state machine, 1D/2D blend spaces, optional layers and humanoid bone masks)
only under the conditions in [Recommendation](#recommendation). No `VRMXT_*` extension
name is reserved until a later draft lands under `specs/`.

Warudo is deferred (Unity host). VRChat SDK is a product analogy and a future converter
target; it is not a file or conformance dependency.

## Question

Should Extended VRM standardize an Animator Controller–like animation graph in a
`VRMXT_*` extension for Unity, Unreal (VRM4U), Blender, Three.js, and Godot?

| Outcome | Meaning |
|---------|---------|
| No | Controllers stay host-owned; VRM/VRMXT ship clips and avatar data only |
| Conditional / narrow | Portable subset (e.g. locomotion + emote FSM), not full Mecanim |
| Yes (full-ish) | Broad Animator-like graph as first-class portable data |

## Motivations

1. **Cross-engine portability:** one `.vrm` / `.glb` can carry motion policy so
   consumers do not each invent incompatible graphs.
2. **VRChat-like apps:** hosts that load user avatars and expect locomotion / gesture /
   emote policy in the file (host drives parameters; avatar ships graph + clips).
3. **Author once:** stop treating Unity `.controller` or Unreal AnimBP assets as the
   Extended source of truth.
4. **Future VRMXT → VRChat avatar converter:** a downstream tool maps portable graph +
   clips into a VRChat-ready Unity avatar. A Mecanim-shaped subset lowers converter cost.
   The converter consumes the contract; the schema does not embed the VRChat SDK.

Primary product shape for this decision: **avatar ships the graph**. Game hosts that
already own a full character controller remain free to ignore the extension.

## Hard constraints

| Constraint | Rule |
|------------|------|
| Portable file | Optional `VRMXT_*` in the same glTF/VRM; no engine-private sidecar ([architecture](../architecture.md)) |
| Stock VRM | Humanoid, look-at, and expressions stay `VRMC_vrm`; controller must not redefine them |
| `extensionsRequired` | Optional controller MUST NOT be listed there |
| No third-party deps | Conformance uses stock engine animation APIs and/or a first-party VRMXT interpreter. Marketplace animation packs, Magica-style backends, and VRChat SDK are not allowed as the normative playback path |
| Engine profiles | MAY document how a host maps portable data onto Animator / AnimBP / AnimationTree / `AnimationMixer`; MUST NOT require third-party middleware for conformance |

## Platforms

| Platform | Native analog | Stock VRM / VRMXT today |
|----------|---------------|-------------------------|
| Unity | Animator Controller | UniVRM VRM 1.0 skips glTF animation import (`LoadAnimation = false`); VRM 1.0 export does not write `animations[]`. No controller serialization in UniVRMXT |
| Unreal | AnimBP (FSM + Blend Space) | VRM4U maps clips / VRMA and wires engine AnimBP nodes; topology is host-owned |
| Blender | Actions / NLA | Import tries clips; on glTF-addon failure, strips `animations` and retries. Export of glTF animations is off unless Advanced prefs + `export_gltf_animations` |
| Three.js | App mixer / custom SM | Avatar via three-vrm; no portable graph |
| Godot | AnimationTree | Avatar via godot-vrm; no portable graph |

Upstream `VRMC_vrm_animation` (VRMA) maps humanoid / expressions / look-at onto glTF
clips, usually in a separate file. It does not define state machines or blend spaces.

## Concept overlap (Unity vs Unreal)

Shared production pattern: host sets parameters → state machine → blend space/tree inside
states → optional layers / masks → pose.

| Concept | Unity | Unreal | Portable candidate |
|---------|-------|--------|--------------------|
| Named parameters (float / bool / int / trigger) | Animator params | AnimBP variables | Yes |
| FSM (states, transitions, conditions, exit time) | Animator Controller | AnimGraph state machine | Yes (declarative) |
| Clip references | AnimationClip | AnimSequence | Yes via glTF `animations[]` or named external clips |
| 1D / 2D continuous blend | Blend Tree | Blend Space | Yes |
| Layers + override / additive | Animator layers | Layered blend / slots | Partial |
| Bone masks | Avatar Mask | Branch filter / Layered Blend per Bone | Partial (VRM humanoid bone names) |
| Nested FSMs | Sub-State Machines | Nested SMs | Yes if depth-capped |
| Arbitrary gameplay logic | C# drivers | Event Graph | No (host sets parameters) |
| IK / Control Rig / pose graphs | Animation Rigging | Anim nodes / Control Rig | No |
| Montages / slot one-shots | CrossFade / layers | Montages | No as first-class |
| Anim events / notifies | Animation Events | AnimNotifies | Maybe later (named markers only) |
| Sync groups, mirror metadata | Mecanim extras | Sync groups | Out of v1 |

Full Mecanim and full AnimBP diverge on EventGraph, Montages, Control Rig, and sync
rules. A 1:1 Unity `.controller` JSON dump cannot round-trip Blender, Three, or Godot
cleanly and fails the no-third-party / portable-file rules.

## Clip packaging gap

A controller without playable clips is empty. Current authoring tools often drop clips:

| Tool | Import clips in `.vrm` | Export clips into `.vrm` |
|------|------------------------|--------------------------|
| UniVRM VRM 1.0 | Skipped | None written |
| UniVRM VRM 0.x | Skipped by default | Opt-in `KeepAnimation` (default false); harvests clips, discards Animator topology |
| Blender VRM add-on | Best-effort; may strip on failure | Opt-in advanced preference |

Any future controller extension must pick one packaging policy (and document it in the
spec draft):

| Option | Notes |
|--------|-------|
| A. In-file `animations[]` | Needs stock UniVRM / Blender I/O improvements or Extended-only write paths |
| B. External VRMA / glTF clip packs | Matches upstream VRMA separation; controller references clip ids / URIs |
| C. Host-owned clips | Graph only; each host supplies motion assets (weak for VRChat-like and converter goals) |

## Criteria scores

| Criterion | Full Mecanim dump | Narrow portable profile | Host-owned only (no VRMXT graph) |
|-----------|-------------------|-------------------------|----------------------------------|
| Cross-engine fidelity | Fail | Pass if subset stays declarative | Pass (nothing to map) |
| Authoring / round-trip | Fail outside Unity | Hard; needs Blender or JSON authoring + interpreter | N/A |
| Clip dependency | Blocked by stock I/O | Blocked until packaging chosen | Host solves locally |
| VRChat-like + converter pull | Strong Unity fit; fails other engines | Strong if Mecanim-shaped | Converter invents graph at convert time |
| Scope control | Fail | Pass | Pass |
| Architecture fit | Fail (engine asset dump) | Pass if optional `VRMXT_*` | Pass |
| No third-party deps | Fail if SDK/assets required | Pass on stock APIs + VRMXT interpreter | Pass |

## Recommendation

1. **Do not** standardize full Unity Animator Controller semantics, serialize
   `.controller` / AnimBP assets into the file, or make VRChat / other SDKs a
   conformance dependency.
2. **Do** treat a **narrow portable controller profile** as the candidate for a later
   `specs/` draft when the flip conditions below are met. Working shape:
   - Named parameters (float, bool, int, trigger)
   - State machine with declarative transitions
   - 1D / 2D blend spaces referencing clips
   - Optional layers with override/additive and humanoid bone masks
   - Depth-capped nested state machines
   - Explicitly out: EventGraph-equivalent logic, Montages-as-first-class, IK/Control Rig
     graphs, sync groups, engine UI dumps
3. Until then, leave graphs host-owned; keep using glTF / VRMA for clips; keep shipping
   materials, VFX, spring override, and lattice work under existing `VRMXT_*` drafts.
4. Optimize the portable profile for **avatar-ships-graph** consumers (VRChat-like hosts
   and a future VRMXT → VRChat converter). Game apps that own locomotion MAY ignore the
   extension.

### Flip conditions (when to open a `specs/` draft)

All of the following:

1. Packaging policy chosen (A, B, or C above) with a path that works for at least Unity
   authoring export and one non-Unity consumer.
2. Authoring path identified (Blender UI, Unity generator from portable JSON, or both).
3. Confirmed product pull for in-file graphs (VRChat-like host and/or converter work
   scheduled).
4. Subset frozen in a short non-normative sketch that Unreal AnimBP, Godot AnimationTree,
   and Three can implement with stock APIs or a VRMXT interpreter.

### Flip conditions (when to abandon)

Any of:

- Product priority stays on materials / VFX / spring and no VRChat-like or converter work
  is planned.
- Team refuses to fix or bypass the clip I/O gap (options A/B) and option C is rejected
  as too weak for the stated motivations.

## Follow-on (out of this note)

| Item | When |
|------|------|
| `specs/vrmxt-*.md` schema draft | After flip conditions pass; pick extension name then |
| `implementations/*` profiles | After a draft exists |
| UniVRM / Blender clip I/O changes | Only if packaging chooses A; propose upstream or Extended-only |
| VRMXT → VRChat avatar converter | Separate product; consumes portable contract |

## Related

- [Extended VRM Architecture](../architecture.md)
- Upstream [VRMC_vrm_animation](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0) (clips / retarget map, not graphs)
- Materials multi-engine pattern: [VRMXT_materials_override](../specs/vrmxt-materials-override.md) (`engine` + `variant` profiles, stock fallback)
