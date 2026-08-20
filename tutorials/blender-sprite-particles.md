---
title: Blender sprite particles
aliases:
  - author VRMXT_sprite_particle
  - Blender VFX emitters
tags:
  - extended-vrm
  - type/guide
  - implementation/blender
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# Blender sprite particles

Add camera-facing sprite emitters on the VRM 1.0 armature. They play in a
VRMXT-supported app (Warudo, VRMXT Player, etc) after export.

Use the VRMXT **VFX** list, not a Blender particle system. Viewport preview
objects are temporary; they are not part of the exported avatar.

Finish [Getting started in Blender](getting-started-blender.md) first. A sprite
image is optional until you want a textured sprite.

## Steps

1. Select the armature. Open **VFX** (Properties or the VRM sidebar).
2. Add an emitter and give it a name you will recognize later.
3. Attach it to a pose bone. For an offset, parent an Empty under the bone and
   attach to the Empty.
4. Set texture, size in meters, and color.
5. Set emission rate, max particles, lifetime, and start speed.
6. Click **Rebuild VFX preview** to see them in the viewport. **Clear VFX
   preview** removes the preview objects.
7. Export as VRM 1.0.

Re-import and the emitter list should come back. Preview objects should not
appear as extra meshes in the exported file.