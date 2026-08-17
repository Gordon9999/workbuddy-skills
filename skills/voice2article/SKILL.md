---
name: voice2article
description: "语音/文本转写技能。当用户上传录音（m4a/mp3/wav 等）或文本文件，说「转写成文」「改成文章」「语音转写」「整理成文章」时触发。职责单一：只负责把语音转成文字（或直接接收文本），保存原始转录到 raw/ 目录；改写与 HTML 排版交给 my-writer skill 执行。工作流：判断输入类型 → 语音转写（环境配置引用 openai-whisper）→ 拟定中文标题 + 英文 slug 目录 → 保存 raw 原始材料 → 调用 my-writer 做风格改写 + HTML 排版 → 交付。"
agent_created: true
---

# voice2article — 语音/文本转写（转写专用，排版交 my-writer）

## 概述

把用户录制的口述语音转成文字，或直接接收文本，保存原始材料到 raw/ 目录。**本 skill 只负责转写与原始材料管理，不做改写、不做 HTML 排版**——改写与排版交给 my-writer skill 执行。

**核心原则：原始转写绝不改写。改写只发生在 my-writer 里。**

## 触发条件

| 用户指令 | 输入 | 行为 |
|---------|------|------|
| 上传语音（.m4a/.mp3/.wav/.aac/.ogg 等）+「转写成文 / 改成文章」 | 音频 | 本地转写 → 保存 raw → 交 my-writer |
| 上传文本（.txt/.md）+「转写成文 / 整理成文章」 | 文本 | 直接读取 → 保存 raw → 交 my-writer |

## 一、判断输入类型

1. 扩展名在音频列表（m4a/mp3/wav/aac/ogg/flac/mov）→ **语音路径**
2. 扩展名是 txt/md → **文本路径**
3. 其他 → 询问用户意图

## 二、语音转写（仅语音输入）

转写环境（faster-whisper、hf-mirror 镜像、解释器路径、模型选择、网络注意）**统一见 `openai-whisper` skill**，本 skill 不重复维护，避免环境变更时两处不同步。

本 skill 的调用方式：
- 运行 `scripts/transcribe.py <音频路径> --model small`
  - 用 managed venv 的 python：`/Users/qitmac001618/.workbuddy/binaries/python/envs/default/bin/python`
  - 环境配置细节（`HF_ENDPOINT`、`HF_HUB_ENABLE_HF_TRANSFER`、模型大小权衡）见 openai-whisper skill
- 首次约 1-3 分钟下载模型
- **转写结果就是原始转录文本，绝不在此步改写、润色、纠错**
- 中文识别不准的专有名词，先记下，交给 my-writer 时一并提示结合上下文修正

## 三、拟定标题并创建目录

1. 通读内容（转录文本或上传文本），拟定一个**中文、简洁有力**的标题（用于 HTML 内展示）
2. 根据标题生成**英文 slug** 作为目录名和文件名：把标题译成英文 → 小写 → 空格/特殊字符替换为连字符 `-`（如《从 Sierra 看 AI Agent 平台：护城河在哪里》→ `sierra-ai-agent-platform`）
3. 创建目录：`<输出根目录>/<EN_SLUG>/`（输出根目录默认当前 workspace 根目录）
4. 输出根目录结构（所有 skill 生成的文件名用英文，原始语音副本保留用户原文件名）：
   ```
   <EN_SLUG>/
   ├── <EN_SLUG>.html          # 由 my-writer 生成的最终文章（英文文件名）
   └── raw/
       ├── <原始语音文件名>    # 原始语音副本，保留原名（语音输入时）
       ├── raw_transcript.txt  # 语音直接转出的文字，不改写（语音输入时）
       └── raw_source.txt      # 上传文本的副本（文本输入时）
   ```

## 四、交给 my-writer 改写与排版

转写/读取完成后，将以下信息交给 **my-writer skill** 执行：
- 原始转录文本（或上传文本）
- 拟定的中文标题
- 专有名词修正提示（语音转写中识别不准的词，结合上下文修正）

my-writer 按其工作流处理：
- 转录稿属口语化纯文本 → 触发**模式 B（短句口语化改写）**
- 生成 FT 头版风格标题（如用户已拟定标题则直接用）
- 用 my-writer 的 `assets/article-template.html` 生成 HTML（视觉基线见 `my-writer/references/shared-html-spec.md`）
- 保存为 `<EN_SLUG>.html`，放入第三步创建的目录

## 五、交付说明

向用户说明：
- 最终文章路径与标题
- 原始语音 + 未改写转录保存在 `raw/` 下
- 专有名词修正情况（如有不确定处请用户确认）
- 可调整点：若风格不满意可一句话重写（由 my-writer 处理）

## 六、发布到 git（可选，用户说「发布到 git / 发到 AIKefu」时触发）

与 insightview 相同的发布约定：文章 HTML 发布到 GitHub 仓库 **AIKefu**（https://github.com/Gordon9999/AIKefu，公开，已开 Pages）。发布后**必须重建根目录导航页**。

详细技术要点见 insightview skill「第四步：发布到 git」。摘要：
1. 确认目标目录名（用户可直接给，如 `biji`，未给则先询问）
2. 用 GitHub Contents API 上传 `<EN_SLUG>.html` 到 `AIKefu/<目录名>/`
3. 运行 `insightview/scripts/gen_aikefu_index.py` 重建导航页并上传覆盖根目录 index.html
4. curl 验证返回 200，给链接

## 资源文件

| 文件 | 用途 |
|------|------|
| `scripts/transcribe.py` | faster-whisper 本地转写脚本（环境配置见 openai-whisper skill） |

> 注：本 skill 不再维护自己的文章模板与风格指南——改写与 HTML 排版统一由 my-writer skill 负责（`my-writer/assets/article-template.html` + `my-writer/references/writing-style-guide.md`）。
