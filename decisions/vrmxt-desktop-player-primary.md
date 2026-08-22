---
title: VRMXT desktop Player primary
aliases:
  - Drop Hub browser extension
  - Desktop Unity Player primary consumer
  - Supersede Hub WebGL viewer
tags:
  - extended-vrm
  - decision/integration
  - implementation/unity
  - implementation/optional-consumer
  - compatibility/vrm1
  - reference/unity-shader
type: decision
status: accepted
---

# VRMXT desktop Player primary

## Status

Accepted. Supersedes
[VRoid Hub browser viewer architecture](vroid-hub-browser-viewer-architecture.md)
for **Hub + Unity WebGL**. A separate Three.js consumer is
[VRMXT three-vrm web viewer](vrmxt-three-vrm-web-viewer.md).

## Context

[VRoid Hub](https://hub.vroid.com/) hosts VRM 1.0 and previews with a path that ignores
`VRMXT_*`. Original downloads can keep `VRMXT_materials_override`
([round-trip note](../references/vroid-hub-vrmxt-roundtrip.md)).

An earlier decision proposed a Chrome/Firefox extension that downloaded originals and
embedded a Unity WebGL build of
[VRMXT Unity Player](../implementations/vrmxt-unity-player.md) on the same
`2021.3.45f2` pin as [Warudo VRMXT](../implementations/warudo-vrmxt.md).

Player WebGL work showed that path cannot carry Warudo-parity materials-override
shaders at acceptable cost:

- ShaderLab sources are shared; WebGL recompiles to GLES3 with tighter cook, strip,
  and download size limits than desktop.
- Poiyomi Toon plus Thry unlocked-shader stripping, Always Included pressure, and
  variant product made a Hub-in-browser claim of Warudo-class shaders impractical.
- lilToon-shaped claims are closer to WebGL budgets; full Poiyomi parity is not.
- Headless browser smoke is a weak shader check. Desktop Play and player builds match
  Warudo better.

Megashader ship / cook gates (deprecated UPM profile):
[VRMXT Unity Shader Plugins](../implementations/vrmxt-unity-shader-plugins.md).
Planned Player packs:
[VRMXT Player Shader AssetBundles](../references/vrmxt-player-shader-assetbundles.md).
Operational Player notes: `Assets/VRMXTPlayer/SHADERS.md` in the Player repo.

## Decision

1. The primary optional Unity consumer for **preview and edit** of VRM 1.0 +
   `VRMXT_*` is the **desktop** [VRMXT Unity Player](../implementations/vrmxt-unity-player.md)
   (drag-drop / file open, view, edit supported extensions, export / write).
2. Keep Unity editor pin **`2021.3.45f2`** and megashader ship discipline aligned with
   Warudo BIRP ([Warudo VRMXT](../implementations/warudo-vrmxt.md);
   Player packs research:
   [Player Shader AssetBundles](../references/vrmxt-player-shader-assetbundles.md)).
3. Do **not** ship a VRoid Hub extension that embeds **Unity WebGL**, and do **not**
   ship Player WebGL as a Hub preview product. In-browser lilToon / Poiyomi cook
   stays rejected.
4. Local files are the first ingest path for the **Unity** Player. Hub OAuth / download
   inside that desktop app is deferred.
5. A WebGL build MAY remain in the Unity Player project for experiments. It is not a
   claimed Hub product and MUST NOT be documented as Warudo-parity shader support.
6. A **separate** web consumer uses `@pixiv/three-vrm` plus optional `three-vrmxt`
   ([three-vrm web viewer](vrmxt-three-vrm-web-viewer.md)). Unity Player stays **desktop
   Unity** for megashaders and Player edit/export. Browser MToonXT is Three.js stencil
   state, not ShaderLab packs.

## Alternatives considered

| Alternative | Outcome |
|-------------|---------|
| Keep extension + Unity WebGL with full Poiyomi claim | Rejected — cook / strip / size vs Warudo parity |
| Unity WebGL lite only (MToon + lil) | Deferred as Player experiment; not the Hub product path |
| Keep extension + Unity WebGL as planned product | Superseded — same WebGL shader limits |
| Desktop app embeds Hub site in a WebView beside Unity | Deferred — local Player first |
| three-vrm + three-vrmxt browser viewer | Accepted as a **separate** consumer; see [three-vrm web viewer](vrmxt-three-vrm-web-viewer.md) |

## Consequences

- [VRMXT Unity Player](../implementations/vrmxt-unity-player.md) is desktop-first Unity.
- Unity Hub WebGL notes stay superseded:
  [old ADR](vroid-hub-browser-viewer-architecture.md),
  [old extension](../implementations/vroid-hub-browser-extension.md),
  [Unity WebGL VRMXT viewer](../implementations/unity-webgl-vrmxt-viewer.md).
- Later Hub preview, if shipped, is WXT + Three.js
  ([VRMXT Hub extension](../implementations/vrmxt-hub-extension.md)), not a Unity iframe.
- Architecture and README list desktop Player as the Unity app consumer.
- Hub round-trip evidence remains useful for file survival. It does not imply Unity
  WebGL Hub preview.

## Related

- [VRMXT Unity Player](../implementations/vrmxt-unity-player.md)
- [VRMXT three-vrm web viewer](vrmxt-three-vrm-web-viewer.md)
- [VRMXT Unity Shader Plugins](../implementations/vrmxt-unity-shader-plugins.md)
- [Warudo VRMXT](../implementations/warudo-vrmxt.md)
- [VRoid Hub VRMXT round-trip](../references/vroid-hub-vrmxt-roundtrip.md)
- [VRoid Hub browser viewer architecture](vroid-hub-browser-viewer-architecture.md) (superseded)
- [Extended VRM Architecture](../architecture.md)
