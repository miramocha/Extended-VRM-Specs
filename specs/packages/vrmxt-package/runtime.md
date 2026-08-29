---
title: VRMXT Package Runtime
aliases:
  - VRMXTPKG loader
  - VRMXT Package anti-export
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT Package Runtime

Engine-agnostic rules for constructing a live avatar from Payload chunks.
Engine profiles add API names. Conforms to [VRMXT Package Format](README.md).

## Incremental construction

1. Verify header, signature, and index ([Container](container.md)).
2. Obtain keys if `ENCRYPTED` ([Delivery](delivery.md)).
3. Fetch chunks concurrently (suggested 4–12).
4. Decrypt and authenticate one chunk at a time ([Protection](protection.md)).
5. Decompress / meshopt / KTX2-decode into engine buffers.
6. Upload or bind to GPU / runtime objects.
7. Overwrite or detach plaintext `ArrayBuffer` / native buffers.
8. Repeat. Never concatenate all plaintext chunks.

A consumer MUST NOT build a GLB (`glTF` magic + JSON chunk + BIN chunk) or a `.vrm`
byte array as an intermediate.

Main-thread stalls over 50 ms during decode SHOULD be avoided (Worker/WASM recommended).
This number is a quality target, not a file-format requirement.

## Semantic runtime

After construction, the avatar MUST support VRM 1.0-equivalent operations:

- Humanoid normalized pose get/set
- Expression `setValue` / `resetValues` including presets present in the payload
- Look-at update
- Spring bone / node constraint update on a per-frame `update(delta)`
- MToon (and packaged `VRMXT_*` when the engine profile supports them)

Site and engine code MAY duck-type these operations. They MUST NOT require
`instanceof` a stock VRM class.

## Stock exporter resistance

A conforming Three.js-family consumer MUST:

1. NOT attach a stock `@pixiv/three-vrm` `VRM` instance on `scene.userData.vrm`.
2. NOT satisfy `object instanceof VRM` for the object handed to application code.
3. NOT leave authoring-space `BufferAttribute` POSITION/NORMAL (and texture texels)
   in CPU buffers in a layout that `GLTFExporter` or community `VRMExport(vrm)` can
   serialize into a loadable VRM.

Application-facing object: **VRMXT avatar facade**. It MAY wrap internal helpers,
including three-vrm manager classes, if those objects are not reachable from
`scene.userData` or from a public `vrm` property.

Recommended mesh protection: store swizzled or shuffled attributes; restore in the
vertex shader (and analogously shuffle texture channels restored in the fragment
shader). `GLTFExporter.parse(scene)` MUST produce a non-loadable or geometrically
garbage VRM/GLB under the engine profile's tests.

Bones remain `Object3D` (or engine equivalent). IK needs transforms. This specification
does not hide the skeleton.

## Hard limit

A process that can read GPU memory, hook the decode Worker, or walk heap objects MAY
still recover geometry. Runtime rules target **stock exporters and casual scene dumps**,
not a DRM guarantee.

## three-vrm

Do not fork `@pixiv/three-vrm` by default. Prefer public constructors
(`VRMHumanoid`, `VRMExpressionManager`, `MToonMaterial`, …) behind the facade.
`VRMLoaderPlugin` MUST NOT be the load path (it needs a full `GLTFParser` graph).

If a required class is not constructible without `GLTFParser`, that is an
implementation checkpoint, not a file-format change.

## Engine profiles

| Profile | Notes |
|---------|-------|
| Three.js | [vrmxt-package implementation](../../../implementations/vrmxt-package.md) |
| Unity / UniVRM | TBD; same payload, native meshes |
| Other | Same Payload; no GLB round-trip |

## Open questions

- [ ] Exact swizzle algorithm (normative vs implementation-defined)
- [ ] Whether morph targets stay in authoring space (expressions need them)
- [ ] `VRMUtils.combineSkeletons` equivalent after custom build

## Related

- [Payload](payload.md)
- [Security](security.md)
