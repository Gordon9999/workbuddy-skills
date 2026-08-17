# WorkBuddy Custom Skills

个人定制的 WorkBuddy Skill 集合，clone 后复制到 `~/.workbuddy/skills/` 即可直接使用。

## 使用方法

```bash
git clone https://github.com/Gordon9999/workbuddy-skills.git
cp -r workbuddy-skills/skills/* ~/.workbuddy/skills/
```

## Skills 清单

| Skill | 用途 | 依赖 |
|-------|------|------|
| **business-trip-planner** | 出差行程管理，生成三件套页面（行程/订单/清单） | Python, GitHub API |
| **hotel-recommender** | 出差酒店推荐，搜索+HTML输出 | Web Search |
| **insightview** | 主题阅读与综合报告生成 | Python, YouTube/媒体素材 |
| **my-writer** | 个人书写风格格式化，HTML排版 | - |

## 目录结构

```
skills/
├── business-trip-planner/   # SKILL.md + scripts/
├── hotel-recommender/       # SKILL.md
├── insightview/             # SKILL.md + scripts/ + references/ + assets/
└── my-writer/               # SKILL.md + references/ + assets/
```

## 注意事项

- `insightview` 的 `scripts/gen_aikefu_index.py` 用于生成 AIKefu 导航页
