---
title: Getting started in Unity
aliases:
  - install UniVRMXT
  - UPM UniVRMXT
tags:
  - extended-vrm
  - type/guide
  - implementation/unity
  - compatibility/vrm1
type: guide
status: draft
---

# Getting started in Unity

Install the Unity packages from git URLs. Minimum Unity **2022.3 LTS**.

Use these URLs, not [vrm-c/UniVRM](https://github.com/vrm-c/UniVRM) Releases. UniVRMXT
needs the Extended UniVRM fork.

These packages are not on Unity’s registry.

| Package | Git URL |
|---------|---------|
| Extended UniVRM (glTF) | `https://github.com/miramocha/Extended-UniVRM.git?path=/Packages/UniGLTF` |
| Extended UniVRM (VRM 1.0) | `https://github.com/miramocha/Extended-UniVRM.git?path=/Packages/VRM10` |
| UniVRMXT | `https://github.com/miramocha/UniVRMXT.git` |

## Install

1. **Window → Package Manager**.
2. **+ → Add package from git URL…**
3. Paste the Extended UniVRM (glTF) URL, then the VRM 1.0 URL.
4. Paste the UniVRMXT URL.

Install Extended UniVRM first. UniVRMXT will not resolve without it.
