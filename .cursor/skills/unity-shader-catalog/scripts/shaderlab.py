#!/usr/bin/env python3
"""ShaderLab Properties helpers for VRMXT materials-override catalogs."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SHADER_NAME_RE = re.compile(r'Shader\s+"([^"]+)"')
# Leading attributes + _Name ( "display", Type ) = default
# Type may contain nested parens: Range(0, 1), Range(-0.001,1.001)
PROP_LINE_RE = re.compile(
    r"^\s*(?P<attrs>(?:\[[^\]]+\]\s*)*)"
    r"(?P<name>_[A-Za-z0-9]+)\s*"
    r'\(\s*"(?P<display>[^"]*)"\s*,\s*(?P<type>.+)\s*\)\s*'
    r"=\s*(?P<default>.+?)\s*$"
)

SKIP_NAMES = {"_DummyProperty"}
HIDDEN_ATTRS = {"HideInInspector"}


@dataclass(frozen=True)
class ShaderProperty:
    name: str
    display: str
    lab_type: str
    default_raw: str
    attributes: tuple[str, ...]
    line: int

    @property
    def hidden(self) -> bool:
        return any(a in HIDDEN_ATTRS for a in self.attributes)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["attributes"] = list(self.attributes)
        d["hidden"] = self.hidden
        d["catalog_type"] = map_catalog_type(self.lab_type)
        d["catalog_default"] = parse_catalog_default(self.lab_type, self.default_raw)
        return d


def map_catalog_type(lab_type: str) -> str:
    base = lab_type.strip().split("(", 1)[0].strip().lower()
    if base == "color":
        return "vector"
    if base in {"2d", "cube", "2darray", "3d"}:
        return "texture"
    if base in {"float", "range", "int"}:
        return "scalar"
    if base == "vector":
        return "vector"
    return "scalar"


def _split_top_level_commas(s: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(s[start:i].strip())
            start = i + 1
    parts.append(s[start:].strip())
    return parts


def _num(value: str) -> int | float:
    f = float(value)
    if f.is_integer():
        return int(f)
    return f


def parse_catalog_default(lab_type: str, default_raw: str) -> Any | None:
    """Map ShaderLab default literal to catalog JSON default, or None to omit."""
    raw = default_raw.strip()
    catalog_type = map_catalog_type(lab_type)
    if catalog_type == "texture":
        return None
    if catalog_type == "vector":
        if raw.startswith("(") and raw.endswith(")"):
            inner = raw[1:-1]
            return [_num(part) for part in _split_top_level_commas(inner)]
        return None
    # scalar
    try:
        return _num(raw)
    except ValueError:
        return None


def extract_shader_name(source: str) -> str | None:
    m = SHADER_NAME_RE.search(source)
    return m.group(1) if m else None


def extract_properties_block(source: str) -> str | None:
    """Return text inside the first top-level Properties { ... } block."""
    key = "Properties"
    idx = source.find(key)
    if idx < 0:
        return None
    brace = source.find("{", idx)
    if brace < 0:
        return None
    depth = 0
    for i in range(brace, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1 : i]
    return None


def parse_attributes(attrs_blob: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\[([^\]]+)\]", attrs_blob))


def parse_properties(
    source: str,
    *,
    include_hidden: bool = False,
    names: Iterable[str] | None = None,
) -> list[ShaderProperty]:
    block = extract_properties_block(source)
    if block is None:
        return []
    allow = set(names) if names is not None else None
    # Absolute line numbers: locate block start in full source
    block_start = source.find(block)
    prefix_lines = source[:block_start].count("\n")

    found: list[ShaderProperty] = []
    seen: set[str] = set()
    for offset, line in enumerate(block.splitlines()):
        m = PROP_LINE_RE.match(line)
        if not m:
            continue
        name = m.group("name")
        if name in SKIP_NAMES:
            continue
        if allow is not None and name not in allow:
            continue
        if name in seen:
            continue
        attrs = parse_attributes(m.group("attrs") or "")
        prop = ShaderProperty(
            name=name,
            display=m.group("display"),
            lab_type=m.group("type").strip(),
            default_raw=m.group("default").strip(),
            attributes=attrs,
            line=prefix_lines + offset + 1,
        )
        if prop.hidden and not include_hidden:
            continue
        seen.add(name)
        found.append(prop)
    return found


def read_shader(path_or_url: str) -> str:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return fetch_text(path_or_url)
    return Path(path_or_url).read_text(encoding="utf-8", errors="replace")


def fetch_text(url: str, timeout: float = 60.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "vrmxt-shader-catalog/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} fetching {url}") from e


def github_raw_url(repo: str, ref: str, path: str) -> str:
    """repo like 'lilxyzw/lilToon', path without leading slash."""
    path = path.lstrip("/")
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any, path: Path | None = None) -> str:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return text


def scaffold_catalog(
    *,
    curated: dict[str, Any],
    props_by_name: dict[str, ShaderProperty],
    catalog_version: str = "1.0",
    engine: str = "unity",
    id_type: str = "shaderName",
) -> dict[str, Any]:
    """Build catalog JSON from curated metadata + parsed ShaderLab props."""
    enable_toggles = set(curated.get("enableToggles") or [])
    omit_texture_defaults = curated.get("omitTextureDefaults", True)
    out: dict[str, Any] = {
        "catalogVersion": curated.get("catalogVersion", catalog_version),
        "engine": curated.get("engine", engine),
        "displayName": curated["displayName"],
        "shaderName": curated["shaderName"],
        "idType": curated.get("idType", id_type),
    }
    if "defaultVariant" in curated:
        out["defaultVariant"] = curated["defaultVariant"]
    if "supportedVariants" in curated:
        out["supportedVariants"] = curated["supportedVariants"]
    if "provider" in curated:
        out["provider"] = curated["provider"]

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for entry in curated["properties"]:
        name = entry["name"]
        parsed = props_by_name.get(name)
        if parsed is None:
            missing.append(name)
            continue
        catalog_type = entry.get("type") or parsed.to_dict()["catalog_type"]
        row: dict[str, Any] = {
            "name": name,
            "type": catalog_type,
            "displayName": entry.get("displayName") or entry.get("display") or name,
            "common": bool(entry.get("common", False)),
        }
        if catalog_type == "vector":
            row["vectorSize"] = int(entry.get("vectorSize") or 4)

        default: Any
        if "default" in entry:
            default = entry["default"]
        elif name in enable_toggles:
            default = 1
        else:
            default = parse_catalog_default(parsed.lab_type, parsed.default_raw)
            if catalog_type == "texture" and omit_texture_defaults:
                default = None

        if default is not None:
            row["default"] = default
        rows.append(row)

    if missing:
        raise SystemExit(
            "Curated properties missing from ShaderLab Properties block:\n  "
            + "\n  ".join(missing)
        )
    out["properties"] = rows
    return out


def index_props(props: Iterable[ShaderProperty]) -> dict[str, ShaderProperty]:
    return {p.name: p for p in props}


def diff_prop_maps(
    left: dict[str, ShaderProperty],
    right: dict[str, ShaderProperty],
    names: Iterable[str] | None = None,
) -> dict[str, Any]:
    keys = set(names) if names is not None else (set(left) | set(right))
    only_left = sorted(k for k in keys if k in left and k not in right)
    only_right = sorted(k for k in keys if k in right and k not in left)
    changed = []
    for k in sorted(keys):
        if k not in left or k not in right:
            continue
        a, b = left[k], right[k]
        if (
            a.lab_type != b.lab_type
            or a.default_raw != b.default_raw
            or a.attributes != b.attributes
        ):
            changed.append(
                {
                    "name": k,
                    "left": {
                        "lab_type": a.lab_type,
                        "default": a.default_raw,
                        "attributes": list(a.attributes),
                    },
                    "right": {
                        "lab_type": b.lab_type,
                        "default": b.default_raw,
                        "attributes": list(b.attributes),
                    },
                }
            )
    return {
        "onlyLeft": only_left,
        "onlyRight": only_right,
        "changed": changed,
        "identical": not only_left and not only_right and not changed,
    }
