# WorkBuddy Custom Skills

个人定制的 WorkBuddy Skill 集合，clone 后复制到 `~/.workbuddy/skills/` 即可直接使用。

## 使用方法

```bash
git clone https://github.com/Gordon9999/workbuddy-skills.git
cp -r workbuddy-skills/skills/* ~/.workbuddy/skills/
```

国内网络若不通，可走加速站：

```bash
git clone --depth 1 https://gh-proxy.com/https://github.com/Gordon9999/workbuddy-skills.git
```

云端沙箱（Linux）直接跑仓库根目录的 `cloud-setup.sh`，它会把 skills 装到 `/root/.codebuddy/skills`。

## Skills 清单

| Skill | 用途 | 依赖 |
|-------|------|------|
| **business-trip-planner** | 出差行程管理，生成三件套页面（行程/订单/清单） | Python, GitHub API |
| **finance-news-daily** | 每日四主题财经新闻推文流（ai / enterprise-agent / agent-startups / ota） | Web Search |
| **hotel-recommender** | 出差酒店推荐，搜索+HTML输出 | Web Search |
| **insightview** | 主题阅读与综合报告生成 | Python, YouTube/媒体素材 |
| **my-writer** | 个人书写风格格式化，HTML排版 | - |

## 目录结构

```
skills/
├── business-trip-planner/   # SKILL.md + scripts/
├── finance-news-daily/      # SKILL.md
├── hotel-recommender/       # SKILL.md
├── insightview/             # SKILL.md + scripts/ + references/ + assets/
└── my-writer/               # SKILL.md + references/ + assets/
```

## 注意事项

- `insightview` 的 `scripts/gen_aikefu_index.py` 用于生成 AIKefu 导航页
- `business-trip-planner` 的 `scripts/put_life.py` 走 GitHub Contents API（本机 git push 常被代理挡），token 支持 `GH_TOKEN` 环境变量 / macOS 钥匙串双模式

## 换机 / 重装系统恢复清单

仓库只放 skill（公开，**不含任何凭证**）。重装系统后按序恢复：

1. **Skill**：`git clone` 本仓库 → 复制 `skills/*` 到 `~/.workbuddy/skills/`
2. **人格与长期记忆**：`~/.workbuddy/` 下的 `SOUL.md` / `IDENTITY.md` / `USER.md` / `MEMORY.md` —— **不入库**，需自行备份（这些含个人信息，别推公开仓库）
3. **MCP 配置**：`~/.workbuddy/mcp.json`
4. **连接器**：在客户端重新授权（agent-mail 等 token 不落盘到本仓库）
