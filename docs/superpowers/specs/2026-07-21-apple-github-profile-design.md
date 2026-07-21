# Apple 风格 GitHub 主页重构设计

日期：2026-07-21  
仓库：`LiangLiang723/LiangLiang723`

## 1. 目标

将当前固定深色赛博风 GitHub 主页完整重构为 Apple Design（苹果设计）风格，并自动适配明亮与深色主题。

最终效果应当：

- 视觉克制、清晰、精致，强调层级、留白、材质与字体；
- 自动跟随 GitHub 页面或系统的明暗主题；
- 保留用户最重要的身份、能力、项目、统计和当前方向；
- 核心视觉资源存放在当前仓库中，避免第三方图片服务不可用；
- 在桌面和移动端均保持良好可读性；
- 尊重减少动态效果偏好，不使用持续闪烁或大面积循环动画。

## 2. 设计依据

本设计遵循 `emilkowalski/skills` 中 `apple-design` 的核心原则：

- Purpose（目的）：每个模块都必须服务于个人主页展示；
- Simplicity（简洁）：删除重复信息与无意义装饰，而不是单纯减少内容；
- Craft（工艺）：统一字体、间距、圆角、颜色、明暗主题与细节；
- Familiarity（熟悉感）：使用系统字体、系统蓝、卡片层级和标准阅读顺序；
- Flexibility（适应性）：同时适配明亮、深色、移动端和无障碍偏好；
- Delight（愉悦）：通过克制的材质、柔和阴影和精确排版产生品质感，而不是依赖霓虹与持续动画。

## 3. 页面结构

主页采用 Apple 精简型结构，共六个区域：

1. Hero（首屏主视觉）
2. 个人简介
3. 技术能力
4. 精选项目
5. 开发数据与贡献轨迹
6. 当前方向与页尾

顺序如下：

```text
Hero 主视觉
↓
个人简介
↓
技术能力
↓
精选项目
↓
开发数据与贡献轨迹
↓
当前方向与页尾
```

## 4. 内容设计

### 4.1 Hero 主视觉

显示：

- `LiangLiang723`
- 嵌入式软件工程师
- 一句简短理念：让复杂系统保持清晰，让可靠软件持续演进
- 核心方向：`C / C++ · RTOS · STM32 · Flutter · Self-hosted`

视觉要求：

- 明亮主题使用浅灰白背景、半透明白色卡片和 Apple Blue（苹果蓝）；
- 深色主题使用黑色或深灰背景、半透明深灰材质和更明亮的系统蓝；
- 使用系统字体；
- 大标题采用较紧字距与较低行高；
- 不使用霓虹辉光、快速渐变、网格背景和循环缩放。

### 4.2 个人简介

不再使用代码块树状排版，改为简洁的说明卡片，包含三项：

- 嵌入式软件、设备通信与控制系统；
- RTOS、任务调度、状态管理与可维护架构；
- Flutter、Docker、自托管服务与 AI Agent 辅助开发。

### 4.3 技术能力

技术能力合并为一个统一面板，分为三组：

- Embedded：C、C++、STM32、FreeRTOS、Zephyr；
- Application：Flutter、Python、Go；
- Infrastructure：Docker、Linux、Git。

每项以简洁标签呈现，不使用外部徽章服务，不堆叠大量品牌色。

### 4.4 精选项目

保留以下四个项目：

- AI Berkshire
- SuperCom
- MultiTimer
- English Level Up Tips

布局：

- 桌面端两列；
- 移动端自然缩放；
- 每个项目使用独立卡片和独立链接；
- 每张卡片包含名称、简述、标签和箭头提示；
- 不把四个项目合成一张图片，以确保链接可独立点击。

### 4.5 开发数据与贡献轨迹

统计卡片：

- 明亮主题使用 `github`；
- 深色主题使用 `github_dark`；
- 继续由 GitHub Actions 自动生成并写回仓库；
- 通过 `<picture>` 根据主题选择对应资源。

贡献轨迹：

- 保留亮色和深色两套贡献贪吃蛇；
- 继续读取当前仓库 `output` 分支；
- 不增加额外循环动画。

### 4.6 当前方向与页尾

将原“开发理念”和“当前关注方向”合并，保留四个重点：

- 嵌入式架构；
- RTOS；
- 个人知识管理；
- AI 辅助开发。

页尾仅保留一句简短文字和轻量分隔视觉，不再使用强发光效果。

## 5. 明暗主题实现

