---
title: three-vrm VFX
aliases:
  - VRMXT_vfx for three-vrm
  - Three.js VRM particles
  - WebGL VRMXT_vfx
tags:
  - extended-vrm
  - implementation/three-js
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# three-vrm VFX

Three.js / web implementation profile for [VRMXT_vfx](../specs/vrmxt-vfx.md). Support
belongs in a **separate** optional npm package (working name `@miramocha/three-vrmxt`),
registered beside [@pixiv/three-vrm](https://github.com/pixiv/three-vrm). Do not fork
or replace the stock VRM loader plugin.

VRM 1.0 only. The extension is optional: stock three-vrm load MUST succeed when the
VRMXT package is absent or when `VRMXT_vfx` is missing.

Host stack is **Three.js**. Typical renderers:

| Renderer | Notes |
|----------|-------|
| `WebGLRenderer` | Default path for most apps |
| `WebGPURenderer` | Supported by three-vrm v3+ via `MToonNodeMaterial`; particle materials MAY need a separate WebGPU-compatible path |

## Package

| Item | Value |
|------|-------|
| Host VRM importer | [`@pixiv/three-vrm`](https://www.npmjs.com/package/@pixiv/three-vrm) (`VRMLoaderPlugin` on Three.js `GLTFLoader`) |
| Extended package | Separate npm package (name TBD); peer on `three` |
| three-vrm peer | Soft; load only needs `GLTF` + node `Object3D` list |
| Integration API | `GLTFLoaderPlugin` via `loader.register((parser) => …)` |

three-vrm already splits `VRMC_*` features into loader plugins (springBone, MToon,
node constraint, …). `VRMXT_vfx` follows that peer-plugin pattern.

## Architecture fit

See [Extended VRM Architecture](../architecture.md). three-vrm maps to the optional
consumer package row:

| Architecture rule | three-vrm approach |
|-------------------|--------------------|
| Stock VRM load unchanged | Keep `@pixiv/three-vrm`; add VRMXT package separately |
| Do not replace stock import | Own `GLTFLoaderPlugin`; do not patch `VRMLoaderPlugin` |
| Parse + attach | `afterRoot` and/or explicit `tryAttach` helper |
| No `extensionsRequired` | Never list `VRMXT_vfx` there |
| Missing package / missing ext | Avatar loads; no emitters |

Rejected: shipping Extended VFX only by forking pixiv/three-vrm.

## Import seam (GLTFLoader plugin)

Preferred path: register a VRMXT plugin next to `VRMLoaderPlugin`:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin } from '@pixiv/three-vrm';
// import { VRMXTVfxLoaderPlugin } from '@miramocha/three-vrmxt'; // planned

const loader = new GLTFLoader();
loader.register((parser) => new VRMLoaderPlugin(parser));
loader.register((parser) => new VRMXTVfxLoaderPlugin(parser));
```

Plugin behavior (mirror `VRMSpringBoneLoaderPlugin`):

1. `afterRoot(gltf)`:
   - If `json.extensionsUsed` lacks `VRMXT_vfx`, store null / no-op and return.
   - Read `json.extensions.VRMXT_vfx`.
   - Require `specVersion` `"1.0"` for this draft; other versions: **TBD**.
   - `const nodes = await gltf.parser.getDependencies('node')`.
   - Iterate `emitters[]`. Skip invalid entries per the base spec.
   - Resolve `emitters[].node` as `nodes[nodeIndex]`. Missing → skip that emitter.
   - Resolve `particle.texture` when present via `parser.getDependency('texture', index)`
     (or equivalent). Unresolved → solid tint fallback.
   - Attach particle objects under the resolved `Object3D` using `localPosition` /
     `localRotation` (see [Emitter transform](../specs/vrmxt-vfx.md#emitter-transform)).
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
| Format | Parse / validate `VRMXT_vfx` JSON only |
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
| `localPosition` / `localRotation` | Child `Object3D` under resolved node | Spec / glTF node-local; xyzw quat |
| emitter drawable | `THREE.Points`, instanced quads, or small custom billboard system | **TBD** which default |
| `emissionRate` | Spawner rate in updater | particles / second |
| `maxParticles` | Buffer / pool size | Cap ≥ 1 |
| `lifetime` | Per-particle life | Seconds |
| `startSize` | Point size / quad scale | Meters |
| `startSpeed` | Velocity along local +Y | Emitter local frame |
| `startColor` | Vertex / material color | Linear RGBA |
| `texture` | Material map | Omitted / unresolved → solid tint |
| billboard | Camera-facing points or quads | When the path supports it |

WebGL vs WebGPU material choice is **TBD**. Prefer one MVP path (likely WebGL
`Points` + `PointsMaterial` or textured quads) before a NodeMaterial variant.

## Export

Export of authored VFX from three-vrm / Three.js editors is **TBD**. Prefer Blender
([Blender VFX](blender-vfx.md)) as the authoring path until a web exporter lands.

If export is added later: write root `extensions.VRMXT_vfx`, add `VRMXT_vfx` to
`extensionsUsed`, and do **not** add it to `extensionsRequired`.

## Validation and fallback

Per emitter, skip (do not fail the whole load) when:

- `type` missing or unknown
- `node` missing, out of range, or unresolved
- `type` is `"particle"` but `particle` is missing
- Non-finite or negative `emissionRate` / `lifetime` / `startSize` / `startSpeed`
- `maxParticles` not an integer `>= 1`
- Invalid `localPosition` / `localRotation` per the base spec

Stock three-vrm without the VRMXT package: avatar loads; no emitters. three-vrm MAY
still load VRM 0.0 files; `VRMXT_vfx` remains VRM 1.0-only — skip when the file is
not VRM 1.0 / lacks the extension.

## Tests

Minimum coverage:

| Case | Expectation |
|------|-------------|
| Load valid emitter on bone / object node | Particle child under resolved `Object3D` |
| Bad `node` / invalid scalars | Emitter skipped; VRM otherwise loads |
| Texture index | Map assigned when texture resolves |
| Missing `VRMXT_vfx` with package present | No-op |
| Explicit `tryAttach` after stock load | Same result as plugin path |
| Empty `emitters` | Valid file; no required extension entry |

## Related

- [VRMXT_vfx](../specs/vrmxt-vfx.md)
- [Extended VRM Architecture](../architecture.md)
- [UniVRM VFX](univrm-vfx.md)
- [Godot VFX](godot-vfx.md)
- [Blender VFX](blender-vfx.md)
- [pixiv/three-vrm](https://github.com/pixiv/three-vrm)

## Open questions

| Topic | Status |
|-------|--------|
| Final npm package name | TBD |
| `Points` vs instanced quad default | TBD |
| WebGPU / NodeMaterial particle path | TBD |
| `userData` key name for manager | TBD |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |
| three.js export | TBD |
