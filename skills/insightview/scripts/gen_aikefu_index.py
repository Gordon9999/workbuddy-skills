#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a static AIKefu index.html.

v3: the file list is rendered into static HTML at generation time — the page
shows content with zero JS dependency (instant load, never blank). A small JS
block powers the optional "refresh" button only.

Usage:
    python gen_aikefu_index.py [--repo Gordon9999/AIKefu] [--branch main] [--out index.html]
"""
import argparse
import json
import subprocess
import urllib.request

BASE = "https://gordon9999.github.io/"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_static(paths):
    """Render the file list into pure static HTML."""
    root_files = []
    dir_map = {}
    for p in paths:
        idx = p.find("/")
        if idx == -1:
            if p != "index.html":
                root_files.append(p)
            continue
        d = p[: idx + 1]
        name = p[idx + 1:]
        if d not in dir_map:
            dir_map[d] = {"dir": d, "hasIndex": False, "files": []}
        if name.lower() == "index.html":
            dir_map[d]["hasIndex"] = True
        else:
            dir_map[d]["files"].append(name)

    root_files.sort()
    html = ""
    if root_files:
        html += '<div class="section-title">📄 根目录页面</div>'
        for f in root_files:
            href = BASE + "AIKefu/" + urllib.parse.quote(f)
            html += (f'<div class="card file-list"><span><span class="icon">📄</span>'
                     f'<a href="{esc(href)}" target="_blank">{esc(f)}</a></span></div>')
    dirs = sorted(dir_map.values(), key=lambda d: d["dir"])
    if dirs:
        html += '<div class="section-title">📁 子目录</div>'
        for d in dirs:
            label = [x for x in d["dir"].split("/") if x][-1]
            if d["hasIndex"]:
                href = BASE + "AIKefu/" + d["dir"] + "index.html"
                html += (f'<div class="card"><span><span class="icon">📁</span>'
                         f'<a href="{esc(href)}" target="_blank">{esc(label)}</a></span>'
                         f'<span class="badge">主页</span></div>')
            else:
                # 无 index.html 的目录：GitHub Pages 不提供目录浏览，直接展开文件列表
                html += (f'<div class="card dir-card"><span><span class="icon">📁</span>'
                         f'<span class="dir-name">{esc(label)}</span></span>'
                         f'<span class="badge">{len(d["files"])} 个页面</span></div>')
                for fn in sorted(d["files"]):
                    fhref = BASE + "AIKefu/" + d["dir"] + urllib.parse.quote(fn)
                    html += (f'<div class="card file-list"><span><span class="icon">📄</span>'
                             f'<a href="{esc(fhref)}" target="_blank">{esc(fn)}</a></span></div>')
    if not root_files and not dirs:
        html = '<div class="status">暂无页面</div>'
    return html


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIKefu · 目录导航</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.8;
            -webkit-font-smoothing: antialiased;
        }
        .container { max-width: 760px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
        .report-header {
            text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        .report-header h1 { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem; }
        .report-header .subtitle { font-size: 0.9rem; color: #64748b; }
        .report-header .meta { font-size: 0.8rem; color: #94a3b8; margin-top: 0.4rem; }
        .section-title {
            font-size: 1.1rem; font-weight: 700; color: #0f172a;
            margin-top: 2rem; margin-bottom: 0.6rem; padding-bottom: 0.4rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .card {
            background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
            padding: 0.9rem 1.2rem; margin-bottom: 0.6rem;
            display: flex; align-items: center; justify-content: space-between; gap: 1rem;
            transition: border-color 0.15s;
        }
        .card:hover { border-color: #2563eb; }
        .card a { color: #2563eb; text-decoration: none; font-size: 0.95rem; word-break: break-all; }
        .card a:hover { text-decoration: underline; }
        .card .icon { margin-right: 0.4rem; }
        .badge {
            flex-shrink: 0; display: inline-block; padding: 0.1rem 0.5rem;
            font-size: 0.72rem; font-weight: 600; border-radius: 4px;
            background: #dcfce7; color: #16a34a; white-space: nowrap;
        }
        .file-list { padding-left: 0.2rem; }
        .file-list .card { padding: 0.6rem 1rem; }
        .dir-card { background: #f1f5f9; }
        .dir-card .dir-name { font-weight: 600; color: #0f172a; }
        .toolbar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
        .refresh-btn {
            background: #fff; border: 1px solid #2563eb; color: #2563eb;
            border-radius: 6px; padding: 0.35rem 0.9rem; font-size: 0.82rem;
            cursor: pointer; transition: background 0.15s;
        }
        .refresh-btn:hover { background: #eff6ff; }
        .refresh-btn:disabled { opacity: 0.5; cursor: wait; }
        .toast {
            position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
            background: #0f172a; color: #f8fafc; padding: 0.5rem 1.2rem;
            border-radius: 6px; font-size: 0.82rem; opacity: 0; transition: opacity 0.25s;
            pointer-events: none; z-index: 99;
        }
        .toast.show { opacity: 1; }
        .status { text-align: center; padding: 3rem 1rem; color: #64748b; font-size: 0.95rem; }
        .footer { text-align: center; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #94a3b8; }
        @media (max-width: 640px) {
            .container { padding: 1.5rem 1rem 3rem; }
            .report-header h1 { font-size: 1.3rem; }
            .card { padding: 0.7rem 1rem; }
        }
    </style>
</head>
<body>
<div class="container">

    <div class="report-header">
        <h1>📚 AIKefu · 目录导航</h1>
        <div class="subtitle">仓库内容索引（静态生成，秒开）</div>
        <div class="meta">数据快照：__GENERATED_AT__ · 子目录含 index 时展示入口，无 index 时展开文件列表</div>
    </div>

    <div class="toolbar">
        <button class="refresh-btn" id="refresh-btn">🔄 刷新列表</button>
    </div>

    <!-- 静态渲染的内容：不依赖 JS，必定显示 -->
    <div id="content">
__STATIC_CONTENT__
    </div>

    <div class="footer">Generated by AIKefu Index · <span id="footer-date"></span></div>
</div>

<div class="toast" id="toast"></div>

<script>
(function () {
    'use strict';
    var REPO = '__REPO__';
    var BRANCH = '__BRANCH__';
    var BASE = 'https://gordon9999.github.io/AIKefu/';

    // 内置快照（path 列表），用于「刷新列表」时重新渲染
    var SNAPSHOT = __SNAPSHOT__;

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function buildList(paths) {
        var rootFiles = [];
        var dirMap = {};
        for (var i = 0; i < paths.length; i++) {
            var p = paths[i];
            var idx = p.indexOf('/');
            if (idx === -1) { if (p !== 'index.html') rootFiles.push(p); continue; }
            var dir = p.slice(0, idx + 1);
            var name = p.slice(idx + 1);
            if (!dirMap[dir]) dirMap[dir] = { dir: dir, hasIndex: false, files: [] };
            if (name.toLowerCase() === 'index.html') dirMap[dir].hasIndex = true;
            else dirMap[dir].files.push(name);
        }
        rootFiles.sort(function (a, b) { return a.localeCompare(b, 'zh'); });
        var dirKeys = Object.keys(dirMap).sort(function (a, b) { return a.localeCompare(b, 'zh'); });
        var html = '';
        if (rootFiles.length) {
            html += '<div class="section-title">📄 根目录页面</div>';
            for (var j = 0; j < rootFiles.length; j++) {
                html += '<div class="card file-list"><span><span class="icon">📄</span><a href="' + esc(BASE + encodeURIComponent(rootFiles[j])) + '" target="_blank">' + esc(rootFiles[j]) + '</a></span></div>';
            }
        }
        if (dirKeys.length) {
            html += '<div class="section-title">📁 子目录</div>';
            for (var k = 0; k < dirKeys.length; k++) {
                var d = dirMap[dirKeys[k]];
                var label = d.dir.split('/').filter(Boolean).pop();
                if (d.hasIndex) {
                    html += '<div class="card"><span><span class="icon">📁</span><a href="' + esc(BASE + d.dir + 'index.html') + '" target="_blank">' + esc(label) + '</a></span><span class="badge">主页</span></div>';
                } else {
                    // 无 index.html 的目录：GitHub Pages 不提供目录浏览，直接展开文件列表
                    html += '<div class="card dir-card"><span><span class="icon">📁</span><span class="dir-name">' + esc(label) + '</span></span><span class="badge">' + d.files.length + ' 个页面</span></div>';
                    d.files.sort(function (a, b) { return a.localeCompare(b, 'zh'); });
                    for (var fi = 0; fi < d.files.length; fi++) {
                        html += '<div class="card file-list"><span><span class="icon">📄</span><a href="' + esc(BASE + d.dir + encodeURIComponent(d.files[fi])) + '" target="_blank">' + esc(d.files[fi]) + '</a></span></div>';
                    }
                }
            }
        }
        if (!rootFiles.length && !dirKeys.length) html = '<div class="status">暂无页面</div>';
        return html;
    }

    function toast(msg) {
        var el = document.getElementById('toast');
        el.textContent = msg;
        el.classList.add('show');
        setTimeout(function () { el.classList.remove('show'); }, 2500);
    }

    document.getElementById('refresh-btn').addEventListener('click', function () {
        var btn = this;
        btn.disabled = true;
        fetch('https://api.github.com/repos/' + REPO + '/git/trees/' + BRANCH + '?recursive=1', {
            headers: { 'Accept': 'application/vnd.github+json' }
        })
        .then(function (res) { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
        .then(function (data) {
            var paths = (data.tree || [])
                .filter(function (t) { return t.type === 'blob' && t.path.toLowerCase().endsWith('.html'); })
                .map(function (t) { return t.path; });
            SNAPSHOT = paths;
            document.getElementById('content').innerHTML = buildList(paths);
            toast('已刷新 ✅');
        })
        .catch(function (e) { toast('刷新失败：' + e.message); })
        .finally(function () { btn.disabled = false; });
    });

    document.getElementById('footer-date').textContent = new Date().toISOString().slice(0, 10);
})();
</script>
</body>
</html>
"""


