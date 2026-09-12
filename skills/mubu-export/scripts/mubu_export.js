const fs = require('fs');
const path = require('path');
const https = require('https');

const HERE = __dirname;
const TOKEN = fs.readFileSync(path.join(HERE, 'token.txt'), 'utf8').trim();
const CACHE_DIR = path.join(HERE, 'cloud_cache');
const OUT_DIR = path.join(HERE, 'markdown');

const COMMON_HEADERS = {
  'Jwt-Token': TOKEN, 'jwt-token': TOKEN,
  'mubu-desktop': 'true', 'platform': 'windows', 'platform-version': '10.0',
  'User-Agent': 'windows Mubu Electron', 'userId': '3718236', 'version': '5.7.2',
  'Content-Type': 'application/json;'
};

function post(urlPath, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body || {});
    const req = https.request({
      hostname: 'api2.mubu.com', path: urlPath, method: 'POST',
      headers: { ...COMMON_HEADERS, 'Content-Length': Buffer.byteLength(data) },
      timeout: 30000
    }, res => {
      let chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
        catch (e) { reject(new Error('bad json: ' + Buffer.concat(chunks).toString('utf8').slice(0, 100))); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.write(data);
    req.end();
  });
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------------- markdown converter (same as local export) ----------------
function decodeEntities(s) {
  return s.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'").replace(/&#x2F;/g, '/').replace(/&hellip;/g, '…')
    .replace(/&mdash;/g, '—').replace(/&ldquo;|&rdquo;/g, '"').replace(/&#(\d+);/g, (_, d) => String.fromCharCode(d));
}
function htmlToMd(html) {
  if (!html) return '';
  const tokens = [];
  const re = /<img[^>]*>|<a\s[^>]*>|<\/a>|<span[^>]*>|<\/span>|<br\s*\/?>|<[^>]+>/g;
  let last = 0, m;
  while ((m = re.exec(html)) !== null) {
    if (m.index > last) tokens.push({ t: 'text', v: html.slice(last, m.index) });
    const tag = m[0];
    if (/^<img/i.test(tag)) {
      const src = (tag.match(/src=\\?"([^"\\]+)\\?"/) || tag.match(/src="([^"]+)"/) || [])[1];
      tokens.push({ t: 'img', src });
    } else if (/^<a\s/i.test(tag)) {
      const href = (tag.match(/href=\\?"([^"\\]+)\\?"/) || tag.match(/href="([^"]+)"/) || [])[1] || '';
      tokens.push({ t: 'a_open', href });
    } else if (/^<\/a/i.test(tag)) tokens.push({ t: 'a_close' });
    else if (/^<span/i.test(tag)) {
      const cls = (tag.match(/class=\\?"([^"\\]*)\\?"/) || tag.match(/class="([^"]*)"/) || [])[1] || '';
      tokens.push({ t: 'span_open', cls });
    } else if (/^<\/span/i.test(tag)) tokens.push({ t: 'span_close' });
    else if (/^<br/i.test(tag)) tokens.push({ t: 'br' });
    else tokens.push({ t: 'other' });
    last = re.lastIndex;
  }
  if (last < html.length) tokens.push({ t: 'text', v: html.slice(last) });
  function renderTokens(list) {
    let s = ''; let k = 0;
    while (k < list.length) {
      const tk = list[k];
      if (tk.t === 'text') { s += decodeEntities(tk.v); k++; }
      else if (tk.t === 'img') { s += `![图片](${tk.src})`; k++; }
      else if (tk.t === 'br') { s += ' '; k++; }
      else if (tk.t === 'a_open' || tk.t === 'span_open') {
        let depth = 1, j2 = k + 1;
        for (; j2 < list.length; j2++) {
          if (list[j2].t === 'a_open' || list[j2].t === 'span_open') depth++;
          else if (list[j2].t === 'a_close' || list[j2].t === 'span_close') { depth--; if (!depth) break; }
        }
        let txt = renderTokens(list.slice(k + 1, j2));
        if (tk.t === 'a_open') s += `[${txt}](${tk.href})`;
        else {
          const cls = tk.cls || '';
          if (cls.includes('bold')) txt = `**${txt}**`;
          if (cls.includes('italic')) txt = `*${txt}*`;
          if (cls.includes('strike')) txt = `~~${txt}~~`;
          if (cls.includes('code')) txt = '`' + txt + '`';
          if (cls.includes('highlight') || /text-color-/.test(cls)) txt = `==${txt}==`;
          s += txt;
        }
        k = j2 + 1;
      } else { k++; }
    }
    return s;
  }
  return renderTokens(tokens).replace(/^\s+|\s+$/g, '');
}
function richTextToMd(text) {
  if (!text) return '';
  if (typeof text === 'string') return htmlToMd(text);
  if (Array.isArray(text)) {
    let s = '';
    for (const seg of text) {
      if (!seg) continue;
      let t = decodeEntities(String(seg.text || ''));
      const st = seg.style || {};
      if (st.bold) t = `**${t}**`;
      if (st.italic) t = `*${t}*`;
      if (st.code) t = '`' + t + '`';
      if (seg.link || seg.type === 3) s += `[${t}](${seg.link || ''})`;
      else s += t;
    }
    return s.trim();
  }
  return String(text);
}
function nodeToMd(node, depth, lines) {
  const text = richTextToMd(node.text);
  const emoji = node.emoji ? node.emoji + ' ' : '';
  const isTask = node.taskStatus !== undefined;
  const taskMark = isTask ? (node.taskStatus === 0 ? '[ ] ' : '[x] ') : '';
  let line;
  if (node.heading !== undefined && node.heading !== null) {
    const level = Math.min(6, 2 + (node.heading || 0));
    line = '#'.repeat(level) + ' ' + emoji + text;
  } else if (isTask) {
    line = '  '.repeat(depth) + '- ' + taskMark + emoji + text;
  } else {
    line = '  '.repeat(depth) + '- ' + emoji + text;
  }
  lines.push(line);
  if (node.note) {
    for (const seg of String(node.note).replace(/\r/g, '').split(/\n/)) {
      if (seg.trim()) lines.push('  '.repeat(depth + 1) + '> ' + seg.trim());
    }
  }
  if (node.image && node.image.url) lines.push('  '.repeat(depth + 1) + `![图片](${node.image.url})`);
  for (const ch of (node.children || [])) nodeToMd(ch, depth + 1, lines);
}
function docToMarkdown(tree, title) {
  const lines = ['# ' + title, ''];
  const nodes = (tree && tree.nodes) || [];
  let startNodes = nodes, rootDepth = 0;
  if (nodes.length === 1) {
    const rootText = richTextToMd(nodes[0].text).trim();
    if (rootText === title || rootText === '') startNodes = nodes[0].children || [];
  }
  for (const n of startNodes) nodeToMd(n, rootDepth, lines);
  return lines.join('\n') + '\n';
}
function sanitizeName(s) {
  let r = String(s || '未命名').replace(/[\\/:*?"<>|\r\n]/g, '_').replace(/\s+$/, '').trim();
  return (r || '未命名').slice(0, 80);
}
const usedPaths = new Map();
function uniquePath(p) {
  if (!usedPaths.has(p)) { usedPaths.set(p, 1); return p; }
  const n = usedPaths.get(p) + 1; usedPaths.set(p, n);
  const ext = path.extname(p);
  return p.slice(0, p.length - ext.length) + ` (${n})` + ext;
}
function fmtDate(ts) {
  if (!ts) return '';
  const d = new Date(ts); const p = x => String(x).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

// ---------------- main ----------------
(async () => {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
  const listFile = path.join(HERE, 'cloud_list.json');
  let allDocs = [], allFolders = [], rootRelation = null;

  if (fs.existsSync(listFile)) {
    const saved = JSON.parse(fs.readFileSync(listFile, 'utf8'));
    allDocs = saved.docs; allFolders = saved.folders; rootRelation = saved.rootRelation;
    console.log('loaded cached list:', allDocs.length, 'docs');
  } else {
    let start = null, page = 0;
    while (true) {
      const body = start ? { start } : {};
      const r = await post('/v3/api/list/get_all_documents_page', body);
      if (r.code !== 0) throw new Error('list failed: ' + JSON.stringify(r).slice(0, 200));
      const d = r.data;
      allDocs.push(...(d.documents || []));
      allFolders.push(...(d.folders || []));
      if (!rootRelation && d.root_relation) { try { rootRelation = JSON.parse(d.root_relation); } catch (e) {} }
      page++;
      console.log(`page ${page}: +${(d.documents || []).length} docs, +${(d.folders || []).length} folders, next:`, JSON.stringify(d.next_start));
      if (!d.next_start || !(d.documents || []).length) break;
      start = d.next_start;
      await sleep(300);
    }
    // dedupe
    const dm = new Map(), fm = new Map();
    for (const doc of allDocs) dm.set(doc.id, doc);
    for (const f of allFolders) fm.set(f.id, f);
    allDocs = [...dm.values()]; allFolders = [...fm.values()];
    fs.writeFileSync(listFile, JSON.stringify({ docs: allDocs, folders: allFolders, rootRelation }));
    console.log('TOTAL: docs', allDocs.length, 'folders', allFolders.length);
  }

  const alive = allDocs.filter(d => !d.deleted);
  const deleted = allDocs.filter(d => d.deleted);
  console.log('alive docs:', alive.length, 'deleted docs:', deleted.length);

  // folders map
  const folders = new Map();
  for (const f of allFolders) folders.set(f.id, { id: f.id, name: f.name || f.id, parent: f.folderId || '0', children: (f.relation ? JSON.parse(f.relation) : []) });
  function folderPath(fid) {
    const parts = []; let cur = fid, guard = 0;
    while (cur && cur !== '0' && folders.has(cur) && guard++ < 50) {
      parts.unshift(folders.get(cur).name.replace(/[\\/:*?"<>|]/g, '_'));
      cur = folders.get(cur).parent;
    }
    return parts;
  }

  // move old output aside instead of deleting (bulk-delete guard)
  if (fs.existsSync(OUT_DIR)) {
    const old = path.join(HERE, 'markdown_local_only');
    if (fs.existsSync(old)) fs.rmSync(old, { recursive: true, force: true });
    fs.renameSync(OUT_DIR, old);
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const manifest = [];
  let okCount = 0, failCount = 0;
  for (let i = 0; i < alive.length; i++) {
    const doc = alive[i];
    const cacheFile = path.join(CACHE_DIR, doc.id + '.json');
    let def = null;
    if (fs.existsSync(cacheFile)) {
      try { def = JSON.parse(fs.readFileSync(cacheFile, 'utf8')).definition; } catch (e) {}
    }
    if (!def) {
      let done = false;
      for (let attempt = 0; attempt < 3 && !done; attempt++) {
        try {
          const r = await post('/v3/api/document/get', { docId: doc.id });
          if (r.code === 0 && r.data && r.data.definition) {
            fs.writeFileSync(cacheFile, JSON.stringify({ definition: r.data.definition, name: r.data.name }));
            def = r.data.definition;
            done = true;
          } else if (r.code === 2) {
            console.error('token expired at doc', doc.id); process.exit(2);
          } else {
            console.warn('unexpected resp for', doc.id, JSON.stringify(r).slice(0, 120));
            done = true; // skip
          }
        } catch (e) {
          console.warn('retry', doc.id, e.message);
          await sleep(1000 * (attempt + 1));
        }
      }
      await sleep(150);
    }
    const fparts = folderPath(doc.folderId || '0');
    const relDir = fparts.length ? path.join(...fparts) : '';
    const folderStr = fparts.join('/') || '我的文档';
    const created = fmtDate(doc.createTime), updated = fmtDate(doc.updateTime);
    if (def) {
      let tree;
      try { tree = typeof def === 'string' ? JSON.parse(def) : def; } catch (e) { tree = null; }
      if (tree) {
        const md = docToMarkdown(tree, doc.name);
        const outDir = path.join(OUT_DIR, relDir);
        fs.mkdirSync(outDir, { recursive: true });
        const filePath = uniquePath(path.join(outDir, sanitizeName(doc.name) + '.md'));
        fs.writeFileSync(filePath, md, 'utf8');
        manifest.push({ docId: doc.id, title: doc.name, folder: folderStr, created, updated, exported: true, file: path.relative(OUT_DIR, filePath) });
        okCount++;
      } else { manifest.push({ docId: doc.id, title: doc.name, folder: folderStr, created, updated, exported: false }); failCount++; }
    } else {
      manifest.push({ docId: doc.id, title: doc.name, folder: folderStr, created, updated, exported: false });
      failCount++;
    }
    if ((i + 1) % 100 === 0) console.log(`progress: ${i + 1}/${alive.length}, ok=${okCount} fail=${failCount}`);
  }

  // csv manifest
  const csv = ['docId,标题,文件夹,创建时间,更新时间,已导出,文件'];
  for (const m of manifest) csv.push([m.docId, `"${(m.title || '').replace(/"/g, '""')}"`, `"${m.folder}"`, m.created, m.updated, m.exported ? '是' : '否', m.file || ''].join(','));
  fs.writeFileSync(path.join(HERE, '导出清单.csv'), '\uFEFF' + csv.join('\n'), 'utf8');

  // summary report
  const summary = [
    '# 幕布全量导出报告', '',
    `- 账号文档总数：${allDocs.length}（云端列表）`,
    `- 正常文档：${alive.length}，已导出：${okCount}，失败：${failCount}`,
    `- 回收站/已删除：${deleted.length}`, '',
    '## 导出失败的文档', '',
    '| 标题 | 文件夹 |', '|---|---|',
  ];
  for (const m of manifest.filter(x => !x.exported)) summary.push(`| ${m.title} | ${m.folder} |`);
  summary.push('', '## 回收站中的文档（未导出）', '', '| 标题 | 删除时间 |', '|---|---|');
  for (const d of deleted) summary.push(`| ${d.name} | ${fmtDate(d.deleteTime)} |`);
  fs.writeFileSync(path.join(HERE, '导出报告.md'), summary.join('\n'), 'utf8');
  console.log('DONE. exported:', okCount, 'failed:', failCount, 'deleted(skipped):', deleted.length);
})().catch(e => { console.error(e); process.exit(1); });
