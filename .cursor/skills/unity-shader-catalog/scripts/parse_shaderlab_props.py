#!/usr/bin/env python3
"""Parse Unity ShaderLab Properties into JSON."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shaderlab import (  # noqa: E402
    dump_json,
    extract_shader_name,
    github_raw_url,
    parse_properties,
    read_shader,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="Local .shader path")
    src.add_argument(
        "--github",
        metavar="REPO@REF:PATH",
        help="e.g. lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader",
    )
    ap.add_argument(
        "--names",
        help="Comma-separated property names to include (default: all non-hidden)",
    )
    ap.add_argument(
        "--include-hidden",
        action="store_true",
        help="Keep HideInInspector properties",
    )
    ap.add_argument("-o", "--output", type=Path, help="Write JSON to path")
    args = ap.parse_args()

    if args.file:
        source = read_shader(args.file)
        origin = args.file
    else:
        try:
            repo_ref, path = args.github.split(":", 1)
            repo, ref = repo_ref.split("@", 1)
        except ValueError as e:
            raise SystemExit(
                "--github must be REPO@REF:PATH "
                "(example: lilxyzw/lilToon@2.3.4:Assets/lilToon/Shader/lts.shader)"
            ) from e
        url = github_raw_url(repo, ref, path)
        source = read_shader(url)
        origin = url

    names = [n.strip() for n in args.names.split(",")] if args.names else None
    props = parse_properties(
        source, include_hidden=args.include_hidden, names=names
    )
    payload = {
        "origin": origin,
        "shaderName": extract_shader_name(source),
        "count": len(props),
        "properties": [p.to_dict() for p in props],
    }
    text = dump_json(payload, args.output)
    if args.output is None:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
