---
name: insightview
description: "InsightView: 主题阅读与综合报告生成技能（v4.3）。当用户上传访谈/视频/文章素材并说「用 insightview 总结」时触发；当用户直接给出主题（无上传素材）时亦触发，此时技能主动从三类来源搜集素材：YouTube/播客视频、重要媒体深度文章、关键人物 Twitter/X。默认输出 HTML 格式的 xInsightView 推文串报告，支持长文（Markdown）、推文串、HTML 三种输出模式。核心工作流：设定主题 - 主动搜集素材（无上传时）- 逐篇处理（主题匹配度检查 - 生成长文 - 改写推文）- 生成综合 HTML 报告。"
agent_created: true
---

# InsightView — 主题阅读 + 综合报告生成（v4.3）

## 概述

InsightView 是一套主题阅读与综合报告生成工作流。用户围绕一个主题逐篇上传素材（访谈/视频/文章），技能逐篇提取信息并结构化为长文，再将长文改写为 xInsightView 推文串，最终汇总为一份模块化 HTML 报告。

**核心原则：先生成长文，再从长文改写推文。长文是完整的信息提取结果，推文是长文的精简表达。绝不直接从原文生成推文。**

## 一、触发条件

### 基础触发

- 用户上传访谈/视频/文章素材，说「用 insightview 总结」时触发
- 用户直接给出一个主题（如「用 insightview 分析一下 AI agent 是否会颠覆 Salesforce」）但未上传素材时**同样触发**——此时执行「第一步半：主动搜集素材」

### 模式指定

| 用户指令 | 输出 |
|---------|------|
| 「用 insightview 总结」 | 默认输出 xInsightView 推文模式的 HTML 文件 |
| 「用 insightview 总结，出长文」 | InsightView 完整长文（Markdown 格式） |
| 「用 insightview 总结，出推文」 | 先生成长文，再基于长文改写为 xInsightView 推文串 |
| 「用 insightview 总结，出全部」 | 长文 + 推文 HTML 都输出 |
| 「用 insightview 总结，出 HTML」 | xInsightView 推文串的 HTML 文件（与默认行为相同） |

### 改写触发

- 「把这篇 insightview 改写成推文」→ 基于已生成的长文改写为推文（不从原文直接生成）
- 「把这篇推文改成长文」→ 推文转长文

## 二、工作流程

### 第一步：设定主题

用户先明确本次阅读的主题，例如：「AI 客服之 Decagon」。后续所有上传的素材都围绕该主题处理。

### 第一步半：主动搜集素材（用户约定，2026-08-09）

当用户直接给出主题但**未上传素材**时，技能必须主动从以下三类来源搜集素材，然后进入第二步逐篇处理：

#### 三类必搜来源

| 来源类型 | 搜集方式 | 优先级 |
|---------|---------|--------|
| **YouTube / 播客视频** | `site:youtube.com <主题关键词>` 搜索，覆盖创始人/CEO 访谈、行业播客深度对话、产品发布演讲；对找到的视频用 WebFetch 获取转录稿或摘要 | 🔴 最高 |
| **重要媒体深度文章** | WebSearch 搜索主题相关深度分析文章，覆盖科技媒体（TechCrunch/The Verge/Stratechery）、行业垂直媒体、中文科技媒体（36kr/虎嗅/腾讯科技）、分析师报告 | 🔴 最高 |
| **关键人物 Twitter/X** | 搜索主题相关的关键决策者、创始人、行业意见领袖的 Twitter/X 帖文（`site:x.com <人物名> <主题>` 或 `site:twitter.com`），捕捉他们的公开表态、争论、预测 | 🟡 重要 |

#### 搜集要点

- **多轮搜索**：每类来源至少 2-3 轮 WebSearch，用不同关键词组合（`query_keyword_groups`）覆盖多角度
- **中英文并行**：主题涉及海外公司/产品时，必须同时搜英文和中文素材
- **补充搜索**：首轮搜集后如发现视角缺口（如缺少反方观点、缺少竞争对手视角），主动追加搜索补齐
- **素材量目标**：至少 15-20 篇有效素材，确保覆盖正方/反方/中立多维度观点
- **来源记录**：每篇素材的标题、来源平台、URL 记入附录索引，最终体现在报告底部

