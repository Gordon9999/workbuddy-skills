#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""摘句本 Quote Clipper — 追加一条摘录并重建静态 HTML（Twitter/X 流风格）。

用法:
  quote.py add --text "原句" --note "解释" [--source ""] [--url ""] [--tag "a,b"] [--time "YYYY-MM-DD HH:mm"]
  quote.py add --json /tmp/quote.json
  quote.py edit --id 3 --note "新解释"
  quote.py --list
  quote.py rebuild
  quote.py add ... --dir /path/to/quotes
"""
import argparse
import html
import json
import os
import sys
from datetime import datetime
from string import Template

DEFAULT_DIR = os.path.expanduser("~/.workbuddy/quotes")

IC_COPY = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" '
           'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
           '<rect x="9" y="9" width="11" height="11" rx="2.5"/><path d="M5 15V5.5A2.5 2.5 0 0 1 7.5 3H17"/></svg>')
IC_LINK = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" '
           'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M10.5 13.5a4.5 4.5 0 0 0 6.4 0l2-2a4.5 4.5 0 0 0-6.4-6.4l-1 1"/>'
           '<path d="M13.5 10.5a4.5 4.5 0 0 0-6.4 0l-2 2a4.5 4.5 0 0 0 6.4 6.4l1-1"/></svg>')

IC_QUOTE_MARK = ('<svg viewBox="0 0 16 16" width="26" height="26" fill="currentColor" aria-hidden="true">'
                 '<path d="M12 12a1 1 0 0 0 1-1V8.558a1 1 0 0 0-1-1h-1.388c0-.351.021-.703.062-1.054'
                 '.062-.372.166-.703.31-.992.145-.29.331-.517.559-.683.227-.186.516-.279.868-.279V3'
                 'c-.579 0-1.085.124-1.52.372a3.322 3.322 0 0 0-1.085.992 4.92 4.92 0 0 0-.62 1.458'
                 'A7.712 7.712 0 0 0 9 7.558V11a1 1 0 0 0 1 1h2Zm-6 0a1 1 0 0 0 1-1V8.558a1 1 0 0 0-1-1'
                 'H4.612c0-.351.021-.703.062-1.054.062-.372.166-.703.31-.992.145-.29.331-.517.559-.683'
                 '.227-.186.516-.279.868-.279V3c-.579 0-1.085.124-1.52.372a3.322 3.322 0 0 0-1.085.992'
                 ' 4.92 4.92 0 0 0-.62 1.458A7.712 7.712 0 0 0 3 7.558V11a1 1 0 0 0 1 1h2Z"/></svg>')

IC_HEART = ('<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 20.2C10.6 19 4.8 15.1 4.8 10.7A4.2 4.2 0 0 1 12 8.1a4.2 4.2 0 0 1 7.2 2.6'
            'c0 4.4-5.8 8.3-7.2 9.5z"/></svg>')

SVG_OPEN = ('<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">')

# ── 标签分类：图标 = 分类 ────────────────────────────────────
# 每条摘录的左侧图标由它的标签决定：标签命中的第一条分类规则，用该类图标 + 类色。
# 多个标签时取第一个能识别的；都识别不到（或无标签）用 default（灰色引号）。
# CATS: (key, 中文名, 暗色, 亮色, [命中关键词])
CATS = [
    ("invest", "投资", "#4a9eff", "#1273d4",
     ["投资", "金融", "财经", "股票", "交易", "财富", "复利", "市场", "基金", "估值", "经济", "资产"],
     '<path d="M3 17.5l5.2-5.2 3.4 3.4L20.5 6.9"/><path d="M15.2 6.9h5.3v5.3"/>'),
    ("people", "识人", "#a78bfa", "#6d3fd4",
     ["识人", "看人", "人性", "人心", "人品", "人际", "心理", "性格", "情绪", "情商"],
     '<path d="M2.5 12S6.2 5.8 12 5.8 21.5 12 21.5 12 17.8 18.2 12 18.2 2.5 12 2.5 12z"/>'
     '<circle cx="12" cy="12" r="3.1"/>'),
    ("manage", "管理", "#f59e0b", "#b4740a",
     ["管理", "团队", "组织", "领导", "决策", "执行", "制度", "协作", "用人"],
     '<circle cx="12" cy="5.2" r="2.5"/><circle cx="5.2" cy="18.8" r="2.5"/>'
     '<circle cx="18.8" cy="18.8" r="2.5"/>'
     '<path d="M12 7.7v3.4M10.4 12.6l-3.5 3.6M13.6 12.6l3.5 3.6"/>'),
    ("talk", "沟通", "#2dd4bf", "#0d8f83",
     ["沟通", "对话", "说话", "表达", "谈判", "说服", "语言", "交流", "演讲"],
     '<path d="M20.5 12.2c0 3.7-3.8 6.7-8.5 6.7-1 0-2-.15-2.9-.42L4 20.6l1.3-3.4'
     'c-1.1-1.2-1.8-2.9-1.8-4.9C3.5 8.5 7.3 5.5 12 5.5s8.5 3 8.5 6.7z"/>'),
    ("life", "人生", "#34d399", "#0b8f5c",
     ["人生", "生活", "价值观", "哲学", "意义", "成长", "选择", "命运", "自我", "心态", "处世"],
     '<circle cx="12" cy="12" r="8.8"/><path d="M15.4 8.6l-2 5.1-5.1 2 2-5.1z"/>'),
    ("grit", "韧性", "#fb7185", "#c93a58",
     ["韧性", "坚持", "毅力", "逆境", "忍耐", "长期", "耐心", "熬", "沉浮"],
     '<path d="M12 3.2l7 2.8v5.5c0 4.3-2.9 8.2-7 9.8-4.1-1.6-7-5.5-7-9.8V6z"/>'),
    ("learn", "学习", "#818cf8", "#4a45cf",
     ["学习", "读书", "知识", "认知", "思维", "方法", "教育", "笔记"],
     '<path d="M4 4.6h5.4A2.6 2.6 0 0 1 12 7.2v12.4a2 2 0 0 0-2-2H4z"/>'
     '<path d="M20 4.6h-5.4A2.6 2.6 0 0 0 12 7.2v12.4a2 2 0 0 1 2-2h6z"/>'),
    ("time", "时间", "#facc15", "#a97b00",
     ["时间", "效率", "节奏", "拖延", "习惯", "自律", "早起"],
     '<circle cx="12" cy="12" r="8.6"/><path d="M12 7.3V12l3.1 2"/>'),
    ("biz", "商业", "#fb923c", "#c05e0d",
     ["商业", "创业", "公司", "战略", "竞争", "产品", "生意", "品牌", "营销", "客户"],
     '<path d="M4 20.2V8.4l6-4v15.8"/><path d="M10 20.2V10l6.2 3v7.2"/>'
     '<path d="M2.2 20.2h19.6"/>'),
    ("tech", "科技", "#38bdf8", "#0277b0",
     ["科技", "技术", "工程", "代码", "互联网", "算法", "模型", "智能", "数据"],
     '<rect x="7.2" y="7.2" width="9.6" height="9.6" rx="2.2"/>'
     '<path d="M10 3.2v4M14 3.2v4M10 16.8v4M14 16.8v4"/>'
     '<path d="M3.2 10h4M3.2 14h4M16.8 10h4M16.8 14h4"/>'),
]

CAT_ICON = {k: SVG_OPEN + p + "</svg>" for k, n, d, l, ks, p in CATS}
CAT_NAME = {k: n for k, n, d, l, ks, p in CATS}
CAT_CSS = "\n".join(
    [".cat-%s{color:%s}" % (k, d) for k, n, d, l, ks, p in CATS]
    + ['html[data-theme="light"] .cat-%s{color:%s}' % (k, l) for k, n, d, l, ks, p in CATS]
    + [".cat-default{color:var(--tx3)}"])


def cat_of(tags):
    """标签 → 分类 key，识别不到返回 default。"""
    for t in tags:
        lt = t.lower()
        for k, n, d, l, ks, p in CATS:
            if any(w.lower() in lt for w in ks):
                return k
    return "default"

TPL = Template("""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>摘句本</title>
<style>
:root{
  --bg:#101419; --line:#232a33; --tx:#e7e9ea; --tx2:#8b98a5; --tx3:#697684;
  --accent:#4a9eff; --panel:#171c23; --hover:#151a20; --av1:#1d9bf0; --av2:#7c5cff;
}
html[data-theme="light"]{
  --bg:#ffffff; --line:#eff3f4; --tx:#0f1419; --tx2:#536471; --tx3:#8b98a5;
  --accent:#1d9bf0; --panel:#f1f4f5; --hover:#f7f9f9; --av1:#1d9bf0; --av2:#8b5cf6;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);
  font:15px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:visited{color:var(--accent)}
a:hover{text-decoration:underline}
button{font-family:inherit}
.wrap{max-width:600px;margin:0 auto;border-left:1px solid var(--line);border-right:1px solid var(--line);
  min-height:100vh;padding-bottom:20px}
.topbar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:12px;
  padding:14px 18px;background:var(--bg);border-bottom:1px solid var(--line)}
