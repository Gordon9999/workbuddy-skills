---
name: my-writer
description: "个人书写风格格式化技能。当用户说「用我的风格写」「格式化成我的风格」「按我的风格排版」「转写」时触发；产出任何文章类 HTML 前都应先加载。接收任意文本/素材，根据原文复杂度自动选择模式：原文丰富（有表格/流程图/架构图/图片/多级标题/超 2000 字）时只做 HTML 排版不改文字不改结构，且必须保留原文所有图表和图片（SVG 内联、图片 base64）；原文简单时按短句口语化风格改写。输出 HTML 文件。核心特征：1）HTML 视觉风格提取自 insightview；2）文字风格为短句口语化；3）标题走 FT 头版新闻风格；4）绿色高亮 `.highlight` #16a34a（自写 CSS 时必须显式定义，最常漏）；5）转写/长文类固定带开头「序」（只写背景一段，不写「背景。」前缀，附近不带横线）+ 结尾「修改日志」（日期，标题，作者）；6）配套推文版每条 = 小标题 + 右序号 + 多句正文，不要头像/handle/互动数；7）尾部注明生成日期、来源、是否使用 LLM；8）换行纪律（硬要求，用户强强调）：一个意思一个段落，一段最多 3 句，超过必拆，金句可单句成段，禁止连续 4 句以上无换行，Markdown/纯文本段间必须空行。"
agent_created: true
---

# My Writer — 个人书写风格格式化

## 概述

接收任意文本或素材，按照用户固定的个人书写风格重新组织内容，输出为一份干净的 HTML 文件。风格提取自 insightview 的 HTML 视觉体系，文字风格遵循短句口语化原则，标题采用 FT 头版新闻风格。

**HTML 视觉基线**：颜色、字体、容器、高亮、底部、响应式等共享值见 `references/shared-html-spec.md`（insightview / my-writer / voice2article 三 skill 共用的单一事实来源），本 skill 模板 CSS 须与之一致。

**可被 voice2article 调用**：voice2article 完成语音转写后，将原始转录文本交本 skill 执行模式 B（短句口语化改写）+ HTML 排版。转录稿属于口语化纯文本，默认触发模式 B。

## 触发条件

- 用户说「用我的风格写」「格式化成我的风格」「按我的风格排版」时触发
- 用户上传文本/素材并说「整理一下」「排版一下」时触发
- 用户给出一段文字并说「帮我重写」时触发
- 用户贴上会议/语音转写稿并说「转写」「整理成文章」时触发（走模式 A 排版 + 序 + 修改日志 + 配套推文版）
- **只要产出文章类 HTML（长文 / 转写稿 / 推文流 / 报告）就应先加载本 skill，不要自己现写 CSS**——2026-09-11 因跳过本 skill 导致绿色高亮整体缺失

## 工作流程

### 第一步：接收素材

接收用户提供的任意文本内容。来源可以是：
- 直接输入的文字
- 上传的文件（txt/md/docx 等）
- 转录稿、笔记、草稿

读取内容，理解核心信息。

### 第二步：判断改写模式（关键决策）

根据原文的复杂度和结构丰富度，选择以下两种模式之一：

#### 模式 A：仅排版（原文丰富时不改文字）

**触发条件**（满足任一即可）：
- 原文包含表格
- 原文包含流程图 / 架构图 / 代码块 / **SVG 图 / 图片 / 截图**
- 原文有明确的多级标题结构（3 个以上小节）
- 原文超过 2000 字且结构清晰

**做法**：
- **不改原文文字**——不缩写、不改写、不调整语序、不删减内容
- **不改原文结构**——保留所有章节、表格、代码块、列表
- **保留原文所有图片和图表**——SVG 架构图、流程图、截图等必须原样嵌入 HTML，不得丢弃或省略
- 只做 HTML 排版：套用模板样式、表格转 HTML 表格、代码块转 `code-block`、引用转 `quote-block`、关键概念加绿色高亮、标题用 `part-title` / `section-title` 样式
- SVG 图直接内联到 HTML 中（`<svg>` 标签），图片用 `<img>` 或 base64
- 尾部标注「本文为原文排版，未做内容改写」，不标 LLM

#### 模式 B：风格改写（原文简单时转写）

