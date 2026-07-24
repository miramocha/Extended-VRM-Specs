---
title: VRMXT_AnimationController
aliases:
  - VRMXT animation controller
  - portable Animator FSM
tags:
  - extended-vrm
  - spec/animation
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_AnimationController

Root glTF extension for a portable, flat animation state machine on a VRM 1.0 avatar.
States bind to in-file glTF `animations[]` entries that carry
[VRMXT_AnimationClip](vrmxt-animation-clip.md) (packaging A). Parallel to VRM 1.0
expressions binding morph targets: the controller forces both keyframes and clip
metadata on every referenced clip. Hosts drive the machine through a first-party VRMXT
bridge (`PlayOneShot`, `GoToState`, `SetFloat` / `SetBool` / `SetInt`, `SetStateClip`).

Decision context:
[animation-controller-standardization](../../../decisions/animation-controller-standardization.md).
Khronos overlap (non-normative):
[KHR / glTF overlap](../../../references/khr-gltf-overlap.md).

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_AnimationController` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_AnimationController` |
| Layers | One pose layer only (implicit; no `layers[]` in file) |
| FSM shape | Flat named states + declarative transitions |
| Parameter types | `float`, `bool`, `int` only |
| Clip packaging | In-file `animations[]` + required `VRMXT_AnimationClip` on each bound clip |
| Stock importer | no required change |
| Consumer package | optional |

### Out of scope (permanent)

| Item | Notes |
|------|-------|
| `trigger` parameter type | One-shots use the bridge + named one-shot states |
| Nested state machines | — |
| Additive / override layers, bone masks | — |
| Event graphs, Montages-in-file, IK graphs, sync groups | Engine-private |
| `KHR_interactivity` as the avatar brain | Peer host feature only |
| VRM 0.x | Unsupported |

## Conformance

This specification conforms to [VRMXT Conformance](../../core/vrmxt-conformance.md).

## Normative requirements

1. Files that use this extension MUST list `VRMXT_AnimationController` in
   `extensionsUsed`.
2. The extension object MUST appear at root `extensions.VRMXT_AnimationController`.
3. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
4. The extension object MUST contain a non-empty `states` array.
5. Each state MUST contain a unique case-sensitive `name` string within `states`.
6. The extension object MUST contain `entryState`, equal to exactly one `states[].name`.
7. Each state MUST provide either a single clip binding (`clip` and/or `clipName`) or a
   `blendSpace` object. A state MUST NOT provide both a single-clip binding and
   `blendSpace`.
8. When present, `clip` MUST be a valid zero-based index into the glTF `animations`
   array. When present, `clipName` MUST equal some `animations[i].name`. If both are
   present and disagree, consumers MUST prefer `clip` and MAY warn.
9. Every `animations[i]` referenced by a state or blend-space entry MUST include
   `animations[i].extensions.VRMXT_AnimationClip` with a valid `specVersion`. Files that
   use this controller MUST also list `VRMXT_AnimationClip` in `extensionsUsed`.
10. If a state's clip binding cannot be resolved (missing animation, missing or invalid
    `VRMXT_AnimationClip`, or empty keyframe data when the consumer requires channels),
    consumers MUST skip that state for playback and MAY fall back to `entryState` when
    the unresolved state is current.
11. `parameters` MAY be omitted or empty. Each parameter MUST have a unique
    case-sensitive `name` and a `type` of `"float"`, `"bool"`, or `"int"`.
12. Parameter type `"trigger"` MUST NOT appear. Consumers MUST ignore unknown parameter
    types.
13. `transitions` MAY be omitted or empty. Each transition MUST name `from` and `to`
    states that exist in `states` (or use `"*"` for `from` as a global transition; **TBD**
    whether `"*"` is allowed in `1.0`).
14. Transition `conditions` are evaluated as a conjunction (all must hold). An empty
    `conditions` array means the transition is always eligible when other rules allow
    (**exit-time / interrupt rules TBD**).
15. Consumers MUST ignore unknown properties and unknown condition `op` values.
16. Files using this optional design MUST NOT list `VRMXT_AnimationController` in
    `extensionsRequired`.
17. This extension MUST NOT replace `VRMC_vrm` humanoid, look-at, or expression data.

