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

## AssetDatabase limits (UniVRMXT findings)

Optional consumer packages cannot patch the stock imported `.vrm` prefab after
`VrmScriptedImporter` finishes (`AddComponent` on the main asset fails; reimport rebuilds
the hierarchy).

**Current UniVRMXT workaround** (dual path):

- **Extended-UniVRM:** import hooks (Project Settings/VRM10 enable) → VFX on original `.vrm`
- **Stock UniVRM / hooks disabled:** sibling companion prefab `*.vrmxt.prefab`
- Runtime / Warudo: stock load, then `TryAttachFromGlb`
- VFX-only textures: second GLB image decode (texture enum hook still open)

Full write-up: [univrm-upstream-hooks.md](univrm-upstream-hooks.md).

## Open questions

| Topic | Status |
|-------|--------|
| Editor `.vrm` ScriptedImporter integration | Workaround: companion prefab; prefer upstream import callback — see [univrm-upstream-hooks.md](univrm-upstream-hooks.md) |
| VFX-only `textures[]` import | Workaround: re-read GLB; prefer texture enumeration hook |
| Unknown `specVersion` policy | TBD (shared with base spec) |
| Trigger / play mode | TBD |

## Related

- Spec: [VRMXT_vfx](../specs/vrmxt-vfx.md)
- Upstream hooks / AssetDatabase workaround: [univrm-upstream-hooks.md](univrm-upstream-hooks.md)
- UniVRMXT: https://github.com/miramocha/UniVRMXT
- [Blender VFX](blender-vfx.md)
