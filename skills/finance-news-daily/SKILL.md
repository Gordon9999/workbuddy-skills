---
name: finance-news-daily
version: 1.5
description: 每日四主题财经新闻推文流生成器。用户说「收集新闻/今天的新闻」时触发：按固定四主题（ai / enterprise-agent / agent-startups / ota）搜集近 30 天资讯，增量更新到固定主题文件 Documents/news&research/data/<slug>.json（无日期目录），生成 HTML twitter 流页面到根目录 <slug>.html，带 ++（InsightView 候选）/ --（今日精选）交互、关键词深紫高亮（≤3 个/条）、agent-startups 含各公司发言人 X 账号。整版 X/Twitter 流排版。
triggers:
  - 收集新闻
  - 今天的新闻
  - 新闻推文流
  - daily news
  - finance daily
---

# finance-news-daily：每日四主题财经新闻推文流

## 触发条件
用户说「收集新闻」「今天的新闻」「生成新闻页」等，无特殊指定时默认跑**全部四主题**。

## 固定四主题（配置见 `/Users/qitmac001618/Documents/news&research/themes.json`）
| slug | 主题 | 范围 |
|---|---|---|
| `ai` | AI · 大模型 / Agent Infra | 大模型发布、Agent infra（MCP/A2A/算力）、行业大新闻、A 股 AI 板块 |
| `enterprise-agent` | Enterprise Agent · SaaS 转型 | SaaS 巨头 → Agent 转型与平台生态（Salesforce/ServiceNow/SAP/微软/Workday/Oracle/Intercom）；创业新贵见 agent-startups |
| `agent-startups` | Agent 创业 · AI 原生公司 | Sierra/Decagon/Cresta/Wonderful/Harvey/Manus/Omilia 等 AI 原生创业公司：产品技术、融资、创始人、客户动态 |
| `ota` | OTA · 在线旅游 | TCOM/同程/Booking/Expedia/Airbnb/抖音酒店/大酒店连锁（万豪/希尔顿/洲际/凯悦/雅高）：战略、管理层调整、业务进展、财经评估 |

> **历史变更**：v1.0 首发四主题（含 `china` 中国政经）→ 2026-09-04 大哥要求去掉 china → v1.1 三主题 → 同日要求增加 agent-startups（Sierra/Decagon/Cresta/Wonderful 类）→ v1.2 四主题。`china` 的 data/china.json 与 china.html 留作历史快照不索引；`enterprise-agent` 边界收窄为 SaaS 巨头，创业公司内容归 `agent-startups`（避免重复采集）。

## 硬性规则
1. **时效红线：只收录近 30 天资讯**。评上个季度之前的业绩、旧目标价、旧融资一律不收（宁可少条数）。
2. 信源：权威财经 / X / 雪球，每条推文必须带可点击的原文链接。
3. 每页 8–13 条，摘要放 intro，正文 2-3 段/条、每段 2-3 句、数据具体（my-writer 风格）。
4. 用户可能临时增减主题或指定单主题 — 以当天指令为准。

## 生成流程（每主题）
1. **搜索**：每主题 2-4 次 WebSearch（中英文并行），只取近 30 天素材。
2. **写数据（增量）**：`/Users/qitmac001618/Documents/news&research/data/<slug>.json`
   - **v1.5 起无日期目录**：四个主题各有一个固定 JSON 文件（`data/ai.json` / `data/enterprise-agent.json` / `data/agent-startups.json` / `data/ota.json`），每天新增信息直接追加到该文件 `tweets[]` 里（新条目插最前，按 date 降序），并顺手清掉超过 30 天的旧条目
   - 结构见 `tools/gen_page.py` 文件头注释（date/slug/topic/title/accent/pills/summary/tweets[]）
   - tweet 必填：avatar、avatar_color（green/gold/purple/pink/gray/blue/cyan）、name、handle、time、paras（HTML 内联 strong 可用）、links（label+url）、title、source、date
   - **topic 字段决定 ++/-- 清单分组**，四主题固定为：AI / Enterprise Agent / Agent 创业 / OTA
   - **v1.3 `keywords` 字段**（数组）：列出本条推文里要**深紫高亮**的关键实体（公司名/产品/人名/协议/财报数字），**每条 ≤ 3 个**（用户反馈"绿色词太多"，2026-09-04 起从 5-9 个砍到 2-3 个）。例：`["OpenAI", "GPT-6 Astra", "ARC-AGI-3"]`。渲染时自动包 `<span class="kw">` 染深紫 `var(--kw)`；`++/--` 投进清单后清单页推文卡片也带高亮（共用 paras）。关键词应**长而具体**避免误伤（用 `"Salesforce"` 而非 `"Sales"`，用 `"GPT-6 Astra"` 而非 `"GPT"`）。去掉通用词：`AI/数据/营收/Q1/Q2/中国/美国/市场/Agent/平台`等一律不收
   - **v1.5 `spokespeople` 字段**（可选，agent-startups 用）：数组，每项 `{company, official(公司官方 X), people:[{name, handle, role}]}`，渲染成「发言人 X 账号」面板。个人无公开 X 时 `handle` 留空 → 显示「无个人 X」。已确认 handle：Sierra→Bret Taylor `@btaylor`、Clay Bavor `@claybavor`；Decagon→Jesse Zhang `@thejessezhang`、Ashwin Sreenivas `@AshwinSreenivas`（官方 `@DecagonAI`）；Harvey→Winston Weinberg `@winstonweinberg`。Wonderful/Cresta/Manus 创始人无公开个人 X
