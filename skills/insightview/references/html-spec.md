# HTML 生成规范

## 1. 顶层板块结构

主报告和每篇附录都必须遵循以下板块结构。板块是顶层结构，推文编号是板块内部的子项。

### 主报告板块

```
📌 一句话总结
📦 公司角度
🧩 产品角度
🏗️ 组织角度
```

### 附录可额外包含

```
👤 访谈人背景
💡 核心观点
💬 行业观点（可选）
```

## 2. 推文卡片 HTML 结构

正确的 HTML 结构示例：

```html
<div class="section-title"><span class="emoji">📦</span> 公司角度</div>
<div class="tweet">
    <div class="tweet-label">推 1 · 定位：从客服 Agent 到 AI 管家</div>
    <div class="tweet-body">
        <p>内容段落1。</p>
        <p>内容段落2。</p>
    </div>
</div>
<div class="tweet">
    <div class="tweet-label">推 2 · 竞争格局：产品化 vs 服务化</div>
    <div class="tweet-body">
        <p>内容段落1。</p>
    </div>
</div>
```

## 3. 推文标签格式

- 使用「推 N · [主题标题]」格式
- N 为连续编号（推 1、推 2、推 3……），**不按板块重置**
- 主题标题用中文，简洁精准

示例：
- 「推 1 · 核心结论」
- 「推 2 · 谁在说话」
- 「推 3 · 如何选定方向」

## 4. 内容换行规范

- **严格换行**：每段 2-4 句，表达完一个完整意思后立即换行
- 用 `<p>` 标签包裹每一段
- 不把所有内容塞在一个 `<p>` 里
- 段与段之间用 `</p><p>` 分隔

正确示例：

```html
<div class="tweet-body">
    <p>Decagon 用两年时间从零到 45 亿美元估值。</p>
    <p>核心差异化是 AOPs——让 CX 团队用自然语言配置 AI Agent，而非依赖专业服务。</p>
    <p>90% 工作流运行在开源模型上。</p>
</div>
```

错误示例（禁止）：

```html
<div class="tweet-body">
    <p>Decagon 用两年时间从零到 45 亿美元估值。核心差异化是 AOPs——让 CX 团队用自然语言配置 AI Agent。90% 工作流运行在开源模型上。产品从客服 Agent 演进为 AI 管家。</p>
</div>
```

## 5. 绿色高亮规范

- 核心概念、关键数据、专有名词用绿色高亮
- 使用 `<span class="highlight">关键词</span>`
- 高亮不宜过多，每条推文 1-3 个即可

示例：

```html
<p>核心差异化是 <span class="highlight">AOPs</span>——让 CX 团队用自然语言配置 AI Agent。</p>
```

## 6. 推文数量

- **不限数量**，核心观点到位即可
- 主报告通常 20-40 条，单篇附录 16-23 条
- 不要为了凑数注水，也不要为了限制而砍掉关键观点

## 6.5 来源标注（必备）

每条推文末尾必须标注来源附录序号，方便读者去附录找原文：

```html
<p class="source-ref">📎 来源：01, 14, 16</p>
```

- 序号对应附录索引中的编号
- 多个来源用逗号分隔
- 放在 `tweet-body` 内最后一个 `<p>` 之后
- CSS 样式：`.source-ref { font-size: 0.78rem; color: #94a3b8; margin-top: 0.6rem; }`

## 7. 素材来源平等原则

- **不设独立的"补充视角"或"Twitter/X 表态"章节**
- 所有素材（YouTube/播客、媒体文章、Twitter/X、研报）按主题逻辑合并进主流章节
- 附录索引不区分来源类型（不标 "Twitter/X" 或 "已综合" 徽章），统一列出

## 7. 附录索引规范

### 位置

附录索引放在页面底部（主报告和所有已生成附录之后、底部版权信息之前），**不在顶部**。

### 索引列表格式

即使未生成，附录标题也必须在索引中列出，并标注状态。已生成的用可点击链接 + 绿色徽章。

```html
<li><a href="#p1">01 · 已生成标题</a> <span class="badge">已生成</span></li>
<li><span class="pending">02 · 待生成标题</span> <span class="badge pending">待生成</span></li>
```

## 8. CSS 样式规范

### 推文卡片样式

```css
.tweet {
    padding: 1.2rem 0 1.2rem 0.8rem;
    border-bottom: 1px solid #eef2f6;
}
.tweet:last-of-type { border-bottom: none; }
.tweet .tweet-label {
    font-weight: 600;
    font-size: 0.9rem;
    color: #2563eb;
    margin-bottom: 0.2rem;
}
.tweet .tweet-body {
    font-size: 1rem;
    color: #1e293b;
    line-height: 1.8;
}
.tweet .tweet-body p {
    margin-bottom: 0.3rem;
}
.tweet .tweet-body p:last-child {
    margin-bottom: 0;
}
.highlight {
    color: #16a34a;
    font-weight: 500;
}
```

### 完整页面样式

完整 CSS 样式参见 `assets/report-template.html` 模板文件。模板包含：
- 页面基础样式（字体、背景、最大宽度、居中布局）
- 板块标题样式（`.section-title`）
- 推文卡片样式（`.tweet` 系列）
- 高亮样式（`.highlight`）
- 徽章样式（`.badge`、`.badge.pending`）
- 附录索引样式（`.appendix-index`、`.pending`）
- 底部版权样式（`.footer`）
- 响应式适配

## 9. 结构优先级

**板块 > 推文编号**。板块是顶层结构，推文编号是板块内部的子项。生成 HTML 时先确定板块，再在板块内按顺序排列推文。
