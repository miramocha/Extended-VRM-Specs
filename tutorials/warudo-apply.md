---
title: Warudo apply
aliases:
  - Warudo VRMXT plugin
  - load VRMXT in Warudo
tags:
  - extended-vrm
  - type/guide
  - implementation/warudo
  - compatibility/vrm1
type: guide
status: draft
---

# Warudo apply

Load your exported `.vrm` as a Warudo Character. The VRMXT plugin applies
particles, shader overrides, and MToonXT stencil after the avatar loads.

You do not author emitters in Warudo. To change Unity shaders here, use
**VRMXT Manager**, then [patch export](warudo-patch-export.md) if you need a new
file.

## What you'll need

- Warudo
- [VRMXT Plugin for Warudo](https://github.com/miramocha/VRMXT-Plugin-for-Warudo)
  (Steam Workshop:
  [VRMXT](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210))
- A Character whose **Source** is a `.vrm` in the character folder. On the
  Character **Source** dropdown, choose **Open Character Folder**. That folder
  lives under `Warudo_Data/StreamingAssets` (Steam example:
  `C:\Program Files (x86)\Steam\steamapps\common\Warudo\Warudo_Data\StreamingAssets`).
- For override: that Unity shader installed in Warudo (lilToon, Poiyomi, or the
  packaged test shaders). A missing shader skips that material; the avatar still
  loads.
- For stencil clip: [MToonXT Shader for VRMXT (BIRP)](https://steamcommunity.com/sharedfiles/filedetails/?id=3786449905)
  (Warudo Built-In). A missing shader keeps stock MToon; the avatar still loads.

Open **VRMXT** plugin settings and turn on **Enable VRMXT** (default on).

## Steps

1. Subscribe to the Workshop item(s).
2. Open a scene and set a Character Source to your VRMXT file.
3. Wait until the Character is active. You should get:
   - particles from your emitters
   - override shaders on matching materials
   - MToonXT clip when those shader plugins are present (a materials override
     on the same material still replaces MToonXT)
4. Check the viewport, and the plugin status / log for skipped materials.

If nothing extra appears, the plugin may be off, or you loaded an older export
from before VRMXT was on at export.

## Related

- [Warudo patch export](warudo-patch-export.md)
