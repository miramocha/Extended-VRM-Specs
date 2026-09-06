---
title: Getting started in Blender
aliases:
  - Getting started
  - Blender setup
  - install VRMXT for Blender
tags:
  - extended-vrm
  - type/guide
  - implementation/blender
  - compatibility/vrm1
type: guide
status: draft
---

# Getting started in Blender

Install stock [VRM format **4.6.0** or later](https://github.com/saturday06/VRM-Addon-for-Blender/releases/tag/v4.6.0),
then VRMXT. Blender **4.2** through **&lt;5.3**.

VRMXT uses that add-on's VRM 1.0 user-extension hooks
(`Vrm1ImportUserExtension` / `Vrm1ExportUserExtension`). Builds older than 4.6.0
do not expose those classes.

| Package | Releases |
|---------|----------|
| VRM format 4.6.0+ | [VRM Add-on for Blender](https://github.com/saturday06/VRM-Addon-for-Blender/releases/tag/v4.6.0) |
| VRMXT | [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender/releases/) |

If you install from GitHub, download a `.zip` and do not unzip it. The Blender
Get Extensions catalog is fine when the listed VRM format version is **4.6.0**
or later.

## Install

1. **Edit → Preferences → Add-ons**.
2. Install VRM format 4.6.0+ (Get Extensions, or **Install from Disk** with the
   zip). Enable it. Confirm the add-on version is 4.6.0 or later.
3. **Install from Disk** again with the VRMXT zip. Enable **VRMXT Extensions**.

Install VRM format first. VRMXT will not load without it.
