#!/usr/bin/env python3
"""Normalize generated profile summary cards to Apple Editorial 2.0 styling."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SUMMARY_ROOT = ROOT / "profile-summary-card-output"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


@dataclass(frozen=True)
class Palette:
    surface: str
    border: str
    accent: str
    secondary: str
    chart: tuple[str, ...]


PALETTES = {
    "github": Palette(
        surface="#FFFFFF",
        border="#D2D2D7",
        accent="#0071E3",
        secondary="#6E6E73",
        chart=("#0071E3", "#5AA7F2", "#9AC7F7", "#D6E8FA"),
    ),
    "github_dark": Palette(
        surface="#1C1C1E",
        border="#38383A",
        accent="#0A84FF",
        secondary="#A1A1A6",
        chart=("#0A84FF", "#5A8DB8", "#3D5F7A", "#2C3E50"),
    ),
}

KEEP_FILES = {"0-profile-details.svg", "1-repos-per-language.svg", "3-stats.svg"}


def split_style(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in value.split(";"):
        if ":" not in item:
            continue
        key, raw = item.split(":", 1)
        result[key.strip()] = raw.strip()
    return result


def join_style(values: dict[str, str]) -> str:
    return "; ".join(f"{key}: {value}" for key, value in values.items()) + ";"


def style_card(path: Path, palette: Palette) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    rects = list(root.iter(f"{{{SVG_NS}}}rect"))
    if not rects:
        raise ValueError(f"No background rect in {path}")
    background = rects[0]
    background.set("rx", "18")
    background.set("ry", "18")
    background.set("fill", palette.surface)
    background.set("stroke", palette.border)
    background.set("stroke-opacity", "1")

    texts = list(root.iter(f"{{{SVG_NS}}}text"))
    for index, node in enumerate(texts):
        style = split_style(node.get("style", ""))
        style["fill"] = palette.accent if index == 0 else palette.secondary
        node.set("style", join_style(style))

    icon_groups = [node for node in root.iter(f"{{{SVG_NS}}}g") if node.get("fill")]
    for node in icon_groups:
        node.set("fill", palette.accent)

    chart_nodes = rects[1:] + list(root.iter(f"{{{SVG_NS}}}path"))
    color_index = 0
    for node in chart_nodes:
        fill = node.get("fill")
        style = split_style(node.get("style", ""))
        style_fill = style.get("fill")
        candidate = style_fill or fill
        if not candidate or candidate in {"none", palette.surface, palette.secondary, palette.accent}:
            continue
        if path.name == "3-stats.svg" and node.tag.endswith("path"):
            node.set("fill", palette.accent)
            continue
        color = palette.chart[color_index % len(palette.chart)]
        color_index += 1
        if style_fill:
            style["fill"] = color
            node.set("style", join_style(style))
        else:
            node.set("fill", color)
        if node.get("stroke"):
            node.set("stroke", palette.surface)

    if path.name == "3-stats.svg":
        groups = list(root.iter(f"{{{SVG_NS}}}g"))
        for node in groups:
            transform = node.get("transform", "")
            if "scale(6)" in transform:
                node.set("style", f"fill: {palette.accent}; opacity: 0.16;")

    tree.write(path, encoding="unicode", xml_declaration=False)
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    styled = 0
    for theme_name, palette in PALETTES.items():
        theme_dir = SUMMARY_ROOT / theme_name
        if not theme_dir.is_dir():
            raise FileNotFoundError(f"Missing summary theme directory: {theme_dir}")
        for path in sorted(theme_dir.glob("*.svg")):
            if path.name in KEEP_FILES:
                style_card(path, palette)
                styled += 1
    if styled != 6:
        raise RuntimeError(f"Expected to style 6 summary cards, styled {styled}")
    print("Styled 6 Apple Editorial 2.0 summary cards.")


if __name__ == "__main__":
    main()
