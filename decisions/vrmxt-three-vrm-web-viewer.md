---
title: VRMXT three-vrm web viewer
aliases:
  - three-vrmxt web consumer
  - Vite VRMXT viewer
  - three-vrmxt peer plugin
tags:
  - extended-vrm
  - decision/integration
  - implementation/three-js
  - implementation/optional-consumer
  - compatibility/vrm1
  - spec/materials
type: decision
status: accepted
---

# VRMXT three-vrm web viewer

## Status

Accepted. Adds a Three.js web consumer beside [@pixiv/three-vrm](https://github.com/pixiv/three-vrm).
Does not reopen [VRMXT desktop Player primary](vrmxt-desktop-player-primary.md): Unity
Player stays desktop Unity; Hub + Unity WebGL + in-browser lilToon / Poiyomi stay rejected.

## Context

Optional `VRMXT_*` consumers already exist or are planned on Unity (UniVRMXT, Warudo,
desktop Player), Blender, Godot, and VRM4U. Architecture already listed a planned npm
package beside pixiv/three-vrm. That package had no repo, no claimed MToonXT path, and
no local viewer.

[VRoid Hub](https://hub.vroid.com/) still previews with stock three-vrm and ignores
`VRMXT_*` / `VRMC_materials_mtoonxt`. Original downloads can keep extension JSON
([round-trip note](../references/vroid-hub-vrmxt-roundtrip.md)). An earlier Hub product
tried to embed a Unity WebGL build of
[VRMXT Unity Player](../implementations/vrmxt-unity-player.md) to get Warudo-class
megashaders. ShaderLab → GLES3 cook, strip, and download size made Poiyomi (and full
lilToon parity) impractical in that iframe. That path is superseded.

WebGL stencil on Three.js `WebGLRenderer` is a different budget: stock MToon from
three-vrm plus portable MToonXT extras mapped onto Three.js material stencil state.

## Decision

1. Register `packages/three-vrmxt` as a peer `GLTFLoaderPlugin` beside pixiv
   `VRMLoaderPlugin`. Repo:
   [miramocha/three-vrmxt](https://github.com/miramocha/three-vrmxt) (public). Local
   checkout: `D:\MiraGameDev\three-vrmxt`. pnpm workspace.
2. Publishable library: `packages/three-vrmxt` as **`@vrmxt/three-vrmxt`**. If the npm
   org is unavailable, publish **`@miramocha/three-vrmxt`**. Peers: `three`,
   `@pixiv/three-vrm`. Register a `GLTFLoaderPlugin` beside `VRMLoaderPlugin`.
3. **v1 viewer** is a standalone Vite app at `apps/viewer`. Local file ingest only
   (picker + drag-drop). Orbit camera. Stock VRM 1.0 MToon via three-vrm. Apply / view
   [VRMC_materials_mtoonxt](../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
   with **stencil first**. Construct `WebGLRenderer` with `stencil: true`. No edit UI, no export write,
   no Hub API, no Electron/Tauri.
4. Shared view logic lives in `packages/viewer-core`. Later a Hub [WXT](https://wxt.dev/)
   extension MAY fetch original bytes through the Hub API and mount the same core.
   View-first. That extension is **not** v1.
5. Later still: in-memory create/edit of supported `VRMXT_*` / MToonXT extras and
   export per [VRMXT Editor](../implementations/vrmxt-editor.md). Writers MUST list
   names in `extensionsUsed` and MUST NOT list them in `extensionsRequired`.
6. [VRMXT Unity Player](../implementations/vrmxt-unity-player.md) remains the desktop
   Unity app for Warudo-aligned megashaders and Player edit/export. Do not revive Hub
   + Unity WebGL as a product. Do not claim lilToon or Poiyomi inside the browser
   viewer.

## Rationale

pixiv already splits `VRMC_*` into loader plugins. A peer `GLTFLoaderPlugin` matches
that seam and keeps stock VRM load working when the VRMXT package is absent.

Local Vite ingest proves MToonXT stencil on Three.js without OAuth, Hub CSP, or a
desktop shell. Hub WXT can reuse `viewer-core` once file view works.

Unity megashaders stay on desktop Player / Warudo. Browser MToonXT is stencil (and
later Face SDF) on three-vrm MToon material state.

## Alternatives considered

| Alternative | Outcome |
|-------------|---------|
| Fork pixiv/three-vrm | Rejected — drop-in use of `@pixiv/three-vrm`; architecture forbids fork-as-only-path |
| UniVRM/Blender-style hooks into pixiv | Rejected — pixiv has no such registry; peer `GLTFLoaderPlugin` is the host seam |
| Hub + Unity WebGL iframe | Rejected — [desktop Player primary](vrmxt-desktop-player-primary.md); cook / size vs Poiyomi |
| lilToon / Poiyomi in-browser | Rejected — ShaderLab megashaders are Unity desktop / Warudo |
| Electron / Tauri v1 | Rejected — browser Vite + local files first |
| Edit + export in v1 | Deferred — view / Apply MToonXT stencil first |
| Hub API in v1 | Deferred — same `viewer-core`, later WXT |

## Consequences

- Library profile: [three-vrmxt](../implementations/three-vrmxt.md).
- Vite host: [VRMXT web viewer](../implementations/vrmxt-web-viewer.md).
- Later Hub WXT: [VRMXT Hub extension](../implementations/vrmxt-hub-extension.md). Historical
  Unity Hub notes stay superseded:
  [old ADR](vroid-hub-browser-viewer-architecture.md),
  [old extension](../implementations/vroid-hub-browser-extension.md),
  [Unity WebGL viewer](../implementations/unity-webgl-vrmxt-viewer.md).
- Desktop Player primary still governs Unity preview/edit and megashader ship.
- Architecture and README list three-vrmxt as an optional consumer with a public repo.

## Related

- [VRMXT desktop Player primary](vrmxt-desktop-player-primary.md)
- [three-vrmxt](../implementations/three-vrmxt.md)
- [VRMXT web viewer](../implementations/vrmxt-web-viewer.md)
- [VRMXT Hub extension](../implementations/vrmxt-hub-extension.md)
- [VRMXT Editor](../implementations/vrmxt-editor.md)
- [VRMC_materials_mtoonxt](../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
- [Extended VRM Architecture](../architecture.md)
- [pixiv/three-vrm](https://github.com/pixiv/three-vrm)
- [miramocha/three-vrmxt](https://github.com/miramocha/three-vrmxt)
