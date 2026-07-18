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
[UniVRMXT](https://github.com/miramocha/UniVRMXT) (`com.miramocha.univrmxt`). UniVRM
source changes are not required.

VRM 1.0 only. The extension is optional: stock UniVRM load MUST succeed when UniVRMXT
is absent or when `VRMXT_vfx` is missing.

## Package

| Item | Value |
|------|-------|
| UPM id | `com.miramocha.univrmxt` |
| Host | [Extended-UniVRM](https://github.com/miramocha/Extended-UniVRM) / UniVRM `0.131.1`+ |
| Unity | `2022.3` |

## Import seam

UniVRM has no general root-extension registry. UniVRMXT foundation:

1. Parse root `extensions.VRMXT_vfx` from glTF JSON (`specVersion` `"1.0"`).
2. Skip invalid emitters per the base spec.
3. After `Vrm10.LoadGltfDataAsync` (or equivalent), map `emitters[].node` through
   `RuntimeGltfInstance.Nodes`.
4. Attach portable emitter data on a UniVRMXT component / ScriptableObject.

Unresolved nodes skip that emitter only.

## Runtime behavior (foundation)

MVP stores parsed emitter data. Native `ParticleSystem` mapping, billboard materials,
and texture policy are **TBD**.

## Export

Export of authored VFX from Unity is **TBD**. Prefer Blender
([Blender VFX](blender-vfx.md)) as the authoring path until a Unity exporter lands.

## Open questions

| Topic | Status |
|-------|--------|
| `ParticleSystem` field mapping | TBD |
| Billboard / texture material | TBD |
| Editor `.vrm` ScriptedImporter integration | TBD (UniVRM importer has no post-extension callback) |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |
