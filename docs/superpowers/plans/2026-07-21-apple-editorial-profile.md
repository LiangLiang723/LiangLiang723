# Apple Editorial 2.0 GitHub Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 GitHub 个人主页重构为统一、克制、可自动切换明暗主题的 Apple Editorial 2.0 风格。

**Architecture:** 由一个确定性的 Python 生成器统一产出 18 张明暗主题 SVG；由独立后处理脚本统一第三方统计卡片；验证脚本检查主题配对、设计令牌、项目尺寸、引用完整性和工作流配置；README 仅负责页面结构与主题选择。

**Tech Stack:** Python 3、SVG、XML、Markdown、GitHub Actions、Platane/snk、github-profile-summary-cards。

## Global Constraints

- 全页仅使用 Apple Blue 作为主强调色：明亮 `#0071E3`，深色 `#0A84FF`。
- 自制资源不得出现旧赛博色 `#A855F7`、`#22D3EE` 或高饱和亮绿色主视觉。
- 所有自制卡片为单层表面；大卡片圆角 24，小卡片圆角 18。
- 中文为主体语言；英文仅保留账号名、项目名、技术名和页尾短句。
- 必须保留 18 张明暗主题 SVG、四个独立项目链接和明暗主题贡献轨迹。
- 不使用 JavaScript、在线徽章服务或在线横幅生成器。
- README 不再引用高效时段卡片。
- 生成过程必须确定性；连续运行两次文件哈希一致。

---

### Task 1: 建立失败验收规则

**Files:**
- Modify: `.github/scripts/validate_profile.py`

**Interfaces:**
- Consumes: `README.md`、`assets/apple/*.svg`、`.github/workflows/profile.yml`。
- Produces: `validate() -> list[str]`，零错误表示页面符合 Editorial 2.0 规范。

- [ ] **Step 1: 增加失败检查**

加入设计令牌、旧颜色、禁用文案、项目尺寸、统计卡片引用和后处理工作流检查。

- [ ] **Step 2: 在旧资源上运行验证**

Run: `python3 .github/scripts/validate_profile.py`

Expected: FAIL，至少报告旧赛博颜色、多色项目卡片、旧英文微文案或贡献轨迹配色问题。

- [ ] **Step 3: 提交失败验收规则**

```bash
git add .github/scripts/validate_profile.py
git commit -m "✅ 增加 Editorial 2.0 主页验收规则"
```

### Task 2: 重构 SVG 生成器

**Files:**
- Modify: `.github/scripts/generate_apple_assets.py`
- Generated: `assets/apple/*.svg`

**Interfaces:**
- Consumes: `Theme` 设计令牌及固定页面文案。
- Produces: 18 张宽度为 1200 的明暗主题 SVG。

- [ ] **Step 1: 收敛 Theme 数据结构**

只保留 `background`、`surface`、`surface_subtle`、`text`、`secondary`、`border`、`accent`、`shadow`；删除 cyan、green、orange、purple 等多主色字段。

- [ ] **Step 2: 重构 Hero**

生成 290 像素高、单层卡片、左对齐文案、单行技术方向和低饱和蓝色球体；删除胶囊标签、网格、辉光和嵌套底座。

- [ ] **Step 3: 重构个人介绍与技术能力**

个人介绍改为一张三列卡片；技术能力改为三行中文索引，技术点统一使用系统蓝。

- [ ] **Step 4: 重构四张项目卡片**

每张卡片统一 1200×260，只保留项目名、右上角 `↗`、一行说明和最多三个标签；所有图标和状态点使用系统蓝。

- [ ] **Step 5: 重构当前方向和页尾**

当前方向统一为四张蓝色小卡片；页尾仅保留细分隔线和 `Keep systems clear. Ship reliable software.`。

- [ ] **Step 6: 生成并验证 XML**

Run:
```bash
python3 .github/scripts/generate_apple_assets.py
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
files = sorted(Path('assets/apple').glob('*.svg'))
assert len(files) == 18
for path in files:
    ET.parse(path)
print('18 SVG files parsed')
PY
```

Expected: `18 SVG files parsed`。

### Task 3: 统一统计卡片

**Files:**
- Create: `.github/scripts/style_summary_cards.py`
- Modify: `.github/workflows/profile.yml`

