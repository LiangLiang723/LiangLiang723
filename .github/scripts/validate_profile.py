#!/usr/bin/env python3
"""Validate the Apple Editorial 2.0 GitHub profile and workflow wiring."""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "profile.yml"
GENERATOR = ROOT / ".github" / "scripts" / "generate_apple_assets.py"
STYLER = ROOT / ".github" / "scripts" / "style_summary_cards.py"
APPLE_DIR = ROOT / "assets" / "apple"

EXPECTED_ASSETS = {
    "hero-light.svg", "hero-dark.svg",
    "profile-light.svg", "profile-dark.svg",
    "tech-stack-light.svg", "tech-stack-dark.svg",
    "project-ai-berkshire-light.svg", "project-ai-berkshire-dark.svg",
    "project-supercom-light.svg", "project-supercom-dark.svg",
    "project-multitimer-light.svg", "project-multitimer-dark.svg",
    "project-learning-light.svg", "project-learning-dark.svg",
    "focus-light.svg", "focus-dark.svg",
    "footer-light.svg", "footer-dark.svg",
}

CUSTOM_PAIRS = [
    ("hero-light.svg", "hero-dark.svg"),
    ("profile-light.svg", "profile-dark.svg"),
    ("tech-stack-light.svg", "tech-stack-dark.svg"),
    ("project-ai-berkshire-light.svg", "project-ai-berkshire-dark.svg"),
    ("project-supercom-light.svg", "project-supercom-dark.svg"),
    ("project-multitimer-light.svg", "project-multitimer-dark.svg"),
    ("project-learning-light.svg", "project-learning-dark.svg"),
    ("focus-light.svg", "focus-dark.svg"),
    ("footer-light.svg", "footer-dark.svg"),
]

PROJECT_URLS = [
    "https://github.com/LiangLiang723/ai-berkshire",
    "https://github.com/LiangLiang723/SuperCom",
    "https://github.com/LiangLiang723/MultiTimer",
    "https://github.com/LiangLiang723/English-level-up-tips",
]

FORBIDDEN_EXTERNAL = [
    "img.shields.io",
    "github-readme-stats.vercel.app",
    "capsule-render",
]

FORBIDDEN_ASSET_TOKENS = [
    "#A855F7",
    "#22D3EE",
    "#34C759",
    "#30D158",
    "#FF9F0A",
    "#AF52DE",
    "#BF5AF2",
    "Featured project",
    "Technical capabilities",
    "Focused · Reliable · Maintainable",
    ">Embedded<",
    ">Application<",
    ">Infrastructure<",
]

SUMMARY_REFERENCES = [
    "profile-summary-card-output/github/0-profile-details.svg",
    "profile-summary-card-output/github_dark/0-profile-details.svg",
    "profile-summary-card-output/github/1-repos-per-language.svg",
    "profile-summary-card-output/github_dark/1-repos-per-language.svg",
    "profile-summary-card-output/github/3-stats.svg",
    "profile-summary-card-output/github_dark/3-stats.svg",
]

PROJECT_ASSETS = [
    "project-ai-berkshire-light.svg", "project-ai-berkshire-dark.svg",
    "project-supercom-light.svg", "project-supercom-dark.svg",
    "project-multitimer-light.svg", "project-multitimer-dark.svg",
    "project-learning-light.svg", "project-learning-dark.svg",
]


def local_references(markdown: str) -> set[str]:
    refs: set[str] = set()
    for match in re.finditer(r'(?:src|srcset)="(\./[^"?#]+)', markdown):
        refs.add(match.group(1)[2:])
    return refs


def hashes() -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(APPLE_DIR.glob("*.svg"))
    }


def validate_determinism(errors: list[str]) -> None:
    if not GENERATOR.is_file():
        errors.append("Missing asset generator")
        return
    result_a = subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, capture_output=True, text=True)
    if result_a.returncode:
        errors.append(f"Asset generator failed: {result_a.stderr.strip() or result_a.stdout.strip()}")
        return
    hash_a = hashes()
    result_b = subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, capture_output=True, text=True)
    if result_b.returncode:
        errors.append(f"Asset generator failed on second run: {result_b.stderr.strip() or result_b.stdout.strip()}")
        return
    hash_b = hashes()
    if hash_a != hash_b:
        errors.append("Asset generator is not deterministic across consecutive runs")


