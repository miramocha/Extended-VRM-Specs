---
title: VRMXT_materials_mtoonxt stencil relationships
aliases:
  - MToonXT stencil relationship graph
  - portable stencil presentation
tags:
  - extended-vrm
  - spec/materials
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
type: specification
status: draft
---

# VRMXT_materials_mtoonxt stencil relationships

Portable, root-level stencil presentation for relationships that cannot be expressed
by one per-material [`stencil.op`](stencil.md). The relationship graph records visual
intent. It does not serialize Unity shader property names, a numeric stencil reference,
or an engine command buffer.

Use the per-material shorthand for ordinary `write` / `inside` / `insideOverlay` /
`outside` clips. Use `stencilRelationships` when the requested result needs more than
one subject pass, a full reader silhouette, background-only presentation, independent
depth publication, or an authored depth comparison.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_materials_mtoonxt` |
| Parent | `extensions.VRMXT_materials_mtoonxt` on the glTF root |
| Field | `stencilRelationships` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) |
| Material references | zero-based `materials[]` indices |

The root object MUST contain `specVersion: "1.0"`. A file that uses this object MUST
list `VRMXT_materials_mtoonxt` in `extensionsUsed` and MUST NOT list it in
`extensionsRequired`.

## Relationship schema

Every array element describes one writer/reader relationship. Defaults are part of the
file contract so exporters MAY omit properties whose value equals the default.

| Property | Type | Required | Default | Meaning |
|----------|------|----------|---------|---------|
| `writers` | integer array | yes | — | Non-empty, unique material indices presented as the relationship subject. |
| `readers` | integer array | yes | — | Non-empty, unique material indices whose screen coverage controls the relationship. |
| `comparison` | string | no | `outside` | Reader test for the ordinary writer-first relationship: `inside` or `outside`. |
| `showWritersThroughOccluders` | boolean | no | `false` | Ignore intervening scene depth on reader-qualified writer pixels while retaining ordinary depth elsewhere. |
| `writersOnlyInsideReaders` | boolean | no | `false` | Present writers only inside the reader screen silhouette. |
| `writersOnlyOutsideReaders` | boolean | no | `false` | Present writers only outside the reader screen silhouette. With show-through enabled, material silhouettes reject the writer and clear background remains eligible. |
| `writersSelfOcclude` | boolean | no | `true` | Resolve each writer to its nearest authored face before final color presentation. |
| `ignoreOccludedReaderAreas` | boolean | no | `true` | Use only reader pixels that pass ordinary scene depth. `false` uses the reader's complete projected silhouette without forcing reader color through occluders. |
| `writersWriteColor` | boolean | no | `true` | Publish accepted writer color. `false` keeps the writer colorless while retaining its stencil and optional depth effects. |
| `writersWriteDepth` | boolean | no | `true` | Publish accepted writer depth independently of writer color. |
| `readersWriteDepth` | boolean | no | `true` | Publish accepted reader depth after color presentation. |
| `writerDepthTest` | string | no | `lessEqual` | Portable depth comparison for writer fragments. |
| `readerDepthTest` | string | no | `lessEqual` | Portable depth comparison for reader fragments. |

`writersOnlyInsideReaders` and `writersOnlyOutsideReaders` MUST NOT both be `true`.
A material index MUST be in range and MUST NOT appear in both arrays of the same
relationship. Unknown or invalid relationship entries are skipped individually.
Exporters SHOULD combine relationships that have the same writer set and identical
presentation fields by unioning their reader arrays. Consumers MUST treat such equivalent
rows as one relationship so one writer material is not assigned competing stencil
references.

Depth comparisons are `never`, `less`, `equal`, `lessEqual`, `greater`, `notEqual`,
`greaterEqual`, and `always`. They describe the comparison result, not an engine enum
number. A consumer maps them to its local API.

## Presentation requirements

The following requirements are stated as pixels, not as a required render-pass
implementation.

1. With both `writersOnly*` properties false, writers use ordinary depth outside reader
   pixels. If `showWritersThroughOccluders` is true, writer color MUST also be presented
   on qualified reader pixels even when closer unrelated depth exists.
2. `writersOnlyInsideReaders` MUST reject writer pixels over clear background and over
   non-reader material silhouettes. `showWritersThroughOccluders` changes only depth
   acceptance inside the reader silhouette.
3. `writersOnlyOutsideReaders` MUST reject writer pixels inside the reader silhouette.
   When `showWritersThroughOccluders` is false, ordinary-depth writer pixels MAY remain
   visible over clear background. When it is true, writer color MUST be restricted to
   clear background: reader and non-reader material silhouettes both reject it.
4. `ignoreOccludedReaderAreas: false` uses the full posed reader silhouette. A consumer
   MUST NOT reveal reader color merely to build that silhouette.
5. `writersSelfOcclude: false` MUST preserve the authored face presentation even when
   multiple writer faces overlap. `writersWriteDepth` remains independent; enabling it
   MUST NOT silently re-enable self-occlusion during color presentation.
6. `writersWriteColor: false` MUST suppress writer body and outline color while preserving
   the relationship's stencil writes. `writersWriteDepth` independently controls whether
   those accepted writer fragments publish depth. This supports invisible avatar masks,
   such as a moving control plane that reveals or hides selected hair materials.
7. Body and outline passes that participate in a relationship MUST use the same semantic
   relationship unless the file also supplies a valid per-material `outlineStencil`
   override.

## Compatibility with per-material shorthand

Exporters SHOULD also emit equivalent per-material `stencil` objects when one relationship
can be represented exactly by the shorthand. This helps older consumers. The root
relationship is authoritative for every `(writers, readers)` pair it names. A supporting
consumer MUST NOT apply both representations as two independent effects.

The following mappings are exact shorthand fallbacks:

| Relationship | Per-material shorthand |
|--------------|------------------------|
| Default Outside, stock depth and publication | each writer `write`; each reader `outside` targeting writers |
| Default Inside, stock depth and publication | each writer `write`; each reader `inside` targeting writers |
| Writers only inside readers | each reader `write`; each writer `inside` targeting readers |
| Writers only inside readers plus show-through | each reader `write`; each writer `insideOverlay` targeting readers |
| Writers only outside readers without show-through | each reader `write`; each writer `outside` targeting readers |

Relationships with `writersWriteColor: false` and other combinations not listed above
MUST NOT be approximated by a misleading shorthand.

## Non-normative Unity mapping

The [13-scenario parity matrix](../../../../examples/stencil-parity-matrix.md)
maps every presentation control to a distinct showcase and focused control variant.
Its runtime recipes and recorded results are non-normative implementation evidence,
not new schema fields or proof that every consumer satisfies every requirement.

Alpha blending, culling, stencil qualification and depth publication are separate
concerns. In particular, `writersWriteDepth: false` MUST NOT force opaque color.
For reader-qualified show-through blending (M07), the consumer MUST retain reader
color beneath translucent writer color. Split ordinary-depth and show-through writer
passes must use complementary coverage, avoiding duplicate alpha contributions from
those two presentation passes at the same pixel. This does not prohibit intentionally
layered writer faces when self-occlusion is disabled or change ordinary reader clipping.
Disabling `readersWriteDepth` does not disable its depth test. `readerDepthTest: always`
can expose reader color; `ignoreOccludedReaderAreas: false` only broadens the mask
used to qualify writer presentation. These are deliberately different controls.

`writersSelfOcclude: true` describes the intended nearest-face result; a consumer's
back-face-culling approximation is not general conformance for arbitrary topology.
Implementations SHOULD disclose restrictions such as camera-locked ordering,
unavailable render phases, unsupported alpha ordering or active-pass culling changes.

An implementation can compile the relationship into ordinary stencil passes:

- visible reader mask: `Comp Always`, `Pass Replace`
- reader-qualified subject: `Comp Equal`, `Pass Keep`
- reader-excluded subject: `Comp NotEqual`, `Pass Keep`
- all pass failures: `Keep`

Unrestricted show-through uses an ordinary-depth `NotEqual` subject pass followed by an
`Equal` depth-ignore subject pass. Background-only presentation uses a colorless full-scene
coverage prepass before the `NotEqual` subject. Full reader silhouettes use a colorless
reader-only depth-ignore prepass. These are implementation examples; numeric refs, command
buffer events, and shader property names are local state.

## Example

Non-normative. Writer `1` uses ordinary depth over background, shows through intervening
geometry only on reader `0`, self-occludes, and publishes depth.

```json
{
  "extensionsUsed": ["VRMXT_materials_mtoonxt"],
  "extensions": {
    "VRMXT_materials_mtoonxt": {
      "specVersion": "1.0",
      "stencilRelationships": [
        {
          "writers": [1],
          "readers": [0],
          "showWritersThroughOccluders": true
        }
      ]
    }
  }
}
```

## Related

- [Scenario settings, Unity profile and validation limits](../../../../examples/stencil-parity-matrix.md)
- [VRMXT_materials_mtoonxt](README.md)
- [Per-material stencil shorthand](stencil.md)
- [VRMXT Conformance](../../../core/vrmxt-conformance.md)
