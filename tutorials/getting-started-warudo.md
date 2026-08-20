---
title: Getting started in Warudo
aliases:
  - Warudo apply
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

# Getting started in Warudo

Subscribe to the Workshop plugins and load your `.vrm` as a Character. The
VRMXT plugin applies particles, shader overrides, and MToonXT stencil after
the avatar loads.

Use these Workshop items. You do not author emitters in Warudo. To change
Unity shaders here, use **VRMXT Manager**, then
[patch export](warudo-patch-export.md) if you need a new file.

| Package | Workshop |
|---------|----------|
| VRMXT | [VRMXT](https://steamcommunity.com/sharedfiles/filedetails/?id=3767350210) |
| MToonXT shader (BIRP, for stencil) | [MToonXT Shader for VRMXT (BIRP)](https://steamcommunity.com/sharedfiles/filedetails/?id=3786449905) |

A Character **Source** must be a `.vrm` in the character folder. On the
Character **Source** dropdown, choose **Open Character Folder**. That folder
lives under `Warudo_Data/StreamingAssets` (Steam example:
`C:\Program Files (x86)\Steam\steamapps\common\Warudo\Warudo_Data\StreamingAssets`).

For override, that Unity shader must be installed in Warudo (lilToon, Poiyomi,
or the packaged test shaders). A missing shader skips that material; the
avatar still loads. A missing MToonXT shader keeps stock MToon.

## Install

1. Subscribe to the Workshop item(s).
2. Open **VRMXT** plugin settings and turn on **Enable VRMXT** (default on).
3. Open a scene and set a Character Source to your VRMXT file.
4. Wait until the Character is active. You should get:
   - particles from your emitters
   - override shaders on matching materials
   - MToonXT clip when the shader plugin is present (a materials override on
     the same material still replaces MToonXT)
5. Check the viewport, and the plugin status / log for skipped materials.

If nothing extra appears, the plugin may be off, or you loaded an older export
from before VRMXT was on at export.

## Related

- [Warudo patch export](warudo-patch-export.md)
