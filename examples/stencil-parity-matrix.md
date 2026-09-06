---
title: MToonXT stencil parity matrix
tags:
  - extended-vrm
  - type/example
  - spec/materials
type: example
status: draft
---

# MToonXT stencil parity matrix

[Watch the Blender / Unity comparisons](https://tdw46.github.io/BVT-Stencil-Matrix/).

This non-normative, 13-scenario matrix accompanies the
[portable relationship contract](../specs/extensions/materials/vrmxt-materials-mtoonxt/stencil-relationships.md).
It records authoring intent, controls, implementation constraints and evidence as of
2026-09-06. It is not an expansion of the JSON schema or a claim that every engine
implements every mode. The relationship graph remains **additive** to legacy
per-material stencil authoring; a supporting consumer applies the authoritative graph
once, not again as a second shorthand effect.

## Reading the settings

Vectors below use `[T, I, O, S, R, W, D]`, where `1` means true.

| Key | Portable property |
| --- | --- |
| T | `showWritersThroughOccluders` |
| I | `writersOnlyInsideReaders` |
| O | `writersOnlyOutsideReaders` |
| S | `writersSelfOcclude` |
| R | `ignoreOccludedReaderAreas` |
| W | `writersWriteDepth` |
| D | `readersWriteDepth` |

Unless noted, `comparison=outside`, both depth tests are `lessEqual`, and
`writersWriteColor=true`. These defaults do not imply opaque color: source MToon
alpha mode, alpha texture, base alpha and double-sidedness remain separate inputs.
Disabling depth writes does not enable transparency or disable the depth test.

## Scenarios and focused controls

| ID | Configured showcase | Flags | Exception / control | Distinguishing observation |
| --- | --- | --- | --- | --- |
| M01 | Invisible bangs reveal | `[0,0,0,1,1,0,1]` | Writer color **off**; control disables stencil and omits the invisible helper | Hair is cut by a moving colorless mask; it is not a visible overlay. |
| M02 | Facial features through hair | `[1,0,0,1,1,1,1]` | Control disables stencil | Features show through reader-qualified coverage; ordinary depth remains outside it. |
| M03 | Face-only anime hair shadow | `[0,1,0,1,1,1,1]` | Control disables stencil | A hair-derived shadow decal is confined to face pixels. This is a decal demonstration, not a fresh cast-shadow test. |
| M04 | Animated lens-clipped visor HUD | `[1,1,0,1,1,1,1]` | Stencil off / on | Oversized, animated HUD components are visible only within the stationary curved visor lens. |
| M05 | Orbiting spirit ribbons | `[0,0,1,1,1,1,1]` | Control disables stencil | Writer ribbons avoid the avatar while retaining ordinary depth against other objects. |
| M06 | Negative-space power-up | `[1,0,1,1,1,1,1]` | Control sets T to 0 | Ribbons avoid **all** scene silhouettes, including an unrelated talisman, and remain on clear background. |
| M07 | Surrounding magical aura | `[1,0,0,0,1,0,1]` | Control sets S and W to 1 | Translucent wisps/embers remain layered across reader pixels without losing reader color. |
| M08 | Anatomical through-cover X-ray | `[1,0,0,1,0,1,1]` | Control sets R to 1 (M02) | Skeleton remains visible through an unrelated opaque shield **only** on the full body-reader silhouette. |
| M09 | Feather-crest flight visor | `[0,0,0,1,1,0,1]` | Control sets W to 1 | Rear amber HUD passes the cyan crest when writer depth is off; remaining lens still writes depth. |
| M10 | Crystal-iris AR visor | `[0,0,0,1,1,1,0]` | Control sets D to 1 | Rear cyan HUD passes the violet lens when reader depth is off; crystal iris still blocks it. |
| A01 | Ice-silver character transformation | `[0,0,0,1,1,1,1]` | `comparison=inside`; control uses `outside` | Complementary regions of a detailed character recolor switch across a feather-edged veil. |
| A02 | Amber spirit familiar reliquary | `[0,0,0,1,1,1,1]` | `writerDepthTest=always`; control uses `lessEqual` | A miniature writer projection bypasses unrelated cover **outside** reader coverage. |
| A03 | Feather-shutter spirit projection | `[0,0,0,1,1,1,1]` | `readerDepthTest=always`; control uses `lessEqual` | Reader color bypasses a petal screen while an ordinary-depth feather writer still cuts it. |

M09 shares M01's seven flags but keeps writer color on and introduces a later
transparent witness surface. M09/M10 test **depth ownership**, not M04's lens clipping.
M08 changes eligibility of hidden reader coverage; it does not reveal reader color.
A02/A03 bypass the writer/reader color depth test itself, so they are not synonyms
for M02 or M08. M07 intentionally changes two flags together: it is not a factorial
test isolating self-occlusion from depth publication.

## Unity Built-in reproduction profile

The recorded consumer is UniVRMXT in Unity 2022.3.22f1, Built-in, Linear color space.
Queues below describe the first compiled relationship; reference allocation and
later queue offsets are implementation state, not serialized specification values.
Pass and depth failures retain stencil (`Keep`).

| Mode | Reader / writer plan |
| --- | --- |
| M01 | Colorless writer q2451 Always/Replace, LEqual, depth off; reader q2452 NotEqual/Keep, LEqual, depth on. |
| M02 | Reader q2451 Always/Replace; base writer q2452 NotEqual/Keep, LEqual; reader-qualified writer overlay q2453 Equal/Keep, Always. Depth on for all three. |
| M03 / M04 | Reader q2451 Always/Replace, LEqual; writer q2452 Equal/Keep. M03 writer uses LEqual; M04 uses Always. Depth on. |
| M05 | Reader mask then NotEqual writer with ordinary depth. |
| M06 | Colorless non-writer scene-coverage pass, then background-qualified writer. Do not reveal the coverage pass as a visible material. |
| M07 | Native-lit, complementary reader-excluded / reader-qualified writer passes; writer depth off, overlay Cull Off. Keep reader color and source alpha. |
| M08 | Colorless full-reader-silhouette coverage plus native-lit writer presentation. Ordinary writer depth remains outside reader coverage. |
| M09 / M10 | Writer q2451 Always/Replace; reader q2452 NotEqual/Keep; both LEqual. M09 disables only writer depth, M10 only reader depth. HUD q3000, depth off; frame q2000. |
| A01 | Writer Always/Replace, reader Equal/Keep, both LEqual and depth on. Original-color foundation draws late; both character copies use BLEND with transparent depth write. |
| A02 | Writer Always/Replace with ZTest Always; reader NotEqual/Keep with LEqual. Both depth on. |
| A03 | Writer Always/Replace with LEqual; reader NotEqual/Keep with ZTest Always. Both depth on. |

Colored auxiliary passes use extra material/submesh slots on the **original renderer**
so native lights and received shadows are initialized. Only colorless coverage uses
retained command buffers. Do not fix shadows by substituting unlit manual draws,
duplicating renderer objects or expanding bounds. A skinned mesh is positioned by its
bones/bindposes; moving its renderer transform is not a reliable geometry test.

The M02 closed-box recipe uses Cull Back on the auxiliary overlay with S enabled;
its duplicate ShadowCaster is disabled and the base remains the caster. It does not
prove a nearest-surface solution for open, concave or layered translucent writers.
Source double-sidedness and the active pass's culling must be inspected separately:
the current A02/A03 exports say `doubleSided=false`, while their active Unity stencil
variants use Cull Off. These camera-locked examples do **not** certify culling parity.

## Capture contract and progress

M01–M03 and M05–M10/A01–A03 have 24 configured/control exports, 48 real capture
streams (96 frames, 24 fps), and 38 encoded comparison videos. M04 retains its separate
approved animated-visor recordings. All 24 graph/material-target transport checks
passed; the batch's 38 videos and 147 HTML references passed local validation.

Camera framing, clip planes, posed geometry, timeline, white directional lighting,
black ambient and solid background are matched. Coordinate conversion is explicit;
the Blender Sun surface-to-light direction is opposite its emission direction.
Matching these inputs does not make different shader/rasterization implementations
bit-identical. Sampled RGB differences are measurements, not a visual pass threshold.
VRM carries geometry/materials/morph targets; a **separate companion timeline** drives
the showcase animation. Do not describe these clips as native VRM animation export.

| Scope | Current evidence / acceptance |
| --- | --- |
| M01–M03 | Fresh matched pairs recorded 2026-09-06; new recordings await individual review. Older Blender approvals remain attached to the older media. |
| M02 supplemental | Mira Bunny closed-box native-lighting/self-occlusion setup user-approved; not a blanket topology or all-angle approval. |
| M04 | Animated visor HUD and paired recordings user-approved. Supersedes the earlier unfinished visor/shadow proposal. |
| M05–M06 | Recorded; broad positive batch feedback, no separate exhaustive conformance sign-off. |
| M07 | Corrected transparent blend and replacement magical aura explicitly user-approved. |
| M08–M10, A01–A03 | Redesigned, exported, imported and recorded; retained as review candidates, not blanket conformance passes. |

The A02/A03 projections use a single atlas, far-to-near face ordering and vertical
bobbing from a locked camera. They do not demonstrate arbitrary-camera self-occlusion.
M09/M10/A03 ornaments have no generated MToon outlines; those captures do not newly
validate outline or cast-shadow behavior. M05/M06 use a single textured writer;
earlier multi-writer interference is not claimed resolved by that fixture change.
Compound URP coverage requires an equivalent renderer feature and was not tested.
Separate UniVRM spring-bone subasset identity warnings remain open; stencil checks
do not validate physics or collider references after reimport.

## Review assets and attribution

The [published matrix](https://tdw46.github.io/BVT-Stencil-Matrix/) keeps controls,
paired videos, content-hash cache revisions and row-specific limitations together.
Visible videos autoplay muted and loop; off-screen videos pause. Open comparison
links use the standalone looping player. Raw client `.blend`/VRM assets and source
texture atlases are not part of the publication.

M08 uses adapted skeletal anatomy from Z-Anatomy / BodyParts3D. Attribution and
license notices accompany the review site; this is a stylized graphics fixture, not
a medically validated anatomical model. Character rights are separate from anatomy
licensing and are not granted by the specification or demonstration.