3. **生成主题页**（输出到根目录，非日期子目录）：
   ```bash
   PY=/Users/qitmac001618/.workbuddy/binaries/python/versions/3.13.12/bin/python3
   BASE="/Users/qitmac001618/Documents/news&research"
   "$PY" "$BASE/tools/gen_page.py" "$BASE/data/<slug>.json" "$BASE/<slug>.html"
   ```
   ⚠️ 必须用**绝对路径** + `dangerouslyDisableSandbox: true`（Documents 受 TCC 保护；相对路径会触发 PermissionError）。页面 `<script src="common.js">`（根目录直引，非 `../common.js`）。
4. **生成聚合首页**（index.html 把四主题推文流全部展开）：
   ```bash
   "$PY" "$BASE/tools/gen_index.py" "$BASE"
   ```
   - gen_index.py 读固定 `data/<slug>.json`、链接 `./<slug>.html`，复用 gen_page.py 的 CSS 与 render_tweet/render_spokespeople（import），CSS 需 `.replace("__ACCENT__", ...)` 否则占位符残留
   - 生成后 stat 验证 index.html（四主题全量嵌入 >200KB 属正常）

## 交互机制（已实现，勿重复造）
- `common.js`：++（cand）/ --（pick）写 localStorage（key: nr_insightview_candidates / nr_daily_picks），同浏览器全目录共享；**投票数据携带推文全文**（paras/links/reactions/avatar/name 等），清单页用 nrTweetCard(x) 渲染完整推文卡片；重复点击同条目会自动补全全文（旧数据只有标题时可升级）
- `common.js`：评论功能 nrGetComment/nrSetComment/nrToggleComment/nrSaveComment（key: nr_comments，按条目 id 存），两个清单页每条可写评论；导出 JSON 时自动附上 comment 字段
- `insightview-candidates.html`：候选清单，点圆圈 = 确认进 InsightView 深研；每条带 💬 评论（紫色系）
- `daily-picks.html`：每日精选，按日期归档；每条带 💬 评论（金色系）
- 评论快捷键：⌘/Ctrl+Enter 保存，Esc 取消；有评论的条目按钮变「✏️ 编辑评论」并直接展示评论块
- 两清单页均可导出 JSON 备份

## 视觉规范 v2.0（2026-09-04 极简灰阶 + X/Twitter 流，勿加回彩色）
- 用户反馈旧版「深蓝字体刺眼、页面花里胡哨」，全套已收敛为**中性灰阶**：bg `#12161b` / text `#e7ebef` / muted `#9aa3ad` / border `#2a3139`，链接浅灰白（**禁用蓝色系** `#1d9bf0`/`紫蓝`/任何饱和蓝紫）
- 头像统一灰渐变（不再按 avatar_color 变色）；accent/avatar_color 字段保留向后兼容但 CSS 不引用
- 语义色只保留两枚柔和色（投票/选中态才出现）：green `#4daa7f`、red `#d9605a`；按钮常态灰描边，hover/voted 才上色
- 改动入口：`gen_page.py` 的 CSS 常量（主题页+首页共用）、`gen_index.py` 的 extra_css、两清单页手工 CSS
- **v2.2 整版 X/Twitter 流**（2026-09-04 13:30 重做）：
    - 头部紧凑：name(粗) + ✓verified(紫底) + @handle(灰) · 时间 · 来源（点状分隔，一行 flex 不换行）
    - 头像 40px 圆形（清单页缩到 36px）
    - 正文 15px / line-height 1.45（清单页 14px）
    - **操作栏 4 槽 X 流样式**：reply(气泡图标) / ++ (repost 循环箭头 + "++" 字) / -- (heart 心形 + "--" 字) / 分享 (upload 图标 → 原文链接)。每个 `.action` 槽用 SVG 图标，hover 显示语义色背景 (`var(--kw-soft)` / `rgba(77,170,127,.12)` / `rgba(217,96,90,.12)`)
    - 推文间 1px 细分割线，hover 整条微微高亮
    - 全局 `a, a:link, a:visited, a:hover, a:active { color: inherit; text-decoration: none; }` 兜底防浏览器默认深蓝