**触发条件**：
- 原文以纯文字为主，无表格、无图、无代码块
- 原文结构简单（1-2 个小节或无小节）
- 原文是口语转录稿、笔记、草稿

**做法**：
- 按用户书写风格（短句口语化）改写
- 保留全部关键信息，只改变表达方式
- 按第三步的风格规则执行
- 尾部标注「本文由 AI 辅助改写（LLM: 模型名）」

**判断原则**：宁可选模式 A 也不要在丰富内容上强行改写。内容损失的风险远大于风格统一的收益。

### 第三步：生成标题（FT 头版风格）

按照 FT（Financial Times）头版新闻风格生成标题。FT 头版标题特征：

- **简洁有力**：5-15 个字（中文），直击核心，不含废话
- **陈述事实或判断**：不搞噱头，不问反问句，直接说事
- **可带角度**：用冒号或破折号分隔主题和角度
- **权威感**：像报纸头版编辑写的，不是自媒体标题党

**必须给出 2-3 个标题选项**，让用户选择。格式如下：

```
请选择标题：

A. [选项一：直述型]
B. [选项二：分析型，带角度]
C. [选项三：判断型，带结论]
```

标题选项要风格各异，覆盖不同角度。用户选定后再进入下一步。

如果用户已经给了明确标题，直接使用，不再生成选项。

### 第四步：改写正文（模式 B 专用）

> 如果第二步判断为模式 A（仅排版），跳过此步，直接进入第五步生成 HTML——原文文字原样保留。

将原始内容按照用户书写风格改写。**改写不是缩写**——保留全部关键信息，只改变表达方式。

#### 书写风格规则（严格遵守）

1. **短句优先**：每句话不超过 25 个字。长句必须拆短。
2. **口语化**：像跟朋友聊天时说的话，不像写论文。用「的」「了」「着」等口语助词。
3. **每段 2-3 句**：说完一个意思就换行。不要把多个意思塞在一段里。
4. **禁止假大空**：不写「赋能」「抓手」「闭环」「生态」这类词。说人话。
5. **禁止排比堆砌**：不用「不仅…而且…更重要的是」这种递进句式。直接说结论。
6. **数据要具体**：写「45 亿美元」不写「数十亿美元」。写「90%」不写「绝大部分」。
7. **绿色高亮**：核心概念、关键数据、专有名词用 `<span class="highlight">关键词</span>` 标注。每段 0-2 个，不宜过多。
8. **换行是硬要求（最重要，违反即不合格）**：
   - **一个意思 = 一个 `<p>` = 一次换行**。禁止把多个意思塞进同一个 `<p>` 里。
   - **一段最多 3 句**，超过 3 句必须断开换行，另起一段。
   - **金句 / 判断句 / 关键数据句可单句成段**（一行一段），读起来有呼吸感——允许，甚至是加分项。
   - **禁止「一大坨」**：正文里出现连续 4 句以上中间没有任何换行 ＝ 不合格，必须拆开。
   - 段落之间靠 `<p>` 自带的 margin 分开（模板已设 1.05rem），**只有需要更大间隔时才用 `<br>`**，不要拿 `<br>` 当换行工具。
   - Markdown / 纯文本输出同理：**段与段之间必须空一行**，不得把多段合并成一整段。
   - **输出前自查一遍换行**：逐段数句子，超 3 句就拆，拆完再交付。

#### 改写示例

原文（长句风格）：
> 该公司通过引入先进的自然语言处理技术和大规模语言模型，实现了客户服务流程的全面自动化，从而显著降低了运营成本并提升了用户满意度。

改写后（用户风格）：
```html
<p>他们用大模型把客服流程跑通了。</p>
<p>运营成本降下来了，用户满意度也上去了。</p>
```

### 第五步：生成 HTML

使用 `assets/article-template.html` 作为基础模板，将改写后的内容填入。

#### 固定版式：开头「序」+ 结尾「修改日志」（用户约定，2026-09-11）

**转写稿 / 长文类 HTML 必须带这两块**，顺序固定：

**① 开头：序**（放在 kicker + 标题 + pills + meta 之后，第一个 part-title 之前）

- 内容为**背景一段**：时间、地点、做了什么、目的是什么
- **不写「背景。」前缀**——与「序」标题重复，用户明确要求去掉
- **序附近不带任何横线**：不设 `border-bottom`，不做渐隐分隔线，靠留白和正文拉开距离
- 结构：`<div class="preface"><span class="preface-char">序</span><p>…</p></div>`
- 样式：`.preface-char` 1.3rem 粗体亮色、`letter-spacing: 0.12em`、`display: block`、下边距 0.9rem；`.preface p` 1.02rem / line-height 1.95