**Interfaces:**
- Consumes: `profile-summary-card-output/github` 与 `github_dark` 下的原始 SVG。
- Produces: 使用统一圆角、背景、边框、蓝色标题和蓝灰图表的统计卡片。

- [ ] **Step 1: 编写后处理脚本**

脚本解析 SVG 文本并完成：根卡片圆角改为 18；背景和边框替换为设计令牌；标题替换为系统蓝；正文替换为中性灰；语言颜色映射为蓝灰梯度；弱化 GitHub 图标。

- [ ] **Step 2: 在工作流中调用后处理脚本**

两套统计主题生成后执行：

```yaml
- name: 统一统计卡片样式
  run: python3 .github/scripts/style_summary_cards.py
```

- [ ] **Step 3: 删除高效时段卡片引用**

README 只保留 `0-profile-details.svg`、`1-repos-per-language.svg` 和 `3-stats.svg`。

### Task 4: 统一贡献轨迹

**Files:**
- Modify: `.github/workflows/profile.yml`

**Interfaces:**
- Consumes: GitHub 贡献数据。
- Produces: 蓝灰色亮色和深色贡献轨迹 SVG。

- [ ] **Step 1: 设置明亮配色**

```text
color_snake=#0071E3
color_dots=#EBEDF0,#D6E8FA,#9AC7F7,#5AA7F2,#0071E3
```

- [ ] **Step 2: 设置深色配色**

```text
color_snake=#0A84FF
color_dots=#1C1C1E,#2C3E50,#3D5F7A,#5A8DB8,#0A84FF
```

### Task 5: 调整 README 页面节奏

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: 18 张自制 SVG、6 张统计 SVG、2 张贡献轨迹 SVG。
- Produces: 连续、紧凑、明暗自适应的 GitHub 主页。

- [ ] **Step 1: 保持六个中文栏目**

保留关于我、技术能力、精选项目、开发数据、贡献轨迹、当前方向。

- [ ] **Step 2: 减少表格边框存在感**

项目与统计表格使用 `cellpadding="0" cellspacing="0"`，在单元格内使用统一宽度图片，不增加额外 Markdown 分隔线。

- [ ] **Step 3: 压缩垂直留白**

移除多余 `<br>` 和空容器；保留稳定的栏目标题到内容间距。

### Task 6: 完整验证与确定性测试

**Files:**
- Modify: `.github/scripts/validate_profile.py`

**Interfaces:**
- Produces: 失败时逐项报告，成功时打印 `Profile validation passed.`。

- [ ] **Step 1: 验证新资源**

Run: `python3 .github/scripts/validate_profile.py`

Expected: PASS。

- [ ] **Step 2: 验证确定性**

Run:
```bash
python3 .github/scripts/generate_apple_assets.py
find assets/apple -type f -name '*.svg' -print0 | sort -z | xargs -0 sha256sum > /tmp/assets-a.sha
python3 .github/scripts/generate_apple_assets.py
find assets/apple -type f -name '*.svg' -print0 | sort -z | xargs -0 sha256sum > /tmp/assets-b.sha
diff -u /tmp/assets-a.sha /tmp/assets-b.sha
```

Expected: 无差异。

- [ ] **Step 3: 编译 Python 脚本**

Run:
```bash
python3 -m py_compile .github/scripts/generate_apple_assets.py .github/scripts/style_summary_cards.py .github/scripts/validate_profile.py
```

Expected: exit 0。

- [ ] **Step 4: 检查工作流 YAML**

Run:
```bash
python3 - <<'PY'
from pathlib import Path
import yaml
yaml.safe_load(Path('.github/workflows/profile.yml').read_text())
print('workflow yaml parsed')
PY
```

Expected: `workflow yaml parsed`。

### Task 7: Pull Request 与合并

**Files:**
- All changed files on `feat/apple-editorial-profile`

- [ ] **Step 1: 推送分支并等待 GitHub Actions**

Expected: 验证、构建统计卡片和贡献轨迹任务成功。

- [ ] **Step 2: 创建 Pull Request**

标题：`🎨 统一 Apple Editorial 2.0 GitHub 主页`

- [ ] **Step 3: 检查完整差异和页面资源**

确认 18 张资源、统计卡片、贡献轨迹、项目链接和旧颜色检查全部通过。

- [ ] **Step 4: 合并到 main**

使用 squash 合并，提交标题保持中文 Emoji 规范。