#### 与上传素材的关系

- 用户上传素材 → 直接进入第二步逐篇处理
- 用户仅给主题（无上传）→ 执行主动搜集 → 将搜集到的素材视为"已上传" → 进入第二步
- 用户既给主题又上传素材 → 先处理上传素材，再主动搜集补充视角

### 第二步：逐篇处理（核心工作流）

每上传一篇文章/视频/访谈，依次执行：

#### 步骤 A：检查主题匹配度

- 将素材内容与已设定主题进行匹配度判断
- **不匹配**：提示用户，询问「继续读实际主题」还是「结束换一篇」
- **匹配**：进入步骤 B

#### 步骤 B：生成 InsightView 长文（必要步骤）

- **无论用户最终要长文还是推文，都必须先生成长文**
- 长文是完整的信息提取和结构化结果，是一切输出的源材料
- 长文结构遵循六大板块（详见 `references/html-spec.md` 的板块定义）
- 长文以 Markdown 格式输出

#### 步骤 C：根据用户模式输出

| 用户模式 | 输出动作 |
|---------|---------|
| 长文 | 直接输出步骤 B 的长文（Markdown 格式） |
| 推文 / HTML / 未指定 | 将步骤 B 的长文改写为 xInsightView 推文串，生成 HTML 文件 |
| 全部 | 先出长文，再出推文 HTML |

**为什么必须先生成长文？**
- 长文是完整的信息提取，确保不丢失任何细节
- 推文是长文的精简表达，信息质量取决于长文的完整性
- 直接从原文生成推文，容易遗漏关键信息或误解上下文

### 第三步：生成综合报告

沿用模块化 HTML 生成策略，分批发文（先主报告 + 高质量篇目，其余按需追加）。

详见 `references/batch-strategy.md`。

### 发布前自检（必做，2026-09-12 补充）

每篇附录写完、发布前，跑一遍这四项检查（写成一次性 Python 脚本最快）：

1. **附录内部编号 = 文件名编号**：`appendix-06.html` 里的 `<div class="tag">附录 NN</div>`、`<title>`、footer 三处都必须是 `06`。
   *（2026-09-12 实际踩坑：`appendix-06.html` 内部标着「附录 07」，主报告索引却写 06，两边对不上，发布后才发现。）*
2. **内部链接零缺失**：主报告的 `href="appendix-NN.html"`、每篇附录的 `href="index.html"` 逐个验证目标文件存在。
3. **标签白名单 + div 配对**：只允许 `html/head/body/meta/title/style/div/span/p/a/ul/li/h1/h2/h3/strong/br/em/link/table/tr/td/th/thead/tbody`；`<div` 与 `</div>` 数量必须相等。
   **禁止用 `<b>`**——统一写成 `<span class="highlight">`，否则与既有篇目风格不一致。
4. **推文数与高亮密度**：主报告 12-16 条、单篇附录 16-23 条；高亮数为 `class="highlight"` 总数减去 CSS 里那 1 处定义，再除以推文数，应落在 1-3。

**主报告索引收尾**：全部附录生成完后，把索引里所有 `<span class="pending">` 和 `badge pending` 换成可点击 `<a href="appendix-NN.html">`，同时去掉「已生成」徽章（全生成后徽章不再有信息量，只留编号列表最干净）。

### 第四步：发布到 git（用户约定，2026-08-07）

- 用户说「发布到 git」= 将**推文版**（`tweets/` 下 HTML：主报告 `index.html` + `appendix-NN.html`）发布到 GitHub 仓库 **SaaS2Agent**（https://github.com/Gordon9999/SaaS2Agent，公开仓库，已开启 GitHub Pages；导航页对外标题为 **SaaS2Agent**）。
- **仓库目录结构（2026-09-12 重组，已上线）**：不再扁平存放，一级目录按研究方向分组，主题放在对应分组下：

