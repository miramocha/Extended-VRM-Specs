---
title: VRM Posing Desktop VRMXT
aliases:
  - VRMPosingDesktop consumer
  - Posing Desktop VRMXT profile
tags:
  - extended-vrm
  - implementation/unity
  - implementation/optional-consumer
  - compatibility/vrm1
  - spec/materials
  - spec/vfx
type: guide
status: draft
---

# VRM Posing Desktop VRMXT

Future **consumer** profile for
[VRM Posing Desktop](https://store.steampowered.com/app/1895630/VRM_Posing_Desktop/)
(Steam app `1895630`, developer ELVNEKO). Stock host loads VRM; a VRMXT add-on would
attach `VRMXT_*` after load. No authoring UI and no VRMXT re-export from this host.

Related: [Warudo VRMXT](warudo-vrmxt.md), [UniVRMXT](univrm-vrmxt.md),
[Extended VRM Architecture](../architecture.md).

## Goal

After Posing Desktop loads a VRM 1.0 `.vrm`, attach supported `VRMXT_*` runtime
behavior (at minimum materials override and sprite particles) without replacing the
app's stock UniVRM import path.

| Item | Value |
|------|-------|
| Product | [VRM Posing Desktop](https://store.steampowered.com/app/1895630/VRM_Posing_Desktop/) |
| Steam app id | `1895630` |
| Role | Runtime consumer only (planned) |
| Stock VRM | App-bundled UniVRM |
| Extended | TBD plugin / inject path (not shipped) |
| Measured build | Local Steam install `VRM Posing Desktop` (2026-07-21) |

## Host baseline (measured)

Values from the installed player under `VrmPosingDesktop_Data/Managed/` and
`UnityPlayer.dll`:

| Item | Value | Source |
|------|-------|--------|
| UniVRM | `0.129.3` | `UniGLTF.PackageVersion` (`VERSION` / `VRM_VERSION` `UniVRM-0.129.3`) |
| UniGLTF | `2.65.3` | `UniGLTF.UniGLTFVersion` string in `UniGLTF.dll` |
| Assemblies present | `UniGLTF.dll`, `VRM10.dll`, `VRM10.MToon10.dll`, `VrmLib.dll`, `FastSpringBone10.dll` | Managed folder |
| Unity player | `2022.3.62f3` | `UnityPlayer.dll` version string |

Public Steam news still cites UniVRM `0.113.0` for app version 4.0.8 (2023-08-31).
Treat the Managed `PackageVersion` as the current pin; re-check after Steam updates.

## Compatibility vs Extended stack

| Host | UniVRM pin | Notes |
|------|------------|-------|
| VRM Posing Desktop (this profile) | `0.129.3` | Same package line as noted for VRM Live Viewer |
| Warudo runtime | `0.130.1` | [Warudo VRMXT](warudo-vrmxt.md) |
| Extended-UniVRM fork | `0.131.1` package line | Upstream `vrm-c/UniVRM` base; see fork remotes |

A Posing Desktop consumer MUST target the app's bundled UniVRM (`0.129.3` as of the
measured build), not the Extended-UniVRM authoring pin, unless the host ships a newer
UniVRM first.

## Architecture fit

| Architecture rule | Posing Desktop approach |
|-------------------|-------------------------|
| Stock VRM load unchanged | Keep ELVNEKO UniVRM import |
| Optional Extended package | Post-load attach only |
| No `extensionsRequired` | Missing VRMXT → stock pose/view still works |
| Consumer only | No VRMXT export from this app |

## Open questions

| Topic | Status |
|-------|--------|
| Distribution (Workshop mod, sidecar DLL, official partner hook) | TBD |
| Load seam (when bytes / `Vrm10Instance` become available) | TBD |
| Which `VRMXT_*` extensions to claim first | TBD; materials + sprite particle likely |
| Unity / UniVRM drift vs Extended-UniVRM `0.131.x` | Re-measure after each host update |

## Non-goals

- Forking or replacing Posing Desktop's UniVRM assemblies as the default path
- Authoring or exporting `VRMXT_*` from Posing Desktop
- Treating the 2023 Steam `0.113.0` announcement as the current pin
