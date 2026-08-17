# 共享 HTML 视觉基线（InsightView 视觉体系）

本文件是 `insightview`、`my-writer`、`voice2article` 三个 skill 生成 HTML 时**共享的视觉基线**，是颜色、字体、容器、高亮、底部、响应式的**单一事实来源**。三个 skill 的模板 CSS 必须与本基线保持一致；改样式只改本文件，再同步到各模板。

> 宿主：`my-writer`（排版核心 skill）。其余 skill 引用本文件，不重复定义基线值。

## 1. 基础样式（三者一致）

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;
    background: #f8fafc;
    color: #1e293b;
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
}
```

## 2. 页面容器（三者一致）

```css
.container {
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
}
```

## 3. 绿色高亮（三者一致）

核心概念、关键数据、专有名词用绿色高亮。每段 0-3 个，高亮词 2-6 个字，绝不整句高亮。

```css
.highlight {
    color: #16a34a;
    font-weight: 500;
}
```

## 4. 底部信息（三者一致）

```css
.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
    font-size: 0.8rem;
    color: #94a3b8;
}
```

底部必备三要素：生成日期（YYYY-MM-DD）、来源说明、LLM 标注（AI 改写注明「本文由 AI 辅助改写」；纯排版不标注；AI 从零生成标「本文由 AI 生成」）。

## 5. 响应式断点（三者一致）

```css
@media (max-width: 640px) {
    .container { padding: 1.5rem 1rem 3rem; }
    /* 标题、正文字号按各模板结构层等比缩小 */
}
```

## 6. 结构层（各自定义，不共享）

基线只管「视觉观感」的统一，不管结构。各 skill 保留自己的结构层：

| Skill | 结构层特征 |
|-------|-----------|
| **insightview** | 居中报告头 + emoji 板块标题（📌📦🧩🏗️）+ 推文卡片（`.tweet` / `.tweet-label` / `.tweet-body`）+ 附录索引 + 徽章 |
| **my-writer** | FT 头版：左对齐 kicker + h1 + standfirst + 一级标题（`.part-title`，2px 深色边框，一、二、三编号）+ 二级标题（`.section-title`）+ 引用块 + 表格 |
| **voice2article** | 职责分离后不再自建 HTML；转写完成后交 `my-writer` 排版，沿用 my-writer 结构层 |

## 7. 同步规则

- 改基线值（颜色、字体、容器宽度、高亮、底部、断点）→ 只改本文件 → 同步到三个模板的内联 CSS。
- 改结构层 → 只改对应 skill 的模板，不动本文件。
- 新增 skill 若要复用 InsightView 视觉体系，引用本文件，不另起 CSS。