.logo{width:38px;height:38px;border-radius:50%;flex:0 0 38px;
  background:linear-gradient(135deg,var(--av1),var(--av2));color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:19px;font-weight:700}
.brand{flex:1;min-width:0}
.brand h1{margin:0;font-size:17px;font-weight:700;letter-spacing:-.01em}
.brand .sub{margin:1px 0 0;font-size:13px;color:var(--tx2)}
.tgl{padding:7px 13px;border:1px solid var(--line);border-radius:999px;background:transparent;
  color:var(--tx2);font-size:12.5px;cursor:pointer;white-space:nowrap}
.tgl:hover{color:var(--tx);border-color:var(--tx3)}
.searchbar{padding:10px 18px;border-bottom:1px solid var(--line)}
#q{width:100%;padding:9px 16px;border:1px solid var(--line);border-radius:999px;
  background:var(--panel);color:var(--tx);font-size:14px;outline:none}
#q::placeholder{color:var(--tx3)}
#q:focus{border-color:var(--accent)}
.tweet{display:flex;gap:12px;padding:14px 18px;border-bottom:1px solid var(--line);transition:background .12s}
.tweet:hover{background:var(--hover)}
.avatar{flex:0 0 44px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;opacity:.94;transition:opacity .15s,transform .15s}
.avatar svg{display:block}
.avatar:hover{transform:scale(1.08)}
.avatar.dim{opacity:.25}
$catcss
.body{flex:1;min-width:0}
.head{display:flex;align-items:baseline;gap:6px;flex-wrap:wrap;margin-bottom:4px;min-height:20px}
.handle,.time{color:var(--tx3);font-size:13.5px}
.head>.time{margin-left:auto}
.tag{border:0;background:none;padding:0;color:var(--accent);font-size:14.5px;
  font-weight:700;cursor:pointer;letter-spacing:.01em}
