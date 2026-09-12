#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a static SaaS2Agent index.html.

v4: three-level structure (group / theme / files). A theme directory that
contains index.html is rendered as a single "主页" card — its appendix files are
NOT expanded, so the nav page stays short. A theme directory without index.html
is expanded into a file list (GitHub Pages offers no directory browsing).

Usage:
    python gen_saas2agent_index.py [--repo Gordon9999/SaaS2Agent] [--branch main] [--out index.html]
"""
import argparse
import json
import subprocess
import urllib.parse
import urllib.request

BASE = "https://gordon9999.github.io/"
SITE = "SaaS2Agent"

# 一级目录分组（顺序即展示顺序；未列出的目录归入「其他」）
GROUPS = [
    ("XiaoP", "🤖 个人助理方向"),
    ("Kefu", "🎧 客服 AI"),
    ("CRM", "🏢 AI + CRM / 内部系统"),
    ("SaaS", "💰 传统 SaaS 大佬"),
]


def site_url(path=""):
    return BASE + SITE + "/" + path


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _label(d):
    return d.rsplit("/", 1)[-1]


def _theme_entry(t):
    """Render one theme dir (group/theme) as a card, or expand it when no index."""
    label = _label(t["dir"])
    if t["hasIndex"]:
        href = site_url(t["dir"] + "/index.html")
        return (f'<div class="card"><span><span class="icon">📁</span>'
                f'<a href="{esc(href)}" target="_blank">{esc(label)}</a></span>'
                f'<span class="badge">主页</span></div>')
    html = (f'<div class="card dir-card"><span><span class="icon">📁</span>'
            f'<span class="dir-name">{esc(label)}</span></span>'
            f'<span class="badge">{len(t["files"])} 个页面</span></div>')
    for fn in sorted(t["files"]):
        fhref = site_url(t["dir"] + "/" + urllib.parse.quote(fn))
        html += (f'<div class="card file-list"><span><span class="icon">📄</span>'
                 f'<a href="{esc(fhref)}" target="_blank">{esc(fn)}</a></span></div>')
    return html


def _top_entry(label, href):
    return (f'<div class="card"><span><span class="icon">📁</span>'
            f'<a href="{esc(href)}" target="_blank">{esc(label)}</a></span>'
            f'<span class="badge">主页</span></div>')


def _file_entry(path):
    href = site_url(urllib.parse.quote(path))
    return (f'<div class="card file-list"><span><span class="icon">📄</span>'
            f'<a href="{esc(href)}" target="_blank">{esc(path)}</a></span></div>')


def render_static(paths):
    """Render the file tree into pure static HTML (group / theme / files)."""
    themes = {}      # {"XiaoP/instinct": {"dir":..., "hasIndex":bool, "files":[...]}}
    root_files = []  # files sitting directly in the repo root
    for p in paths:
        if "/" not in p:
            if p != "index.html":
                root_files.append(p)
            continue
        d, name = p.rsplit("/", 1)
        t = themes.setdefault(d, {"dir": d, "hasIndex": False, "files": []})
        if name.lower() == "index.html":
            t["hasIndex"] = True
        else:
            t["files"].append(name)

    html = ""
    used = set()
    for gdir, glabel in GROUPS:
        own = themes.get(gdir)
        children = sorted((t for k, t in themes.items() if k.startswith(gdir + "/")),
                          key=lambda t: t["dir"])
        loose = sorted(f for f in root_files if f.startswith(gdir + "/"))
        if not own and not children and not loose:
            continue
        used.add(gdir)
        for c in children:
            used.add(c["dir"])
        html += f'<div class="section-title">{esc(glabel)}</div>'
        if own and own["hasIndex"]:
            html += _top_entry(glabel, site_url(gdir + "/index.html"))
        for f in loose:
            html += _file_entry(f)
        for c in children:
            html += _theme_entry(c)

    remaining_root = sorted(f for f in root_files if f.split("/")[0] not in used)
    others = sorted((t for k, t in themes.items() if k not in used), key=lambda t: t["dir"])
    if remaining_root or others:
        html += '<div class="section-title">📦 其他</div>'
        for f in remaining_root:
            html += _file_entry(f)
        for t in others:
            html += _theme_entry(t)
    if not html:
        html = '<div class="status">暂无页面</div>'
    return html


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS2Agent · 目录导航</title>
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
        <h1>📚 SaaS2Agent · 目录导航</h1>
        <div class="subtitle">仓库内容索引（静态生成，秒开）</div>
        <div class="meta">数据快照：__GENERATED_AT__ · 主题含 index 时只展示入口，无 index 时展开文件列表</div>
    </div>

    <div class="toolbar">
        <button class="refresh-btn" id="refresh-btn">🔄 刷新列表</button>
    </div>

    <!-- 静态渲染的内容：不依赖 JS，必定显示 -->
    <div id="content">
__STATIC_CONTENT__
    </div>

    <div class="footer">Generated by SaaS2Agent Index · <span id="footer-date"></span></div>
</div>

<div class="toast" id="toast"></div>

<script>
(function () {
    'use strict';
    var REPO = '__REPO__';
    var BRANCH = '__BRANCH__';
    var BASE = '__BASE__';

    // 内置快照（path 列表），用于「刷新列表」时重新渲染
    var SNAPSHOT = __SNAPSHOT__;

    var GROUPS = __GROUPS__;

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function themeEntry(t) {
        var label = t.dir.split('/').filter(Boolean).pop();
        if (t.hasIndex) {
            return '<div class="card"><span><span class="icon">📁</span><a href="' + esc(BASE + t.dir + '/index.html') + '" target="_blank">' + esc(label) + '</a></span><span class="badge">主页</span></div>';
        }
        var h = '<div class="card dir-card"><span><span class="icon">📁</span><span class="dir-name">' + esc(label) + '</span></span><span class="badge">' + t.files.length + ' 个页面</span></div>';
        t.files.sort(function (a, b) { return a.localeCompare(b, 'zh'); });
        for (var i = 0; i < t.files.length; i++) {
            h += '<div class="card file-list"><span><span class="icon">📄</span><a href="' + esc(BASE + t.dir + '/' + encodeURIComponent(t.files[i])) + '" target="_blank">' + esc(t.files[i]) + '</a></span></div>';
        }
        return h;
    }

    function topEntry(label, dir) {
        return '<div class="card"><span><span class="icon">📁</span><a href="' + esc(BASE + dir + '/index.html') + '" target="_blank">' + esc(label) + '</a></span><span class="badge">主页</span></div>';
    }

    function fileEntry(path) {
        return '<div class="card file-list"><span><span class="icon">📄</span><a href="' + esc(BASE + encodeURIComponent(path)) + '" target="_blank">' + esc(path) + '</a></span></div>';
    }

    function buildList(paths) {
        var themes = {}, rootFiles = [];
        for (var i = 0; i < paths.length; i++) {
            var p = paths[i];
            var si = p.lastIndexOf('/');
            if (si === -1) { if (p !== 'index.html') rootFiles.push(p); continue; }
            var d = p.slice(0, si), name = p.slice(si + 1);
            if (!themes[d]) themes[d] = { dir: d, hasIndex: false, files: [] };
            if (name.toLowerCase() === 'index.html') themes[d].hasIndex = true;
            else themes[d].files.push(name);
        }
        var html = '', used = {};
        for (var g = 0; g < GROUPS.length; g++) {
            var gdir = GROUPS[g][0], glabel = GROUPS[g][1];
            var own = themes[gdir] || null;
            var children = [];
            for (var k in themes) {
                if (k.indexOf(gdir + '/') === 0) children.push(themes[k]);
            }
            children.sort(function (a, b) { return a.dir.localeCompare(b.dir, 'zh'); });
            var loose = [];
            for (var r = 0; r < rootFiles.length; r++) {
                if (rootFiles[r].indexOf(gdir + '/') === 0) loose.push(rootFiles[r]);
            }
            loose.sort();
            if (!own && !children.length && !loose.length) continue;
            used[gdir] = true;
            for (var cu = 0; cu < children.length; cu++) used[children[cu].dir] = true;
            html += '<div class="section-title">' + esc(glabel) + '</div>';
            if (own && own.hasIndex) html += topEntry(glabel, gdir);
            for (var l = 0; l < loose.length; l++) html += fileEntry(loose[l]);
            for (var c = 0; c < children.length; c++) html += themeEntry(children[c]);
        }
        var restRoot = [], others = [];
        for (var r2 = 0; r2 < rootFiles.length; r2++) {
            if (!used[rootFiles[r2].split('/')[0]]) restRoot.push(rootFiles[r2]);
        }
        restRoot.sort();
        for (var k2 in themes) { if (!used[k2]) others.push(themes[k2]); }
        others.sort(function (a, b) { return a.dir.localeCompare(b.dir, 'zh'); });
        if (restRoot.length || others.length) {
            html += '<div class="section-title">📦 其他</div>';
            for (var r3 = 0; r3 < restRoot.length; r3++) html += fileEntry(restRoot[r3]);
            for (var o = 0; o < others.length; o++) html += themeEntry(others[o]);
        }
        if (!html) html = '<div class="status">暂无页面</div>';
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

    def _extract(data):
        return [t["path"] for t in data.get("tree", [])
                if t["type"] == "blob" and t["path"].lower().endswith(".html")]

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            return _extract(json.loads(r.read()))
    except Exception as e:
        print(f"WARN: live fetch failed ({e}); trying with keychain token", flush=True)
        try:
            cred = subprocess.run(["git", "credential", "fill"],
                                  input="protocol=https\nhost=github.com\n\n",
                                  capture_output=True, text=True).stdout
            token = [l.split("=", 1)[1] for l in cred.splitlines() if l.startswith("password=")][0]
            req = urllib.request.Request(url, headers={**headers, "Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return _extract(json.loads(r.read()))
        except Exception as e2:
            raise SystemExit(f"FATAL: cannot fetch tree: {e2}")


def main():
    global SITE
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="Gordon9999/SaaS2Agent")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--site", default=None, help="GitHub Pages site name (defaults to repo basename)")
    ap.add_argument("--local", action="store_true", help="skip GitHub API, use local git ls-files (needed before push)")
    args = ap.parse_args()
    SITE = args.site or args.repo.split("/")[-1]

    if args.local:
        paths = None
    else:
        try:
            paths = fetch_tree(args.repo, args.branch)
        except SystemExit:
            paths = None
    if paths is None:
        # API 匿名限流/网络异常/--local 时，回退到本地 git 工作副本（须先 clone 并 cd 进仓库根目录）
        print("falling back to local git ls-files ...", flush=True)
        out = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
        if out.returncode != 0:
            raise SystemExit("FATAL: no API access and not inside a git repo; cd into the repo clone first")
        paths = [p for p in out.stdout.split() if p.lower().endswith(".html")]
    paths.sort()
    generated_at = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    static = render_static(paths)
    html = TEMPLATE \
        .replace("__REPO__", args.repo) \
        .replace("__BRANCH__", args.branch) \
        .replace("__BASE__", site_url()) \
        .replace("__GROUPS__", json.dumps(GROUPS, ensure_ascii=False, separators=(",", ":"))) \
        .replace("__GENERATED_AT__", generated_at) \
        .replace("__SNAPSHOT__", json.dumps(paths, ensure_ascii=False, separators=(",", ":"))) \
        .replace("__STATIC_CONTENT__", static)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK: {len(paths)} html files, static content rendered -> {args.out}")


if __name__ == "__main__":
    main()
