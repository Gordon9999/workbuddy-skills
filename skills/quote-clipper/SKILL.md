---
name: quote-clipper
description: "摘句本 / Quote Clipper：当用户贴一句话并说「摘录」「摘下来」「记一句」「quote」「摘录这句话」「收进摘句本」时触发；也用于查看/重建摘句本。把句子 + 记录时间 + 一句话解释 + 来源追加到本地摘句本（JSON 数据 + 静态快照 HTML），HTML 为 Twitter/X 时间线流风格，支持来源、标签、搜索过滤与一键复制；左侧图标按标签自动分类着色（投资/识人/管理/沟通/人生/韧性/学习/时间/商业/科技 共 10 类），点图标可按类筛选。解释文字遵循 my-writer 的短句口语化风格与换行纪律；来源必查证、查不到写「出处待考」，绝不编造；每次摘录后自动把 HTML 覆盖更新到资料库在线页。"
agent_created: true
---

# 摘句本 · Quote Clipper

## 概述

用户读到一句有意思的话，贴过来 → 存进本地摘句本。每条记录三件事：**原句、记录时间、一句话解释**。

产物：`~/.workbuddy/quotes/index.html`（静态快照，双击即开）+ `~/.workbuddy/quotes/quotes.json`（数据源）+ 资料库在线页（自动同步，见 §2.3）。

**每次摘录后自动把 HTML 覆盖更新到资料库**，节点 id 存 `~/.workbuddy/quotes/publish.json`，链接固定：https://www.workbuddy.cn/space/d/sy4Q7vUCgkVwhEkB09DbBB

## 一、触发条件

- 用户贴一段话/一句话并说：「摘录」「摘下来」「记一句」「收录」「quote」「这句话有意思」「存一下」
- 用户说「看摘句本 / 打开摘句本 / 摘了多少句」→ 直接 `open` HTML 或跑 `--list`
- 一次贴多句 → 拆成多条，循环调用 add

## 二、执行流程

### 1. 判断输入

- 用户给了现成解释 → 直接用
- 用户只给句子 → 你写解释，**必须按 my-writer 的书写风格**（见下）
- **来源必须交代**（见 1.8）
- 可选 `--tag`：1-2 个主题标签，逗号分隔（如 `投资,人性`）。拿不准就留空。

### 1.8 来源（必做，用户强要求）

每条摘录都要有来源，写在 `--source` 里，显示在解释下方。

1. 用户给了出处 → 直接填，格式「作者/作品（年份）」，有链接就填 `--url`
2. 用户没给 → **先搜再问**，用 WebSearch 查证：
   - 中文金句：搜关键短语 + 「出处」
   - 外文段子/谚语：**用英文原句搜**（如 "never play chess with a pigeon"），英文来源更准
3. 查到了 → 填 source，`--url` 填可靠的原始出处（原书 / 原访谈 / 原帖）；解释里可顺带点一句「这句出自 X」
4. **查不到 → source 填「出处待考」**，并在回复里说明一句，请用户补
5. **绝不编造出处**。宁可写「出处待考」，也不许把网络流传的段子安到名人头上（鸽子下棋句常被误挂到马克·吐温、丘吉尔名下，实际出自 2005 年亚马逊一条书评）

### 1.5 解释的写法（= my-writer 风格，硬规则）

1. **每句 ≤25 字**，长句必拆
2. **口语化**：像跟朋友聊天，不要书面语、不要论文腔
3. **2-3 句一段**，只写一段，说完就停
4. **不解释字面意思**，不复述原句，不写「这句话告诉我们 / 揭示了 / 体现了」
5. **说它真正在说什么**：反直觉的点、适用场景、什么时候会踩坑
6. **换行纪律**（同 my-writer）：解释超过 3 句必须断开换行，用 `\n` 分隔成两行，不写成一坨
7. **数据具体**：涉及数字就给准数，不写「很多」「大部分」
8. 禁用词：赋能、抓手、闭环、生态、维度、底层逻辑

好例子：
> 忙着活，是把时间投进能攒住的事。忙着死也不是真死，是混着等结束。停在那不动，其实一直在往后掉。

坏例子：
> 这句话以简洁有力的对比揭示了人生选择的重要性，体现了积极进取的人生态度，启示我们要珍惜时间。

