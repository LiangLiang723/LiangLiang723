#!/usr/bin/env python3
"""Generate deterministic Linear-inspired SVG assets for the GitHub profile."""
from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "linear"
STATS_PATH = OUT / "profile-stats.json"
WIDTH = 1200
FONT = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif"


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    surface: str
    grid: str
    text: str
    secondary: str
    border: str
    accent: str
    accent_secondary: str


LIGHT = Theme(
    name="light",
    background="#F7F7F8",
    surface="#FAFAFB",
    grid="#1717190A",
    text="#171719",
    secondary="#6B6B70",
    border="#17171916",
    accent="#6E56CF",
    accent_secondary="#5E6AD2",
)

DARK = Theme(
    name="dark",
    background="#0F1012",
    surface="#121316",
    grid="#FFFFFF0A",
    text="#F7F7F8",
    secondary="#96969D",
    border="#FFFFFF1A",
    accent="#8B7CF6",
    accent_secondary="#6E7BF2",
)


def load_stats(path: Path = STATS_PATH) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    public_repos = payload.get("public_repos")
    contributions = payload.get("contributions")
    primary_language = payload.get("primary_language")
    updated_at = payload.get("updated_at")
    if not isinstance(public_repos, int) or public_repos < 0:
        raise ValueError("public_repos must be a non-negative integer")
    if not isinstance(contributions, int) or contributions < 0:
        raise ValueError("contributions must be a non-negative integer")
    if not isinstance(primary_language, str) or not primary_language.strip():
        raise ValueError("primary_language must be a non-empty string")
    if not isinstance(updated_at, str) or not updated_at.strip():
        raise ValueError("updated_at must be a non-empty string")
    return {
        "public_repos": public_repos,
        "contributions": contributions,
        "primary_language": primary_language.strip(),
        "updated_at": updated_at,
    }


def svg_document(*, title: str, description: str, height: int, body: str, theme: Theme) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="{theme.grid}" stroke-width="1"/>
    </pattern>
    <radialGradient id="glowA" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="{theme.accent}" stop-opacity="0.26"/>
      <stop offset="0.52" stop-color="{theme.accent}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{theme.accent}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowB" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="{theme.accent_secondary}" stop-opacity="0.20"/>
      <stop offset="1" stop-color="{theme.accent_secondary}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="accentLine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{theme.accent}"/>
      <stop offset="1" stop-color="{theme.accent_secondary}"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: {FONT}; }}
    .display {{ font-weight: 720; letter-spacing: -2px; }}
    .title {{ font-weight: 650; letter-spacing: -0.35px; }}
    .body {{ font-weight: 430; }}
    .label {{ font-weight: 560; letter-spacing: 0.15px; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
{body}
</svg>
'''


def render_hero(theme: Theme) -> str:
    height = 238
    body = f'''  <rect x="1" y="1" width="1198" height="236" rx="18" fill="{theme.background}" stroke="{theme.border}" stroke-width="1"/>
  <rect x="1" y="1" width="1198" height="236" rx="18" fill="url(#grid)"/>
  <ellipse cx="1035" cy="94" rx="235" ry="180" fill="url(#glowA)"/>
  <ellipse cx="1105" cy="174" rx="160" ry="118" fill="url(#glowB)"/>
  <rect x="54" y="39" width="42" height="2" rx="1" fill="url(#accentLine)"/>
  <text x="54" y="69" font-size="15" fill="{theme.secondary}" class="label">LiangLiang723</text>
  <text x="51" y="129" font-size="52" fill="{theme.text}" class="display">亮亮</text>
  <text x="54" y="163" font-size="21" fill="{theme.text}" class="title">嵌入式软件工程师</text>
  <text x="54" y="199" font-size="17" fill="{theme.secondary}" class="body">专注设备控制、RTOS 与可靠软件架构。</text>
  <g opacity="0.68">
    <circle cx="1052" cy="112" r="4" fill="{theme.accent}"/>
    <line x1="1052" y1="112" x2="1122" y2="72" stroke="{theme.border}"/>
    <line x1="1052" y1="112" x2="1114" y2="158" stroke="{theme.border}"/>
    <circle cx="1122" cy="72" r="3" fill="{theme.accent_secondary}"/>
    <circle cx="1114" cy="158" r="3" fill="{theme.accent_secondary}"/>
  </g>
'''
    return svg_document(
        title=f"亮亮的 Linear 风格主页横幅（{theme.name}）",
        description="显示 LiangLiang723、亮亮、嵌入式软件工程师和开发方向",
        height=height,
        body=body,
        theme=theme,
    )


def stat_item(x: int, *, label: str, value: str, theme: Theme) -> str:
    return f'''  <text x="{x}" y="52" font-size="14" fill="{theme.secondary}" class="label">{escape(label)}</text>
  <text x="{x}" y="91" font-size="29" fill="{theme.text}" class="title">{escape(value)}</text>
'''


def render_stats(theme: Theme, stats: dict[str, object]) -> str:
    height = 132
    body = f'''  <rect x="1" y="1" width="1198" height="130" rx="16" fill="{theme.background}" stroke="{theme.border}" stroke-width="1"/>
  <rect x="1" y="1" width="1198" height="130" rx="16" fill="url(#grid)" opacity="0.42"/>
  <rect x="52" y="32" width="3" height="66" rx="1.5" fill="url(#accentLine)"/>
{stat_item(78, label='公开仓库', value=str(stats['public_repos']), theme=theme)}
  <line x1="380" y1="32" x2="380" y2="100" stroke="{theme.border}"/>
{stat_item(430, label='过去一年贡献', value=str(stats['contributions']), theme=theme)}
  <line x1="750" y1="32" x2="750" y2="100" stroke="{theme.border}"/>
{stat_item(800, label='主要语言', value=str(stats['primary_language']), theme=theme)}
  <circle cx="1137" cy="65" r="5" fill="{theme.accent}"/>
  <circle cx="1137" cy="65" r="12" fill="none" stroke="{theme.accent}" stroke-opacity="0.22"/>
'''
    return svg_document(
        title=f"亮亮的精简开发数据（{theme.name}）",
        description=f"公开仓库 {stats['public_repos']}，过去一年贡献 {stats['contributions']}，主要语言 {stats['primary_language']}",
        height=height,
        body=body,
        theme=theme,
    )


def write_asset(name: str, content: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    stats = load_stats()
    for theme in (LIGHT, DARK):
        write_asset(f"hero-{theme.name}.svg", render_hero(theme))
        write_asset(f"stats-{theme.name}.svg", render_stats(theme, stats))
    files = sorted(path.name for path in OUT.glob("*.svg"))
    expected = ["hero-dark.svg", "hero-light.svg", "stats-dark.svg", "stats-light.svg"]
    if files != expected:
        raise RuntimeError(f"Expected {expected}, generated {files}")
    print("Generated 4 Linear profile assets.")


if __name__ == "__main__":
    main()
