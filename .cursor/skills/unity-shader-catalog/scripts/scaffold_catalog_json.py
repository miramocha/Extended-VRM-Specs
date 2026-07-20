#!/usr/bin/env python3
"""Scaffold materials-override catalog JSON from curated list + ShaderLab."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shaderlab import (  # noqa: E402
    dump_json,
    github_raw_url,
    index_props,
    load_json,
    parse_properties,
    read_shader,
    scaffold_catalog,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--curated",
        type=Path,
        required=True,
        help="Curated JSON: displayName, shaderName, properties[{name,displayName,common}], …",
    )
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="Local .shader path")
    src.add_argument(
        "--github",
        metavar="REPO@REF:PATH",
        help="e.g. lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Catalog JSON output path",
    )
    args = ap.parse_args()

    curated = load_json(args.curated)
    if "properties" not in curated or "displayName" not in curated or "shaderName" not in curated:
        raise SystemExit(
            "Curated JSON needs displayName, shaderName, and properties[]"
        )

    if args.file:
        source = read_shader(args.file)
    else:
        try:
            repo_ref, path = args.github.split(":", 1)
            repo, ref = repo_ref.split("@", 1)
        except ValueError as e:
            raise SystemExit(
                "--github must be REPO@REF:PATH "
                "(example: lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader)"
            ) from e
        source = read_shader(github_raw_url(repo, ref, path))

    want = [p["name"] for p in curated["properties"]]
    # Include hidden so curated HideInInspector names still resolve if listed
    props = parse_properties(source, include_hidden=True, names=want)
    catalog = scaffold_catalog(
        curated=curated, props_by_name=index_props(props)
    )
    dump_json(catalog, args.output)
    print(f"Wrote {args.output} ({len(catalog['properties'])} properties)")


if __name__ == "__main__":
    main()