### 2. 写入

长文本/含引号优先走 JSON 文件，避免 shell 转义出错：

```bash
cat > /tmp/quote.json <<'EOF'
{"text":"...","note":"...","source":"","tag":""}
EOF
python3 ~/.workbuddy/skills/quote-clipper/scripts/quote.py add --json /tmp/quote.json
```

短句可直接传参：

```bash
python3 ~/.workbuddy/skills/quote-clipper/scripts/quote.py add \
  --text "原句" --note "解释" --source "《书名》/作者" --tag "标签1,标签2"
```

脚本自动：追加到 `quotes.json`（新条目在最前，id 自增）→ 重新生成 `index.html` → 打印已存条数。

### 3. 同步到资料库（自动，每条摘录后必做）

add 成功后**顺手把 `index.html` 覆盖更新到资料库**，链接固定不变，用户随时点开都是最新的。

- 节点信息存 `~/.workbuddy/quotes/publish.json`（`node_block_id` / `url`），先读它
- 换票：`ToolSearch` 查 `connect_open_platform` → `DeferExecuteTool` 调用（`skill_id=library`），token 只走 stdin 首行、不落地、不写文件、不回显
- 覆盖更新（**有 node_block_id 时走这条**）：

```bash
L=/Applications/WorkBuddy.app/Contents/Resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/library
printf '%s' "<token>" | python3 "$L/page/import_html.py" \
  ~/.workbuddy/quotes/index.html --node-block-id "<publish.json 的 node_block_id>" --token-stdin
```

- **首次**（`publish.json` 不存在）→ 不带 `--node-block-id`，新建节点；然后把返回的 `node_block_id` / `url` 写进 `publish.json`
- 成功输出 `KS_IMPORT_OK {"node_block_id":...,"url":"https://www.workbuddy.cn/space/d/<id>"}` → 用 `present_files` 打开这个 url
- 一句话给多条时，**全部 add 完再同步一次**，不要每条都传
- token 有效期 30 分钟，同一轮/同一会话内可复用，报 `AUTH_REQUIRED` 再重新换票一次
- 失败处理：`56161` = 重导入需管理员权限（本人节点不会遇到）；其它错误按资料库 skill 的 `error_handling.md`
- 资料库链接是**协作态**，需要登录 workbuddy.cn 才能看；用户要无需登录的公开链接时，另走 `page/publish_page.py` 发布，别默认发
- 产物只搬 HTML 成品：token、本地路径、工具调用过程都不进产物、不进回显

### 4. 回复用户

只回一句确认：句子 + 解释 + **来源** + 时间，**不要长篇汇报**。然后 `present_files` 打开摘句本（本地 HTML 或资料库链接，二者给一个即可，优先资料库链接）。

一句话给多条时，全部存完 + 同步完再一次性 present。

## 三、命令

| 命令 | 作用 |
|---|---|
| `add --json f.json` / `add --text ... --note ...` | 追加一条，重建 HTML |
| `edit --id N --note "..."` | 改已有条目（可改 text/note/source/tag/time） |
| `--list` | 打印已有条目（倒序，仅编号/时间/首 30 字），含 id |
| `rebuild` | 从 JSON 重生成 HTML（手工改过 JSON 后） |
| `--dir <path>` | 换存储目录，默认 `~/.workbuddy/quotes` |
| `--time "YYYY-MM-DD HH:mm"` | 补录时指定时间，默认此刻 |

同步到资料库用的是库 skill 的 `page/import_html.py`（见 §2.3），节点信息在 `~/.workbuddy/quotes/publish.json`。

## 四、风格约定（改 HTML 时遵守）

**视觉 = Twitter / X 时间线流**，一条摘录 = 一条推文。