**② 结尾：修改日志**（放在 `.footer` 之前）

```html
<div class="changelog">
  <h2>修改日志</h2>
  <ul>
    <li><span class="date">2026.09.11</span>硅谷 AI 客服调研总结，陈刚</li>
  </ul>
</div>
```

- 条目格式：`日期 + 逗号 + 标题 + 逗号 + 作者`
- 每次修改追加一行，不覆盖旧记录

#### HTML 结构

```html
<div class="container">
    <!-- 文章头部：FT 风格 -->
    <div class="article-header">
        <div class="kicker">{{分类标签}}</div>
        <h1>{{标题}}</h1>
        <div class="standfirst">{{导语：1-2 句话概括全文核心}}</div>
    </div>

    <!-- 正文 -->
    <div class="article-body">
        <!-- 引子（可选）：数据/事实亮相 -->
        <p>先看一组数字。</p>
        <p>...</p>
        <br>
        <p>总结性判断。</p>
        <!-- 注意：引子和 part-title 之间不用 <br>，part-title 自带 margin -->

        <!-- 一级标题 -->
        <div class="part-title">一、大段标题</div>
        <!-- 二级标题 -->
        <div class="section-title">小节标题</div>
        <!-- 换行纪律：一个意思一个 <p>，超过 3 句必拆，金句可单句成段 -->
        <p>一个意思，单独一个段落。</p>
        <p>换行了，每个意思各占一行。</p>
        <p>关键判断句可以单句成段。</p>
        <!-- 段间留白由 <p> 的 margin 负责；只有要更大间隔时才用 <br> -->

        <!-- 二级标题 -->
        <div class="section-title">下一个小节</div>
        <p>...</p>

        <div class="part-title">二、下一个大段</div>
        <!-- ... -->
    </div>

    <!-- 尾部信息 -->
    <div class="footer">
        <div class="footer-meta">生成日期：{{YYYY-MM-DD}}</div>
        <div class="footer-meta">来源：{{来源说明}}</div>
        <div class="footer-meta">本文由 AI 辅助改写（LLM: {{模型名}}）</div>
    </div>
</div>
```

#### Kicker（分类标签）

标题上方的小标签，类似 FT 的栏目分类。根据内容选择：
- 行业观察 / 产品分析 / 组织管理 / 技术解读 / 市场趋势 / 人物访谈
- 也可以自定义，但要简短（2-4 个字）

#### Standfirst（导语）

标题下方的一句话概括。1-2 句，不超过 50 字。点出文章最核心的信息或判断。

#### 正文两级标题

如果内容较多，用两级标题组织结构：

- **一级标题（大段分隔）**：`<div class="part-title">一、某某</div>` —— 用 `一、` `二、` `三、` 编号，粗底边框
- **二级标题（小节内分节）**：`<div class="section-title">小节标题</div>` ——  2-6 个字，浅底边框

一级标题之间留 `<br>` 换行，拉开视觉距离。

#### 引子段落

在文章最前面（标题与第一个一级标题之间），可以用一组数据或事实作为引子。格式：

```html
<p>先看一组数字。</p>
<p>具体数据1。</p>
<p>具体数据2。</p>
...
<br>
<p>总结性判断。</p>
<p>抛出问题。</p>
<div class="part-title">一、...</div>
```

引子是全文的亮相环节，不说废话，直接上场。

**注意**：引子和第一个 `part-title` 之间不用额外的 `<br>`——`part-title` 自带的 `margin-top: 2.5rem` 已足够，加 `<br>` 反而间距过大。

#### 段落分组空行

同一个小节内，当一个意思说完、切换到另一个意思时，用 `<br>` 隔开。

```html
<p>讲完一个意思。</p>
<p>这个意思的延续。</p>
<br>
<p>切换到另一个意思。</p>
```

不要在所有段落之间都用 `<br>`——只在意群切换处使用。同一个意思内的几句话不需要空行。

#### 表格

如需列出对比数据或清单，用内联样式表格：

