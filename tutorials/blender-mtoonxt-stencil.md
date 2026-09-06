---
title: Blender MToonXT stencil
aliases:
  - author VRMXT_materials_mtoonxt stencil
tags:
  - extended-vrm
  - type/guide
  - implementation/blender
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Author stencil in Blender

Use the VRM add-on's VRM 1.0 importer/exporter with VRMXT enabled. VRMXT owns the
stencil graph and material references; BVT/BVES is an optional preview consumer,
not an import/export requirement.

1. Open **MToonXT stencil** in Scene Properties or under **VRMXT Material**.
   Both panels edit the same Scene graph.
2. Add an entry, then assign non-empty, disjoint **Writers** and **Readers**
   material lists. Use the avatar's source MToon materials.
3. Choose presentation, color output, and independent reader/writer depth controls.
   Start with a row from the [scenario matrix](../examples/stencil-parity-matrix.md).
4. Keep source alpha mode, alpha textures, and double-sidedness configured separately.
   Disabling depth writes alone does not make a material transparent.
5. Export with the ordinary **VRM** exporter. The official pre-save hook resolves
   the final material indices and emits
   `extensions.VRMXT_materials_mtoonxt.stencil`.
6. Reimport to restore the graph automatically. Without BVES, VRMXT still provides
   all graph authoring fields. With BVES automatic import preview enabled, its
   post-import integration enables or refreshes preview.

For a visor HUD, use M04: HUD materials are writers, the lens is the reader, and
inside-only plus show-through clips the HUD to the lens. For a translucent aura,
use M07 and retain the aura material's alpha settings.

The root graph replaces the former per-material `stencil` / `outlineStencil`
operations and the old `stencilRelationships` name. Older draft assets require
explicit migration or re-export. There is no parallel shorthand or separate
outline format.

- [Stencil specification](../specs/extensions/materials/vrmxt-materials-mtoonxt/stencil.md)
- [Visual matrix](https://tdw46.github.io/BVT-Stencil-Matrix/)
- [Unity workflow](unity-mtoonxt-stencil.md)
