---
title: Unity MToonXT stencil
aliases:
  - author VRMC_materials_mtoonxt stencil in Unity
tags:
  - extended-vrm
  - type/guide
  - implementation/unity
  - spec/materials
  - compatibility/vrm1
type: guide
status: draft
---

# Unity MToonXT stencil

Set **Stencil** and **Outline stencil** on a material that already uses MToon
1.0, then switch the shader to MToonXT so the Scene view can clip. Export
writes those settings into the `.vrm`.

Finish [Getting started in Unity](getting-started-unity.md) first. Load a VRM 1.0
avatar into the scene and select it (a mesh on the avatar is enough).

Built-In uses `VRMXT/MToonXT10`. URP uses
`VRMXT/Universal Render Pipeline/MToonXT10`.

## Steps

1. On the material, set **Shader** to the MToonXT name for your pipeline. Stock
   MToon has no stencil block.
2. Open the material inspector. If it says there are no stencil settings yet,
   click **Add MToonXT extras**. You can also select the avatar root, find the
   `VrmcMaterialsMtoonxtInstance` component, and click **Add extras from MToonXT
   materials**.
3. Set **Stencil** to **Off**, **Write**, **Clip inside**, or **Clip outside**.
4. Set **Outline stencil**. Use **Same as body** to copy the body clip onto the
   outline. Leave it **Off** while **Stencil** is **Off**.
5. For **Clip inside** or **Clip outside**, assign **Write** materials under
   **Clip against writers** (drag slots; Size grows the list). Export skips
   other targets.
6. Export as VRM 1.0. Keep **Project Settings → VRM10 → Enable VRM Export
   Extensions** on.

The material must already be MToon, then MToonXT. If a materials override
applies on that material, MToonXT (and this clip) is skipped.

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
3. Under **Clip against writers**, assign the eyebrow material. Left and right
   brow materials both **Write**: add both; hair skips pixels from every
   material in the list.
4. If that hair uses outline, set **Outline stencil** to **Same as body** so
   the outline skips the same pixels.
5. Repeat 2–4 for every overlapping hair material. One brow on **Write** and
   several hair materials is the usual setup. Do not clip the brow to the hair.
6. Export as VRM 1.0 with export extensions on.

The Game view and Scene view clip the hair once MToonXT is on the mesh.

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
3. Under **Clip against writers**, assign the sclera. Separate left and right
   whites: add both; iris uses every material in the list.
4. If the iris uses outline, set **Outline stencil** to **Same as body**.
5. Do not clip the sclera to the iris.
6. Export as VRM 1.0 with export extensions on.
