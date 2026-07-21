# Apple Editorial 2.0 GitHub 主页重构设计

日期：2026-07-21  
仓库：`LiangLiang723/LiangLiang723`

## 1. 背景与问题

当前主页已经具备 Apple 风格的明暗主题能力，但各区域仍呈现出明显的拼接感：

- GitHub 页面背景之外，多个 SVG 内部又绘制一层纯黑底座；
- Hero、个人介绍、技术能力、精选项目、统计卡片和当前方向使用了不同的视觉语言；
- 蓝、绿、紫、橙、黄等颜色同时作为主视觉出现，注意力过于分散；
- 中英文标题、辅助文案、标签和第三方统计卡片字体层级不一致；
- 精选项目区域信息密度过高，项目卡片外还有表格硬边框；
- 开发数据区域面积与视觉对比度过高，抢走了精选项目的页面重心；
- 贡献轨迹仍使用绿色主色，与全页蓝灰体系不一致。

本次采用 **Apple Editorial 2.0** 方案，从设计令牌、内容密度、组件结构和生成流程四个层面统一整页。

## 2. 目标

最终主页应满足：

- 整体像一篇连续的 Apple 产品介绍页，而不是多张独立海报拼接；
- 明亮和深色主题下保持同一视觉语言；
- 全页只使用 Apple Blue 作为主强调色；
- 中文作为主体语言，英文只保留账号名、项目名和必要技术名；
- 减少黑色底座、嵌套容器、彩色装饰和无意义微文案；
- 保留身份、能力、精选项目、开发数据、贡献轨迹和当前方向；
- 所有项目仍可独立点击；
- 桌面和移动端均保持清晰可读；
- 资源生成、主题配对和页面引用可自动验证。

## 3. 设计原则

本设计继续遵循 `emilkowalski/skills` 中 `apple-design` 的原则：

- **Purpose（目的）**：每个元素必须服务于个人能力与项目展示；
- **Simplicity（简洁）**：通过层级和内容优先级降低复杂度，而不是仅删除信息；
- **Craft（工艺）**：颜色、圆角、边框、字体、间距和主题必须系统化；
- **Familiarity（熟悉感）**：使用系统字体、系统蓝和清晰阅读顺序；
- **Flexibility（适应性）**：适配明暗主题、移动端和减少动态效果偏好；
- **Delight（愉悦）**：品质感来自比例、排版和细节，而不是辉光与持续动画。

## 4. 统一视觉系统

### 4.1 设计令牌

所有自制 SVG 使用统一令牌。

```python
LIGHT = {
    "background": "#FFFFFF",
    "surface": "#FFFFFF",
    "surface_subtle": "#F5F5F7",
    "text": "#1D1D1F",
    "secondary": "#6E6E73",
    "border": "#D2D2D7",
    "accent": "#0071E3",
}

DARK = {
    "background": "#1C1C1E",
    "surface": "#1C1C1E",
    "surface_subtle": "#2C2C2E",
    "text": "#F5F5F7",
    "secondary": "#A1A1A6",
    "border": "#38383A",
    "accent": "#0A84FF",
}
```

### 4.2 色彩规则

- 明亮模式主强调色：`#0071E3`；
- 深色模式主强调色：`#0A84FF`；
- 紫色、绿色、橙色和黄色不再用于标题、边框或大面积装饰；
- 技术标签状态点全部使用统一蓝色；
- 统计图表和贡献轨迹统一转换为蓝灰色系；
- 禁止重新引入旧赛博色：`#A855F7`、`#22D3EE` 和高饱和亮绿色。

### 4.3 卡片规则

| 属性 | 统一规则 |
|---|---|
| 大卡片圆角 | 24 像素 |
| 小卡片圆角 | 18 像素 |
| 边框 | 1 像素低对比度边框 |
| 内边距 | 28 至 32 像素 |
| 标题字重 | 700 |
| 正文字重 | 400 至 500 |
| 阴影 | 仅明亮模式使用柔和阴影 |
| 深色层级 | 通过边框、表面差异和留白体现 |

### 4.4 背景层级

取消当前 SVG 中的“黑色底座 + 深灰卡片”双层结构。

新的层级仅为：

```text
GitHub 页面背景
└─ 单层内容卡片
```

所有自制资源四周只保留少量透明边距，不再绘制大面积纯黑外框。

### 4.5 字体与语言

统一字体：

```text
system-ui
-apple-system
BlinkMacSystemFont
Segoe UI
Microsoft YaHei
sans-serif
```

文字规则：

- 页面栏目标题使用中文；
- `Technical capabilities` 改为“技术能力”；
- `Embedded` 改为“嵌入式开发”；
- `Application` 改为“应用开发”；
- `Infrastructure` 改为“基础设施”；
- 删除 `Featured project`、`CHART`、`TERMINAL`、`TIMER`、`BOOK` 等无实际价值的小英文；
- 英文仅保留 `LiangLiang723`、项目名、技术名和页尾短句。

