#!/usr/bin/env python3
"""Generate deterministic Apple Editorial 2.0 SVG assets for the GitHub profile."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "apple"
WIDTH = 1200
CARD_X = 8
CARD_W = WIDTH - CARD_X * 2
LARGE_RADIUS = 24
SMALL_RADIUS = 18
FONT = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif"


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    surface: str
    surface_subtle: str
    text: str
    secondary: str
    border: str
    accent: str
    shadow: str


LIGHT = Theme(
    name="light",
    background="#FFFFFF",
    surface="#FFFFFF",
    surface_subtle="#F5F5F7",
    text="#1D1D1F",
    secondary="#6E6E73",
    border="#D2D2D7",
    accent="#0071E3",
    shadow="#00000018",
)

DARK = Theme(
    name="dark",
    background="#1C1C1E",
    surface="#1C1C1E",
    surface_subtle="#2C2C2E",
    text="#F5F5F7",
    secondary="#A1A1A6",
    border="#38383A",
    accent="#0A84FF",
    shadow="#00000000",
)


def svg_document(*, title: str, description: str, height: int, body: str, theme: Theme) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <linearGradient id="heroSurface" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{theme.surface}"/>
      <stop offset="1" stop-color="{theme.surface_subtle}"/>
    </linearGradient>
    <radialGradient id="blueOrb" cx="32%" cy="26%" r="74%">
      <stop offset="0" stop-color="{theme.accent}" stop-opacity="0.28"/>
      <stop offset="0.58" stop-color="{theme.accent}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{theme.accent}" stop-opacity="0.04"/>
    </radialGradient>
    <filter id="cardShadow" x="-10%" y="-20%" width="120%" height="150%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="{theme.shadow}"/>
    </filter>
  </defs>
  <style>
    text {{ font-family: {FONT}; }}
    .display {{ font-weight: 760; letter-spacing: -2.2px; }}
    .title {{ font-weight: 700; letter-spacing: -0.5px; }}
    .body {{ font-weight: 460; }}
    .label {{ font-weight: 620; letter-spacing: 0.1px; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
{body}
</svg>
'''


def rect(x: int, y: int, w: int, h: int, r: int, *, fill: str, stroke: str = "none", shadow: bool = False) -> str:
    filter_attr = ' filter="url(#cardShadow)"' if shadow else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1"{filter_attr}/>'


def text(x: int, y: int, value: str, *, size: int, fill: str, cls: str = "body", anchor: str = "start", opacity: float | None = None) -> str:
    opacity_attr = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" class="{cls}" text-anchor="{anchor}"{opacity_attr}>{escape(value)}</text>'


def multiline_text(x: int, y: int, lines: Sequence[str], *, size: int, fill: str, line_height: int, cls: str = "body", anchor: str = "start") -> str:
    tspans = []
    for index, line in enumerate(lines):
        dy = "0" if index == 0 else str(line_height)
        tspans.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" class="{cls}" text-anchor="{anchor}">{"".join(tspans)}</text>'


def card(height: int, theme: Theme, *, fill: str | None = None) -> str:
    return rect(CARD_X, 8, CARD_W, height - 16, LARGE_RADIUS, fill=fill or theme.surface, stroke=theme.border, shadow=theme.name == "light")


def chip(x: int, y: int, label: str, *, width: int, theme: Theme, height: int = 42) -> str:
    return "\n".join([
        rect(x, y, width, height, SMALL_RADIUS, fill=theme.surface_subtle, stroke=theme.border),
        f'<circle cx="{x + 22}" cy="{y + height // 2}" r="5" fill="{theme.accent}"/>',
        text(x + 38, y + height // 2 + 6, label, size=16, fill=theme.text, cls="label"),
    ])


def render_hero(theme: Theme) -> str:
    height = 300
    body = f'''  {card(height, theme, fill='url(#heroSurface)')}
  <circle cx="1010" cy="148" r="78" fill="url(#blueOrb)"/>
  <circle cx="985" cy="122" r="24" fill="{theme.accent}" opacity="0.08"/>
  {text(60, 54, '你好，我是亮亮', size=17, fill=theme.accent, cls='label')}
  {text(56, 116, 'LiangLiang723', size=58, fill=theme.text, cls='display')}
  {text(60, 153, '嵌入式软件工程师', size=24, fill=theme.secondary, cls='title')}
  {text(60, 205, '让复杂系统保持清晰，', size=22, fill=theme.text, cls='title')}
  {text(60, 236, '让可靠软件持续演进。', size=22, fill=theme.text, cls='title')}
  {text(60, 271, 'C / C++ · RTOS · STM32 · Flutter', size=16, fill=theme.secondary, cls='label')}
'''
    return svg_document(title=f"亮亮的 Apple Editorial 2.0 主页首屏（{theme.name}）", description="显示 LiangLiang723、嵌入式软件工程师身份、开发理念和核心技术方向", height=height, body=body, theme=theme)


def render_profile(theme: Theme) -> str:
    height = 214
    columns = [
        (56, "设备与控制", ("嵌入式软件、设备通信", "与控制系统")),
        (424, "架构与实时系统", ("RTOS、任务调度、状态管理", "与可维护架构")),
        (792, "应用与自动化", ("Flutter、Docker、自托管服务", "与 AI 辅助开发")),
    ]
    chunks = [f"  {card(height, theme)}"]
    for x, heading, lines in columns:
        chunks.extend([
            f'<circle cx="{x}" cy="62" r="6" fill="{theme.accent}"/>',
            text(x + 18, 69, heading, size=21, fill=theme.text, cls="title"),
            multiline_text(x, 112, lines, size=17, fill=theme.secondary, line_height=28),
        ])
    return svg_document(title=f"关于亮亮（{theme.name}）", description="设备控制、实时系统架构、应用开发与自动化能力概览", height=height, body="\n".join(chunks), theme=theme)


def tech_row(y: int, heading: str, labels: Iterable[str], theme: Theme) -> str:
    chunks = [text(52, y + 29, heading, size=18, fill=theme.secondary, cls="label")]
    x = 240
    for label in labels:
        width = max(96, 58 + len(label) * 14)
        chunks.append(chip(x, y, label, width=width, theme=theme, height=42))
        x += width + 12
    return "\n".join(chunks)


def render_tech_stack(theme: Theme) -> str:
    height = 246
    body = f'''  {card(height, theme)}
  {tech_row(31, '嵌入式开发', ('C', 'C++', 'STM32', 'FreeRTOS', 'Zephyr'), theme)}
  {tech_row(102, '应用开发', ('Flutter', 'Python', 'Go'), theme)}
  {tech_row(173, '基础设施', ('Docker', 'Linux', 'Git'), theme)}
'''
    return svg_document(title=f"亮亮的技术能力（{theme.name}）", description="嵌入式开发、应用开发和基础设施技术索引", height=height, body=body, theme=theme)


def tag(x: int, y: int, value: str, *, theme: Theme, width: int) -> str:
    return "\n".join([
        rect(x, y, width, 42, SMALL_RADIUS, fill=theme.surface_subtle, stroke=theme.border),
        text(x + width // 2, y + 27, value, size=16, fill=theme.secondary, cls="label", anchor="middle"),
    ])


def render_project(theme: Theme, *, title_value: str, subtitle: str, tags: tuple[str, ...], symbol: str) -> str:
    height = 252
    chunks = [f"  {card(height, theme)}"]
    chunks.extend([
        f'<circle cx="62" cy="61" r="22" fill="{theme.accent}" opacity="0.12"/>',
        text(62, 69, symbol, size=22, fill=theme.accent, cls="title", anchor="middle"),
        text(102, 72, title_value, size=39, fill=theme.text, cls="display"),
        text(1138, 70, "↗", size=30, fill=theme.accent, cls="title", anchor="end"),
        text(54, 132, subtitle, size=24, fill=theme.secondary),
    ])
    x = 54
    for value in tags[:3]:
        width = max(116, 54 + len(value) * 17)
        chunks.append(tag(x, 178, value, theme=theme, width=width))
        x += width + 12
    return svg_document(title=f"项目：{title_value}（{theme.name}）", description=subtitle, height=height, body="\n".join(chunks), theme=theme)


def render_focus(theme: Theme) -> str:
    height = 218
    items = [
        (44, "⌘", "嵌入式架构", "模块边界与状态流转"),
        (328, "◴", "RTOS", "任务、事件与消息机制"),
        (612, "◇", "个人知识管理", "Markdown 与多端同步"),
        (896, "✦", "AI 辅助开发", "Agent 工作流与自动化"),
    ]
    chunks = [f"  {card(height, theme)}"]
    for x, symbol, heading, desc in items:
        chunks.extend([
            rect(x, 38, 260, 142, SMALL_RADIUS, fill=theme.surface_subtle, stroke=theme.border),
            f'<circle cx="{x + 34}" cy="74" r="18" fill="{theme.accent}" opacity="0.12"/>',
            text(x + 34, 81, symbol, size=18, fill=theme.accent, cls="title", anchor="middle"),
            text(x + 62, 81, heading, size=20, fill=theme.text, cls="title"),
            text(x + 24, 132, desc, size=16, fill=theme.secondary),
        ])
    return svg_document(title=f"亮亮当前关注方向（{theme.name}）", description="嵌入式架构、RTOS、个人知识管理和 AI 辅助开发", height=height, body="\n".join(chunks), theme=theme)


def render_footer(theme: Theme) -> str:
    height = 78
    body = f'''  <line x1="40" y1="20" x2="1160" y2="20" stroke="{theme.border}" stroke-width="1"/>
  {text(600, 55, 'Keep systems clear. Ship reliable software.', size=16, fill=theme.secondary, cls='label', anchor='middle')}
'''
    return svg_document(title=f"亮亮主页页尾（{theme.name}）", description="简洁分隔线与开发理念", height=height, body=body, theme=theme)


def write_asset(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    projects = [
        ("project-ai-berkshire", "AI Berkshire", "面向 AI 时代的价值投资研究框架", ("AI Agent", "Research", "Skills"), "◎"),
        ("project-supercom", "SuperCom", "服务嵌入式联调的串口通信与设备调试工具", ("Serial", "Device", "Debug"), "⌁"),
        ("project-multitimer", "MultiTimer", "用于周期任务、延时任务与状态调度的多定时器", ("Timer", "Scheduler", "MCU"), "◷"),
        ("project-learning", "English Level Up Tips", "结构化整理英语学习资料与持续实践方法", ("Learning", "Markdown", "Open Source"), "A"),
    ]
    for theme in (LIGHT, DARK):
        write_asset(f"hero-{theme.name}.svg", render_hero(theme))
        write_asset(f"profile-{theme.name}.svg", render_profile(theme))
        write_asset(f"tech-stack-{theme.name}.svg", render_tech_stack(theme))
        for key, project_title, subtitle, tags, symbol in projects:
            write_asset(f"{key}-{theme.name}.svg", render_project(theme, title_value=project_title, subtitle=subtitle, tags=tags, symbol=symbol))
        write_asset(f"focus-{theme.name}.svg", render_focus(theme))
        write_asset(f"footer-{theme.name}.svg", render_footer(theme))
    files = sorted(OUT.glob("*.svg"))
    if len(files) != 18:
        raise RuntimeError(f"Expected 18 assets, generated {len(files)}")
    print("Generated 18 Apple Editorial 2.0 profile assets.")


if __name__ == "__main__":
    main()