- 容器 600px 居中，左右细边线；顶部 sticky 头部（圆形渐变 logo ❝ + 「摘句本」+ `N 条摘录 · 更新于 时间`）+ 亮暗色切换 + 圆角搜索框
- 每条：**左侧分类图标**（见 §4.1，由标签决定分类、每类一色、24px 线性 SVG，**无底色圆圈、无序号**）→ 头部行 = **`#标签`（accent 粗体，点击筛选）+ 时间日期靠右**（**不要序号、不要「摘句本」/@handle 之类无信息量的占位**；无标签时显示灰色「摘录」）→ 原句（19px、保留换行）→ 解释（次级灰）→ 来源（`— 来源`，有 url 时是链接）→ 底部互动行（**点赞 ♥（点一次 +1，红心 `#f91880` 填充 + 数字）** + 复制按钮 + 原始出处链接，用 17px 线性 SVG 图标）
- **点赞机制**：`quotes.json` 里每条可有 `likes` 基准值，页面点击的增量存浏览器 localStorage（key `quote-likes-<id>`），刷新不丢；显示值 = 基准 + 增量。想看累计赞数就 `add --json` 时带上 `"likes"`，或直接 `edit`（暂无双向同步，页面点击不会写回 JSON）
- 卡片 hover 背景微亮，1px 分隔线，不做卡片圆角框
- 暗色优先（`#101419` 系）+ 亮色切换，accent 用 X 蓝（暗 `#4a9eff` / 亮 `#1d9bf0`）
- **所有 `<a>` 必须显式写 `color`，包括 `:visited`**（含 footer 里的链接）
- 搜索框即时过滤（原句/解释/来源/标签），标签点击切换筛选，复制按钮 `navigator.clipboard` 写「原句 + 解释 + 来源」
- 数据全量内嵌进 HTML，纯静态、秒开，不依赖网络

### 4.1 分类图标（图标 = 标签的类别）

左侧图标**不用统一引号**，而是表达「这条属于哪一类」：标签命中关键词 → 换成该分类的图标 + 类色；无标签或认不出 → 灰色引号（`default`）。

| 分类 | 图标形状 | 关键词（标签含任一即命中） | 暗色 | 亮色 |
|---|---|---|---|---|
| `invest` 投资 | 上扬趋势线 | 投资 金融 财经 股票 交易 财富 复利 市场 基金 估值 经济 资产 | #4a9eff | #1273d4 |
| `people` 识人 | 眼睛 | 识人 看人 人性 人心 人品 人际 心理 性格 情绪 情商 | #a78bfa | #6d3fd4 |
| `manage` 管理 | 节点网络 | 管理 团队 组织 领导 决策 执行 制度 协作 用人 | #f59e0b | #b4740a |
| `talk` 沟通 | 对话气泡 | 沟通 对话 说话 表达 谈判 说服 语言 交流 演讲 | #2dd4bf | #0d8f83 |
| `life` 人生 | 罗盘 | 人生 生活 价值观 哲学 意义 成长 选择 命运 自我 心态 处世 | #34d399 | #0b8f5c |
| `grit` 韧性 | 盾牌 | 韧性 坚持 毅力 逆境 忍耐 长期 耐心 熬 沉浮 | #fb7185 | #c93a58 |
| `learn` 学习 | 翻开的书 | 学习 读书 知识 认知 思维 方法 教育 笔记 | #818cf8 | #4a45cf |
| `time` 时间 | 时钟 | 时间 效率 节奏 拖延 习惯 自律 早起 | #facc15 | #a97b00 |
| `biz` 商业 | 楼群 | 商业 创业 公司 战略 竞争 产品 生意 品牌 营销 客户 | #fb923c | #c05e0d |
| `tech` 科技 | 芯片 | 科技 技术 工程 代码 互联网 算法 模型 智能 数据 | #38bdf8 | #0277b0 |
| `default` 摘录 | 引号 | 无标签 / 认不出 | var(--tx3) | 同左 |

规则：

- **多标签取第一个命中的分类**（按上表顺序）。例：`#沟通,人性` → 沟通（不是识人）；`#投资,韧性` → 投资
- 打标签时留意分类：几个常用组合已固定映射——`人生,价值观` → 人生（罗盘）；`识人,管理` → 识人（眼睛）；`投资,韧性` → 投资（趋势线）
- 想加分类或换图标：只改 `scripts/quote.py` 顶部的 `CATS` 表（key / 中文名 / 暗色 / 亮色 / 关键词 / SVG 路径），HTML 内联 CSS 与卡片会自动生成，不用手改 HTML
- 单条可用 JSON 的 `"cat_name"` 覆盖 hover 提示文字
- **点图标 = 按分类筛选**：同类留下，其余淡出到 25% 透明，再点一次取消；可与标签筛选、搜索框过滤叠加