### 4.6 间距节奏

统一页面节奏：

```text
栏目标题
16 像素
内容卡片
40 像素
下一栏目标题
```

卡片内部标题、说明、标签和分组间距也使用统一比例。

## 5. 页面结构

最终页面顺序保持：

```text
紧凑 Hero 主视觉
↓
个人能力概览
↓
技术能力索引
↓
四个精选项目
↓
紧凑开发数据
↓
低调贡献轨迹
↓
当前方向
↓
轻量页尾
```

## 6. 组件设计

### 6.1 Hero 主视觉

内容：

```text
LiangLiang723
嵌入式软件工程师

让复杂系统保持清晰，
让可靠软件持续演进。

C / C++ · RTOS · STM32 · Flutter
```

要求：

- 高度从约 390 像素缩短到 280 至 300 像素；
- 文字整体左对齐；
- 小型眉题保持克制；
- 右侧渐变球缩小到当前约 60%，降低饱和度；
- 删除五个胶囊技术标签；
- 删除黑色底座；
- 只保留一行技术方向文字；
- 不使用辉光、网格、循环动画和快速渐变。

### 6.2 关于我

从三张独立编号卡片改为一张横向大卡片，内部三列：

| 设备与控制 | 架构与实时系统 | 应用与自动化 |
|---|---|---|
| 嵌入式软件、设备通信和控制系统 | RTOS、任务调度、状态管理和可维护架构 | Flutter、Docker、自托管服务和 AI 辅助开发 |

要求：

- 删除 `01 / 02 / 03` 编号；
- 删除三套独立颜色；
- 删除底部彩色短线；
- 三列主要通过留白区分，不使用明显分割线；
- 每列只保留标题与一句说明。

### 6.3 技术能力

结构：

```text
嵌入式开发
C · C++ · STM32 · FreeRTOS · Zephyr

应用开发
Flutter · Python · Go

基础设施
Docker · Linux · Git
```

要求：

- 删除重复英文大标题和右上角英文口号；
- 所有技术标签使用中性灰表面；
- 所有状态点统一使用系统蓝；
- 标签高度、圆角和水平间距统一；
- 不再使用品牌色区分技术。

### 6.4 精选项目

保留：

- AI Berkshire；
- SuperCom；
- MultiTimer；
- English Level Up Tips。

每张卡片只保留：

```text
项目名称                                    ↗
一句项目说明

最多三个技术标签
```

要求：

- 删除 `Featured project`；
- 删除右下角英文分类；
- 删除大型圆形箭头按钮；
- 右上角只保留轻量 `↗`；
- 项目说明最多一行；
- 标签最多三个；
- 所有图标统一蓝色；
- 项目卡片尺寸完全一致；
- 保持每个项目独立链接；
- 减弱 HTML 表格硬边框的存在感。

### 6.5 开发数据

保留：

- 一张横向开发概览；
- 一张主要语言卡片；
- 一张统计数据卡片。

删除：

- 高效时段卡片；
- 不必要的额外统计模块。

要求：

- 继续使用 `github` 和 `github_dark` 两套基础主题；
- 生成后由本地脚本统一处理圆角、背景、边框、标题色和辅助文字；
- 弱化或删除过于显眼的 GitHub 图标；
- 语言图表从橙、棕配色转换为蓝色系；
- 区域整体高度减少约三分之一；
- 统计内容不得成为页面最大视觉中心。

### 6.6 贡献轨迹

要求：

- 使用透明背景；
- 明亮主题使用浅灰至系统蓝；
- 深色主题使用深灰蓝至明亮系统蓝；
- 贪吃蛇统一使用 Apple Blue；
- 删除绿色主色与底部长条；
- 缩小上下空白；
- 保留动画能力，但降低视觉存在感。

建议生成参数：

```yaml
outputs: |
  dist/github-contribution-grid-snake.svg?color_snake=%230071E3&color_dots=%23EBEDF0,%23D6E8FA,%239AC7F7,%235AA7F2,%230071E3
  dist/github-contribution-grid-snake-dark.svg?palette=github-dark&color_snake=%230A84FF&color_dots=%231C1C1E,%232C3E50,%233D5F7A,%235A8DB8,%230A84FF
```

### 6.7 当前方向

保留四项：

- 嵌入式架构；
- RTOS；
- 个人知识管理；
- AI 辅助开发。

要求：

- 所有卡片统一蓝色图标；
- 删除紫、绿、橙等独立主色；
- 删除英文小标题；
- 删除底部彩色短线；
- 卡片圆角、边框、标题和说明与其他模块统一。

### 6.8 页尾