```html
<table style="width:100%;border-collapse:collapse;margin:1rem 0;font-size:0.92rem;">
    <tr>
        <th style="background:#1e293b;color:#fff;padding:0.6rem 0.8rem;text-align:left;font-weight:600;">列头A</th>
        <th style="background:#1e293b;color:#fff;padding:0.6rem 0.8rem;text-align:left;font-weight:600;">列头B</th>
    </tr>
    <tr>
        <td style="padding:0.55rem 0.8rem;border-bottom:1px solid #eef2f6;">内容</td>
        <td style="padding:0.55rem 0.8rem;border-bottom:1px solid #eef2f6;">内容</td>
    </tr>
</table>
```

#### 引用块

突出关键案例或判断，用蓝色左边框：

```html
<div class="quote-block">
    Intercom 是正面案例。...
</div>
```

#### SVG 架构图 / 流程图（模式 A 必须保留）

如果原文包含 SVG 架构图、流程图等可视化内容，**必须原样内联嵌入 HTML**，不得丢弃。做法：

1. **SVG 直接内联**：把 `<svg>` 标签直接粘贴到 HTML 正文中，不要用 `<img>` 引用外部文件
2. **SVG 容器样式**：用 `figure-container` 包裹，加标题和间距

```html
<div class="figure-container" style="margin: 1.5rem 0; text-align: center;">
    <svg viewBox="0 0 680 400" style="width:100%;max-width:680px;height:auto;">
        <!-- SVG 内容 -->
    </svg>
    <div style="margin-top: 0.5rem; font-size: 0.82rem; color: #94a3b8;">图 1：架构总览</div>
</div>
```

3. **图片用 base64 内联**：如果是 PNG/JPG 截图，转 base64 嵌入 `<img>` 标签

```html
<div class="figure-container" style="margin: 1.5rem 0; text-align: center;">
    <img src="data:image/png;base64,{{base64内容}}" style="max-width:100%;border-radius:6px;" />
    <div style="margin-top: 0.5rem; font-size: 0.82rem; color: #94a3b8;">图 2：流程示意</div>
</div>
```

**关键检查**：生成 HTML 后，对照原文检查每张图/表是否都存在。原文有几张图，HTML 里就必须有几张图。

### 第六步：尾部信息（必备）

HTML 底部必须包含以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| 生成日期 | 当前日期，YYYY-MM-DD 格式 | 2026-08-10 |
| 来源 | 素材来源说明 | 原始素材来自 XX 访谈 / 用户提供文本 / 基于 XX 文章改写 |
| LLM 标注 | 如果使用了 LLM 改写，必须注明模型名 | 本文由 AI 辅助改写（LLM: Auto） |

如果完全是对用户原文的排版（未做内容改写），则不标注 LLM。
如果使用 LLM 做了改写、重写、润色，必须标注。

尾部 HTML 示例：

```html
<div class="footer">
    <div class="footer-meta">生成日期：2026-08-10</div>
    <div class="footer-meta">来源：用户提供文本</div>
    <div class="footer-meta">本文由 AI 辅助改写（LLM: Auto）</div>
</div>
```

#### 推文版格式（tweets/index.html，用户约定 2026-09-11）

长文之外常配套一份推文流。**每条推文的结构**：

```html
<div class="tweet">
  <div class="head"><span class="title">这条的小标题</span><span class="no">01</span></div>
  <div class="text">
    <p>正文 2-4 句。</p>
    <p>…</p>
    <div class="quote">金句引用（可选）</div>
  </div>
</div>
```

硬性要求：

- **头部写这条自己的小标题**（4-10 字，概括本条主题），**不要重复作者名 / @handle**——每条都一样毫无信息量
- **不要头像图标**（不用 `.avatar`），**不要「作者名 @handle」行**，**不要假互动数**
- 序号靠右，灰色小字
- 正文是**多句段落**（2-4 句），不是一句话碎片——一句话版被用户否过
- 关键概念 / 数据同样上绿色高亮
- 按主题分 5-8 个 `.group` 小标题分组

## 第七步：发布到 git（用户约定，2026-08-12）

当用户说「发布到 git」时，默认发布到用户的 GitHub 仓库 **AIKefu**（https://github.com/Gordon9999/AIKefu，公开仓库，已开启 GitHub Pages），目录为 **`biji/`**。

### 默认行为

