---
title: VRMXT_springBone_override
aliases:
  - spring bone override
  - VRM spring bone runtime override
tags:
  - extended-vrm
  - spec/spring-bone
  - format/gltf-extension
  - compatibility/vrm1
  - implementation/optional-consumer
  - implementation/unity
type: specification
status: draft
---

# VRMXT_springBone_override

Root glTF extension for selecting an optional engine-specific simulation backend for
VRM 1.0 spring definitions. `VRMC_springBone` remains the portable source and fallback.

The first target use case translates VRM spring chains to MagicaCloth2 BoneCloth or
BoneSpring at runtime. Unsupported consumers continue using their normal
`VRMC_springBone` implementation.

## Scope

| Item | Value |
|------|-------|
| Extension name | `VRMXT_springBone_override` |
| Target | VRM 1.0 (`VRMC_vrm` 1.0) only |
| Attachment | Root `extensions.VRMXT_springBone_override` |
| Source data | Root `extensions.VRMC_springBone` |
| Engine entries | `overrides[]` |
| UniVRM / stock importer | no required change |
| Consumer package | optional; replaces simulation backend when supported |

## Normative requirements

1. Files that use this extension MUST list `VRMXT_springBone_override` in
   `extensionsUsed`.
2. The extension object MUST appear at root `extensions.VRMXT_springBone_override`.
3. The file MUST also contain a valid root `VRMC_springBone` extension.
4. The extension object MUST contain `specVersion` with value `"1.0"` for this draft.
5. The extension object MUST contain a non-empty `overrides` array.
6. Each override MUST contain a case-sensitive `engine` string and a non-empty
   `bindings` array.
7. A file MUST NOT contain more than one override for the same engine.
8. Each binding MUST contain `spring`, a zero-based index into
   `VRMC_springBone.springs`, and a non-empty engine-specific `backend` identifier.
9. One engine override MUST NOT contain more than one binding for the same `spring`.
10. Consumers MUST ignore unknown engines, backends, modes, and properties.
11. If an override or binding cannot be applied, the consumer MUST preserve normal
    `VRMC_springBone` behavior. It MAY fall back for that spring when its runtime supports
    mixed backends; otherwise it MUST fall back for the whole model.
12. Files using this fallback design MUST NOT list `VRMXT_springBone_override` in
    `extensionsRequired`.

## Extension properties

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `specVersion` | string | yes | Extension version; currently `"1.0"` |
| `overrides` | object[] | yes | Non-empty engine override list |
| `overrides[].engine` | string | yes | Case-sensitive target engine |
| `overrides[].bindings` | object[] | yes | Per-spring backend selections |
| `bindings[].spring` | integer | yes | Index into `VRMC_springBone.springs` |
| `bindings[].backend` | string | yes | Engine-specific simulation backend |
| `bindings[].mode` | string | no | Backend-specific simulation mode |
| `bindings[].preset` | string | no | Backend-specific preset identifier |
| `bindings[].parameters` | object | no | Backend-specific parameters; schema TBD |

Engine names, backend registry, preset resolution, and `parameters` schemas are **TBD**.

## Attachment example

Non-normative. Engine, backend, and preset identifiers are provisional.

```json
{
  "extensionsUsed": [
    "VRMC_vrm",
    "VRMC_springBone",
    "VRMXT_springBone_override"
  ],
  "extensions": {
    "VRMC_springBone": {
      "specVersion": "1.0",
      "colliders": [],
      "colliderGroups": [],
      "springs": [
        {
          "name": "Hair",
          "joints": [
            {
              "node": 12,
              "stiffness": 1.0,
              "gravityPower": 0.3,
              "gravityDir": [0.0, -1.0, 0.0],
              "dragForce": 0.4,
              "hitRadius": 0.02
            }
          ]
        },
        {
          "name": "Chest",
          "joints": [
            {
              "node": 24
            }
          ]
        }
      ]
    },
    "VRMXT_springBone_override": {
      "specVersion": "1.0",
      "overrides": [
        {
          "engine": "unity",
          "bindings": [
            {
              "spring": 0,
              "backend": "magicaCloth2",
              "mode": "boneCloth",
              "preset": "hair-soft"
            },
            {
              "spring": 1,
              "backend": "magicaCloth2",
              "mode": "boneSpring",
              "preset": "body-medium"
            }
          ]
        }
      ]
    }
  }
}
```