GitHub README 无法运行 JavaScript，因此使用 `<picture>` 和 `prefers-color-scheme` 自动切换：

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/apple/hero-dark.svg" />
  <img src="./assets/apple/hero-light.svg" alt="亮亮的 GitHub 主页首屏" />
</picture>
```

每个核心视觉模块都提供独立的明亮与深色文件。

## 6. 文件架构

```text
LiangLiang723/
├─ README.md
├─ assets/
│  └─ apple/
│     ├─ hero-light.svg
│     ├─ hero-dark.svg
│     ├─ profile-light.svg
│     ├─ profile-dark.svg
│     ├─ tech-stack-light.svg
│     ├─ tech-stack-dark.svg
│     ├─ project-ai-berkshire-light.svg
│     ├─ project-ai-berkshire-dark.svg
│     ├─ project-supercom-light.svg
│     ├─ project-supercom-dark.svg
│     ├─ project-multitimer-light.svg
│     ├─ project-multitimer-dark.svg
│     ├─ project-learning-light.svg
│     ├─ project-learning-dark.svg
│     ├─ focus-light.svg
│     ├─ focus-dark.svg
│     ├─ footer-light.svg
│     └─ footer-dark.svg
└─ .github/
   └─ workflows/
      └─ profile.yml
```

旧赛博风资源在新版本验证完成后删除，避免两套视觉系统长期并存。

## 7. 视觉系统

### 7.1 明亮主题

- 页面主背景：接近 `#F5F5F7`；
- 卡片：半透明白色；
- 主文字：接近黑色；
- 辅助文字：中性灰；
- 强调色：Apple Blue；
- 边框：低透明度灰色；
- 阴影：大面积、低透明度、柔和。

### 7.2 深色主题

- 页面主背景：接近 `#000000` 与 `#1C1C1E`；
- 卡片：半透明深灰；
- 主文字：柔和白色；
- 辅助文字：浅灰；
- 强调色：明亮系统蓝；
- 边框：低透明度白色；
- 层级主要通过边缘高光和材质差异体现。

### 7.3 字体与排版

统一字体顺序：

```text
system-ui
-apple-system
BlinkMacSystemFont
Segoe UI
Microsoft YaHei
sans-serif
```

排版规则：

- 大标题使用紧字距；
- 正文使用舒适行高；
- 避免无意义的全大写英文；
- 统一圆角为 24 至 28 像素；
- 区域间增加留白；
- 中文为主，英文只用于名称与必要术语。

## 8. 动效与无障碍

- 自制视觉卡片默认保持静态；
- 不使用循环缩放、快速渐变、闪烁或大面积移动背景；
- 所有 SVG 内置减少动态效果规则；
- 对比度必须保证明暗主题下均可阅读；
- 所有图片提供明确的中文替代文字；
- 移动端不得出现文字溢出、卡片裁切或横向滚动。

## 9. 可靠性

- 不使用 `img.shields.io`；
- 不使用在线横幅生成器；
- 自制图片全部存储在当前仓库；
- `<picture>` 始终提供明亮主题默认回退；
- 统计卡片由当前仓库的 GitHub Actions 生成；
- 贡献轨迹只依赖当前仓库的 `output` 分支；
- README 中不得引用不存在的文件。

## 10. 工作流修改

`.github/workflows/profile.yml` 继续承担：

- 定时生成统计卡片；
- 生成 `github` 与 `github_dark` 两套统计主题；
- 定时生成亮色与深色贡献贪吃蛇；
- 支持手动触发；
- 使用 `contents: write` 权限写回仓库。

不引入额外第三方部署服务。

## 11. 验收标准

### 提交前

1. 所有 SVG 均能通过 XML 解析；
2. README 引用的所有本地文件均存在；
3. 不再包含旧赛博风资源引用；
4. 不再包含 `img.shields.io`；
5. 明暗主题文字对比度可读；
6. 四个项目链接均正确；
7. 移动端宽度下无明显溢出；
8. 工作流 YAML 可正常解析。

### 提交后

1. 重新读取远程 README 并确认内容一致；
2. 确认所有新资源存在于 `main` 分支；
3. 确认 GitHub Actions 执行成功；
4. 确认 `github` 与 `github_dark` 统计资源生成；
5. 确认实际主页明亮和深色主题均正常渲染；
6. 确认旧资源已安全删除且无残留引用。

## 12. 非目标

本次不包含：

- JavaScript 交互；
- 自定义 GitHub 页面脚本；
- 音效或触觉反馈；
- 实时在线访客统计；
- 与个人主页重构无关的仓库整理；
- 修改精选项目仓库本身。