- 删除黑色大容器；
- 只保留一条细分隔线；
- 保留一句简短英文：`Keep systems clear. Ship reliable software.`；
- 不使用辉光、渐变流动或大型装饰。

## 7. 文件架构

继续沿用现有明暗资源结构：

```text
assets/apple/
├─ hero-light.svg
├─ hero-dark.svg
├─ profile-light.svg
├─ profile-dark.svg
├─ tech-stack-light.svg
├─ tech-stack-dark.svg
├─ project-ai-berkshire-light.svg
├─ project-ai-berkshire-dark.svg
├─ project-supercom-light.svg
├─ project-supercom-dark.svg
├─ project-multitimer-light.svg
├─ project-multitimer-dark.svg
├─ project-learning-light.svg
├─ project-learning-dark.svg
├─ focus-light.svg
├─ focus-dark.svg
├─ footer-light.svg
└─ footer-dark.svg
```

文件数量不变，但每个资源内部结构更简单，所有视觉由统一设计令牌驱动。

## 8. 生成流程

重构 `.github/scripts/generate_apple_assets.py`：

1. 定义统一设计令牌；
2. 生成 18 张自制明暗 SVG；
3. 确保项目卡片使用同一尺寸；
4. 禁止嵌套黑色底座；
5. 输出确定性文件内容。

统计卡片流程：

```text
生成 github / github_dark 原始统计卡片
↓
本地后处理圆角、背景、边框、强调色和图表配色
↓
XML 解析检查
↓
写入仓库
```

工作流 `.github/workflows/profile.yml` 继续负责：

- 手动触发；
- 每日定时更新；
- 生成自制明暗资源；
- 生成并后处理统计卡片；
- 生成蓝灰色贡献轨迹；
- 运行验证脚本；
- 自动提交生成结果。

## 9. README 结构

`README.md` 继续通过 `<picture>` 自动选择主题：

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/apple/hero-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="./assets/apple/hero-light.svg" />
  <img src="./assets/apple/hero-light.svg" alt="亮亮的 GitHub 主页首屏" />
</picture>
```

要求：

- 明亮主题始终作为默认回退；
- 不引入 JavaScript；
- 不使用外部徽章或在线横幅服务；
- 项目区域维持独立链接；
- 不再引用高效时段卡片；
- 所有本地图片路径必须存在。

## 10. 无障碍与适配

- 所有 SVG 提供 `<title>` 和 `<desc>`；
- 所有 README 图片提供中文替代说明；
- 明暗主题均保持可读对比度；
- 自制资源不包含持续动画；
- `prefers-reduced-motion` 下不得存在额外动画；
- 移动端不得出现文字裁切、标签溢出或横向滚动；
- 项目卡片在缩放后仍必须保留清晰标题和说明。

## 11. 自动验证

升级 `.github/scripts/validate_profile.py`，至少检查：

1. 所有明亮和深色资源成对存在；
2. 18 张自制 SVG 均能通过 XML 解析；
3. 不得出现旧赛博颜色 `#A855F7` 和 `#22D3EE`；
4. 不得出现高饱和亮绿色主视觉；
5. 不得出现旧版黑色底座结构；
6. 所有自制资源使用统一圆角；
7. 所有项目卡片尺寸一致；
8. README 不引用高效时段卡片；
9. README 不引用旧贡献轨迹配色；
10. README 所有本地资源引用真实存在；
11. 明暗主题 `<picture>` 配对完整；
12. 生成器连续运行两次时结果哈希一致；
13. 工作流 YAML 能正常解析；
14. Python 脚本能正常编译。

## 12. 验收流程

### 提交前

- 生成 18 张资源；
- 连续生成两次并比较哈希；
- 运行完整验证脚本；
- 检查 README 的本地资源引用；
- 检查统计卡片后处理结果；
- 检查工作流 YAML；
- 检查移动端尺寸和文字边界。

### 独立分支

1. 创建 `feat/apple-editorial-profile` 分支；
2. 提交生成器、验证脚本、README、工作流和资源；
3. 运行 GitHub Actions；
4. 创建 Pull Request；
5. 检查明亮和深色页面完整截图；
6. 检查字体、圆角、主色、边框和间距是否贯穿全页；
7. 检查四个项目链接；
8. 检查贡献轨迹是否已变为蓝灰色。

### 合并前

- 所有自动化任务成功；
- 没有缺失资源；
- 没有旧赛博色和绿色贡献轨迹残留；
- 页面截图确认整体统一；
- 重要问题全部修复后合并到 `main`。

## 13. 非目标

本次不包含：

- JavaScript 交互；
- 独立 GitHub Pages 网站；
- 音效或触觉反馈；
- 实时访客统计；
- 修改精选项目仓库本身；
- 与主页视觉统一无关的仓库整理。