| 分组 | 展示名 | 收录主题（现有） |
|---|---|---|
| `XiaoP/` | 🤖 个人助理方向 | instinct |
| `Kefu/` | 🎧 客服 AI | cresta / decagon / intercom / sierra / sierra-saas-disruption |
| `CRM/` | 🏢 AI + CRM / 内部系统 | day.ai / rox.ai |
| `SaaS/` | 💰 传统 SaaS 大佬 | hubspot / salesforce / servicenow / zendesk |

- **发布路径 = `<分组>/<主题-slug>/`**（例：`XiaoP/instinct/`、`Kefu/decagon/`）。新主题先判断归属分组；个人助理 / Personal Agent 方向一律进 `XiaoP/`。
- 执行流程：
  1. **先确认目标分组与目录名**（用户可直接给出，如「放入 XiaoP」）；
  2. 将 tweets 下的推文 HTML 复制到 `SaaS2Agent/<分组>/<目录名>/`；
  3. 发布：Pages 已全局开启（main 分支根目录 + `.nojekyll`），上传后自动构建生效，无需重复开启；
  4. 输出访问链接 `https://gordon9999.github.io/SaaS2Agent/<分组>/<目录名>/`（上传后 curl 验证返回 200）。
- 技术要点：
  - **首选 git（2026-09-11 起 SSH 已打通）**：仓库 clone 在 `~/Developer/GitHub/SaaS2Agent`，`~/.ssh/config` 已把 github.com 指向 `ssh.github.com:443`，直接 `git add -A && git commit && git push origin main` 即可，无需代理/token；
  - **网络选路（2026-09-12 实测，别再换回去）**：SSH + ControlMaster 复用稳定 **3-5 秒**；HTTPS `github.com` 匿名 `ls-remote` 实测 **110s / 20s / 75s**，抖动极大。**保持 SSH，不要因为「token 更快」的旧印象切回 HTTPS**；`~/.ssh/config` 的 `ControlPersist` 已设为 `8h`（原 10m，间隔稍久就要重新握手 3-4 秒）；
  - **一键发布用 `~/Developer/GitHub/push.sh <目录名> "<msg>"`**（2026-09-12 重写）：结尾会打印「未推送提交数」，**只信这一行**——脚本中间输出曾出现「打印 no changes 但实际已提交 / 已提交但没推上去」两种假象，务必用 `git rev-list --count origin/main..HEAD`（0 = 已同步）确认；
  - **发布前必查 `.git/index.lock`（2026-09-12 定位的根因）**：沙箱对 `.git` 写保护，任何 git 写操作被中断都会留下 `index.lock`；此后 `git add` **静默失败**（只报 `may have crashed earlier`）→ 暂存区为空 → 脚本误报 `nothing staged`，而沙箱内 `rm index.lock` 又被拒（`Operation not permitted`），**形成死锁**。破法：**清 lock 与所有 git 写操作一律在非沙箱（提权）模式下执行**；push.sh 已加开头的显式检测拦截；
  - **绝不 `rm .git/*.lock` 后再 `set -e`**：沙箱下 `rm` 失败会让脚本静默提前退出；
  - **中断残留体检**：`git count-objects -v` 若报 `warning: garbage found: .git/objects/**/tmp_obj_*`（沙箱写保护导致），执行 `find .git/objects -name 'tmp_obj_*' -type f -delete` 清理；
  - **降级方案（git 不可用时）GitHub Contents API**：`PUT https://api.github.com/repos/Gordon9999/SaaS2Agent/contents/<路径>/<文件名>`，body `{"message": "...", "content": "<base64>"}`，Header `Authorization: Bearer <token>`（201 即成功）；路径带尾斜杠会返回 302 canonical 重定向，须加 `curl -L`；macOS base64 输出带换行，须 `| tr -d '\n'`；
  - 凭证：`printf "protocol=https\nhost=github.com\n\n" | git credential fill` 从钥匙串取（password 字段即 token，**切勿输出**）；
  - 批量上传：遍历 `tweets/*.html` → 逐个 add/commit/push；上传后 curl 检查页面返回 200 确认发布生效。
