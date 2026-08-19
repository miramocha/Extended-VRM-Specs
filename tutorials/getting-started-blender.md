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

Install the two Blender packages from GitHub Releases. Blender **4.2** through
**&lt;5.3**.

Use these zips, not the stock VRM add-on from Blender's extension site. VRMXT
needs the Extended VRM fork.

| Package | Releases |
|---------|----------|
| Extended VRM (VRM 1.0 import/export) | [Extended-VRM-Addon-for-Blender](https://github.com/miramocha/Extended-VRM-Addon-for-Blender/releases) |
| VRMXT | [VRMXT-Extension-for-Blender](https://github.com/miramocha/VRMXT-Extension-for-Blender/releases/) |

Download the latest `.zip` from each page. Do not unzip it.

## Install

1. **Edit → Preferences → Add-ons**.
2. Open the dropdown in the top right and choose **Install from Disk**.
3. Select the Extended VRM zip. Turn the add-on **on** if it is not already
   (**VRM (Extended)** / VRM format).
4. **Install from Disk** again with the VRMXT zip. Enable **VRMXT Extensions**.

Install Extended VRM first. VRMXT will not load without it.
