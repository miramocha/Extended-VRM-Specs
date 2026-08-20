---
title: Blender materials override
aliases:
  - author VRMXT_materials_override
tags:
  - extended-vrm
  - type/guide
  - implementation/blender
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Blender materials override

Point a material at a Unity shader so a VRMXT-supported app (Warudo, VRMXT
Player, etc) can apply it after load. Blender keeps showing MToon or
Principled. You will not see that Unity shader in the EEVEE viewport.

Finish [Getting started in Blender](getting-started-blender.md) first.

## What you'll need

The VRMXT add-on lists known shaders in a dropdown. **Custom…** lets you type
any Unity shader name.

## Steps

The panel sits under **VRMXT Material** in Material Properties.

1. Select the mesh material and open **VRMXT Material**.
2. Click **Add Override**.
3. Set **Engine** to Unity.
4. Set **Variant** to the render pipeline the app will use (**Built-In**,
   URP, …).
5. Pick **Material / Shader** from the list, or **Custom…**.
6. Under **Properties**:
   - **Add common props** fills in the usual subset.
   - **Add** is everything else in the list, plus **Custom…** for a name that
     is not listed.
   - **Remove** deletes that row (the app then uses the shader default again).
7. Edit the values (float, color, vector, Image, keyword).
8. Export as VRM 1.0.

If an imported row stays greyed out, this panel cannot edit that value yet.
Leave it or replace it with a new override.
