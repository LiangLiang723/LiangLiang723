# Linear 风格 GitHub 主页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 Apple Editorial 2.0 主页替换为支持自动明暗切换的 Linear 极简主页，只保留身份介绍、核心能力、当前研究方向、精简开发数据和贡献贪吃蛇。

**Architecture:** 使用 `generate_linear_assets.py` 根据固定设计令牌和 `profile-stats.json` 确定性生成四张 SVG；`fetch_profile_stats.py` 通过 GitHub API 更新统计 JSON，失败时不覆盖已有数据；README 使用原生 Markdown 与 `<picture>` 组合；工作流负责更新数据、生成资源、验证并提交。

**Tech Stack:** Python 3 标准库、SVG、XML、Markdown、GitHub Actions、GitHub REST API、Platane/snk。

## Global Constraints

- 自动适配明亮与深色主题。
- 页面只保留身份介绍、核心能力、当前研究方向、精简开发数据和贪吃蛇贡献轨迹。
- 顶部只有一组 `assets/linear/hero-light.svg` 与 `hero-dark.svg`。
- 核心能力和当前研究方向使用 GitHub 原生文字，不生成卡片图片。
- 开发数据只有一组 `stats-light.svg` 与 `stats-dark.svg`，内容为公开仓库数、贡献总量和主要编程语言。
- README 不得引用 `assets/apple/`、`profile-summary-card-output/`、精选项目或最近动态。
- 贡献贪吃蛇必须保留明暗两套，并使用低饱和紫蓝色。
- 所有生成 SVG 宽度为 1200，具备 `<title>`、`<desc>` 和系统字体。
- 生成器连续运行两次必须产生相同哈希。
- GitHub API 请求失败时必须保留上一份 `profile-stats.json`，不得写入空值。

---

### Task 1: 建立 Linear 资源生成器

**Files:**
- Create: `.github/scripts/generate_linear_assets.py`
- Create: `assets/linear/profile-stats.json`
- Generated: `assets/linear/hero-light.svg`
- Generated: `assets/linear/hero-dark.svg`
- Generated: `assets/linear/stats-light.svg`
- Generated: `assets/linear/stats-dark.svg`

**Interfaces:**
- Consumes: `assets/linear/profile-stats.json`，字段为 `public_repos: int`、`contributions: int`、`primary_language: str`、`updated_at: str`。
- Produces: `main() -> None`，确定性生成四张 SVG。

- [ ] **Step 1: 添加最小统计数据文件**

```json
{
  "public_repos": 13,
  "contributions": 269,
  "primary_language": "C",
  "updated_at": "2026-07-21T00:00:00Z"
}
```

- [ ] **Step 2: 编写生成器**

生成器必须定义：

```python
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


def load_stats(path: Path) -> dict[str, object]: ...
def render_hero(theme: Theme) -> str: ...
def render_stats(theme: Theme, stats: dict[str, object]) -> str: ...
def write_asset(name: str, content: str) -> None: ...
def main() -> None: ...
```

明亮主题令牌：

```python
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
```

深色主题令牌：

```python
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
```

横幅尺寸为 `1200×238`；统计卡片尺寸为 `1200×132`。横幅只展示 `LiangLiang723`、`亮亮`、`嵌入式软件工程师`、`专注设备控制、RTOS 与可靠软件架构。`。

- [ ] **Step 3: 运行生成器并验证 XML**

Run:

```bash
python3 .github/scripts/generate_linear_assets.py
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
files = sorted(Path('assets/linear').glob('*.svg'))
assert [p.name for p in files] == [
    'hero-dark.svg', 'hero-light.svg', 'stats-dark.svg', 'stats-light.svg'
]
for path in files:
    ET.parse(path)
print('4 Linear SVG files parsed')
PY
```

Expected: `4 Linear SVG files parsed`。

- [ ] **Step 4: 提交生成器与首批资源**

```bash
git add .github/scripts/generate_linear_assets.py assets/linear
git commit -m "🎨 新增 Linear 明暗主题主页资源"
```

### Task 2: 添加 GitHub 数据更新脚本

**Files:**
- Create: `.github/scripts/fetch_profile_stats.py`
- Modify: `assets/linear/profile-stats.json`

**Interfaces:**
- Consumes: 环境变量 `GITHUB_TOKEN`、`GITHUB_REPOSITORY_OWNER`，可选 `GITHUB_GRAPHQL_URL`。
- Produces: 原子更新 `assets/linear/profile-stats.json`；异常时退出非零且原文件保持不变。

- [ ] **Step 1: 编写数据获取函数**

脚本必须定义：