def fetch_tree(repo, branch):
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "WorkBuddy"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return [t["path"] for t in data.get("tree", [])
                if t["type"] == "blob" and t["path"].lower().endswith(".html")]
    except Exception as e:
        print(f"WARN: live fetch failed ({e}); trying with keychain token", flush=True)
        try:
            cred = subprocess.run(["git", "credential", "fill"],
                                  input="protocol=https\nhost=github.com\n\n",
                                  capture_output=True, text=True).stdout
            token = [l.split("=", 1)[1] for l in cred.splitlines() if l.startswith("password=")][0]
            req = urllib.request.Request(url, headers={**headers, "Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            return [t["path"] for t in data.get("tree", [])
                    if t["type"] == "blob" and t["path"].lower().endswith(".html")]
        except Exception as e2:
            raise SystemExit(f"FATAL: cannot fetch tree: {e2}")


def main():
    import urllib.parse  # noqa: F401 (used in render_static)
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="Gordon9999/AIKefu")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    paths = fetch_tree(args.repo, args.branch)
    paths.sort()
    generated_at = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    static = render_static(paths)
    html = TEMPLATE \
        .replace("__REPO__", args.repo) \
        .replace("__BRANCH__", args.branch) \
        .replace("__GENERATED_AT__", generated_at) \
        .replace("__SNAPSHOT__", json.dumps(paths, ensure_ascii=False, separators=(",", ":"))) \
        .replace("__STATIC_CONTENT__", static)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK: {len(paths)} html files, static content rendered -> {args.out}")


if __name__ == "__main__":
    main()
