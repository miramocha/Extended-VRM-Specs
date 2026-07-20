#!/usr/bin/env python3
"""Build lilToon curated JSON from ShaderLab section headers @ pin."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shaderlab import (  # noqa: E402
    PROP_LINE_RE,
    extract_properties_block,
    fetch_text,
    github_raw_url,
    parse_properties,
)

PIN = "2.3.4"
SHADER_PATH = "Assets/lilToon/Shader/lts.shader"

# Sections to ship in catalog (authoring features; not render-state chrome).
INCLUDE_SECTIONS = {
    "Base",
    "Main",
    "Main2nd",
    "Main3rd",
    "Alpha Mask",
    "NormalMap",
    "NormalMap 2nd",
    "Anisotropy",
    "Backlight",
    "Shadow",
    "Rim Shade",
    "Reflection",
    "MatCap",
    "MatCap 2nd",
    "Rim",
    "Glitter",
    "Emmision",
    "Emmision2nd",
    "Parallax",
    "Distance Fade",
    "AudioLink",
    "Dissolve",
    "ID Mask",
    "UDIM Discard",
    "For Multi",
    "VRChat",
}

EXCLUDE_SECTIONS = {
    "Dummy",
    "Outline",
    "Tessellation",
    "Save (Unused)",
    "Advanced",
    "Outline Advanced",
}

COMMON_NAMES = {
    "_Color",
    "_MainTex",
    "_Cutoff",
    "_UseShadow",
    "_ShadowColor",
    "_ShadowColorTex",
    "_ShadowBorder",
    "_ShadowBlur",
    "_ShadowStrength",
    "_ShadowReceive",
    "_Shadow2ndColor",
    "_ShadowEnvStrength",
    "_UseRim",
    "_RimColor",
    "_RimColorTex",
    "_RimBorder",
    "_RimBlur",
    "_RimFresnelPower",
    "_RimEnableLighting",
    "_UseEmission",
    "_EmissionColor",
    "_EmissionMap",
}

ENABLE_TOGGLES = {
    "_UseShadow",
    "_UseRim",
    "_UseEmission",
    "_UseMain2ndTex",
    "_UseMain3rdTex",
    "_UseBumpMap",
    "_UseBump2ndMap",
    "_UseAnisotropy",
    "_UseBacklight",
    "_UseRimShade",
    "_UseReflection",
    "_UseMatCap",
    "_UseMatCap2nd",
    "_UseGlitter",
    "_UseEmission2nd",
    "_UseParallax",
    "_UseAudioLink",
}

# Skip render-pipeline / mode switches (separate shader rows or Custom).
SKIP_NAMES = {
    "_TransparentMode",
    "_UseOutline",
    "_DummyProperty",
    "_BaseColor",
    "_BaseMap",
    "_BaseColorMap",
    "_lilToonVersion",
}

DISPLAY_OVERRIDES = {
    "_MainTex": "Main Texture",
    "_BumpMap": "Normal Map",
    "_UseBumpMap": "Use Normal Map",
    "_BumpScale": "Normal Scale",
    "_UseBump2ndMap": "Use Normal Map 2nd",
    "_Bump2ndMap": "Normal Map 2nd",
    "_Bump2ndScale": "Normal Map 2nd Scale",
    "_UseMatCap": "Use MatCap",
    "_MatCapTex": "MatCap Texture",
    "_MatCapColor": "MatCap Color",
    "_UseMatCap2nd": "Use MatCap 2nd",
    "_MatCap2ndTex": "MatCap 2nd Texture",
    "_MatCap2ndColor": "MatCap 2nd Color",
    "_UseEmission2nd": "Use Emission 2nd",
    "_Emission2ndMap": "Emission 2nd Map",
    "_Emission2ndColor": "Emission 2nd Color",
    "_UseParallax": "Use Parallax",
    "_UsePOM": "Use POM",
    "_ParallaxMap": "Parallax Map",
    "_UseGlitter": "Use Glitter",
    "_GlitterColorTex": "Glitter Texture",
    "_UseRimShade": "Use Rim Shade",
    "_UseReflection": "Use Reflection",
    "_UseMain2ndTex": "Use Main 2nd Texture",
    "_UseMain3rdTex": "Use Main 3rd Texture",
    "_Main2ndTex": "Main 2nd Texture",
    "_Main3rdTex": "Main 3rd Texture",
    "_UseAnisotropy": "Use Anisotropy",
    "_UseBacklight": "Use Backlight",
    "_UseAudioLink": "Use AudioLink",
    "_UseDither": "Use Dither",
    "_ShadowColorTex": "Shadow Color Texture",
    "_Shadow2ndColor": "Shadow 2nd Color",
    "_ShadowEnvStrength": "Shadow Env Strength",
    "_RimColorTex": "Rim Texture",
    "_RimFresnelPower": "Rim Fresnel Power",
    "_RimEnableLighting": "Rim Enable Lighting",
    "_EmissionMap": "Emission Map",
    "_Ramp": "Shadow Ramp",
}


def section_title(line: str) -> str | None:
    s = line.strip()
    if not s.startswith("//"):
        return None
    body = s[2:].strip().strip("-").strip()
    if not body or body.startswith("Smooth") or body.startswith("Metallic"):
        return None
    if body.startswith("Reflectance"):
        return "Reflection"
    if body.startswith("Gradation"):
        return None
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 /]+", body) and len(body) < 40:
        return body
    return None


def assign_sections(block: str) -> dict[str, str]:
    current = "Unknown"
    out: dict[str, str] = {}
    for line in block.splitlines():
        title = section_title(line)
        if title:
            current = title
            continue
        m = PROP_LINE_RE.match(line)
        if not m:
            continue
        name = m.group("name")
        if name not in out:
            out[name] = current
    return out


def display_name(name: str, shader_display: str) -> str:
    if name in DISPLAY_OVERRIDES:
        return DISPLAY_OVERRIDES[name]
    if shader_display and not shader_display.startswith("s"):
        return shader_display
    core = name[1:]
    parts = re.sub(r"([a-z])([A-Z0-9])", r"\1 \2", core).split()
    return " ".join(parts)


def build_curated(source: str) -> dict:
    block = extract_properties_block(source)
    if block is None:
        raise SystemExit("No Properties block")
    sections = assign_sections(block)
    props = parse_properties(source, include_hidden=True)
    by_name = {p.name: p for p in props}

    rows = []
    for p in props:
        sec = sections.get(p.name, "Unknown")
        if sec in EXCLUDE_SECTIONS or p.name in SKIP_NAMES:
            continue
        if sec not in INCLUDE_SECTIONS:
            continue
        if p.hidden:
            continue
        rows.append(
            {
                "name": p.name,
                "displayName": display_name(p.name, p.display),
                "common": p.name in COMMON_NAMES,
                "_section": sec,
            }
        )

    # Preserve Properties-block order (already in parse order)
    properties = [
        {"name": r["name"], "displayName": r["displayName"], "common": r["common"]}
        for r in rows
    ]
    return {
        "displayName": "lilToon",
        "shaderName": "lilToon",
        "defaultVariant": "builtin",
        "supportedVariants": ["builtin", "urp"],
        "enableToggles": sorted(n for n in ENABLE_TOGGLES if n in by_name),
        "omitTextureDefaults": True,
        "properties": properties,
        "_meta": {
            "pin": PIN,
            "propertyCount": len(properties),
            "sections": sorted({r["_section"] for r in rows}),
        },
    }


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "examples" / "liltoon-opaque.curated.json"
    source = fetch_text(github_raw_url("lilxyzw/lilToon", PIN, SHADER_PATH))
    curated = build_curated(source)
    meta = curated.pop("_meta")
    out_path.write_text(json.dumps(curated, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"  properties: {meta['propertyCount']}")
    print(f"  common: {sum(1 for p in curated['properties'] if p['common'])}")
    print(f"  extended: {sum(1 for p in curated['properties'] if not p['common'])}")
    print(f"  sections: {', '.join(meta['sections'])}")


if __name__ == "__main__":
    main()