## Extension properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | Extension version; currently `"1.0"` |
| `parameters` | object[] | no | Named parameters; default empty |
| `states` | object[] | yes | Non-empty flat state list |
| `entryState` | string | yes | Name of the initial state |
| `transitions` | object[] | no | Declarative edges; default empty |
| `defaultTransitionDuration` | number | no | Seconds; see [Inter-state blending](#inter-state-blending) |

### Parameters

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `name` | string | yes | Case-sensitive parameter id |
| `type` | string | yes | `"float"`, `"bool"`, or `"int"` |
| `default` | number or boolean | no | Initial value; see defaults below |

| `type` | Default when `default` omitted | `default` JSON type |
|--------|--------------------------------|---------------------|
| `float` | `0` | number (finite) |
| `bool` | `false` | boolean |
| `int` | `0` | integer |

Invalid `default` for the declared `type` MUST cause the consumer to use the type's
omission default.

### States

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `name` | string | yes | Case-sensitive state id |
| `clip` | integer | no* | Index into `animations[]` (target MUST have `VRMXT_AnimationClip`) |
| `clipName` | string | no* | Match `animations[i].name` (same MUST) |
| `blendSpace` | object | no* | 1D or 2D in-state blend |
| `tags` | string[] | no | Authoring / UI labels (e.g. `"emote"`) |

\* Exactly one mode: (`clip` and/or `clipName`) **xor** `blendSpace`.

Bridge `PlayOneShot(name)` resolves `name` to a state (typically one tagged for one-shot
use, e.g. `"oneshot"` / `"emote"`). Exact tag conventions are **TBD**; state `name`
matching is required for `GoToState` / `PlayOneShot` when tags are absent.

### Blend spaces

Optional. Absent = single clip on the state.

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `dimensions` | integer | yes | `1` or `2` |
| `paramX` | string | yes | Parameter name (`float` or `int`) |
| `paramY` | string | yes if `dimensions` is `2` | Second parameter |
| `entries` | object[] | yes | Non-empty sample list |

#### Blend-space entries

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `clip` | integer | no* | Index into `animations[]` (MUST have `VRMXT_AnimationClip`) |
| `clipName` | string | no* | Match `animations[i].name` (same MUST) |
| `threshold` | number | yes if 1D | Position on the X axis |
| `position` | number[2] | yes if 2D | `[x, y]` sample position |

\* Each entry MUST resolve a clip via `clip` and/or `clipName` (same rules as states,
including required `VRMXT_AnimationClip`).

1D blending interpolates between neighboring thresholds along `paramX`. 2D blending
interpolates among samples in the `paramX` / `paramY` plane. Exact interpolation
(linear vs barycentric, extrapolation) is **TBD**; consumers MUST still play a
nearest-neighbor sample when full blend math is unimplemented.

### Transitions

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `from` | string | yes | Source state name (wildcard **TBD**) |
| `to` | string | yes | Destination state name |
| `conditions` | object[] | no | AND-combined; default empty |
| `duration` | number | no | Seconds; overrides `defaultTransitionDuration` when set |

#### Conditions

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `parameter` | string | yes | Name of a declared parameter |
| `op` | string | yes | Comparison operator |
| `value` | number or boolean | yes | Right-hand operand |

| `op` | Allowed parameter `type` | Meaning |
|------|--------------------------|---------|
| `eq` | float, bool, int | Equal |
| `neq` | float, bool, int | Not equal |
| `gt` | float, int | Greater than |
| `gte` | float, int | Greater than or equal |
| `lt` | float, int | Less than |
| `lte` | float, int | Less than or equal |

Float equality uses exact JSON number identity for this draft (**epsilon TBD**).

## Inter-state blending

**Exact policy TBD.** Locked options for this extension:

| Mode | Meaning |
|------|---------|
| Cut | Instant switch (`duration` / default `0`) |
| Single default crossfade | One shared blend duration; no per-bone masks |

Provisional field meaning (subject to change with the policy decision):

1. When both `duration` and `defaultTransitionDuration` are omitted or `0`, the
   transition is a cut.
2. A positive duration means a linear crossfade of that length in seconds, if the
   consumer supports crossfade; otherwise the consumer MUST cut.
3. Interrupt / cancel rules during an in-flight crossfade are **TBD**.

## One-shot end behavior

**TBD.** Candidates:

| Option | Behavior |
|--------|----------|
| Auto-return | After non-looping one-shot clip ends, return to previous or `entryState` |
| Bridge cancel | Stay until host calls `GoToState` / another `PlayOneShot` |

Until decided, consumers MAY auto-return to the state that was current before
`PlayOneShot`, and MUST document the choice in their implementation profile.

## Bridge surface

Normative intent. Concrete type/method names are finalized in `implementations/` notes.

| Call | File effect |
|------|-------------|
| `SetFloat(name, value)` / `SetBool` / `SetInt` | Updates a declared parameter |
| `GoToState(name)` | Forces transition to named state (whether conditions are bypassed is **TBD**) |
| `PlayOneShot(name)` | Enters named one-shot state; one-shot semantics |
| `SetStateClip(stateName, clipIndexOrName)` | Rebinds that state's single-clip reference; new target MUST have `VRMXT_AnimationClip` |

Hosts drive parameters and one-shots. The file MUST NOT encode Unity-style Trigger pulses.

## Unity profile (non-normative)

Phase 1 UniVRMXT intent: author the FSM on Animator **layer index 0** with display name
`VRMXT` (rename the Base Layer — do not add a second layer). Author clip fields as
`VRMXT_AnimationClip` metadata. On export, read layer 0 and emit
`VRMXT_AnimationController` plus required clip extensions on bound `animations[]`. On
import, rebuild layer 0 named `VRMXT`. Do not write other Animator layers into the file.
The portable schema has no layer name or `layers[]`. Non-portable Mecanim features are
out of scope for the mapping; see
[animation-controller-standardization](../../../decisions/animation-controller-standardization.md).

## Attachment example

Non-normative. Every bound animation carries `VRMXT_AnimationClip`.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMXT_AnimationController",
    "VRMXT_AnimationClip"
  ],
  "animations": [
    {
      "name": "Idle",
      "channels": [],
      "samplers": [],
      "extensions": {
        "VRMXT_AnimationClip": {
          "specVersion": "1.0",
          "role": "locomotion",
          "loop": true
        }
      }
    },
    {
      "name": "Walk",
      "channels": [],
      "samplers": [],
      "extensions": {
        "VRMXT_AnimationClip": {
          "specVersion": "1.0",
          "role": "locomotion",
          "loop": true
        }
      }
    },
    {
      "name": "Run",
      "channels": [],
      "samplers": [],
      "extensions": {
        "VRMXT_AnimationClip": {
          "specVersion": "1.0",
          "role": "locomotion",
          "loop": true
        }
      }
    },
    {
      "name": "Wave",
      "channels": [],
      "samplers": [],
      "extensions": {
        "VRMXT_AnimationClip": {
          "specVersion": "1.0",
          "role": "emote",
          "loop": false
        }
      }
    }
  ],
  "extensions": {
    "VRMXT_AnimationController": {
      "specVersion": "1.0",
      "parameters": [
        { "name": "Speed", "type": "float", "default": 0.0 },
        { "name": "Grounded", "type": "bool", "default": true }
      ],
      "entryState": "Locomotion",
      "defaultTransitionDuration": 0.15,
      "states": [
        {
          "name": "Locomotion",
          "blendSpace": {
            "dimensions": 1,
            "paramX": "Speed",
            "entries": [
              { "threshold": 0.0, "clipName": "Idle" },
              { "threshold": 0.5, "clipName": "Walk" },
              { "threshold": 1.0, "clipName": "Run" }
            ]
          }
        },
        {
          "name": "Wave",
          "clip": 3,
          "tags": ["emote"]
        }
      ],
      "transitions": [
        {
          "from": "Locomotion",
          "to": "Wave",
          "conditions": [],
          "duration": 0.1
        },
        {
          "from": "Wave",
          "to": "Locomotion",
          "conditions": [
            { "parameter": "Grounded", "op": "eq", "value": true }
          ]
        }
      ]
    }
  }
}
```

Empty `channels` / `samplers` above are placeholders for the example only.

## Compatibility

| Consumer | Expected behavior |
|----------|-------------------|
| Stock VRM 1.0 importer | Ignore extension; avatar loads; no portable FSM |
| Supporting UniVRMXT / Blender VRMXT / other | Build native Animator / AnimBP / tree / mixer, or interpret directly |
| Missing `animations[]` entry or missing `VRMXT_AnimationClip` on a bound clip | Skip unresolved state / blend entry |
| Unknown parameter / op | Ignore that parameter or condition |

Exact pose parity across engines is not required. Parameter names, state names, clip
indices/names, and required clip metadata fields are.

## Extensibility

Later drafts MAY:

- Lock crossfade interrupt rules and emote-end behavior (replacing TBD).
- Add optional transition fields (exit time, priority) with defaults.
- Allow `"*"` wildcard `from` if reserved in `1.0`.

Adding optional fields with defaults does not by itself require a `specVersion` bump.
Removing or redefining an existing field does. Multi-layer controllers need a new
extension or a major `specVersion`; they stay outside this extension's permanent scope.

## Related

- [VRMXT Conformance](../../core/vrmxt-conformance.md)
- [VRMXT_AnimationClip](vrmxt-animation-clip.md)
- [Animation controller standardization](../../../decisions/animation-controller-standardization.md)
- [KHR / glTF overlap](../../../references/khr-gltf-overlap.md) (non-normative)
- Upstream [VRMC_vrm_animation](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0)

## Open questions

| Topic | Status |
|-------|--------|
| Cut vs default crossfade exact policy | TBD |
| Emote end: auto-return vs bridge cancel | TBD |
| Crossfade interrupt / cancel rules | TBD |
| Float comparison epsilon | TBD |
| Global `"*"` transitions | TBD |
| Whether `GoToState` bypasses conditions | TBD |
| Emote `tags` vocabulary (`"oneshot"`, `"emote"`, …) | TBD |
| 1D/2D blend interpolation details | TBD |
| Interaction with `VRMC_vrm` expressions / look-at while FSM runs | TBD |
| Empty keyframe `animations[i]` with clip meta (authoring stub) | TBD whether unresolved |
