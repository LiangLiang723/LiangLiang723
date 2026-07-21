#!/usr/bin/env python3
"""Generate deterministic Apple-inspired SVG assets for the GitHub profile."""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "apple"


@dataclass(frozen=True)
class Theme:
    name: str
    canvas: str
    canvas_2: str
    surface: str
    surface_alt: str
    text: str
    secondary: str
    tertiary: str
    border: str
    border_strong: str
    blue: str
    blue_soft: str
    cyan: str
    green: str
    orange: str
    purple: str
    shadow: str
    highlight: str


LIGHT = Theme(
    name="light",
    canvas="#F5F5F7",
    canvas_2="#FFFFFF",
    surface="#FFFFFF",
    surface_alt="#F9F9FB",
    text="#1D1D1F",
    secondary="#515154",
    tertiary="#86868B",
    border="#D2D2D7",
    border_strong="#B7B7BC",
    blue="#0071E3",
    blue_soft="#E8F2FF",
    cyan="#32ADE6",
    green="#34C759",
    orange="#FF9F0A",
    purple="#AF52DE",
    shadow="#00000018",
    highlight="#FFFFFFCC",
)

DARK = Theme(
    name="dark",
    canvas="#000000",
    canvas_2="#101012",
    surface="#1C1C1E",
    surface_alt="#242426",
    text="#F5F5F7",
    secondary="#D1D1D6",
    tertiary="#98989D",
    border="#3A3A3C",
    border_strong="#545458",
    blue="#0A84FF",
    blue_soft="#0A2A4A",
    cyan="#64D2FF",
    green="#30D158",
    orange="#FF9F0A",
    purple="#BF5AF2",
    shadow="#00000066",
    highlight="#FFFFFF16",
)

FONT = "system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif"


