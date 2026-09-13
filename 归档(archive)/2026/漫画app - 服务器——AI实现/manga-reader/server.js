/**
 * 刀剑神域 本地漫画阅读器
 * -------------------------------------------------
 * 思路：epub 本质是一个 zip，里面按 OPF(spine) 顺序排列每一页。
 * 本服务不解压、不复制图片，而是在收到请求时直接从 epub 里读出对应页图片返回，
 * 前端呈现为“漫画网站”式的书架 + 翻页阅读器。
 *
 * 依赖：adm-zip（已随项目安装）
 * 运行：node server.js   然后浏览器打开 http://localhost:8080
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');

// ============ 配置 ============
const MANGA_ROOT = 'C:\\Users\\16673\\Desktop\\漫画app - 服务器\\刀剑神域(漫画)';
const PORT = 8080;
const IMG_EXT = /\.(jpe?g|png|gif|webp|bmp)$/i;
const BOOK_EXT = /\.(epub|kepub)$/i;

// ============ 扫描书库 ============
// volumes: 扁平数组，每项 = { id, series, title, file }
// library: 按系列分组，供前端书架展示
let volumes = [];
let library = [];

function scanBooks(dir, rootSeries) {
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    let stat;
    try { stat = fs.statSync(full); } catch { continue; }
    if (stat.isDirectory()) {
      // 顶层目录名作为“系列”，更深层目录沿用最初的系列名
      scanBooks(full, rootSeries || name);
    } else if (BOOK_EXT.test(name)) {
      volumes.push({
        id: volumes.length,
        series: rootSeries || '未分类',
        title: name.replace(BOOK_EXT, ''),
        file: full,
      });
    }
  }
}

function buildLibrary() {
  const map = new Map();
  for (const v of volumes) {
    if (!map.has(v.series)) map.set(v.series, []);
    map.get(v.series).push({ id: v.id, title: v.title });
  }
  library = [...map.entries()].map(([series, vols]) => ({
    series,
    // 卷内按标题自然排序（数字感知）
    volumes: vols.sort((a, b) =>
      a.title.localeCompare(b.title, 'zh', { numeric: true })),
  }));
}

// ============ epub 解析（带缓存）============
// 缓存已打开的 zip 与其页面映射，避免每张图重复读取整个 epub
const zipCache = new Map();        // id -> AdmZip
const pageMapCache = new Map();    // id -> [imageEntryName, ...] 按阅读顺序
const CACHE_LIMIT = 6;

function getZip(id) {
  if (zipCache.has(id)) return zipCache.get(id);
  const zip = new AdmZip(volumes[id].file);
  zipCache.set(id, zip);
  // 简单 LRU：超限时删除最早的
  if (zipCache.size > CACHE_LIMIT) {
    const oldest = zipCache.keys().next().value;
    zipCache.delete(oldest);
    pageMapCache.delete(oldest);
  }
  return zip;
}

// posix 风格路径拼接与规整（zip 内部统一用 /）
function resolveInZip(baseFile, relSrc) {
  const baseDir = baseFile.includes('/')
    ? baseFile.slice(0, baseFile.lastIndexOf('/'))
    : '';
  const parts = (baseDir ? baseDir.split('/') : []);
  for (const seg of decodeURIComponent(relSrc).split('/')) {
    if (seg === '' || seg === '.') continue;
    if (seg === '..') parts.pop();
    else parts.push(seg);
  }
  return parts.join('/');
}

// 计算某卷的阅读顺序（图片条目名数组）
function getPageMap(id) {
  if (pageMapCache.has(id)) return pageMapCache.get(id);
  const zip = getZip(id);
  const entries = zip.getEntries();
  const nameSet = new Set(entries.map((e) => e.entryName));
  let pages = [];

  try {
    // 1) container.xml -> OPF 路径
    const container = zip.readAsText('META-INF/container.xml');
    const opfPath = (container.match(/full-path="([^"]+)"/) || [])[1];
    const opf = zip.readAsText(opfPath);

    // 2) manifest: id -> href
    const manifest = {};
    for (const m of opf.matchAll(/<item\s+[^>]*id="([^"]+)"[^>]*href="([^"]+)"[^>]*>/g)) {
      manifest[m[1]] = resolveInZip(opfPath, m[2]);
    }
    // href 与 id 顺序在 epub 中可能颠倒，补一次反向匹配
    for (const m of opf.matchAll(/<item\s+[^>]*href="([^"]+)"[^>]*id="([^"]+)"[^>]*>/g)) {
      manifest[m[2]] = resolveInZip(opfPath, m[1]);
    }

    // 3) spine: 阅读顺序
    for (const m of opf.matchAll(/<itemref\s+[^>]*idref="([^"]+)"/g)) {
      const href = manifest[m[1]];
      if (!href) continue;
      if (IMG_EXT.test(href) && nameSet.has(href)) {
        pages.push(href); // spine 直接指向图片
        continue;
      }
      // 否则是 html/xhtml，取其中第一张图片
      if (nameSet.has(href)) {
        const doc = zip.readAsText(href);
        const src =
          (doc.match(/<img[^>]*src="([^"]+)"/i) || [])[1] ||
          (doc.match(/xlink:href="([^"]+)"/i) || [])[1] ||
          (doc.match(/href="([^"]+\.(?:jpe?g|png|gif|webp))"/i) || [])[1];
        if (src) {
          const imgPath = resolveInZip(href, src);
          if (nameSet.has(imgPath)) pages.push(imgPath);
        }
      }
    }
  } catch (e) {
    pages = [];
  }

  // 4) 兜底：spine 解析失败则按图片文件名自然排序
  if (pages.length === 0) {
    pages = entries
      .map((e) => e.entryName)
      .filter((n) => IMG_EXT.test(n))
      .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }

  pageMapCache.set(id, pages);
  return pages;
}

function mimeOf(name) {
  const ext = name.toLowerCase().slice(name.lastIndexOf('.'));
  return { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp' }[ext] || 'application/octet-stream';
}

// ============ HTTP 服务 ============
const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const p = url.pathname;

  // 首页 / 阅读器页面：同一个 HTML，前端路由
  if (p === '/' || p === '/read') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(PAGE_HTML);
  }

  // 书库数据
  if (p === '/api/library') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify({ root: MANGA_ROOT, total: volumes.length, library }));
  }

  // 某卷信息（页数 + 标题 + 简介）
  if (p === '/api/volume') {
    const id = Number(url.searchParams.get('id'));
    if (!volumes[id]) { res.writeHead(404); return res.end('no volume'); }
    let count = 0;
    try { count = getPageMap(id).length; } catch { count = 0; }
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify({
      id,
      series: volumes[id].series,
      title: volumes[id].title,
      pages: count,
      // 用卷名生成一句简介，保持界面完整
      summary: `${volumes[id].series} · ${volumes[id].title}，共 ${count} 页。本地 EPUB 漫画，按原始阅读顺序呈现。`,
      status: count > 0 ? '已完结' : '未知',
      author: '刀剑神域系列',
      tags: ['少年', '热血', '奇幻'],
    }));
  }

  // 搜索：按关键词过滤卷
  if (p === '/api/search') {
    const kw = (url.searchParams.get('q') || '').trim().toLowerCase();
    const list = volumes
      .filter(v => !kw || v.title.toLowerCase().includes(kw) || v.series.toLowerCase().includes(kw))
      .map(v => ({ id: v.id, series: v.series, title: v.title }))
      .slice(0, 200);
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify({ total: list.length, list }));
  }

  // 取某卷某页图片：/img?id=0&page=0
  if (p === '/img') {
    const id = Number(url.searchParams.get('id'));
    const page = Number(url.searchParams.get('page'));
    if (!volumes[id]) { res.writeHead(404); return res.end('no volume'); }
    try {
      const map = getPageMap(id);
      const entry = map[page];
      if (!entry) { res.writeHead(404); return res.end('no page'); }
      const buf = getZip(id).readFile(entry);
      res.writeHead(200, { 'Content-Type': mimeOf(entry), 'Cache-Control': 'public, max-age=86400' });
      return res.end(buf);
    } catch (e) {
      res.writeHead(500); return res.end('read error');
    }
  }

  res.writeHead(404);
  res.end('not found');
});

// 前端页面（书架 + 阅读器）在单独文件中注入
const PAGE_HTML = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf-8');

// ============ 启动 ============
console.log('扫描书库中...');
scanBooks(MANGA_ROOT, null);
buildLibrary();
console.log(`共发现 ${volumes.length} 卷，${library.length} 个系列`);
server.listen(PORT, () => {
  console.log(`漫画阅读器已启动： http://localhost:${PORT}`);
});