- **发布后重建导航页（顺序不可颠倒：先 push 内容，再重建导航）**：
  - 仓库根 `index.html` 是**静态渲染导航页**（v4：内容在生成时渲染成纯 HTML，零 JS 依赖、打开必定显示、秒开），必须与仓库最新文件一致；
  - **v4 渲染规则（三段式：分组 / 主题 / 文件）**：分组标题下，主题目录**含 index.html → 只展示一张「主页」入口卡片，绝不展开内部文件**（用户明确要求导航页只展示目录结构）；主题目录无 index.html → 展开文件列表（GitHub Pages 不提供目录浏览，只链目录会空白）；
  - 每次发布/删除内容后运行：`scripts/gen_saas2agent_index.py --out <仓库根 index.html>`（从 GitHub API 拉最新文件清单 → 静态渲染 → 内嵌快照），再 commit/push 覆盖根目录 `index.html`；
  - 该脚本从 GitHub API 取树，因此**必须在内容 push 之后运行**，否则会漏掉刚发布的文件；
  - 页面有「🔄 刷新列表」按钮可手动拉取最新（备用，默认不依赖）；
  - 历史教训：v1 实时 API 版太慢被弃用；v2 内嵌快照版曾因 JS 双引号嵌套语法错误导致内容空白，已升级 v3 静态渲染；v3 只认两级目录，分组重组后会把分组下属主题展开成一长串文件列表，故升级 v4。

## 三、HTML 生成规范

HTML 报告的结构、CSS 样式、推文卡片格式、高亮规范、附录索引等详细规范，参见 `references/html-spec.md`。

**HTML 视觉基线**：颜色、字体、容器、高亮、底部、响应式等共享值见 `my-writer/references/shared-html-spec.md`（insightview / my-writer / voice2article 三 skill 共用的单一事实来源）。本 skill 模板 CSS 须与之一致；改基线值只改该文件，再同步到 `assets/report-template.html`。

### 核心要点速览

- **板块结构**：📌 一句话总结 → 📦 公司角度 → 🧩 产品角度 → 🏗️ 组织角度（附录可额外包含 👤 访谈人背景、💡 核心观点、💬 行业观点）
- **推文标签**：「推 N · [主题标题]」格式，N 为连续编号不按板块重置
- **内容换行**：每段 2-4 句，用 `<p>` 标签包裹，表达完一个完整意思后换行
- **绿色高亮**：核心概念/关键数据/专有名词用 `<span class="highlight">关键词</span>`，每条推文 1-3 个
- **推文数量**：主报告 12-16 条，单篇附录 16-23 条
- **附录索引**：放在页面底部，已生成用可点击链接 + 绿色徽章，未生成标注「待生成」

### HTML 模板

使用 `assets/report-template.html` 作为生成基础模板，替换其中的占位内容。

## 四、长文 ↔ 推文转换规则

详细的转换规则参见 `references/conversion-rules.md`。

### 核心要点速览

- **长文转推文**：保持六大板块结构不变（推文模式将一句话总结提前到最前面），将每个段落/信息点拆成多条推文，每条聚焦一个子主题，长句拆短句，口语化但保留全部信息
- **推文转长文**：将推文串还原为结构化长文，恢复完整上下文和逻辑连接

## 五、批量生成策略

详见 `references/batch-strategy.md`。

### 核心要点速览

- **首次生成**：主报告（index.html）+ 第一批高质量篇目附录，其他附录在索引中标记「待生成」
- **高质量篇目筛选标准**：创始人/CEO 深度访谈、核心技术或产品发布、战略层面内容、内容完整度高
- **追加生成**：用户说「追加附录 N」或「全部生成」时补充对应 HTML

## 资源文件

| 文件 | 用途 |
|------|------|
| `references/html-spec.md` | HTML 结构规范、CSS 样式、推文卡片格式、高亮规范、附录索引格式 |
| `references/conversion-rules.md` | 长文↔推文双向转换规则 |
| `references/batch-strategy.md` | 批量生成策略、高质量篇目筛选标准、追加生成流程 |
| `assets/report-template.html` | HTML 报告基础模板 |
| `scripts/gen_saas2agent_index.py` | 重建仓库根目录导航页 index.html（v4 三段式静态快照；**须在内容 push 之后运行**） |
