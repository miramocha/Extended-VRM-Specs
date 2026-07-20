#!/usr/bin/env python3
"""Diff ShaderLab Properties between two shaders (local or GitHub)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shaderlab import (  # noqa: E402
    diff_prop_maps,
    dump_json,
    extract_shader_name,
    github_raw_url,
    index_props,
    parse_properties,
    read_shader,
)


def load_side(spec: str, *, include_hidden: bool, names: list[str] | None):
    if spec.startswith("github:"):
        body = spec[len("github:") :]
        try:
            repo_ref, path = body.split(":", 1)
            repo, ref = repo_ref.split("@", 1)
        except ValueError as e:
            raise SystemExit(
                "github side must be github:REPO@REF:PATH"
            ) from e
        origin = github_raw_url(repo, ref, path)
        source = read_shader(origin)
    else:
        origin = spec
        source = read_shader(spec)
    props = parse_properties(source, include_hidden=include_hidden, names=names)
    return {
        "origin": origin,
        "shaderName": extract_shader_name(source),
        "props": index_props(props),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--left",
        required=True,
        help="Local path, or github:REPO@REF:PATH",
    )
    ap.add_argument(
        "--right",
        required=True,
        help="Local path, or github:REPO@REF:PATH",
    )
    ap.add_argument(
        "--names",
        help="Comma-separated names to compare (default: union of both)",
    )
    ap.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include HideInInspector properties",
    )
    ap.add_argument("-o", "--output", type=Path, help="Write JSON report")
    args = ap.parse_args()

    names = [n.strip() for n in args.names.split(",")] if args.names else None
    left = load_side(args.left, include_hidden=args.include_hidden, names=names)
    right = load_side(args.right, include_hidden=args.include_hidden, names=names)
    report = diff_prop_maps(left["props"], right["props"], names=names)
    payload = {
        "left": {"origin": left["origin"], "shaderName": left["shaderName"]},
        "right": {"origin": right["origin"], "shaderName": right["shaderName"]},
        **report,
    }
    text = dump_json(payload, args.output)
    if args.output is None:
        sys.stdout.write(text)
    status = "identical" if report["identical"] else "DIFFERS"
    print(
        f"{status}: onlyLeft={len(report['onlyLeft'])} "
        f"onlyRight={len(report['onlyRight'])} changed={len(report['changed'])}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