def validate() -> list[str]:
    errors: list[str] = []
    if not README.is_file():
        return ["Missing README.md"]
    if not WORKFLOW.is_file():
        errors.append("Missing .github/workflows/profile.yml")
    if not STYLER.is_file():
        errors.append("Missing .github/scripts/style_summary_cards.py")

    markdown = README.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""
    existing = {path.name for path in APPLE_DIR.glob("*.svg")} if APPLE_DIR.is_dir() else set()

    for name in sorted(EXPECTED_ASSETS - existing):
        errors.append(f"Missing Apple asset: assets/apple/{name}")
    for name in sorted(existing - EXPECTED_ASSETS):
        errors.append(f"Unexpected Apple asset: assets/apple/{name}")

    ns = {"svg": "http://www.w3.org/2000/svg"}
    project_dimensions: set[tuple[str, str]] = set()
    for name in sorted(existing & EXPECTED_ASSETS):
        path = APPLE_DIR / name
        raw = path.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            errors.append(f"Invalid XML in {path.relative_to(ROOT)}: {exc}")
            continue
        if root.attrib.get("width") != "1200":
            errors.append(f"{path.relative_to(ROOT)} must use width=1200")
        view_box = root.attrib.get("viewBox", "")
        if not view_box.startswith("0 0 1200 "):
            errors.append(f"{path.relative_to(ROOT)} has invalid viewBox: {view_box!r}")
        if root.find("svg:title", ns) is None:
            errors.append(f"{path.relative_to(ROOT)} is missing <title>")
        if root.find("svg:desc", ns) is None:
            errors.append(f"{path.relative_to(ROOT)} is missing <desc>")
        if "prefers-reduced-motion" not in raw:
            errors.append(f"{path.relative_to(ROOT)} lacks reduced-motion handling")
        for token in FORBIDDEN_ASSET_TOKENS:
            if token.lower() in raw.lower():
                errors.append(f"{path.relative_to(ROOT)} contains forbidden Editorial 1.x token: {token}")
        expected_accent = "#0071E3" if name.endswith("-light.svg") else "#0A84FF"
        if expected_accent not in raw:
            errors.append(f"{path.relative_to(ROOT)} does not use expected accent {expected_accent}")
        if not name.startswith("footer-") and 'rx="24"' not in raw:
            errors.append(f"{path.relative_to(ROOT)} is missing the unified 24px main-card radius")
        if name in PROJECT_ASSETS:
            project_dimensions.add((root.attrib.get("width", ""), root.attrib.get("height", "")))

    if len(project_dimensions) != 1:
        errors.append(f"Project cards must share one size, found: {sorted(project_dimensions)}")

    for token in FORBIDDEN_EXTERNAL:
        if token in markdown:
            errors.append(f"README contains forbidden external dependency: {token}")
    if "4-productive-time.svg" in markdown:
        errors.append("README still references the productive-time card")

    picture_blocks = re.findall(r"<picture>.*?</picture>", markdown, flags=re.DOTALL | re.IGNORECASE)
    for light, dark in CUSTOM_PAIRS:
        matching = [block for block in picture_blocks if light in block or dark in block]
        if len(matching) != 1:
            errors.append(f"Expected exactly one picture block for {light}/{dark}, found {len(matching)}")
            continue
        block = matching[0]
        if light not in block or dark not in block:
            errors.append(f"Incomplete light/dark pair in README: {light}/{dark}")
        fallback = re.search(r'<img\s+[^>]*src="([^"]+)"', block, flags=re.IGNORECASE)
        if not fallback or not fallback.group(1).endswith(light):
            errors.append(f"Picture fallback must use light asset: {light}")

    for url in PROJECT_URLS:
        if markdown.count(url) != 1:
            errors.append(f"Expected one featured project link: {url}")

    for path in SUMMARY_REFERENCES:
        if path not in markdown:
            errors.append(f"README missing summary-card reference: {path}")
    for ref in sorted(local_references(markdown)):
        if not (ROOT / ref).is_file():
            errors.append(f"README references missing local file: {ref}")

    required_sections = ["## 关于我", "## 技术能力", "## 精选项目", "## 开发数据", "## 贡献轨迹", "## 当前方向"]
    for section in required_sections:
        if markdown.count(section) != 1:
            errors.append(f"README must contain exactly one section: {section}")

    workflow_tokens = [
        "python3 .github/scripts/style_summary_cards.py",
        "THEME: github\n",
        "THEME: github_dark\n",
        "color_snake=%230071E3",
        "color_snake=%230A84FF",
        "color_dots=%23EBEDF0,%23D6E8FA,%239AC7F7,%235AA7F2,%230071E3",
        "color_dots=%231C1C1E,%232C3E50,%233D5F7A,%235A8DB8,%230A84FF",
    ]
    for token in workflow_tokens:
        if token not in workflow:
            errors.append(f"Workflow missing required Editorial 2.0 token: {token}")

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