.tag:hover{text-decoration:underline}
.tag.on{text-decoration:underline}
.tag.none{color:var(--tx3);font-weight:400;font-size:13.5px;cursor:default}
.text{font-size:19px;line-height:1.72;font-weight:500;color:var(--tx);
  white-space:pre-wrap;margin:6px 0 10px;letter-spacing:.005em}
.note{color:var(--tx2);font-size:15px;line-height:1.72;white-space:pre-wrap}
.src{margin-top:9px;font-size:13px;color:var(--tx3)}
.actions{display:flex;gap:26px;margin-top:12px;align-items:center;color:var(--tx3)}
.act{border:0;background:none;padding:0;color:var(--tx3);cursor:pointer;display:flex;
  align-items:center;gap:6px;font-size:12.5px;transition:color .15s,transform .15s}
.act:hover{color:var(--accent)}
.act.like:hover{color:#f91880}
.act.liked{color:#f91880}
.act.liked svg{fill:#f91880;stroke:#f91880}
.act.liked .cnt{color:#f91880;font-weight:700}
.act.pop{transform:scale(1.22)}
.ok{color:var(--accent);font-size:12.5px}
.empty{color:var(--tx3);padding:60px 18px;text-align:center}
footer{padding:22px 18px;color:var(--tx3);font-size:12px;text-align:center;
  border-top:1px solid var(--line)}
@media(max-width:640px){
  .wrap{border-left:0;border-right:0}
  .text{font-size:17.5px}
  .tweet{padding:13px 14px}
}
</style>
</head>
<body>
<div class="wrap">
<header class="topbar">
  <div class="logo">&#10077;</div>
  <div class="brand">
    <h1>摘句本</h1>
    <p class="sub">$count 条摘录 &middot; 更新于 $updated</p>
  </div>
  <button class="tgl" id="tgl">亮色</button>
</header>
<div class="searchbar">
  <input id="q" type="search" placeholder="搜索句子 / 解释 / 来源 / 标签">
</div>
<main id="feed">
$body
</main>
<footer>摘句本 &middot; 本地静态快照 &middot; 数据源 quotes.json</footer>
</div>
<script>
var tb=document.getElementById('tgl'),rt=document.documentElement;
tb.onclick=function(){var d=rt.getAttribute('data-theme')==='dark';
  rt.setAttribute('data-theme',d?'light':'dark');tb.textContent=d?'暗色':'亮色';};
var qi=document.getElementById('q');
var cards=[].slice.call(document.querySelectorAll('.tweet'));
var active='',activeCat='';
function filt(){
  var k=(qi.value||'').trim().toLowerCase();
  cards.forEach(function(c){
    var t=c.getAttribute('data-k').toLowerCase();
    var ok=(!k||t.indexOf(k)>-1)&&(!active||t.indexOf('['+active.toLowerCase()+']')>-1)
           &&(!activeCat||c.getAttribute('data-c')===activeCat);
    c.style.display=ok?'':'none';
  });
  [].slice.call(document.querySelectorAll('.avatar')).forEach(function(v){
    v.classList.toggle('dim',!!activeCat&&v.getAttribute('data-cat')!==activeCat);
  });
}
qi.oninput=filt;
// 点赞：JSON 里的 likes 是基准值，页面点击的增量存 localStorage，刷新不丢
var LK='quote-likes-';
[].slice.call(document.querySelectorAll('.act.like')).forEach(function(b){
  var id=b.getAttribute('data-id');
  var base=parseInt(b.getAttribute('data-base')||'0',10)||0;
  var extra=parseInt(localStorage.getItem(LK+id)||'0',10)||0;
  var cnt=b.querySelector('.cnt');
  function paint(){cnt.textContent=base+extra;if(extra>0)b.classList.add('liked');}
  paint();
  b.addEventListener('click',function(e){
    e.stopPropagation();
    extra+=1;
    try{localStorage.setItem(LK+id,extra);}catch(err){}
    paint();
    b.classList.add('pop');
    setTimeout(function(){b.classList.remove('pop');},150);
  });
});
document.getElementById('feed').addEventListener('click',function(e){
  var v=e.target.closest('.avatar');
  if(v){
    var c=v.getAttribute('data-cat');
    activeCat=(c===activeCat)?'':c;
    filt();return;
  }
  var b=e.target.closest('.tag');
  if(b){
    active=(b.getAttribute('data-t')===active)?'':b.getAttribute('data-t');
    document.querySelectorAll('.tag').forEach(function(x){
      x.classList.toggle('on',x.getAttribute('data-t')===active);});
    filt();return;
  }
  var a=e.target.closest('.act');
  if(a&&a.getAttribute('data-copy')){
    navigator.clipboard.writeText(a.getAttribute('data-copy'));
    var old=a.innerHTML;a.innerHTML='<span class="ok">已复制</span>';
    setTimeout(function(){a.innerHTML=old;},1200);
  }
});
</script>
</body>
</html>
""")

CARD = Template("""<article class="tweet" data-k="$key" data-c="$cat">
  <div class="avatar cat-$cat" data-cat="$cat" title="$catname">$ic</div>
  <div class="body">
    <div class="head">$headtags<span class="time">$clock &middot; $date</span></div>
    <div class="text">$text</div>
    <div class="note">$note</div>
    $src
    <div class="actions">
      <button class="act like" data-id="$id" data-base="$likes" title="点赞">$ic_heart<span class="cnt">$likes</span></button>
      <button class="act" data-copy="$copy" title="复制这条摘录">$ic_copy</button>
      $actlink
    </div>
  </div>
</article>""")


def load(dirpath):
    p = os.path.join(dirpath, "quotes.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(dirpath, data):
    os.makedirs(dirpath, exist_ok=True)
    with open(os.path.join(dirpath, "quotes.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def esc(s):
    return html.escape(s or "", quote=True)


def br(s):
    return esc(s).replace("\n", "<br>")


def render(dirpath, data):
    cards = []
    for i, it in enumerate(data, 1):
        tags = [t.strip() for t in (it.get("tag") or "").split(",") if t.strip()]
        tm = (it.get("time") or "").split()
        date = tm[0] if len(tm) > 1 else ""
        clock = tm[-1] if len(tm) > 1 else (tm[0] if tm else "")

        src = it.get("source") or ""
        srchtml = ""
        if src:
            inner = esc(src)
            if it.get("url"):
                inner = ('<a href="' + esc(it["url"]) + '" target="_blank" rel="noopener">'
                         + inner + "</a>")
            srchtml = '<div class="src">&mdash; ' + inner + "</div>"

        taghtml = ""
        if tags:
            taghtml = "".join('<button class="tag" data-t="' + esc(t) + '">#' + esc(t) + "</button>"
                              for t in tags)
        else:
            taghtml = '<span class="tag none">摘录</span>'

        actlink = ""
        if it.get("url"):
            actlink = ('<a class="act" href="' + esc(it["url"]) + '" target="_blank" rel="noopener" '
                       'title="原始出处">' + IC_LINK + "</a>")

        key = " ".join([it.get("text", ""), it.get("note", ""), src,
                        " ".join("[" + t.lower() + "]" for t in tags)])
        copytext = it.get("text", "")
        if it.get("note"):
            copytext += "\n" + it["note"]
        if src:
            copytext += "\n—— " + src

        cat = cat_of(tags)
        catname = "分类：" + CAT_NAME.get(cat, "摘录")
        if it.get("cat_name"):
            catname = "分类：" + it["cat_name"]

        cards.append(CARD.substitute(
            key=esc(key), cat=cat, catname=esc(catname),
            ic=CAT_ICON.get(cat, IC_QUOTE_MARK), id=it.get("id", i),
            likes=int(it.get("likes", 0) or 0),
            clock=esc(clock), date=esc(date),
            text=br(it.get("text", "")), note=br(it.get("note", "")),
            src=srchtml, headtags=taghtml, actlink=actlink,
            copy=esc(copytext), ic_copy=IC_COPY, ic_heart=IC_HEART))

    if not cards:
        cards = ['<p class="empty">还没有摘录。贴一句话过来吧。</p>']

    out = TPL.substitute(
        count=len(data), catcss=CAT_CSS,
        updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        body="\n".join(cards))
    path = os.path.join(dirpath, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="add")
    ap.add_argument("--text")
    ap.add_argument("--note")
    ap.add_argument("--source")
    ap.add_argument("--url")
    ap.add_argument("--tag")
    ap.add_argument("--time")
    ap.add_argument("--json")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--id", type=int)
    a = ap.parse_args()

    dirpath = os.path.expanduser(a.dir)
    os.makedirs(dirpath, exist_ok=True)
    data = load(dirpath)

    if a.list or a.cmd == "list":
        for i, it in enumerate(data, 1):
            print("#%s  %s  %s" % (it.get("id", len(data) - i + 1), it.get("time", ""),
                                   (it.get("text", "")[:40]).replace("\n", " ")))
        print("total %d" % len(data))
        return

    if a.cmd == "rebuild":
        print(render(dirpath, data))
        return

    if a.cmd == "edit":
        hit = [x for x in data if x.get("id") == a.id]
        if not hit:
            print("ERROR: 找不到 id=%s" % a.id, file=sys.stderr)
            sys.exit(1)
        it = hit[0]
        for k in ("text", "note", "source", "url", "tag", "time"):
            v = getattr(a, k)
            if v:
                it[k] = v.strip()
        save(dirpath, data)
        print("updated #%d -> %s" % (a.id, render(dirpath, data)))
        return

    if a.cmd == "add":
        item = {}
        if a.json:
            with open(a.json, encoding="utf-8") as f:
                item = json.load(f)
        item["text"] = (item.get("text") or a.text or "").strip()
        item["note"] = (item.get("note") or a.note or "").strip()
        if not item["text"]:
            print("ERROR: --text 为空", file=sys.stderr)
            sys.exit(1)
        item["source"] = (item.get("source") or a.source or "").strip()
        item["url"] = (item.get("url") or a.url or "").strip()
        item["tag"] = (item.get("tag") or a.tag or "").strip()
        item["time"] = (item.get("time") or a.time or "").strip() or datetime.now().strftime("%Y-%m-%d %H:%M")
        item["id"] = (max([x.get("id", 0) for x in data]) + 1) if data else 1

        data.insert(0, item)
        save(dirpath, data)
        path = render(dirpath, data)
        print("saved #%d @ %s -> %s (total %d)" % (item["id"], item["time"], path, len(data)))
        return

    print("ERROR: 未知命令 %s" % a.cmd, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
