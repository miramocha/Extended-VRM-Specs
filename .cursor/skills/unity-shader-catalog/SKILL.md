---
name: unity-shader-catalog
description: >-
  Extract Unity ShaderLab Properties and scaffold VRMXT materials-override
  catalog JSON. Use when pinning a Unity shader revision, updating lilToon or
  Poiyomi catalogs under references/catalogs/data/, comparing opaque/cutout/
  transparent property blocks, or building curated catalog JSON from upstream
  .shader sources.
---

# Unity shader catalog

Build / refresh non-normative catalog JSON for
[Materials Override Catalogs](../../../references/materials-override-catalogs.md).
Human index: [Maintaining catalogs](../../../references/catalogs/maintaining-catalogs.md).

Curated property **lists** stay human (family `.md`). Scripts fill **types** and
**defaults** from ShaderLab. Do not put `.cursor/**` paths in family/reference notes;
link those notes to the maintaining page instead.

## When to use

- New Unity family catalog (lilToon, Poiyomi, …)
- Pin bump: re-extract defaults, diff variants, regenerate JSON
- Check cutout/transparent vs opaque property parity

## Do not

- Dump full `Properties` block into catalog JSON
- Auto-mark `common: true` (read family markdown tables)
- Add `hdrp` to `supportedVariants` without smoke test + doc update
- Edit normative `specs/extensions/materials/vrmxt-materials-override.md` for catalog-only work

## Workflow

1. **Pin** upstream tag/commit; record on family page (`references/catalogs/…`).
2. **Curate** `displayName` / `common` / toggle policy in a curated JSON (see
   [examples/liltoon-opaque.curated.json](examples/liltoon-opaque.curated.json)).
3. **Parse** ShaderLab (sanity / explore):
   ```powershell
   python .cursor/skills/unity-shader-catalog/scripts/parse_shaderlab_props.py `
     --github "lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader" `
     --names "_Color,_UseShadow,_RimFresnelPower"
   ```
4. **Scaffold** catalog JSON:
   ```powershell
   python .cursor/skills/unity-shader-catalog/scripts/scaffold_catalog_json.py `
     --curated .cursor/skills/unity-shader-catalog/examples/liltoon-opaque.curated.json `
     --github "lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader" `
     -o references/catalogs/data/unity-liltoon.json
   ```
5. **Diff** variants (expect identical curated decls for lilToon 2.3.4):
   ```powershell
   python .cursor/skills/unity-shader-catalog/scripts/diff_shader_props.py `
     --left "github:lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader" `
     --right "github:lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts_cutout.shader" `
     --names "_Color,_Cutoff,_UseShadow,_ShadowBorder"
   ```
6. Copy scaffold output for each `shaderName` (change curated `displayName` /
   `shaderName`); update family note, `catalogs/data/README.md`, catalogs index
   Status. Deslop edited prose.

## Curated JSON shape

| Field | Required | Meaning |
|-------|----------|---------|
| `displayName` | yes | Dropdown label |
| `shaderName` | yes | Exact `Shader.Find` string → `material.id` |
| `properties[]` | yes | `{ name, displayName, common }` (+ optional `type` / `default` override) |
| `defaultVariant` / `supportedVariants` | for shipped catalogs | RP filter only |
| `enableToggles` | no | Names forced to catalog `default: 1` (Add Common Props) |
| `omitTextureDefaults` | no | Default `true` — no `default` on `texture` rows |

`displayName` in curated JSON is the catalog UI label. ShaderLab often uses
localization keys (`sColor`); do not copy those blindly.

## Type mapping

| ShaderLab | Catalog `type` |
|-----------|----------------|
| `Color` | `vector` (`vectorSize` 4) |
| `2D` / `Cube` | `texture` |
| `Float` / `Range` / `Int` | `scalar` |
| `[lilToggle]` Int | `scalar` 0/1 — not `shaderFeature` unless real keyword |

Omit `_DummyProperty` and `HideInInspector` chrome unless curated list names them.

## Scripts

| Script | Role |
|--------|------|
| `scripts/parse_shaderlab_props.py` | List props + defaults from `.shader` / GitHub raw |
| `scripts/scaffold_catalog_json.py` | Curated + ShaderLab → catalog JSON |
| `scripts/diff_shader_props.py` | Compare two shaders |
| `scripts/generate_liltoon_curated.py` | lilToon section extract → curated JSON (359 props @ 2.3.4) |
| `scripts/shaderlab.py` | Shared library (import only) |

`--github REPO@REF:PATH` fetches
`https://raw.githubusercontent.com/REPO/REF/PATH`.

## Pitfalls

- `Range(…)` nested parens break naive `[^)]+` type capture — use these scripts
- Attributes may sit on same line as the property (`[PowerSlider(3.0)]_Rim…`)
- ShaderLab toggle default is often `0`; catalog may want `1` via `enableToggles`
- One catalog file per `shaderName` (opaque ≠ cutout ≠ transparent)

## Related

- Schema: [materials-override-catalogs.md](../../../references/materials-override-catalogs.md)
- lilToon family: [unity-liltoon.md](../../../references/catalogs/unity-liltoon.md)
