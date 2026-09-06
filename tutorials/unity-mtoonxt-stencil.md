---
title: Unity MToonXT stencil
aliases:
  - author VRMXT_materials_mtoonxt stencil in Unity
tags:
  - extended-vrm
  - type/guide
  - implementation/unity
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Author stencil in Unity

Stencil is one avatar-level writer/reader graph, stored at
`extensions.VRMXT_materials_mtoonxt.stencil`. The same graph is used by Blender
VRMXT; neither import nor export requires BVT.

## Workflow

1. Import a VRM 1.0 avatar using Extended-UniVRM and UniVRMXT. Imported stencil
   graphs appear on the root `VrmxtMaterialsMtoonxtInstance` component.
2. Open **Stencil** on that component. For new authoring, register the avatar's
   MToonXT materials with **Register MToonXT materials**.
3. Add a graph entry and assign non-empty, disjoint **Writers** and **Readers**
   material lists. Both lists refer to avatar materials, not helper overlay clones.
4. Choose presentation and depth controls using the
   [scenario matrix](../examples/stencil-parity-matrix.md). Keep the source
   material's alpha mode, textures, and double-sidedness appropriate to the effect.
5. Export VRM 1.0 with **Enable VRM Export Extensions** enabled. The exporter
   resolves material references through its final glTF material map and writes the
   root graph; it does not emit per-material stencil operations.
6. Reimport the exported VRM to validate the portable result.

The material inspector's **MToonXT stencil** section edits the same root graph,
not an independent material format. Body and outline follow the graph together.

## Choosing an effect

- **M02 — Show through a reader:** reveal a writer through an occluding reader,
  while retaining its ordinary appearance elsewhere.
- **M03/M04 — Inside-only:** clip a writer to the reader silhouette, for example
  animated HUD graphics constrained to a visor lens.
- **M07 — Translucent aura:** preserve source alpha while disabling writer depth
  and self-occlusion as specified by the row.
- **M08 — Hidden-reader coverage:** keep the reader's entire projected silhouette
  eligible even behind other geometry, without revealing the reader's color.

These controls describe different coverage and depth rules, not merely different
artwork. Use each row's control variant to isolate the changed rule.

## Limits and migration

Built-in compound modes use native material layers for lit writer passes and
colorless auxiliary coverage. Equivalent compound URP coverage requires a renderer
feature. Closed-surface overlay culling is not a general nearest-surface solution
for open or concave double-sided meshes.

The former per-material `stencil` / `outlineStencil` operations and root
`stencilRelationships` name are retired, not aliases. Older draft assets must be
explicitly migrated or re-exported.

## References

- [Stencil specification](../specs/extensions/materials/vrmxt-materials-mtoonxt/stencil.md)
- [Visual matrix](https://tdw46.github.io/BVT-Stencil-Matrix/)
