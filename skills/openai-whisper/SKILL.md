---
name: openai-whisper
description: "Local speech-to-text with the Whisper CLI (no API key)."
description_zh: "本地语音转文字（无需 API 密钥）"
description_en: "Local speech-to-text (no API key needed)"
version: 1.1.0
---

# 本地语音转文字（faster-whisper）

本机**没有** `whisper` CLI，也没有 ffmpeg。实际可用方案：faster-whisper（纯 Python，PyAV 自带音频解码，无需系统 ffmpeg）。

## 环境

- 解释器：`/Users/qitmac001618/.workbuddy/binaries/python/envs/default/bin/python`
- 已装包：`faster-whisper`（1.2.1）、`hf_transfer`

## 网络注意（中国大陆网络）

- `huggingface.co` 不可达（000）→ 必须走镜像 `hf-mirror.com`
- PyPI 可达，包可直接 pip install

## 关键步骤

1. 转写脚本需设置：
   ```python
   os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
   os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"   # 加速模型下载（实测可到几十 MB/s）
   ```
2. 模型选择（中文口语录音）：
   - `small`：约 484MB，下载 ~1.5min，识别质量可接受 —— **默认推荐**
   - `medium`：约 1.53GB，走镜像可能很慢（实测 300kB/s 要 1.5h+），谨慎使用
3. 示例代码：
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel("small", device="cpu", compute_type="int8")
   segments, info = model.transcribe(AUDIO, language="zh", beam_size=5, vad_filter=True)
   # 遍历 segments，seg.text 为文本，seg.start 为秒数
   ```
4. 首次运行下载模型到 `~/.cache/huggingface/hub`，之后秒加载。

## 后续处理

- 口语转写含大量重复、口误、专有名词识别错误（如 Sierra→seria、Decagon→deadgun、护城河→互衬盒、富士康→福斯康）。改写前需结合上下文修正，专有名词按发音还原后再确认。
- 转写完成后通常要按用户要求精简成文（用户偏好：结构化、有观点、短段落）。
