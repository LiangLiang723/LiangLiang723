#!/usr/bin/env python3
"""Validate the GitHub profile README, Apple SVG assets, and workflow wiring."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "profile.yml"
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

FORBIDDEN = [
    "img.shields.io",
    "github-readme-stats.vercel.app",
    "capsule-render",
]

OLD_ASSETS = [
    "assets/header.svg",
    "assets/profile-badges.svg",
    "assets/tech-stack.svg",
    "assets/footer-line.svg",
]


def local_references(markdown: str) -> set[str]:
    refs = set()
    for match in re.finditer(r'(?:src|srcset)="(\./[^"?#]+)', markdown):
        refs.add(match.group(1)[2:])
    return refs


def validate() -> list[str]:
    errors: list[str] = []
    if not README.is_file():
        errors.append("Missing README.md")
        return errors
    if not WORKFLOW.is_file():
        errors.append("Missing .github/workflows/profile.yml")
    markdown = README.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""

    existing = {p.name for p in APPLE_DIR.glob("*.svg")} if APPLE_DIR.is_dir() else set()
    for name in sorted(EXPECTED_ASSETS - existing):
        errors.append(f"Missing Apple asset: assets/apple/{name}")
    unexpected = existing - EXPECTED_ASSETS
    for name in sorted(unexpected):
        errors.append(f"Unexpected Apple asset: assets/apple/{name}")

    ns = {"svg": "http://www.w3.org/2000/svg"}
    for name in sorted(existing & EXPECTED_ASSETS):
        path = APPLE_DIR / name
        try:
            root = ET.parse(path).getroot()
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
        if "prefers-reduced-motion" not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)} lacks reduced-motion handling")

    for token in FORBIDDEN:
        if token in markdown:
            errors.append(f"README contains forbidden external dependency: {token}")

    picture_blocks = re.findall(r"<picture>.*?</picture>", markdown, flags=re.DOTALL | re.IGNORECASE)
    for light, dark in CUSTOM_PAIRS:
        matching = [block for block in picture_blocks if light in block or dark in block]
        if len(matching) != 1:
            errors.append(f"Expected exactly one picture block for {light}/{dark}, found {len(matching)}")
            continue
        block = matching[0]
        if light not in block or dark not in block:
            errors.append(f"Incomplete light/dark pair in README: {light}/{dark}")
        fallback_match = re.search(r'<img\s+[^>]*src="([^"]+)"', block, flags=re.IGNORECASE)
        if not fallback_match or not fallback_match.group(1).endswith(light):
            errors.append(f"Picture fallback must use light asset: {light}")

    for url in PROJECT_URLS:
        if markdown.count(url) != 1:
            errors.append(f"Expected one featured project link: {url}")

    summary_requirements = [
        "profile-summary-card-output/github/0-profile-details.svg",
        "profile-summary-card-output/github_dark/0-profile-details.svg",
        "profile-summary-card-output/github/1-repos-per-language.svg",
        "profile-summary-card-output/github_dark/1-repos-per-language.svg",
        "profile-summary-card-output/github/3-stats.svg",
        "profile-summary-card-output/github_dark/3-stats.svg",
    ]
    for path in summary_requirements:
        if path not in markdown:
            errors.append(f"README missing summary-card theme reference: {path}")

    if "THEME: github\n" not in workflow:
        errors.append("Workflow missing THEME: github step")
    if "THEME: github_dark\n" not in workflow:
        errors.append("Workflow missing THEME: github_dark step")
    if "python3 .github/scripts/validate_profile.py" not in workflow:
        errors.append("Workflow does not run profile validation")

    for old in OLD_ASSETS:
        if old in markdown:
            errors.append(f"README still references old asset: {old}")
        if (ROOT / old).exists():
            errors.append(f"Obsolete asset still exists: {old}")

    for ref in sorted(local_references(markdown)):
        if ref.startswith("profile-summary-card-output/"):
            continue
        if not (ROOT / ref).is_file():
            errors.append(f"README references missing local file: {ref}")

    required_sections = ["## 关于我", "## 技术能力", "## 精选项目", "## 开发数据", "## 贡献轨迹", "## 当前方向"]
    for section in required_sections:
        if markdown.count(section) != 1:
            errors.append(f"README must contain exactly one section: {section}")

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
