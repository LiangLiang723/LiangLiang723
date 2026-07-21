#!/usr/bin/env python3
"""Validate the Linear-inspired GitHub profile and workflow wiring."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "profile.yml"
GENERATOR = ROOT / ".github" / "scripts" / "generate_linear_assets.py"
FETCHER = ROOT / ".github" / "scripts" / "fetch_profile_stats.py"
ASSET_DIR = ROOT / "assets" / "linear"
STATS_PATH = ASSET_DIR / "profile-stats.json"

EXPECTED_ASSETS = {"hero-light.svg", "hero-dark.svg", "stats-light.svg", "stats-dark.svg"}
REQUIRED_SECTIONS = ["## 核心能力", "## 当前研究方向", "## 开发数据", "## 贡献轨迹"]
FORBIDDEN_README_TOKENS = [
    "assets/apple/",
    "profile-summary-card-output/",
    "## 精选项目",
    "最近动态",
    "查看全部仓库",
]
FORBIDDEN_PATHS = [
    ROOT / "assets" / "apple",
    ROOT / "profile-summary-card-output",
    ROOT / ".github" / "scripts" / "generate_apple_assets.py",
    ROOT / ".github" / "scripts" / "style_summary_cards.py",
]
LOCAL_PAIRS = [
    ("assets/linear/hero-light.svg", "assets/linear/hero-dark.svg"),
    ("assets/linear/stats-light.svg", "assets/linear/stats-dark.svg"),
]


def local_references(markdown: str) -> set[str]:
    return {
        match.group(1)[2:]
        for match in re.finditer(r'(?:src|srcset)="(\./[^"?#]+)', markdown)
    }


def asset_hashes() -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(ASSET_DIR.glob("*.svg"))
    }


def validate_determinism(errors: list[str]) -> None:
    first = subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, capture_output=True, text=True)
    if first.returncode:
        errors.append(f"Linear asset generator failed: {first.stderr.strip() or first.stdout.strip()}")
        return
    before = asset_hashes()
    second = subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, capture_output=True, text=True)
    if second.returncode:
        errors.append(f"Linear asset generator failed on second run: {second.stderr.strip() or second.stdout.strip()}")
        return
    if before != asset_hashes():
        errors.append("Linear asset generator is not deterministic")


def validate_stats_json(errors: list[str]) -> None:
    if not STATS_PATH.is_file():
        errors.append("Missing assets/linear/profile-stats.json")
        return
    try:
        payload = json.loads(STATS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid profile stats JSON: {exc}")
        return
    for key in ("public_repos", "contributions"):
        value = payload.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"Profile stats field {key} must be a non-negative integer")
    for key in ("primary_language", "updated_at"):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"Profile stats field {key} must be a non-empty string")


def validate() -> list[str]:
    errors: list[str] = []
    for required in (README, WORKFLOW, GENERATOR, FETCHER):
        if not required.is_file():
            errors.append(f"Missing required file: {required.relative_to(ROOT)}")
    if errors:
        return errors

    markdown = README.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
    existing = {path.name for path in ASSET_DIR.glob("*.svg")} if ASSET_DIR.is_dir() else set()
    for name in sorted(EXPECTED_ASSETS - existing):
        errors.append(f"Missing Linear asset: assets/linear/{name}")
    for name in sorted(existing - EXPECTED_ASSETS):
        errors.append(f"Unexpected Linear SVG: assets/linear/{name}")

    for path in FORBIDDEN_PATHS:
        if path.exists():
            errors.append(f"Legacy profile path still exists: {path.relative_to(ROOT)}")

    for token in FORBIDDEN_README_TOKENS:
        if token in markdown:
            errors.append(f"README contains forbidden legacy content: {token}")

    headings = re.findall(r"^## .+$", markdown, flags=re.MULTILINE)
    if headings != REQUIRED_SECTIONS:
        errors.append(f"README section order must be {REQUIRED_SECTIONS}, found {headings}")

    picture_blocks = re.findall(r"<picture>.*?</picture>", markdown, flags=re.DOTALL | re.IGNORECASE)
    for light, dark in LOCAL_PAIRS:
        matches = [block for block in picture_blocks if light in block or dark in block]
        if len(matches) != 1:
            errors.append(f"Expected one picture block for {light}/{dark}, found {len(matches)}")
            continue
        block = matches[0]
        if light not in block or dark not in block:
            errors.append(f"Incomplete light/dark pair: {light}/{dark}")
        fallback = re.search(r'<img\s+[^>]*src="([^"]+)"', block, flags=re.IGNORECASE)
        if not fallback or fallback.group(1) != f"./{light}":
            errors.append(f"Picture fallback must use ./{light}")

    for ref in sorted(local_references(markdown)):
        if not (ROOT / ref).is_file():
            errors.append(f"README references missing local file: {ref}")

    expected_dimensions = {
        "hero-light.svg": ("1200", "238"),
        "hero-dark.svg": ("1200", "238"),
        "stats-light.svg": ("1200", "132"),
        "stats-dark.svg": ("1200", "132"),
    }
    ns = {"svg": "http://www.w3.org/2000/svg"}
    for name in sorted(existing & EXPECTED_ASSETS):
        path = ASSET_DIR / name
        raw = path.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            errors.append(f"Invalid SVG XML in {path.relative_to(ROOT)}: {exc}")
            continue
        width, height = expected_dimensions[name]
        if root.attrib.get("width") != width or root.attrib.get("height") != height:
            errors.append(f"{path.relative_to(ROOT)} must be {width}x{height}")
        if root.find("svg:title", ns) is None or root.find("svg:desc", ns) is None:
            errors.append(f"{path.relative_to(ROOT)} must contain title and desc")
        if "system-ui" not in raw or "Noto Sans CJK SC" not in raw or "prefers-reduced-motion" not in raw:
            errors.append(f"{path.relative_to(ROOT)} is missing compatible typography or reduced-motion rules")
        if re.search(r"#[0-9A-Fa-f]{8}\b", raw):
            errors.append(f"{path.relative_to(ROOT)} must use explicit opacity instead of 8-digit hex colors")
        if "stroke-opacity=" not in raw:
            errors.append(f"{path.relative_to(ROOT)} is missing explicit low-contrast stroke opacity")
        required_tokens = ("#F7F7F8", "#6E56CF") if name.endswith("-light.svg") else ("#0F1012", "#8B7CF6")
        for token in required_tokens:
            if token not in raw:
                errors.append(f"{path.relative_to(ROOT)} is missing theme token {token}")

    validate_stats_json(errors)

    workflow_tokens = [
        "python3 .github/scripts/fetch_profile_stats.py",
        "python3 .github/scripts/generate_linear_assets.py",
        "python3 .github/scripts/validate_profile.py",
        "git add -A assets/linear",
        "color_snake=%236E56CF",
        "color_snake=%238B7CF6",
        "color_dots=%23ECECF0,%23D8D4F2,%23B9B1EA,%239185DE,%236E56CF",
        "color_dots=%2316171A,%23292735,%233F3A5A,%23625A94,%238B7CF6",
    ]
    for token in workflow_tokens:
        if token not in workflow:
            errors.append(f"Workflow missing required Linear token: {token}")

    validate_determinism(errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Profile validation failed with {len(errors)} error(s).")
        return 1
    print("Profile validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