```python
def graphql_request(url: str, token: str, query: str, variables: dict[str, object]) -> dict[str, object]: ...
def choose_primary_language(language_edges: list[dict[str, object]]) -> str: ...
def build_stats(payload: dict[str, object]) -> dict[str, object]: ...
def atomic_write(path: Path, payload: dict[str, object]) -> None: ...
def main() -> int: ...
```

GraphQL 查询一次取得：

```graphql
query ProfileStats($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
  }
}
```

主要语言按所有非 Fork 公开仓库的语言字节数汇总后取最大值。

- [ ] **Step 2: 验证成功与失败路径**

Run:

```bash
python3 - <<'PY'
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('stats', '.github/scripts/fetch_profile_stats.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
edges = [
    {'size': 100, 'node': {'name': 'C'}},
    {'size': 80, 'node': {'name': 'Python'}},
    {'size': 40, 'node': {'name': 'C'}},
]
assert module.choose_primary_language(edges) == 'C'
print('language aggregation passed')
PY
```

Expected: `language aggregation passed`。

Run:

```bash
cp assets/linear/profile-stats.json /tmp/profile-stats.before.json
GITHUB_TOKEN='' python3 .github/scripts/fetch_profile_stats.py || true
diff -u /tmp/profile-stats.before.json assets/linear/profile-stats.json
```

Expected: 脚本退出非零，`diff` 无输出。

- [ ] **Step 3: 提交数据脚本**

```bash
git add .github/scripts/fetch_profile_stats.py
git commit -m "✨ 新增 GitHub 主页数据更新脚本"
```

### Task 3: 重写 README 页面结构

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: 四张 `assets/linear/*.svg` 与 output 分支的两张贡献轨迹。
- Produces: 仅包含五个已确认模块的主页 Markdown。

- [ ] **Step 1: 用 Linear 结构替换 README**

README 必须按以下顺序：

```markdown
<picture>Linear 横幅明暗主题</picture>

## 核心能力

**嵌入式开发**  
`C / C++ / STM32`  
设备通信、控制逻辑与嵌入式应用开发。

---

**实时系统**  
`RTOS / 状态管理 / 任务调度`  
关注并发、事件、消息与长期可维护性。

---

**工具与应用**  
`Flutter / Docker / AI Agent`  
构建个人工具、自托管服务与辅助开发工作流。

## 当前研究方向

| | 方向 | 说明 |
|---|---|---|
| `●` | 嵌入式软件架构 | 模块边界、状态流转与可测试性 |
| `●` | RTOS | 任务、事件、消息与实时性 |
| `●` | 个人知识管理 | Markdown、多端访问与长期沉淀 |
| `●` | AI Agent 工作流 | 自动化开发、验证与维护 |

## 开发数据

<picture>Linear 统计明暗主题</picture>

## 贡献轨迹

<picture>贡献贪吃蛇明暗主题</picture>
```

表格不使用独立图片、彩色徽章或额外状态列。

- [ ] **Step 2: 搜索禁止内容**

Run:

```bash
! grep -E "assets/apple|profile-summary-card-output|精选项目|最近动态|查看全部仓库" README.md
```

Expected: exit 0。

- [ ] **Step 3: 提交 README**

```bash
git add README.md
git commit -m "♻️ 重构 Linear 极简主页结构"
```

### Task 4: 重写自动验证

**Files:**
- Modify: `.github/scripts/validate_profile.py`

**Interfaces:**
- Consumes: README、四张 Linear SVG、统计 JSON、工作流。
- Produces: `validate() -> list[str]`；成功输出 `Profile validation passed.`。

- [ ] **Step 1: 先加入会对旧页面失败的规则**

验证必须检查：

```python
EXPECTED_ASSETS = {
    'hero-light.svg', 'hero-dark.svg', 'stats-light.svg', 'stats-dark.svg'
}
REQUIRED_SECTIONS = ['## 核心能力', '## 当前研究方向', '## 开发数据', '## 贡献轨迹']
FORBIDDEN_README_TOKENS = [
    'assets/apple/', 'profile-summary-card-output/', '## 精选项目',
    '最近动态', '查看全部仓库'
]
```

还必须检查：

- 四张 SVG 均为宽度 1200。
- Hero 高度为 238，Stats 高度为 132。
- 明亮资源含 `#F7F7F8`、`#6E56CF`；深色资源含 `#0F1012`、`#8B7CF6`。
- README 中两个本地 `<picture>` 块均包含完整明暗配对，fallback 使用明亮资源。
- 统计 JSON 的三个核心字段类型正确且数值非负。
- README 仅有四个 `##` 栏目。
- 生成器连续运行两次哈希一致。
- 工作流包含数据更新、资源生成、验证和紫蓝色贪吃蛇参数。

- [ ] **Step 2: 运行完整验证**

Run:

```bash
python3 .github/scripts/validate_profile.py
```

Expected: `Profile validation passed.`。

- [ ] **Step 3: 验证故障检测**

Run:

```bash
cp README.md /tmp/README.linear
printf '\n## 精选项目\n' >> README.md
python3 .github/scripts/validate_profile.py && exit 1 || true
mv /tmp/README.linear README.md
python3 .github/scripts/validate_profile.py
```

Expected: 第一次报告禁止栏目，恢复后通过。

- [ ] **Step 4: 提交验证脚本**

```bash
git add .github/scripts/validate_profile.py
git commit -m "✅ 增加 Linear 主页完整验证"
```

### Task 5: 精简 GitHub Actions 工作流

**Files:**
- Modify: `.github/workflows/profile.yml`

**Interfaces:**
- Consumes: GitHub token、生成器、数据脚本、验证脚本。
- Produces: 更新后的 Linear 资源提交和 output 分支贡献轨迹。

- [ ] **Step 1: 替换资源构建流程**

工作流只保留 `validate`、`build-profile`、`contribution-snake` 三个任务。

`build-profile` 顺序必须是：

```yaml
- name: 更新 GitHub 主页数据
  continue-on-error: true
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GITHUB_REPOSITORY_OWNER: ${{ github.repository_owner }}
  run: python3 .github/scripts/fetch_profile_stats.py

- name: 生成 Linear 明暗主题资源
  run: python3 .github/scripts/generate_linear_assets.py

- name: 验证 Linear 主页
  run: python3 .github/scripts/validate_profile.py
```

提交范围只包含：

```bash
git add -A assets/linear
```

- [ ] **Step 2: 更新贡献轨迹配色**

明亮主题：

```text
color_snake=#6E56CF
color_dots=#ECECF0,#D8D4F2,#B9B1EA,#9185DE,#6E56CF
```

深色主题：

```text
color_snake=#8B7CF6
color_dots=#16171A,#292735,#3F3A5A,#625A94,#8B7CF6
```

- [ ] **Step 3: 解析 YAML 并验证工作流**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
yaml.safe_load(Path('.github/workflows/profile.yml').read_text())
print('workflow yaml parsed')
PY
python3 .github/scripts/validate_profile.py
```

Expected: 两项均通过。

- [ ] **Step 4: 提交工作流**

```bash
git add .github/workflows/profile.yml
git commit -m "🔧 精简 Linear 主页自动更新流程"
```

### Task 6: 删除旧 Apple 与统计资源体系

**Files:**
- Delete: `.github/scripts/generate_apple_assets.py`
- Delete: `.github/scripts/style_summary_cards.py`
- Delete: `assets/apple/*.svg`
- Delete: `profile-summary-card-output/github/*.svg`
- Delete: `profile-summary-card-output/github_dark/*.svg`

**Interfaces:**
- Produces: 仓库中仅维护 Linear 页面资源。

- [ ] **Step 1: 删除旧文件**

```bash
rm -rf assets/apple profile-summary-card-output
git rm .github/scripts/generate_apple_assets.py .github/scripts/style_summary_cards.py
```

- [ ] **Step 2: 检查旧引用**

Run:

```bash
! grep -R "generate_apple_assets\|style_summary_cards\|assets/apple\|profile-summary-card-output" README.md .github/scripts .github/workflows
```

Expected: exit 0。

- [ ] **Step 3: 运行最终验证**

```bash
python3 .github/scripts/generate_linear_assets.py
python3 .github/scripts/validate_profile.py
python3 -m py_compile .github/scripts/generate_linear_assets.py .github/scripts/fetch_profile_stats.py .github/scripts/validate_profile.py
```

Expected: 全部 exit 0。

- [ ] **Step 4: 提交清理**

```bash
git add -A
git commit -m "🧹 删除旧 Apple 主页资源体系"
```

### Task 7: Pull Request、自动化验证与合并

**Files:**
- All changed files on `feat/linear-profile`

- [ ] **Step 1: 创建 Pull Request**

标题：`🎨 重构 Linear 极简 GitHub 主页`

正文必须概括五个模块、自动明暗主题、精简统计和保留贪吃蛇。

- [ ] **Step 2: 检查 GitHub Actions**

Expected:

- 结构验证成功。
- GitHub 数据更新成功或安全降级到上一次数据。
- 四张 Linear SVG 生成并验证成功。
- 明暗贡献贪吃蛇生成成功。

- [ ] **Step 3: 审查最终文件清单**

确认不存在旧 Apple SVG、旧统计目录、临时诊断文件或未使用脚本。

- [ ] **Step 4: 压缩合并到 main**

提交标题：`🎨 重构 Linear 极简 GitHub 主页`。
