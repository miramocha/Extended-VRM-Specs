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
[VRoid Hub browser viewer architecture](vroid-hub-browser-viewer-architecture.md).

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
3. Do **not** ship the VRoid Hub browser extension or Player WebGL viewer as a product
   path for Hub preview.
4. Local files are the first ingest path. Hub OAuth / download inside the desktop app
   is deferred.
5. A WebGL build MAY remain in the Player project for experiments. It is not a claimed
   Hub product and MUST NOT be documented as Warudo-parity shader support.

## Alternatives considered

| Alternative | Outcome |
|-------------|---------|
| Keep extension + WebGL with full Poiyomi claim | Rejected — cook / strip / size vs Warudo parity |
| WebGL lite only (MToon + lil) | Deferred as experiment; not the Hub product path |
| Keep extension + WebGL as planned product | Superseded — same WebGL shader limits |
| Desktop app embeds Hub site in a WebView beside Unity | Deferred — local Player first |

## Consequences

- [VRMXT Unity Player](../implementations/vrmxt-unity-player.md) is desktop-first.
- [VRoid Hub browser viewer architecture](vroid-hub-browser-viewer-architecture.md),
  [VRoid Hub browser extension](../implementations/vroid-hub-browser-extension.md), and
  [Unity WebGL VRMXT viewer](../implementations/unity-webgl-vrmxt-viewer.md) are
  superseded / historical.
- Architecture and README list desktop Player as the planned app consumer; Hub
  extension + WebGL rows point here as superseded.
- Hub round-trip evidence remains useful for file survival; it does not imply an
  in-browser VRMXT preview product.

## Related

- [VRMXT Unity Player](../implementations/vrmxt-unity-player.md)
- [VRMXT Unity Shader Plugins](../implementations/vrmxt-unity-shader-plugins.md)
- [Warudo VRMXT](../implementations/warudo-vrmxt.md)
- [VRoid Hub VRMXT round-trip](../references/vroid-hub-vrmxt-roundtrip.md)
- [VRoid Hub browser viewer architecture](vroid-hub-browser-viewer-architecture.md) (superseded)
- [Extended VRM Architecture](../architecture.md)
