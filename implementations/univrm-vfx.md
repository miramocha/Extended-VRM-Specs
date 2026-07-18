---
title: UniVRM VFX
aliases:
  - VRMXT_vfx for UniVRM
  - UniVRMXT particles
tags:
  - extended-vrm
  - implementation/unity
  - spec/vfx
  - compatibility/vrm1
type: guide
status: draft
---

# UniVRM VFX

Unity implementation profile for [VRMXT_vfx](../specs/vrmxt-vfx.md). Support belongs in
[UniVRMXT](https://github.com/miramocha/UniVRMXT) (`com.miramocha.univrmxt`). Stock
[UniVRM](https://github.com/vrm-c/UniVRM) source changes are not required.

VRM 1.0 only. The extension is optional: stock UniVRM load MUST succeed when UniVRMXT
is absent or when `VRMXT_vfx` is missing.

## Package

| Item | Value |
|------|-------|
| UPM id | `com.miramocha.univrmxt` |
| Stock VRM I/O | [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) (`0.131.1`+) |
| Optional host fork | [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) |
| Unity | `2022.3` |

## Import seam

UniVRM has no general root-extension registry. UniVRMXT foundation:

1. Parse root `extensions.VRMXT_vfx` from glTF JSON (`specVersion` `"1.0"`) via
   `VrmxtVfx.TryParse`.
2. Skip invalid emitters per the base spec.
3. After `Vrm10.LoadGltfDataAsync` (or equivalent), map `emitters[].node` through
   `RuntimeGltfInstance.Nodes`.
4. Call `VrmxtVfxRuntime.TryAttach(root, gltfJson, nodes, out instance)` to store
   resolved emitters on `VrmxtVfxInstance` (avatar root). `VrmxtVfxData` remains
   available as a ScriptableObject mirror for asset workflows.

Unresolved nodes skip that emitter only. UniVRMXT Runtime does not hard-reference
UniGLTF/VRM10 asmdefs; the load caller supplies JSON and the node Transform list.

## Runtime behavior (foundation)

MVP stores parsed emitter data on `VrmxtVfxInstance` (node index, `Transform`, local
TR, particle scalars, texture index). `VrmxtVfxParticleSystemMapper` maps portable
fields onto Unity `ParticleSystem` (billboard, local +Y velocity, optional texture).
See UniVRMXT [vfx-particle-mapping.md](https://github.com/miramocha/UniVRMXT/blob/main/docs/vfx-particle-mapping.md).

## Export

Export of authored VFX from Unity is **TBD**. Prefer Blender
([Blender VFX](blender-vfx.md)) as the authoring path until a Unity exporter lands.

## Open questions

| Topic | Status |
|-------|--------|
| Editor `.vrm` ScriptedImporter integration | TBD (UniVRM importer has no post-extension callback) |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |
