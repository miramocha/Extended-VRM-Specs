---
title: VRMXT_materials_directional_dissolve
aliases:
  - directional dissolve
  - plane clip
  - height wipe
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_materials_directional_dissolve

Per-material glTF extension. Axis/plane clip with an optional glowing lip on a VRM
1.0 MToon material. Sibling of `VRMC_materials_mtoon` on the same `materials[]`
entry. Independent of
[VRMXT_materials_mtoonxt](vrmxt-materials-mtoonxt/README.md),
[VRMXT_materials_stencil](vrmxt-materials-stencil.md), and
[VRMXT_materials_face_sdf](vrmxt-materials-face-sdf.md).

This document is an Extended VRM draft. It is not a VRM Consortium specification.

Stock VRM 1.0 importers ignore the extension. No shipping consumer applies it from
file JSON yet. MiraSite `heightWipe.ts` is a host shader patch (world Y); it does
not read this extra.

This extra is **directional dissolve**: clip from fragment height along an axis.
It is not lilToon / catalog texture dissolve (`DISSOLVE`, `_Dissolve*`).

This pass locks the axis to **avatar-root Y** (horizontal clip plane). An arbitrary
plane normal is **TBD**.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_materials_directional_dissolve` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | `materials[i].extensions.VRMXT_materials_directional_dissolve` |
| Required sibling | `VRMC_materials_mtoon` on the same material |
| Root `extensions` | not used |
| Stock importer | no required change |

Do not write these fields inside `VRMC_materials_mtoon` or as a nested extra on
`VRMXT_materials_mtoonxt`.

## Conformance

This specification conforms to [VRMXT Conformance](../../core/vrmxt-conformance.md).

## Normative requirements

1. Files that use this extension MUST list `VRMXT_materials_directional_dissolve` in
   `extensionsUsed`.
2. The extension object MUST appear under
   `materials[i].extensions.VRMXT_materials_directional_dissolve`.
3. The same material MUST contain `extensions.VRMC_materials_mtoon`. If that sibling
   is missing, a supporting implementation MUST ignore this extension on that material.
4. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
5. Files MUST NOT list `VRMXT_materials_directional_dissolve` in `extensionsRequired`.
6. Implementations that do not support the extension MUST ignore it.
7. The skippable unit is this material's `VRMXT_materials_directional_dissolve`
   object. Invalid data there MUST NOT make the glTF or VRM 1.0 asset invalid.
8. Unrecognized properties on the extension object MUST be ignored.
9. When `VRMXT_materials_override` **applies** on the same material, a supporting
   implementation MUST NOT apply this extension on that material.
10. A supporting consumer MUST accept runtime override of `enabled`, `planeY`, and
    `keepAbove` without requiring a rewrite of the glTF. Duration, easing, bounding-box
    pad, and swap choreography MUST NOT be stored on this object.

## Fields

Omit the extension object to leave directional dissolve off. When the object is
present:

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `specVersion` | string | yes | | `"1.0"` for this draft |
| `enabled` | boolean | no | `false` | Apply clip + edge on this material |
| `keepAbove` | boolean | no | `true` | Keep fragments with `h >= planeY`; else keep `h <= planeY` |
| `planeY` | number | no | `0` | Clip plane height in avatar-root space (meters) |
| `edge` | number | no | `0.05` | Fade distance from the plane in meters; MUST be `>= 0` |
| `edgeColor` | number[3] | no | `[0, 0.835, 1]` | Additive RGB (linear 0–1) |
| `edgeGain` | number | no | `2.4` | Multiplier on the edge term |

`h` is fragment position **Y** in **avatar-root / model space** (glTF meters, VRM
Y-up). Consumers MUST transform world or object positions into that space. Do not
treat Unity or Three.js world Y as the stored `planeY`.

A negative `edge`, a non-finite number on any numeric field, or `edgeColor` that is
not a length-3 array of finite numbers makes the object unresolvable (rule 7).

JSON `planeY` MAY be stale. Hosts typically drive `planeY` at runtime.

Fields sit next to `specVersion`.

## Color pass

When `enabled` is true, for each fragment of that material's **color** pass:

1. Compute `h` as avatar-root Y.
2. If `keepAbove` is true, discard when `h < planeY`. Otherwise discard when
   `h > planeY`.
3. If `edge` is `0`, skip the glow. If `edge` is greater than `0`, let
   `band = 1 - clamp(|h - planeY| / edge, 0, 1)`. Add
   `edgeColor * edgeGain * band^2` to the lit RGB **after** MToon shade and
   **before** writing the fragment.

[VRMXT_materials_stencil](vrmxt-materials-stencil.md) still applies to fragments
that survive this discard.

Outline, shadow, and depth passes: **TBD**. A consumer MAY apply the same discard
there; this draft does not require it.

## Example

Non-normative. One body material opted in; the host still animates `planeY`.

```json
"VRMXT_materials_directional_dissolve": {
  "specVersion": "1.0",
  "enabled": true,
  "keepAbove": false,
  "planeY": 0.8,
  "edge": 0.05,
  "edgeColor": [0, 0.835, 1],
  "edgeGain": 2.4
}
```

## Consumer mapping (non-normative)

MiraSite `src/scene/heightWipe.ts` injects world-Y `discard` plus the same `band^2`
additive edge (`uWipeEnabled`, `uWipeY`, `uWipeKeepAbove`, `uWipeEdge`,
`uWipeEdgeColor`, `uWipeEdgeGain`). Default `edge` `0.05`, `edgeGain` `2.4`,
hex `#00d5ff` for the stored color. Reveal uses `keepAbove` false. Wipe duration
`1.12`, bbox pad, and ease stay in `VrmStage.tsx`.

That mapping is a site patch, not Apply of this extra. Replace world Y with
avatar-root Y when the site reads this JSON.

lilToon `DISSOLVE` / `_Dissolve*` catalog rows are a different effect. Do not map
them onto this extra.

## Open questions

- [ ] Arbitrary plane normal (full geometric plane cutout)
- [ ] Outline / shadow / depth pass discard and edge
- [ ] Whether `edgeColor` is strictly linear or matches Three.js `Color('#00d5ff')`
      storage
- [ ] Per-material vs host-wide uniform when several materials carry the extra

## Related

- [VRMXT Conformance](../../core/vrmxt-conformance.md)
- [VRMXT_materials_mtoonxt](vrmxt-materials-mtoonxt/README.md)
- [VRMXT_materials_stencil](vrmxt-materials-stencil.md)
- [VRMXT_materials_face_sdf](vrmxt-materials-face-sdf.md)
- [VRMC_materials_mtoon 1.0](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_materials_mtoon-1.0/README.md)
- [Architecture Naming](../../../architecture.md#naming)
- [MiraSite height wipe refactor](https://github.com/miramocha/Extended-VRM-Specs/issues/47) (non-normative)
