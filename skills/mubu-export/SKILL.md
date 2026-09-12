---
name: mubu-export
description: 导出幕布（Mubu/mubu.com）桌面客户端中的全部文档为本地 Markdown 文件。适用于用户要求"导出幕布文档/笔记"、"把幕布内容保存为 md"、"备份幕布数据"等场景。通过读取桌面端本地 RxDB/LevelDB 数据 + 调用幕布官方 API（api2.mubu.com）全量拉取，保留文件夹结构和正文格式。
agent_created: true
---

# 幕布（Mubu）文档导出为 Markdown

## 适用场景
用户想把自己幕布账号里的文档（大纲笔记）导出成本地 `.md` 文件。

## 前置条件
- 本机装有幕布桌面客户端（Electron），且用户已登录（无需重新登录）。
- 需要联网（正文从云端 API 拉取；本地缓存通常只有最近打开过的少量文档）。

## 数据位置（Windows）
- 本地数据库：`%APPDATA%\Roaming\Mubu\mubu_app_data\mubu_data\.storage\`
  - 集合目录（RxDB + LevelDB，PouchDB 格式）：
    - `mubu_desktop_app_x64-rxdb-2-documents` → 文档正文（`|c` 字段 = 节点树 JSON）
    - `mubu_desktop_app_x64-rxdb-2-document_meta` → 标题（`|n`）、父文件夹（`|h`）等
    - `mubu_desktop_app_x64-rxdb-2-folders` → 文件夹（名称在 `|o`，真 id 在 `id` 字段）
    - `mubu_desktop_app_x64-rxdb-1-users` → 用户记录（`|u` = JWT）
  - 本地备份快照：`...\mubu_data\backup\<docId>\*.json`（每个文档多份时间快照）
- 登录凭据：`%APPDATA%\Roaming\Mubu\mubu_app_data\Local Storage\leveldb\`（Chromium localStorage）
  - 键名：`_rhaegar://mubu.com··Jwt-Token`

## 读取 LevelDB
用 Node `classic-level`（或 `@electron/asar` 同理）：
```
npm i classic-level   # 安装到受管 workspace
```
注意：幕布正在运行时 LOCK 文件被占用，**复制目录时跳过 LOCK**。key 前缀：
- `ÿby-sequenceÿ<seq>` → 文档值（含 `_id`/`_rev`/字段）
- `ÿdocument-storeÿ<docId>` → 获胜修订信息（含 `deleted` 布尔、`winningRev`）

## 关键坑（务必遵守）
1. **JWT 值有 `\x01` 前缀字节**（Chromium localStorage 编码标记），必须 `value.slice(1)` 去掉，否则 HTTP 头非法 → nginx 400（表现为假"登录过期"）。
2. **API 必须带桌面端标志头**，否则即使 token 有效也返回 `{"code":2,"msg":"Login Expired"}`：
   ```
   Jwt-Token: <token>   jwt-token: <token>   mubu-desktop: true
   platform: windows    platform-version: <os.release()>
   User-Agent: windows Mubu Electron   userId: <用户id>   version: <客户端版本>
   Content-Type: application/json;
   ```
   这些头来自反编译 `database-fc4ab582fcc256127efb.js` 中的默认头 `y` + `setDefaultHeaders`。
3. `document/get` 返回 `data.definition`（节点树 JSON **字符串**）；空 body 或错误 docId 会返回 400。

## API 接口
- 全量列表（分页）：`POST https://api2.mubu.com/v3/api/list/get_all_documents_page`
  - body：`{}` 或 `{"start": <上页返回的 next_start>}`；响应 `data.documents / data.folders / data.next_start / data.root_relation`
  - 文档字段：`id`、`name`、`folderId`、`createTime`、`updateTime`、`deleted`
- 单篇正文：`POST https://api2.mubu.com/v3/api/document/get`，body `{"docId":"..."}`

## 执行步骤
1. 复制 `.storage` 各集合目录到工作区（跳过 LOCK），用 `classic-level` dump 成 JSONL，理解结构（可选：仅当用户没有网络时）。
2. 从 localStorage leveldb 提取 JWT（去掉 `\x01`），写 token.txt。
3. 运行 `scripts/mubu_export.js`（Node 22，需 `classic-level` 仅本地用；云端路径不需要）：
   - 分页拉全量列表 → `cloud_list.json`（可断点续传）
   - 逐个 `document/get` → 缓存到 `cloud_cache/<docId>.json`（可续传）→ 转 Markdown
   - 输出 `markdown/`（按文件夹结构）、`导出清单.csv`、`导出报告.md`
4. 对比本地 document_meta 与云端列表：本地有但云端没有的（已删除），若本地有快照则补导出到 `markdown/_已删除文档（本地快照）/`。

## Markdown 转换规则
- 节点树：`{nodes:[{id,text,children,emoji,heading,taskStatus,note,image,...}]}`
- `text` 两种格式：
  - HTML span 字符串：`<span class="bold">` → `**`，italic → `*`，strike → `~~`，code → 反引号，`text-color-*`/highlight → `==`，`<a href>` → `[t](url)`，`<img src>` → `![图片](url)`
  - 富文本数组：`[{type:1,text,style},{type:3,text,link}]`，type3 → 链接
- `heading:0` → `##`（文档标题为 `#`）；`taskStatus:0` → `- [ ]`，否则 `- [x]`
- 根节点文本=标题时，子节点从深度 0 开始；emoji 前缀保留
- 文件按 `folderPath(文件夹树) + 文档名.md` 组织，重名自动加序号，非法字符替换为 `_`

## 注意
- 全量导出 1600+ 篇约需 6-7 分钟（每篇约 150ms 限速 + 3 次重试），务必后台运行并输出日志，脚本可断点续传。
- 不要删除/移动用户的幕布数据目录，只读。