- **v2.1 关键词高亮 → v2.2 改深紫**：
    - 每条推文按 data.json 的 `keywords` 自动包 `<span class="kw">`，CSS `.content .kw { color: var(--kw); font-weight: 500; background: var(--kw-soft); padding: 0 3px; border-radius: 3px; }`（清单页 `.tweet-card .content .kw` 同样）
    - **`--kw: #a78bfa`** 深紫，`--kw-soft: rgba(167, 139, 250, .14)` 紫底
    - **数量克制**：每条 keywords 限 **≤ 3 个**，只保留最具识别度的实体（公司/人名/产品）。去掉通用词如 `AI/数据/营收/Q1/Q2/中国/美国/Agent` 等。新增素材时按"实体"标准筛选
    - `gen_page.py` 的 `highlight_keywords` 用 `_TAG_RE` 拆分 HTML 标签/文本，仅在非标签段做 str.replace（不会破坏已有的 `<strong>` 等标签）；长词优先匹配（sorted by len desc）防短词覆盖
- **`<a class>` 暗色站点颜色陷阱**（v2.0.1 补）：所有 `<a class="...">` 的 CSS 块必须显式写 `color: var(--text)`，否则继承浏览器默认 `#0000ee` 深蓝。常见中招：`.card`、`.tb-title`、卡片型链接。极简改版后跑审计：扫所有 `<a class="X">` 看 X 在 CSS 里有没有 `color:` 行，缺则补 + 补 `:visited { color: ... }`

## 已知坑
- Documents 目录 `ls/find/listdir/rsync` 全部 EPERM（TCC，即使 dangerouslyDisableSandbox），但 Read/Write/python 已知路径文件读写 OK
- 验证文件用 `stat -f "%N %z" <file>`，**禁用 ls/find/rsync/shutil.copytree**
- `gen_page.py` 里 CSS 用 `__ACCENT__` 占位符替换，不能用 %-format（CSS 里 `100%` 会冲突）
- 生成器改动后重跑即可，data JSON 是唯一数据源（HTML 可随时重生成）
- 清单页预览时会被注入 `data-page-node-id` 属性，Edit 前先 Grep 取精确文本
- **vote_anchor data-item HTML 转义陷阱**（v1.3 修）：JSON 里的 `<span class="kw">` 等 HTML 必须保留到前端渲染，不能用 `html.escape()`（会把 `<>` 转 `&lt;` `&gt;`）。vote_anchor 已改用 `raw.replace("&", "&amp;").replace('"', "&quot;")` 只保护属性

## 上云 + 每日自动化
- staging 中转目录 `/Users/qitmac001618/WorkBuddy/news-research-site/`（无 TCC 限制，可被部署工具读取）
- 同步脚本 `/Users/qitmac001618/WorkBuddy/scripts/sync_to_staging.py`：固定文件清单（ROOT_FILES = index.html/common.js/insightview-candidates.html/daily-picks.html/themes.json + 四主题 html），**全部在根目录、无日期目录**，显式路径拷贝绕过 TCC 目录扫描
- 部署工具 `workbuddy_sites_deploy` language=static, directory=staging, appName=`每日财经新闻推文流`
- **daily 发布为大哥授权的常态指令**：每次重部署都传 `userAskedToPublish: true`
- 自动化（automation_update 工具）：每天 08:00 跑 rrule `FREQ=DAILY;BYHOUR=8;BYMINUTE=0`
- 通知：`mcp__agent-mail__SendMessage` 发到 `chengang99@outlook.com`，邮件含四主题直链 + 候选/精选常驻页

## 产出后
- present_files 展示 index.html（首页，四主题全展开）+ 四个主题页
- 回复给摘要表（主题 / 条数 / 当日要点），不超过 10 行
- 若有临时新主题/信源偏好变化 → 同步更新 themes.json 和本 skill