def svg_document(*, title: str, description: str, height: int, body: str, theme: Theme) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(description)}</desc>
  <defs>
    <linearGradient id="canvas" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{theme.canvas_2}"/>
      <stop offset="1" stop-color="{theme.canvas}"/>
    </linearGradient>
    <linearGradient id="blueOrb" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{theme.cyan}"/>
      <stop offset="0.56" stop-color="{theme.blue}"/>
      <stop offset="1" stop-color="{theme.purple}"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{theme.highlight}"/>
      <stop offset="1" stop-color="{theme.surface}"/>
    </linearGradient>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="180%">
      <feDropShadow dx="0" dy="18" stdDeviation="24" flood-color="{theme.shadow}"/>
    </filter>
    <filter id="smallShadow" x="-30%" y="-30%" width="160%" height="180%">
      <feDropShadow dx="0" dy="7" stdDeviation="12" flood-color="{theme.shadow}"/>
    </filter>
  </defs>
  <style>
    text {{ font-family: {FONT}; }}
    .display {{ font-weight: 760; letter-spacing: -2.2px; }}
    .title {{ font-weight: 720; letter-spacing: -0.6px; }}
    .body {{ font-weight: 460; }}
    .label {{ font-weight: 620; letter-spacing: 0.2px; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
{body}
</svg>
'''


def round_rect(x: int, y: int, w: int, h: int, r: int, *, fill: str, stroke: str, filter_id: str | None = None, stroke_width: float = 1) -> str:
    filt = f' filter="url(#{filter_id})"' if filter_id else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{filt}/>'


def text(x: int, y: int, value: str, *, size: int, fill: str, cls: str = "body", anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" class="{cls}" text-anchor="{anchor}">{escape(value)}</text>'


def pill(x: int, y: int, label: str, *, width: int, theme: Theme, accent: str | None = None) -> str:
    accent = accent or theme.blue
    return "\n".join([
        round_rect(x, y, width, 42, 21, fill=theme.surface_alt, stroke=theme.border),
        f'<circle cx="{x + 22}" cy="{y + 21}" r="6" fill="{accent}"/>',
        text(x + 38, y + 27, label, size=15, fill=theme.secondary, cls="label"),
    ])


def divider(y: int, theme: Theme, x1: int = 56, x2: int = 1144) -> str:
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{theme.border}" stroke-width="1"/>'


def render_hero(theme: Theme) -> str:
    body = f'''  <rect width="1200" height="390" rx="34" fill="url(#canvas)"/>
  <g filter="url(#shadow)">
    {round_rect(30, 28, 1140, 334, 34, fill='url(#glass)', stroke=theme.border)}
  </g>
  <circle cx="1015" cy="190" r="116" fill="url(#blueOrb)" opacity="0.96"/>
  <circle cx="978" cy="151" r="46" fill="#FFFFFF" opacity="0.18"/>
  <path d="M958 229c36 21 93 16 128-21" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" opacity="0.26"/>
  {text(82, 92, 'Hello, I’m 亮亮', size=20, fill=theme.blue, cls='label')}
  {text(78, 166, 'LiangLiang723', size=66, fill=theme.text, cls='display')}
  {text(82, 211, '嵌入式软件工程师', size=28, fill=theme.secondary, cls='title')}
  {text(82, 257, '让复杂系统保持清晰，让可靠软件持续演进。', size=20, fill=theme.secondary)}
  {pill(82, 292, 'C / C++', width=132, theme=theme, accent=theme.blue)}
  {pill(226, 292, 'RTOS', width=112, theme=theme, accent=theme.green)}
  {pill(350, 292, 'STM32', width=122, theme=theme, accent=theme.cyan)}
  {pill(484, 292, 'Flutter', width=128, theme=theme, accent=theme.blue)}
  {pill(624, 292, 'Self-hosted', width=158, theme=theme, accent=theme.purple)}
'''
    return svg_document(title=f"亮亮的 Apple 风格主页首屏（{theme.name}）", description="显示 LiangLiang723、嵌入式软件工程师身份、开发理念与核心技术方向", height=390, body=body, theme=theme)


def render_profile(theme: Theme) -> str:
    items = [
        ("01", "设备与控制", "嵌入式软件、设备通信与控制系统", theme.blue),
        ("02", "架构与实时系统", "RTOS、任务调度、状态管理与可维护架构", theme.green),
        ("03", "应用与自动化", "Flutter、Docker、自托管服务与 AI 辅助开发", theme.purple),
    ]
    chunks = [f'  <rect width="1200" height="260" rx="30" fill="url(#canvas)"/>']
    for i, (num, title_value, desc, accent) in enumerate(items):
        x = 40 + i * 380
        chunks.extend([
            round_rect(x, 34, 360, 192, 28, fill=theme.surface, stroke=theme.border, filter_id="smallShadow"),
            f'<circle cx="{x + 54}" cy="88" r="24" fill="{accent}" opacity="0.14"/>',
            text(x + 54, 95, num, size=15, fill=accent, cls="label", anchor="middle"),
            text(x + 32, 140, title_value, size=24, fill=theme.text, cls="title"),
            text(x + 32, 176, desc, size=16, fill=theme.secondary),
            f'<line x1="{x + 32}" y1="198" x2="{x + 112}" y2="198" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>',
        ])
    return svg_document(title=f"关于亮亮（{theme.name}）", description="三张卡片介绍设备控制、实时系统架构、应用与自动化方向", height=260, body="\n".join(chunks), theme=theme)


def tech_row(y: int, heading: str, items: Iterable[tuple[str, str]], theme: Theme) -> str:
    chunks = [text(74, y + 30, heading, size=18, fill=theme.tertiary, cls="label")]
    x = 260
    for label, accent in items:
        width = 42 + max(62, len(label) * 15)
        chunks.extend([
            round_rect(x, y, width, 52, 18, fill=theme.surface_alt, stroke=theme.border),
            f'<circle cx="{x + 24}" cy="{y + 26}" r="7" fill="{accent}"/>',
            text(x + 42, y + 33, label, size=16, fill=theme.text, cls="label"),
        ])
        x += width + 14
    return "\n".join(chunks)


def render_tech_stack(theme: Theme) -> str:
    body = f'''  <rect width="1200" height="340" rx="30" fill="url(#canvas)"/>
  {round_rect(40, 28, 1120, 284, 30, fill=theme.surface, stroke=theme.border, filter_id='smallShadow')}
  {text(74, 76, 'Technical capabilities', size=26, fill=theme.text, cls='title')}
  {text(1090, 75, 'Focused · Reliable · Maintainable', size=14, fill=theme.tertiary, cls='label', anchor='end')}
  {divider(98, theme, 74, 1126)}
  {tech_row(118, 'Embedded', [('C', theme.blue), ('C++', theme.blue), ('STM32', theme.cyan), ('FreeRTOS', theme.green), ('Zephyr', theme.purple)], theme)}
  {tech_row(183, 'Application', [('Flutter', theme.blue), ('Python', theme.orange), ('Go', theme.cyan)], theme)}
  {tech_row(248, 'Infrastructure', [('Docker', theme.blue), ('Linux', theme.orange), ('Git', theme.purple)], theme)}
'''
    return svg_document(title=f"亮亮的技术能力（{theme.name}）", description="嵌入式、应用开发和基础设施三组技术能力", height=340, body=body, theme=theme)


def render_project(theme: Theme, *, key: str, title_value: str, subtitle: str, tags: tuple[str, ...], accent: str, symbol: str) -> str:
    tag_chunks: list[str] = []
    x = 86
    for tag in tags:
        width = 62 + len(tag) * 20
        tag_chunks.append(round_rect(x, 286, width, 54, 27, fill=theme.surface_alt, stroke=theme.border))
        tag_chunks.append(text(x + width // 2, 321, tag, size=20, fill=theme.secondary, cls="label", anchor="middle"))
        x += width + 16
    body = f'''  <rect width="1200" height="420" rx="34" fill="url(#canvas)"/>
  {round_rect(38, 30, 1124, 354, 34, fill=theme.surface, stroke=theme.border, filter_id='smallShadow')}
  <circle cx="132" cy="132" r="58" fill="{accent}" opacity="0.14"/>
  {text(132, 148, symbol, size=48, fill=accent, cls='title', anchor='middle')}
  {text(222, 122, title_value, size=47, fill=theme.text, cls='display')}
  {text(222, 171, subtitle, size=25, fill=theme.secondary)}
  {text(86, 249, 'Featured project', size=18, fill=theme.tertiary, cls='label')}
  {''.join(tag_chunks)}
  <circle cx="1070" cy="207" r="44" fill="{theme.blue_soft}"/>
  <path d="M1052 207h34m-14-14 14 14-14 14" fill="none" stroke="{theme.blue}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  {text(1070, 308, key, size=18, fill=theme.tertiary, cls='label', anchor='middle')}
'''
    return svg_document(title=f"项目：{title_value}（{theme.name}）", description=subtitle, height=420, body=body, theme=theme)


def render_focus(theme: Theme) -> str:
    items = [
        ("Architecture", "嵌入式架构", "模块边界与状态流转", theme.blue, "⌘"),
        ("Real-time", "RTOS", "任务、事件与消息机制", theme.green, "◴"),
        ("Knowledge", "个人知识管理", "Markdown 与多端同步", theme.orange, "◇"),
        ("Intelligence", "AI 辅助开发", "Agent 工作流与自动化", theme.purple, "✦"),
    ]
    chunks = [f'  <rect width="1200" height="285" rx="30" fill="url(#canvas)"/>']
    for i, (eyebrow, title_value, desc, accent, symbol) in enumerate(items):
        x = 40 + i * 285
        chunks.extend([
            round_rect(x, 30, 265, 225, 28, fill=theme.surface, stroke=theme.border, filter_id="smallShadow"),
            f'<circle cx="{x + 48}" cy="78" r="22" fill="{accent}" opacity="0.14"/>',
            text(x + 48, 86, symbol, size=22, fill=accent, cls="title", anchor="middle"),
            text(x + 28, 124, eyebrow, size=13, fill=theme.tertiary, cls="label"),
            text(x + 28, 158, title_value, size=22, fill=theme.text, cls="title"),
            text(x + 28, 193, desc, size=15, fill=theme.secondary),
            f'<circle cx="{x + 28}" cy="224" r="4" fill="{accent}"/>',
            f'<line x1="{x + 42}" y1="224" x2="{x + 108}" y2="224" stroke="{theme.border_strong}" stroke-width="2" stroke-linecap="round"/>',
        ])
    return svg_document(title=f"亮亮当前关注方向（{theme.name}）", description="嵌入式架构、RTOS、个人知识管理和 AI 辅助开发", height=285, body="\n".join(chunks), theme=theme)


def render_footer(theme: Theme) -> str:
    body = f'''  <rect width="1200" height="96" rx="24" fill="url(#canvas)"/>
  {divider(26, theme, 80, 1120)}
  {text(600, 64, 'Keep systems clear. Keep shipping reliable software.', size=17, fill=theme.secondary, cls='label', anchor='middle')}
  <circle cx="1120" cy="64" r="5" fill="{theme.blue}"/>
'''
    return svg_document(title=f"亮亮主页页尾（{theme.name}）", description="简洁的 Apple 风格页尾分隔与开发理念", height=96, body=body, theme=theme)


def write_asset(name: str, content: str) -> None:
    path = OUT / name
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    projects = [
        ("project-ai-berkshire", "AI Berkshire", "面向 AI 时代的价值投资研究框架", ("AI Agent", "Research", "Skills"), "chart", "↗"),
        ("project-supercom", "SuperCom", "服务嵌入式联调的串口通信与设备调试工具", ("Serial", "Device", "Debug"), "terminal", "⌁"),
        ("project-multitimer", "MultiTimer", "用于周期任务、延时任务与状态调度的多定时器", ("Timer", "Scheduler", "MCU"), "timer", "◷"),
        ("project-learning", "English Level Up Tips", "结构化整理英语学习资料与持续实践方法", ("Learning", "Markdown", "Open Source"), "book", "A"),
    ]
    for theme in (LIGHT, DARK):
        write_asset(f"hero-{theme.name}.svg", render_hero(theme))
        write_asset(f"profile-{theme.name}.svg", render_profile(theme))
        write_asset(f"tech-stack-{theme.name}.svg", render_tech_stack(theme))
        accent_map = {
            "chart": theme.blue,
            "terminal": theme.green,
            "timer": theme.orange,
            "book": theme.purple,
        }
        for key, project_title, subtitle, tags, accent_key, symbol in projects:
            write_asset(
                f"{key}-{theme.name}.svg",
                render_project(theme, key=accent_key.upper(), title_value=project_title, subtitle=subtitle, tags=tags, accent=accent_map[accent_key], symbol=symbol),
            )
        write_asset(f"focus-{theme.name}.svg", render_focus(theme))
        write_asset(f"footer-{theme.name}.svg", render_footer(theme))
    files = sorted(OUT.glob("*.svg"))
    if len(files) != 18:
        raise RuntimeError(f"Expected 18 assets, generated {len(files)}")
    print("Generated 18 Apple profile assets.")


if __name__ == "__main__":
    main()
