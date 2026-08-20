---
title: Warudo patch export
aliases:
  - Export VRMXT Patch
  - VRMXT Manager export
tags:
  - extended-vrm
  - type/guide
  - implementation/warudo
  - compatibility/vrm1
type: guide
status: draft
---

# Warudo patch export

After you change shader overrides in Warudo, save them into a **copy** of the
Character's original `.vrm`. Meshes and textures stay as they were. This is not
an export of the live Warudo avatar.

Finish [Getting started in Warudo](getting-started-warudo.md) first.

## What you'll need

Put the `.vrm` in the folder from **Open Character Folder** on the Character
**Source** dropdown. Use this when you need a file to take back to Blender.

## Steps

1. Add the **VRMXT Manager** scene asset.
2. Pick the Character. One Character per manager.
3. Use the feature toggles and per-material shader autocomplete if you are
   changing slots here.
4. Click **Apply** so the live Character materials match.
5. Click **Export VRMXT Patch**. The suffix defaults to `.vrmxt` (you can edit
   it). Warudo writes a separate file next to the original, such as
   `Characters/<name>.vrmxt.vrm` in that same data folder.
6. Read the status line for the output path, skipped entries, and errors.

The copy gets your shader-override edits. Sprite emitters stay as you authored
them in Blender (this patch does not add new textures). The Character you are
playing keeps its current Source; the original file is not overwritten.
Re-import in Blender and the override rows should match what you set in the
Manager.

## Related

- [Getting started in Warudo](getting-started-warudo.md)