## MagicaCloth2 backend profile

`magicaCloth2` identifies an adapter that builds MagicaCloth2 components from
`VRMC_springBone`. It does not require MagicaCloth2 support from UniVRM.

| Mode | Intended use |
|------|--------------|
| `boneCloth` | Hair, skirts, ribbons, wings, and accessory chains |
| `boneSpring` | Localized spring motion such as chest or soft-body bone movement |

BoneCloth is the closer default for ordinary VRM spring chains. BoneSpring MUST be
selected explicitly because its translation-based spring behavior cannot be inferred
reliably from VRM spring data.

The adapter SHOULD:

1. Build one MagicaCloth component per binding or compatible spring group.
2. Derive the simulated transforms from the referenced VRM spring's joints.
3. Assign fixed, moving, and invalid transform attributes so unrelated descendants are
   excluded.
4. Convert supported VRM sphere and capsule collider groups to Magica colliders.
5. Start the Magica runtime only after its components and constraints are configured.
6. Fall back to the stock VRM runtime for the affected spring or whole model when
   conversion fails.

## VRM-to-Magica mapping

The systems use different solvers. The following table identifies related concepts; it
does not define numeric conversion formulas.

| VRMC_springBone | MagicaCloth2 |
|-----------------|---------------|
| `springs[i].joints[].node` | Bone transforms and vertex attributes |
| First joint parent / chain anchor | BoneCloth or BoneSpring fixed root |
| `stiffness` | Angle-restoration stiffness approximation |
| `dragForce` | Damping approximation |
| `gravityPower`, `gravityDir` | Gravity magnitude and direction |
| `hitRadius` | Particle or collision-radius approximation |
| Joint limit extension | Angle-limit constraints where representable |
| Sphere / capsule collider groups | Magica sphere / capsule colliders |
| `center` | Inertia reference; exact mapping TBD |

Numeric conversion curves, depth-dependent parameters, plane/inside collider handling,
and Magica-specific constraints remain **TBD**. Implementations MUST NOT claim physically
equivalent results unless those conversions are specified and tested.

## UniVRM integration

A separate Unity package can implement this backend without modifying UniVRM:

1. Implement `IVrm10SpringBoneRuntime`.
2. Pass it through the `springboneRuntime` argument of `Vrm10.Load*Async`, or provide it
   through `IVrm10SpringBoneRuntimeProvider`.
3. In `InitializeAsync(Vrm10Instance, IAwaitCaller)`, inspect
   `Vrm10Instance.SpringBone`, resolve the override, and construct MagicaCloth2
   components.
4. Let MagicaCloth2 update converted transforms. A hybrid runtime MUST prevent
   FastSpringBone and MagicaCloth2 from simulating the same spring.
5. Dispose or stop generated runtime state through the custom runtime lifecycle.

UniVRM still constructs its spring joint and collider components during import. They
remain source/fallback data because UniVRM has no spring-construction factory equivalent
to `IMaterialDescriptorGenerator`.

## References

- [VRM 1.0 Spring Bone](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_springBone-1.0)
- [MagicaCloth2 cloth types](https://magicasoft.jp/en/mc2_magicacloth_basic/)
- [MagicaCloth2 runtime construction](https://magicasoft.jp/en/mc2_runtime_build/)
- [MagicaCloth2 BoneSpring guide](https://magicasoft.jp/en/mc2_bonespring_startguide/)

## Related

- [VRMXT_materials_override](../materials/vrmxt-materials-override.md)
- [VRMXT_sprite_particle](../vfx/vrmxt-sprite-particle.md)
- [VRMXT_lattice](../deformation/vrmxt-lattice.md) (research draft; may reuse override-engine pattern)

## Open questions

- [ ] Stable engine and backend identifier registry
- [ ] Package discovery metadata for optional backends
- [ ] Numeric parameter conversion formulas
- [ ] Collider conversion for planes, inside colliders, and unsupported shapes
- [ ] Preset identifier ownership and portability
- [ ] Whether multiple VRM springs may share one MagicaCloth component
- [ ] Export rules for Blender and other authoring tools
- [ ] Schema for backend-specific `parameters`
