---
title: Blender MToonXT stencil
aliases:
  - author VRMC_materials_mtoonxt stencil
tags:
  - extended-vrm
  - type/guide
  - implementation/blender
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Blender MToonXT stencil

Set **Stencil** and **Outline stencil** on a material that already uses MToon
1.0. Clip shows up in a VRMXT-supported app (Warudo, VRMXT Player, etc) that
has MToonXT shaders. The Blender viewport will not clip.

Finish [Getting started in Blender](getting-started-blender.md) first. This
panel is stencil only.

## Steps

1. Select the MToon material. Open **VRMXT Material** (same parent panel as
   materials override).
2. Set **Stencil** to **Off**, **Write**, **Clip inside**, **Clip inside overlay**,
   or **Clip outside**.
3. Set **Outline stencil**. **Same as body** is hidden while **Stencil** is
   **Off**.
4. For **Clip inside**, **Clip inside overlay**, or **Clip outside**, under
   **Clip against writers** add materials whose **Stencil** is **Write**. Export
   skips other targets.
5. If the panel warns about draw order, the **Write** material is in a later MToon
   mode than the clip material (Transparent Write vs Cutout or Opaque, or Cutout
   Write vs Opaque). Switch Write to the same mode or an earlier one (prefer
   Opaque), or export knowing clip can miss.
6. Export as VRM 1.0.

The material must already be MToon. If it is not, these stencil settings stay
out of the file.

## Example: eyebrows in front of hair

Front hair that sits closer to the camera than the face covers the
eyebrows. Set the brow material to **Write**, then clip hair so it skips those
pixels.

1. Select the eyebrow material. Set **Stencil** to **Write**. If that material
   draws an outline, set **Outline stencil** to **Write** so the outline is
   marked too.
2. Select each hair material that covers the brows (base hair, front hair,
   highlight — whatever actually overlaps). Set **Stencil** to **Clip
   outside**.
3. Under **Clip against writers**, click **Add clip target** and pick the
   eyebrow material. Left and right brow materials both **Write**: add both;
   hair skips pixels from every material in the list.
4. If that hair uses outline, set **Outline stencil** to **Same as body** so
   the outline skips the same pixels.
5. Repeat 2–4 for every overlapping hair material. One brow on **Write** and
   several hair materials is the usual setup. Do not clip the brow to the hair.
6. If the panel warns that the **Write** material is Transparent, switch the
   brow to Opaque or Cutout so it draws before Transparent or Cutout hair, or
   export knowing clip can miss.
7. Export as VRM 1.0.

EEVEE still will not clip the hair. Check the file in a VRMXT-supported app.

MToon **Transparent** hair still counts every drawn pixel as solid, so the hole
is a hard edge. **Cutout** hair already has that hard alpha, so front hair over
solid brows looks OK. Fuzzy **Transparent** hair can look like a sharp hole.

## Example: iris inside sclera

The iris mesh is usually a disc that sticks out past the white of the eye. Set
the sclera to **Write**, then clip iris so it draws only on those pixels.

VRoid often names the sclera **White**.

1. Select the sclera material. Set **Stencil** to **Write**. Leave **Outline
   stencil** on **Off**. Outline **Write** would count pixels past the white.
2. Select the iris material. Set **Stencil** to **Clip inside**.
3. Under **Clip against writers**, click **Add clip target** and pick the
   sclera. Separate left and right whites: add both; iris uses every material
   in the list.
4. If the iris uses outline, set **Outline stencil** to **Same as body**.
5. Do not clip the sclera to the iris.
6. Export as VRM 1.0.

EEVEE still will not clip the iris. Check the file in a VRMXT-supported app.

## Example: skeleton on swimsuit

Show bones only on swimsuit pixels. Leave body **Stencil** **Off** so the mesh
stays solid (no hole through a leg).

1. Select the swimsuit material. Set **Stencil** to **Write**.
2. Select the skeleton material. Set **Stencil** to **Clip inside overlay**.
3. Under **Clip against writers**, add the swimsuit. Set **Outline stencil** to
   **Same as body** if the skeleton draws an outline.
4. Leave skin / body **Stencil** **Off**.
5. Export as VRM 1.0.

EEVEE still will not overlay the bones. Check the file in a VRMXT-supported app.
A hand or mic in front of the swimsuit can disappear in those pixels.