- **仓库**：`AIKefu`（https://github.com/Gordon9999/AIKefu）
- **目录**：`biji/`（如用户指定其他目录名则用指定的）
- **文件名**：根据文章主题生成英文 slug，如 `ai-customer-service-agent-architecture.md`
- **访问链接**：`https://gordon9999.github.io/AIKefu/biji/<文件名>`

### Git 信息来源

git 仓库地址、凭证获取方式、技术要点**统一从 insightview skill 的「第四步：发布到 git」读取**，不在本 skill 重复维护。关键信息摘要（2026-09-12 更新）：

- **仓库**：`Gordon9999/SaaS2Agent`（原 AIKefu，2026-09-12 改名），Pages 根 `https://gordon9999.github.io/SaaS2Agent/`
- **发布方式**：首选 git（SSH 已打通，clone 在 `~/Developer/GitHub/SaaS2Agent`），用 `bash ~/Developer/GitHub/push.sh SaaS2Agent "msg"`（脚本内置锁清理与重试）；git 不可用时降级 GitHub Contents API
- **目录**：文章按主题归入四大分组 `<分组>/<主题slug>/`——`XiaoP/` 个人助理 / `Kefu/` 客服 AI / `CRM/` AI+CRM / `SaaS/` 传统 SaaS；**旧的 `biji/` 默认目录已废弃**（内容迁至 next3 仓库）
- **上传后验证**：`curl -s -o /dev/null -w "%{http_code}" https://gordon9999.github.io/SaaS2Agent/<分组>/<主题slug>/` 返回 200

### 执行流程

1. 生成文章 HTML（或 Markdown，视用户需求）到本地临时文件
2. 如用户未指定文件名，根据主题生成英文 slug 作为文件名
3. 读取 insightview skill 获取最新的 git 发布技术细节
4. 复制到 `~/Developer/GitHub/SaaS2Agent/<分组>/<主题slug>/` → 用 push.sh 提交推送
5. curl 验证访问链接返回 200
6. 输出访问链接给用户

### 注意事项

- 用户说「发布到 git」但未指定位置时，**先确认目标分组与目录名**，不要默认写入任何目录
- 新增主题目录后需重建导航页：`python3 ~/.workbuddy/skills/insightview/scripts/gen_saas2agent_index.py --out ~/Developer/GitHub/SaaS2Agent/index.html`，且**必须在内容 push 之后运行**（脚本从 GitHub API 取树，顺序反了会漏文件）

## 资源文件

| 文件 | 用途 |
|------|------|
| `assets/article-template.html` | HTML 文章模板，包含完整 CSS 样式 |
| `references/writing-style-guide.md` | 书写风格详细规范、正反示例、常见问题 |
| `references/shared-html-spec.md` | 共享 HTML 视觉基线（insightview / my-writer / voice2article 三 skill 共用，单一事实来源） |

## 关键原则

- **改写模式优先判断**：原文内容丰富（有表格、流程图、多级标题、超 2000 字）时只做排版不改文字；原文简单（纯文字、结构简单）时才用风格改写。内容损失的风险远大于风格统一的收益。
- **图表不可丢弃**：模式 A 下，原文中的每张 SVG 图、流程图、架构图、截图、表格都必须原样嵌入 HTML。生成后逐项对照原文检查，少一张图就是不合格。
- **风格优先于内容**：在模式 B（改写）下，宁可砍掉一段内容，也不写长句。信息密度靠精准表达，不靠堆字数。
- **标题必须可选**：每次生成标题都给 2-3 个选项，除非用户已指定标题。
- **尾部不可省略**：日期、来源、LLM 标注三项缺一不可。模式 A 不标 LLM，模式 B 必须标。
- **高亮克制**：绿色高亮是点睛，不是装饰。每段最多 2 个。
- **高亮必须先定义 CSS（最常漏）**：用 `assets/article-template.html` 就自带 `.highlight`；**自己另起一套 CSS（尤其暗色主题）时，必须在样式表里写 `.highlight { color: #16a34a; }`**，否则整篇完全没有绿色。交付前用 `grep -c 'class="highlight"'` 自查：长文应 ≥ 15 处，推文版每 2-3 条 1 处，为 0 就是没执行。
- **发布到 git 默认 biji**：用户说「发布到 git」= 上传到 AIKefu 仓库 `biji/` 目录，git 技术细节从 insightview skill 读取。
