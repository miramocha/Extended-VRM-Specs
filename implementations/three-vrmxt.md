---
title: three-vrmxt
aliases:
  - three-vrm VFX
  - VRMXT_sprite_particle for three-vrm
  - Three.js VRM particles
  - WebGL VRMXT_sprite_particle
  - @vrmxt/three-vrmxt
tags:
  - extended-vrm
  - implementation/three-js
  - spec/vfx
  - spec/materials
  - compatibility/vrm1
  - implementation/optional-consumer
type: guide
status: draft
---

# three-vrmxt

Three.js consumer library for Extended VRM. Repo:
[miramocha/three-vrmxt](https://github.com/miramocha/three-vrmxt) (pnpm workspace).
Publish `packages/three-vrmxt` as **`@vrmxt/three-vrmxt`** (fallback
**`@miramocha/three-vrmxt`** if the npm org is missing). Peers: `three`,
`@pixiv/three-vrm`.

This package is a peer `GLTFLoaderPlugin` beside
[`VRMLoaderPlugin`](https://github.com/pixiv/three-vrm). Do not fork pixiv/three-vrm.
Do not add UniVRM/Blender-style importer hooks into pixiv.

Product hosts:

| Piece | Role |
|-------|------|
| `packages/three-vrmxt` | Publishable library |
| `apps/viewer` | v1 Vite local-file viewer ([web viewer](vrmxt-web-viewer.md)) |
| `packages/viewer-core` | Shared view/load used by `apps/viewer` and later Hub WXT |
| Later Hub WXT | [VRMXT Hub extension](vrmxt-hub-extension.md) (not v1) |

Decision: [VRMXT three-vrm web viewer](../decisions/vrmxt-three-vrm-web-viewer.md).

VRM 1.0 only. Stock three-vrm load MUST succeed when this package is absent.

Renderer: pass `stencil: true` into the `WebGLRenderer` constructor when applying
MToonXT stencil. Assigning `renderer.stencil` after construct does not allocate the
buffer (Three.js r163+).

## Supported features

| Extension | Status |
|-----------|--------|
| `VRMC_materials_mtoonxt` stencil | Claimed: map extras onto Three.js material stencil state. Face SDF later. |
| `VRMXT_sprite_particle` | Planned |
| Export write | Planned (Editor contract; never `extensionsRequired`) |

Host stack is **Three.js**. Typical renderers:

| Renderer | Notes |
|----------|-------|
| `WebGLRenderer` | Default path for most apps |
| `WebGPURenderer` | Supported by three-vrm v3+ via `MToonNodeMaterial`; particle materials MAY need a separate WebGPU-compatible path |

## Package

| Item | Value |
|------|-------|
| Host VRM importer | [`@pixiv/three-vrm`](https://www.npmjs.com/package/@pixiv/three-vrm) (`VRMLoaderPlugin` on Three.js `GLTFLoader`) |
| Extended package | `@vrmxt/three-vrmxt` (fallback `@miramocha/three-vrmxt`) |
| Peers | `three`, `@pixiv/three-vrm` |
| Integration API | `GLTFLoaderPlugin` via `loader.register((parser) => …)` |

three-vrm already splits `VRMC_*` features into loader plugins (springBone, MToon,
node constraint, …). `VRMXT_sprite_particle` follows that peer-plugin pattern.

## Architecture fit

See [Extended VRM Architecture](../architecture.md). three-vrm maps to the optional
consumer package row:

| Architecture rule | three-vrm approach |
|-------------------|--------------------|
| Stock VRM load unchanged | Keep `@pixiv/three-vrm`; add VRMXT package separately |
| Do not replace stock import | Own `GLTFLoaderPlugin`; do not patch `VRMLoaderPlugin`; do not fork pixiv |
| Parse + attach | `afterRoot` and/or explicit `tryAttach` helper |
| No `extensionsRequired` | Never list `VRMXT_*` or `VRMC_materials_mtoonxt` there |
| Missing package / missing ext | Avatar loads; extras skipped |

Rejected: shipping Extended features only by forking pixiv/three-vrm.

## Import seam (GLTFLoader plugin)

Preferred path: register a VRMXT plugin next to `VRMLoaderPlugin`:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin } from '@pixiv/three-vrm';
import { VRMXTLoaderPlugin } from '@vrmxt/three-vrmxt';

const loader = new GLTFLoader();
loader.register((parser) => new VRMLoaderPlugin(parser));
loader.register((parser) => new VRMXTLoaderPlugin(parser));
```

Plugin behavior (mirror `VRMSpringBoneLoaderPlugin`):

1. `afterRoot(gltf)`:
   - Apply `VRMC_materials_mtoonxt` stencil when present (v1).
   - If `json.extensionsUsed` lacks `VRMXT_sprite_particle`, skip emitters (planned).
   - Read `json.extensions.VRMXT_sprite_particle`.
   - Require `specVersion` `"1.0"` for this draft; other versions: **TBD**.
   - `const nodes = await gltf.parser.getDependencies('node')`.
   - Iterate `emitters[]`. Skip invalid entries per the base spec.
   - Resolve `emitters[].node` as `nodes[nodeIndex]`. Missing → skip that emitter.
   - Resolve `texture` when present via `parser.getDependency('texture', index)`
     (or equivalent). Unresolved → solid tint fallback.
   - Attach particle objects under the resolved `Object3D` (origin / orientation follow
     that node's transform; no extension-local offset fields).
   - Store a manager / handle on `gltf.userData` (name TBD, e.g. `vrmxtVfx`).
2. Do not fail the whole VRM load when individual emitters are skipped.

`VRMLoaderPlugin.afterRoot` builds `gltf.userData.vrm` when meta + humanoid exist.
VRMXT MUST NOT require that object; attach to scene nodes from the parser. Apps MAY
also hang the manager off `vrm` after load if convenient.

## Runtime seam (explicit attach)

Apps that already loaded a VRM without the VRMXT plugin MAY call an explicit helper
(same shape as UniVRMXT `VrmxtVfxRuntime.TryAttach`):

1. Pass glTF JSON (`gltf.parser.json`), the VRM/`Object3D` root, and a node-index →
   `Object3D` map (`getDependencies('node')` result).
2. Missing extension → no-op (`false` / null).
3. Unresolved nodes skip that emitter only.

If the particle implementation needs per-frame updates, the app MUST call an update
method in the render loop next to `vrm.update(delta)`.

## Layering (proposed)

| Layer | Role |
|-------|------|
| Format | Parse / validate `VRMXT_sprite_particle` JSON only |
| Loader plugin | `GLTFLoaderPlugin.afterRoot` |
| Runtime attach | `tryAttach` without re-parsing the whole glTF when JSON + nodes are known |
| Particle mapper | Map portable fields onto Three.js drawables |

Keep format parsing free of `@pixiv/three-vrm` imports so unit tests do not need a
WebGL context.

## Particle mapping (proposed)

Three.js has no Unity-style `ParticleSystem`. Exact visual parity is not required.
Field meaning and units follow the base spec.

| Spec field | Three.js target (MVP candidates) | Notes |
|------------|----------------------------------|-------|
| Attach node | Parent for particle drawable | Origin and orientation from node world transform |
| emitter drawable | `THREE.Points`, instanced quads, or small custom billboard system | **TBD** which default |
| `emissionRate` | Spawner rate in updater | particles / second |
| `maxParticles` | Buffer / pool size | Cap ≥ 1 |
| `lifetime` | Per-particle life | Seconds |
| `size` | Point size / quad scale | Width and height in meters |
| `startSpeed` | Velocity along node local +Y | Node local frame |
| `color` | Vertex / material color | Linear RGBA |
| `texture` | Material map | Omitted / unresolved → solid tint |

WebGL vs WebGPU material choice is **TBD**. Prefer one MVP path (likely WebGL
`Points` + `PointsMaterial` or textured quads) before a NodeMaterial variant.

## MToonXT stencil (claimed)

Spec: [VRMC_materials_mtoonxt stencil](../specs/extensions/materials/vrmc-materials-mtoonxt/stencil.md).

After stock MToon materials exist, read per-material `VRMC_materials_mtoonxt` stencil /
`outlineStencil` extras and set Three.js material stencil state so writer / reader
coverage matches the spec intention (`write`, `inside`, `insideOverlay`, `outside`,
outline `same`). GPU stencil requires `WebGLRenderer` constructed with stencil
enabled.

Face SDF stays later. lilToon / Poiyomi `VRMXT_materials_override` is out of scope
in this library.

## Export

Planned. When a host writes files, follow [VRMXT Editor](vrmxt-editor.md): append
supported extras, list them in `extensionsUsed`, never in `extensionsRequired`.
v1 `apps/viewer` does not write.

Until web export ships, prefer Blender or UniVRMXT for authoring
([Blender VRMXT](blender-vrmxt.md)).

If sprite VFX export is added: write root `extensions.VRMXT_sprite_particle` and add
that name to `extensionsUsed` only.

## Validation and fallback

Per emitter, skip (do not fail the whole load) when:

- `node` missing, out of range, or unresolved
- `size` present but not two finite numbers greater than `0`
- `color` present but not four finite numbers, RGB `>= 0`, alpha in `[0,1]`
- Non-finite or negative `emissionRate` / `lifetime` / `startSpeed`
- `maxParticles` not an integer `>= 1`

Stock three-vrm without the VRMXT package: avatar loads; no emitters. three-vrm MAY
still load VRM 0.0 files; `VRMXT_sprite_particle` remains VRM 1.0-only — skip when the
file is not VRM 1.0 / lacks the extension.

## Tests

Minimum coverage:

| Case | Expectation |
|------|-------------|
| Load valid emitter on bone / object node | Particle child under resolved `Object3D` |
| Bad `node` / invalid scalars | Emitter skipped; VRM otherwise loads |
| Texture index | Map assigned when texture resolves |
| Missing `VRMXT_sprite_particle` with package present | No-op |
| Explicit `tryAttach` after stock load | Same result as plugin path |
| Empty `emitters` | Valid file; no required extension entry |

## Related

- [VRMC_materials_mtoonxt](../specs/extensions/materials/vrmc-materials-mtoonxt/README.md)
- [VRMXT_sprite_particle](../specs/extensions/vfx/vrmxt-sprite-particle.md)
- [VRMXT three-vrm web viewer](../decisions/vrmxt-three-vrm-web-viewer.md)
- [VRMXT web viewer](vrmxt-web-viewer.md)
- [VRMXT Hub extension](vrmxt-hub-extension.md)
- [Extended VRM Architecture](../architecture.md)
- [UniVRMXT](univrm-vrmxt.md)
- [Godot VRMXT](godot-vrmxt.md)
- [Blender VRMXT](blender-vrmxt.md)
- [pixiv/three-vrm](https://github.com/pixiv/three-vrm)
- [miramocha/three-vrmxt](https://github.com/miramocha/three-vrmxt)

## Open questions

| Topic | Status |
|-------|--------|
| npm package name | `@vrmxt/three-vrmxt`; fallback `@miramocha/three-vrmxt` |
| `Points` vs instanced quad default | TBD |
| WebGPU / NodeMaterial particle path | TBD |
| `userData` key name for manager | TBD |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |
| three.js export | Planned (not v1 viewer) |
| Face SDF on Three.js | Later |
