#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transcribe audio to raw text with faster-whisper.

Usage:
    python transcribe.py <audio_path> [--model small] [--out <output_txt>]

- Uses HF mirror (hf-mirror.com) because huggingface.co is blocked on this network.
- Uses hf_transfer for fast model download.
- First run downloads the model to ~/.cache/huggingface/hub (~1-3 min).
- Output: plain transcription, one line per segment with [mm:ss] timestamp prefix.
  This is the RAW transcript — do NOT rewrite or polish it here.
"""
import argparse
import os
import sys
import time

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--model", default="small",
                    help="whisper model size: tiny/base/small/medium (default small)")
    ap.add_argument("--out", default=None, help="output txt path (default: <audio>.txt)")
    ap.add_argument("--language", default="zh")
    args = ap.parse_args()

    out = args.out or (args.audio + ".txt")
    t0 = time.time()
    print(f"loading model '{args.model}' ...", flush=True)
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print(f"model loaded in {time.time()-t0:.0f}s, transcribing ...", flush=True)

    segments, info = model.transcribe(
        args.audio, language=args.language, beam_size=5, vad_filter=True
    )
    lines = []
    for seg in segments:
        txt = seg.text.strip()
        if txt:
            stamp = f"[{int(seg.start // 60):02d}:{int(seg.start % 60):02d}]"
            lines.append(f"{stamp} {txt}")
            print(f"{stamp} {txt}", flush=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nDONE in {time.time()-t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
