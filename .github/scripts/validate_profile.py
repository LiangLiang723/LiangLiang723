#!/usr/bin/env python3
"""Validate the Apple Editorial 2.0 GitHub profile and workflow wiring."""
from __future__ import annotations

import argparse
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
SUMMARY_ROOT = ROOT / "profile-summary-card-output"

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

SUMMARY_FILES = {"0-profile-details.svg", "1-repos-per-language.svg", "3-stats.svg"}
SUMMARY_REFERENCES = [
    f"profile-summary-card-output/{theme}/{name}"
    for theme in ("github", "github_dark")
    for name in sorted(SUMMARY_FILES)
]
SUMMARY_PALETTES = {
    "github": {"surface": "#FFFFFF", "border": "#D2D2D7", "accent": "#0071E3"},
    "github_dark": {"surface": "#1C1C1E", "border": "#38383A", "accent": "#0A84FF"},
}
SUMMARY_LOCALIZED_TOKENS = {
    "0-profile-details.svg": ("GitHub 贡献：", "公开仓库：", "加入 GitHub："),
    "1-repos-per-language.svg": ("主要编程语言",),
    "3-stats.svg": ("开发统计", "星标数：", "提交数：", "合并请求：", "议题数：", "参与仓库："),
}

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
    if hash_a != hashes():
        errors.append("Asset generator is not deterministic across consecutive runs")


def validate_summary_cards(errors: list[str]) -> None:
    for theme, palette in SUMMARY_PALETTES.items():
        theme_dir = SUMMARY_ROOT / theme
        if not theme_dir.is_dir():
            errors.append(f"Missing generated summary theme directory: {theme_dir.relative_to(ROOT)}")
            continue
        files = {path.name for path in theme_dir.iterdir() if path.is_file()}
        for name in sorted(SUMMARY_FILES - files):
            errors.append(f"Missing generated summary card: {theme_dir.relative_to(ROOT)}/{name}")
        for name in sorted(files - SUMMARY_FILES):
            errors.append(f"Unexpected generated summary file: {theme_dir.relative_to(ROOT)}/{name}")
        for name in sorted(SUMMARY_FILES & files):
            path = theme_dir / name
            raw = path.read_text(encoding="utf-8")
            try:
                ET.fromstring(raw)
            except ET.ParseError as exc:
                errors.append(f"Invalid summary-card XML in {path.relative_to(ROOT)}: {exc}")
                continue
            for token in (palette["surface"], palette["border"], palette["accent"], 'rx="18"', "system-ui"):
                if token not in raw:
                    errors.append(f"{path.relative_to(ROOT)} is missing Editorial summary token: {token}")
            for token in SUMMARY_LOCALIZED_TOKENS[name]:
                if token not in raw:
                    errors.append(f"{path.relative_to(ROOT)} is missing localized label: {token}")


def validate(*, require_summary_cards: bool = False) -> list[str]:
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
    if require_summary_cards:
        validate_summary_cards(errors)

    for ref in sorted(local_references(markdown)):
        if ref.startswith("profile-summary-card-output/") and not require_summary_cards:
            continue
        if not (ROOT / ref).is_file():
            errors.append(f"README references missing local file: {ref}")

    required_sections = ["## 关于我", "## 技术能力", "## 精选项目", "## 开发数据", "## 贡献轨迹", "## 当前方向"]
    for section in required_sections:
        if markdown.count(section) != 1:
            errors.append(f"README must contain exactly one section: {section}")

    workflow_tokens = [
        "python3 .github/scripts/style_summary_cards.py",
        "python3 .github/scripts/validate_profile.py --require-summary-cards",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-summary-cards",
        action="store_true",
        help="Require generated and styled summary-card SVG files to exist. Use after the build step.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate(require_summary_cards=args.require_summary_cards)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Profile validation failed with {len(errors)} error(s).")
        return 1
    mode = "full" if args.require_summary_cards else "structural"
    print(f"Profile validation passed ({mode}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
