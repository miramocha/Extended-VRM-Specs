#!/usr/bin/env python3
"""Inspect and compare JSON and binary chunks in glTF, GLB, and VRM files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942
NUMBER_RE = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?")


@dataclass(frozen=True)
class Chunk:
    kind: str
    payload: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.payload).hexdigest()


@dataclass(frozen=True)
class Document:
    path: Path
    file_bytes: bytes
    json_bytes: bytes
    data: dict[str, Any]
    chunks: tuple[Chunk, ...]
    glb_version: int | None


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_document(path: Path) -> Document:
    file_bytes = path.read_bytes()

    if file_bytes[:4] != b"glTF":
        try:
            data = json.loads(file_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: not glTF JSON or GLB/VRM: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"{path}: top-level glTF JSON must be an object")
        return Document(path, file_bytes, file_bytes, data, (), None)

    if len(file_bytes) < 12:
        raise ValueError(f"{path}: truncated GLB header")

    magic, version, declared_length = struct.unpack_from("<4sII", file_bytes, 0)
    if magic != b"glTF":
        raise ValueError(f"{path}: invalid GLB magic")
    if declared_length != len(file_bytes):
        raise ValueError(
            f"{path}: GLB declares {declared_length} bytes, file has {len(file_bytes)}"
        )

    chunks: list[Chunk] = []
    json_bytes: bytes | None = None
    offset = 12
    while offset < len(file_bytes):
        if offset + 8 > len(file_bytes):
            raise ValueError(f"{path}: truncated chunk header at byte {offset}")
        chunk_length, chunk_type = struct.unpack_from("<II", file_bytes, offset)
        offset += 8
        end = offset + chunk_length
        if end > len(file_bytes):
            raise ValueError(f"{path}: truncated chunk payload at byte {offset}")
        payload = file_bytes[offset:end]
        offset = end
        kind = {
            JSON_CHUNK: "JSON",
            BIN_CHUNK: "BIN",
        }.get(chunk_type, f"0x{chunk_type:08X}")
        chunks.append(Chunk(kind, payload))
        if chunk_type == JSON_CHUNK:
            if json_bytes is not None:
                raise ValueError(f"{path}: multiple JSON chunks")
            json_bytes = payload.rstrip(b" \x00")

    if json_bytes is None:
        raise ValueError(f"{path}: GLB has no JSON chunk")

    try:
        data = json.loads(json_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid JSON chunk: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level glTF JSON must be an object")

    return Document(
        path,
        file_bytes,
        json_bytes,
        data,
        tuple(chunks),
        version,
    )


def format_size(size: int) -> str:
    return f"{size:,} bytes"


def iter_extensions(value: Any, path: str = "$") -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        extensions = value.get("extensions")
        if isinstance(extensions, dict):
            for name, payload in extensions.items():
                yield f"{path}.extensions.{name}", name, payload
        for key, child in value.items():
            if key != "extensions":
                yield from iter_extensions(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_extensions(child, f"{path}[{index}]")


def canonical_json(data: dict[str, Any]) -> bytes:
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def short(value: Any, limit: int = 180) -> str:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def recursive_diffs(
    left: Any,
    right: Any,
    path: str = "$",
    *,
    limit: int = 100,
) -> list[tuple[str, str, Any, Any]]:
    result: list[tuple[str, str, Any, Any]] = []

    def visit(a: Any, b: Any, current: str) -> None:
        if len(result) >= limit:
            return
        if type(a) is not type(b):
            result.append((current, "type", type(a).__name__, type(b).__name__))
            return
        if isinstance(a, dict):
            left_keys = set(a)
            right_keys = set(b)
            for key in sorted(left_keys - right_keys):
                result.append((f"{current}.{key}", "only-left", a[key], None))
                if len(result) >= limit:
                    return
            for key in sorted(right_keys - left_keys):
                result.append((f"{current}.{key}", "only-right", None, b[key]))
                if len(result) >= limit:
                    return
            for key in sorted(left_keys & right_keys):
                visit(a[key], b[key], f"{current}.{key}")
                if len(result) >= limit:
                    return
            return
        if isinstance(a, list):
            if len(a) != len(b):
                result.append((current, "length", len(a), len(b)))
            for index, (a_item, b_item) in enumerate(zip(a, b)):
                visit(a_item, b_item, f"{current}[{index}]")
                if len(result) >= limit:
                    return
            return
        if a != b:
            result.append((current, "value", a, b))

    visit(left, right, path)
    return result


def number_spelling_stats(left: bytes, right: bytes) -> tuple[int, int, int] | None:
    left_tokens = NUMBER_RE.findall(left.decode("utf-8"))
    right_tokens = NUMBER_RE.findall(right.decode("utf-8"))
    if len(left_tokens) != len(right_tokens):
        return None

    equal_value_diffs = 0
    unequal_value_diffs = 0
    length_delta = 0
    for left_token, right_token in zip(left_tokens, right_tokens):
        if left_token == right_token:
            continue
        try:
            same_value = float(left_token) == float(right_token)
        except ValueError:
            same_value = False
        if same_value:
            equal_value_diffs += 1
            length_delta += len(left_token) - len(right_token)
        else:
            unequal_value_diffs += 1
    return equal_value_diffs, unequal_value_diffs, length_delta


def command_summary(args: argparse.Namespace) -> int:
    document = parse_document(args.file)
    print(f"file: {document.path}")
    print(f"size: {format_size(len(document.file_bytes))}")
    print(f"sha256: {hash_bytes(document.file_bytes)}")
    print(f"format: {'GLB/VRM ' + str(document.glb_version) if document.glb_version else 'glTF JSON'}")

    for index, chunk in enumerate(document.chunks):
        print(
            f"chunk[{index}]: {chunk.kind} {format_size(len(chunk.payload))} "
            f"sha256={chunk.sha256}"
        )

    data = document.data
    print(f"extensionsUsed: {data.get('extensionsUsed', [])}")
    print(f"extensionsRequired: {data.get('extensionsRequired', [])}")
    root_extensions = data.get("extensions")
    print(
        "root extensions: "
        f"{sorted(root_extensions) if isinstance(root_extensions, dict) else []}"
    )

    for key in (
        "accessors",
        "bufferViews",
        "images",
        "materials",
        "meshes",
        "nodes",
        "textures",
    ):
        value = data.get(key)
        if isinstance(value, list):
            print(f"{key}: {len(value)}")

    hits = list(iter_extensions(data))
    print(f"extension attachments: {len(hits)}")
    for path, name, payload in hits:
        if args.extension and args.extension.lower() not in name.lower():
            continue
        print(f"  {path}: {short(payload, args.payload_limit)}")
    return 0


def command_extract(args: argparse.Namespace) -> int:
    document = parse_document(args.file)
    text = json.dumps(
        document.data,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
    )
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote: {args.output}")
    else:
        print(text)
    return 0


def chunk_by_kind(document: Document, kind: str) -> Chunk | None:
    return next((chunk for chunk in document.chunks if chunk.kind == kind), None)


def command_compare(args: argparse.Namespace) -> int:
    left = parse_document(args.left)
    right = parse_document(args.right)

    print(f"left:  {left.path}")
    print(f"right: {right.path}")
    print(
        f"file: equal={left.file_bytes == right.file_bytes} "
        f"left={format_size(len(left.file_bytes))} "
        f"right={format_size(len(right.file_bytes))} "
        f"delta={len(left.file_bytes) - len(right.file_bytes):+d}"
    )
    print(f"left sha256:  {hash_bytes(left.file_bytes)}")
    print(f"right sha256: {hash_bytes(right.file_bytes)}")

    kinds = sorted({chunk.kind for chunk in left.chunks + right.chunks})
    for kind in kinds:
        left_chunk = chunk_by_kind(left, kind)
        right_chunk = chunk_by_kind(right, kind)
        if left_chunk is None or right_chunk is None:
            print(f"{kind}: missing from {'left' if left_chunk is None else 'right'}")
            continue
        print(
            f"{kind}: equal={left_chunk.payload == right_chunk.payload} "
            f"left={format_size(len(left_chunk.payload))} "
            f"right={format_size(len(right_chunk.payload))} "
            f"delta={len(left_chunk.payload) - len(right_chunk.payload):+d}"
        )

    semantic_equal = left.data == right.data
    left_canonical = canonical_json(left.data)
    right_canonical = canonical_json(right.data)
    print(f"JSON semantic equal: {semantic_equal}")
    print(f"JSON canonical sha256 left:  {hash_bytes(left_canonical)}")
    print(f"JSON canonical sha256 right: {hash_bytes(right_canonical)}")

    if semantic_equal and left.json_bytes != right.json_bytes:
        stats = number_spelling_stats(left.json_bytes, right.json_bytes)
        if stats is not None:
            equal_value_diffs, unequal_value_diffs, length_delta = stats
            print(
                "JSON number spellings: "
                f"same-value differences={equal_value_diffs}, "
                f"value differences={unequal_value_diffs}, "
                f"text length delta={length_delta:+d}"
            )
        print("result: JSON values equal; serialization differs")
        return 0

    if not semantic_equal:
        diffs = recursive_diffs(left.data, right.data, limit=args.diff_limit)
        print(f"JSON differences (up to {args.diff_limit}): {len(diffs)}")
        for path, kind, left_value, right_value in diffs:
            print(
                f"  {path} | {kind} | "
                f"left={short(left_value)} | right={short(right_value)}"
            )
        return 1

    print("result: files are semantically and byte identical" if left.file_bytes == right.file_bytes else "result: non-JSON bytes differ")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect JSON and chunks in .gltf, .glb, and .vrm files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary = subparsers.add_parser("summary", help="show structure and extension data")
    summary.add_argument("file", type=Path)
    summary.add_argument(
        "--extension",
        help="only print extension attachments whose name contains this text",
    )
    summary.add_argument(
        "--payload-limit",
        type=int,
        default=500,
        help="maximum characters shown per extension payload (default: 500)",
    )
    summary.set_defaults(func=command_summary)

    extract = subparsers.add_parser("extract", help="extract glTF JSON")
    extract.add_argument("file", type=Path)
    extract.add_argument("-o", "--output", type=Path)
    extract.add_argument("--pretty", action="store_true")
    extract.set_defaults(func=command_extract)

    compare = subparsers.add_parser(
        "compare",
        help="compare file hashes, chunks, and parsed JSON",
    )
    compare.add_argument("left", type=Path)
    compare.add_argument("right", type=Path)
    compare.add_argument(
        "--diff-limit",
        type=int,
        default=100,
        help="maximum semantic JSON differences shown (default: 100)",
    )
    compare.set_defaults(func=command_compare)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
