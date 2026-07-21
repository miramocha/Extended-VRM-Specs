---
title: VRMXT_lattice
aliases:
  - VRM lattice
  - lattice deform
  - FFD cage
tags:
  - extended-vrm
  - spec/lattice
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
  - implementation/blender
  - implementation/unity
type: specification
status: draft
---

# VRMXT_lattice

Research draft for a portable lattice (FFD / deformation cage) extension.
Authoring source is Blender Lattice + Lattice Modifier. Primary Unity consumer
reference is [Harry Heath Lattice Modifier for Unity](https://harryheath.com/lattice)
(Asset Store package). No field schema is frozen yet.

This capability follows [VRMXT Conformance](../../core/vrmxt-conformance.md). A lattice is a
mesh-deformation capability, not a particle or billboard effect.

Stock VRM 1.0 importers that ignore the extension MUST load the model without
runtime lattice deformation. Today, Blender VRM export typically **bakes** non-armature
modifiers into mesh geometry; this extension would preserve lattice as runtime data
instead of baking it away.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_lattice` (**TBD** — name not reserved) |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_lattice` (**TBD**) |
| v1 intent | Portable lattice grids + mesh bindings |
| Stock importer | no required change |
| Consumer package | optional (first-party solver and/or third-party mapper) |

Out of scope for early draft:

- Exact JSON schema / `specVersion` freeze
- Particle / curve / text lattice targets (Blender allows these; VRM avatars are mesh)
- Guaranteed bit-identical deformation across Blender and Unity solvers
- Engine-specific override tables (may follow `VRMXT_springBone_override` pattern later)

## Why this exists

VRM mesh pipeline assumes skinning + morph targets. Blender Lattice is a third
deformation layer used for squash/stretch, clothing adjust, face tweak, and
non-destructive sculpt. Export today either:

1. Applies / bakes the Lattice Modifier → static mesh (runtime cage lost), or
2. Strips / ignores it → authored deformation lost.

A portable extension keeps cage + bindings in the file so Unity (and later other
engines) can rebuild a runtime modifier.

## Blender model (authoring)

Sources:

- [Lattice object](https://docs.blender.org/manual/en/4.2/animation/lattice.html)
- [Lattice Modifier](https://docs.blender.org/manual/en/4.2/modeling/modifiers/deform/lattice.html)

### Lattice object (datablock + Object)

| Concept | Blender | Notes |
|---------|---------|-------|
| Resolution | `points_u`, `points_v`, `points_w` | Grid subdivisions per axis (U/V/W) |
| Control points | Lattice edit vertices | Absolute positions in lattice local space |
| Interpolation | Per-axis: Linear, Cardinal, Catmull-Rom, B-Spline | Default often B-Spline |
| Outside | Lattice data `use_outside` | When enabled: only surface control points influence (interior ignored) |
| Object transform | Lattice Object location/rotation/scale | Fits cage around target in Object Mode |
| Animation | Lattice shape keys; keyframed point positions | Common authoring path |

### Lattice Modifier (on mesh)

| Property | Meaning |
|----------|---------|
| Object | Lattice Object reference |
| Vertex Group | Optional per-vertex weight mask; Invert flips weights |
| Strength | Blend original ↔ deformed positions |

Stack order vs Armature Modifier decides pre-skin vs post-skin behavior in Blender.
Multiple meshes MAY share one Lattice Object.

## Unity consumer model (reference)

Reference docs: [harryheath.com/lattice](https://harryheath.com/lattice) (v1.3.x).

This is a **third-party** Asset Store package, not UniVRM. A VRMXT consumer MAY:

1. Map portable data onto these components, or
2. Ship a first-party solver with equivalent portable fields, or
3. Support both via an engine override entry (**TBD**).

### Components

| Component | Role |
|-----------|------|
| `Lattice` | Grid + handles; `Resolution`; edit/animate handle offsets |
| `Lattice Modifier` | Static `MeshFilter` / `MeshRenderer` |
| `Skinned Lattice Modifier` | `SkinnedMeshRenderer`; separate pre-skin and post-skin lattice lists |
| `Transform Lattice Modifier` | Deform Transform (lights, helpers); not mesh vertices |

Requirements called out by the package:

- Mesh **Read/Write** enabled
- Skinned path: project **GPU Skinning** enabled
- Blend shapes with Animator: may need `Animator.Rebind()` (`RebindOnStart` utility)

### Per-binding options (Unity)

| Property | Values / notes |
|----------|----------------|
| Interpolation | `Linear Sharp`, `Linear Smooth`, `Cubic` (single mode per binding; not per-axis) |
| Global | If true, deform outside lattice bounds; if false, influence falls off near bounds |
| Mask | Selection: All / Material index; Vertex: None / Constant / Color / UV / Texture |
| Apply Method | Position only; Position+Normal+Tangent; Stretch (writes squash/stretch to a UV channel) |
| Update Mode | Manual / When Visible / Always (pre-skin list; post-skin follows skinning) |

Handles are driven as **offsets from rest grid** (`SetHandleOffset`), or absolute local/world positions via API. Animation keys handle motion.

## Mapping table (Blender → portable → Unity)

Status column: `direct` = same idea; `approx` = closest practical map; `gap` = no clean equivalent; `TBD` = decide later.

| Blender | Portable concept | Unity (Heath) | Status |
|---------|------------------|---------------|--------|
| Lattice Object transform | Lattice node (glTF node) | `Lattice` GameObject transform | direct |
| `points_u/v/w` | `resolution` int[3] | `Resolution` | direct |
| Control point positions | Rest + offsets, or absolute local positions | Handle offsets / positions | approx — need one storage convention |
| Interp Linear | `interpolation` enum | `Linear Sharp` (**TBD**) | approx |
| Interp Cardinal / Catmull-Rom | — | no dedicated mode | gap |
| Interp B-Spline | — | `Cubic` as nearest (**TBD**) | approx |
| Per-axis interpolation | three enums | one enum per binding | gap — collapse policy **TBD** |
| `use_outside` (surface-only controls) | — | no equivalent | gap |
| — (bounds falloff) | `global` bool | `Global` | gap on Blender side (always cage-local influence model) |
| Modifier Strength | `strength` float | Vertex mask Constant multiplier | approx |
| Vertex Group (+ Invert) | weight source ref | Color / UV / Texture mask, or baked weight attribute | approx |
| Modifier before Armature | `skinPhase: before` | `Lattices` list on Skinned modifier | direct |
| Modifier after Armature | `skinPhase: after` | `Skinned Lattices` list | direct |
| Shared lattice → N meshes | one lattice, many bindings | one `Lattice`, many modifiers referencing it | direct |
| Lattice shape keys | morphs on lattice OR animation clips on handles | Animator / timeline on handles | TBD |
| Apply normals/tangents | — | `Apply Method` | TBD default |
| Stretch → UV | — | Stretch + `StretchChannel` | out of v1? TBD |

### Semantic traps

1. **Outside ≠ Global.** Blender `Outside` drops interior control points. Unity `Global` extends deformation beyond the cage AABB. Do not map one onto the other.
2. **Interpolation families differ.** Blender B-Spline / Catmull-Rom are not named Unity modes. Expect visual drift; document “nearest mode” tables, not identity.
3. **Coordinate spaces.** Blender object/lattice local (Z-up) must convert to glTF node space (Y-up) on export, same class of remaps as other Extended VRM node data.
4. **Bake vs runtime.** If exporter still applies Lattice Modifier for stock VRM viewers, runtime consumers would double-apply unless bake is skipped when `VRMXT_lattice` is written.
5. **Read/Write / GPU skinning.** Portable file cannot encode Unity import flags; implementation profile must document importer setup.
6. **Third-party license.** Mapping onto Heath asset couples consumer to Asset Store dependency. First-party solver avoids that; bit-match with Blender still not guaranteed.

## Proposed portable shape (non-normative sketch)

Sketch only. Field names and nesting are **TBD**.

```json
{
  "extensions": {
    "VRMXT_lattice": {
      "specVersion": "1.0",
      "lattices": [
        {
          "name": "face_cage",
          "node": 12,
          "resolution": [4, 4, 4],
          "interpolation": "bSpline",
          "handlePositions": [[0, 0, 0]]
        }
      ],
      "bindings": [
        {
          "lattice": 0,
          "mesh": 3,
          "skinPhase": "after",
          "strength": 1.0,
          "weightAttribute": "COLOR_0"
        }
      ]
    }
  }
}
```

Open schema choices:

| Choice | Options | Lean |
|--------|---------|------|
| Where lattices live | Root extension vs nodes extras | Root, like `VRMXT_sprite_particle` |
| Handle storage | Absolute local positions vs rest+offset | Rest+offset matches Unity API; Blender exports deltas from Make Regular grid |
| Interpolation enum | Blender names / Unity names / portable set | Portable set + consumer remap tables |
| Weight mask | glTF vertex color / extras / accessor | Prefer existing mesh attribute |
| Animation | glTF animation targeting extension paths vs morph-like weights | **TBD** |
| `extensionsRequired` | never for optional design | MUST NOT require (same as other VRMXT) |

## Export / import behavior (draft)

### Blender export

1. Detect Lattice Modifiers on export meshes (and shared Lattice Objects).
2. If writing `VRMXT_lattice`: **do not bake** those modifiers into mesh positions for the portable path.
3. Emit lattice node(s), resolution, handle data, bindings (mesh index, strength, mask, skin phase from stack order).
4. Stock mesh + skin + morph still valid without the extension.
5. Unmapped Blender features (`use_outside`, per-axis interp mismatch): **TBD** (warn, skip, or approximate).

### Unity import (optional consumer)

1. Ignore extension if consumer absent.
2. Create `Lattice` (or first-party equivalent) under mapped node.
3. Attach Skinned / static modifier from mesh type; place binding in pre- or post-skin list from `skinPhase`.
4. Remap portable interpolation → consumer enum via published table.
5. Document Read/Write + GPU Skinning prerequisites in implementation profile.

## Compatibility

| Consumer | Expectation |
|----------|-------------|
| Stock UniVRM / VRM 1.0 | Ignore extension; mesh loads; no runtime cage |
| UniVRMXT (optional) | **TBD** first-party and/or Heath mapper |
| VRMXT Blender extension | Author + round-trip **TBD** |
| VRM4U | Out of scope until Unity path settles |

## Open questions

1. Ship first-party solver in UniVRMXT, map to Heath asset, or both via override `engine` string?
2. v1: static cages only, or animated handles in file?
3. Default `skinPhase` when Armature + Lattice order ambiguous?
4. Collapse three Blender axis interpolations to one portable value how?
5. Encode vertex-group masks as `COLOR_n`, `_WEIGHTS_n`, or named extras?
6. Should exporter offer “bake for stock / keep runtime for VRMXT” dual path in one export?
7. Transform-only lattice targets (Unity `Transform Lattice Modifier`) — include in v1?
8. Normals/tangents / Stretch UV — portable apply-method enum or consumer-only?

## References

| Source | URL |
|--------|-----|
| Lattice Modifier for Unity (docs) | https://harryheath.com/lattice |
| Blender Lattice object | https://docs.blender.org/manual/en/4.2/animation/lattice.html |
| Blender Lattice Modifier | https://docs.blender.org/manual/en/4.2/modeling/modifiers/deform/lattice.html |
| Related: VRMXT family requirements | [vrmxt-conformance.md](../../core/vrmxt-conformance.md) |
| Related: `VRMXT_sprite_particle` root-extension pattern | [vrmxt-sprite-particle.md](../vfx/vrmxt-sprite-particle.md) |
| Related: engine override pattern | [vrmxt-spring-bone-override.md](../physics/vrmxt-spring-bone-override.md) |
| Related: material override sibling | [vrmxt-materials-override.md](../materials/vrmxt-materials-override.md) |
| Related: Blender VRM1 hooks | [blender-extension-hooks.md](../../../implementations/blender-extension-hooks.md) |

## Related implementation notes

Implementation profiles not started. When work begins:

- `implementations/blender-lattice.md` — detect modifiers, skip bake, axis remap
- `implementations/univrm-lattice.md` — consumer components, import flags, remap tables
