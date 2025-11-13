# dm5_playwright_downloader.py
import asyncio
import os
import re
import math
import time
import random
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urljoin, urlparse

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm

from playwright.async_api import async_playwright

# ------------- CONFIG -------------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)
OUT_DIR = "dm5_downloads"
CONCURRENT_IMAGE_DOWNLOADS = 6    # aiohttp 并发下载数
PAGE_RENDER_DELAY = 0.6           # 每页加载后等待时间（s），可调
RETRY_IMAGE = 3                   # 图片下载重试次数
DELAY_BETWEEN_PAGE_NAV = (0.1, 0.6)  # 随机延时范围（s）
# ----------------------------------

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

async def fetch_page_content(page, url: str, wait_for: float = PAGE_RENDER_DELAY) -> str:
    # 导航并返回渲染后的 HTML
    await page.goto(url, wait_until="networkidle")
    await asyncio.sleep(wait_for)
    return await page.content()

def parse_chapters_from_listing(html: str, base_domain: str) -> List[Tuple[str, str]]:
    """
    从漫画主页的章节列表区域（#chapterlistload）解析章节链接和标题
    返回 [(chapter_url, title), ...]（按从旧到新或网页顺序，可以 reverse）
    """
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", id="chapterlistload")
    if not div:
        # 如果没有找到 id 区域，尽量在整个页面找可能匹配的链接
        div = soup

    chapters = []
    for a in div.find_all("a", href=True):
        title = a.get_text(strip=True)
        href = a["href"]
        if href.startswith("/"):
            href = urljoin(base_domain, href)
        # 仅保留像 /mxxxxx/ 这一类的章节链接
        if re.search(r"/m\d+(-p\d+)?/?$", href):
            chapters.append((href, title))
    # 常见页面顺序：新->旧，用户可能想从第一话开始下载，反转为旧->新
    chapters = list(dict.fromkeys(chapters))  # 去重保持顺序
    chapters.reverse()
    return chapters

def parse_total_pages_from_pager(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    pager = soup.find("div", id="chapterpager")
    if not pager:
        return 1
    a_list = pager.find_all("a", href=True)
    if not a_list:
        return 1
    last_href = a_list[-1]["href"]
    m = re.search(r"-p(\d+)/?$", last_href)
    if m:
        return int(m.group(1))
    # 也可能是数字直接
    nums = [int(x.get_text()) for x in a_list if x.get_text().strip().isdigit()]
    return max(nums) if nums else 1

async def collect_image_urls_for_chapter(page, chapter_url: str, base_domain: str) -> List[Tuple[str, str]]:
    """
    返回该章节所有页的 (page_url, image_src) 列表（image_src 可能包含 query）
    这里我们逐页渲染并拿 #cp_image 的 src
    """
    # 确保结尾有斜杠
    if not chapter_url.endswith('/'):
        chapter_url = chapter_url + '/'

    # 先拿分页数量
    html0 = await fetch_page_content(page, chapter_url)
    total_pages = parse_total_pages_from_pager(html0)
    base = chapter_url.rstrip('/')

    results = []
    # 遍历每一页，渲染拿到图片
    for i in range(1, total_pages + 1):
        if i == 1:
            page_url = base + '/'
        else:
            page_url = f"{base}-p{i}/"
        try:
            # navigate + small random delay for stealth
            html = await fetch_page_content(page, page_url, wait_for=PAGE_RENDER_DELAY)
            soup = BeautifulSoup(html, "html.parser")
            img = soup.find("img", id="cp_image")
            img_src = img["src"] if img and img.get("src") else None
            # 若没有 id=cp_image，再尝试查找较可能的图元素
            if not img_src:
                img = soup.select_one("img[src*='cdndm5'], img[src*='manhua']")
                img_src = img["src"] if img else None

            if img_src:
                img_url = urljoin(page_url, img_src)
                results.append((page_url, img_url))
            else:
                print(f"[!] 未找到图片：{page_url}")
        except Exception as e:
            print(f"[x] 渲染/解析失败 {page_url} -> {e}")

        await asyncio.sleep(random.uniform(*DELAY_BETWEEN_PAGE_NAV))

    return results

def cookies_from_playwright(cookies_list: List[Dict]) -> Dict[str, str]:
    # 转换成 aiohttp 可用的 cookie dict
    cookie_dict = {}
    for c in cookies_list:
        cookie_dict[c['name']] = c['value']
    return cookie_dict

async def download_image_with_retries(session: ClientSession, img_url: str, referer: str, out_path: Path, retries: int = RETRY_IMAGE):
    headers = {
        "Referer": referer,
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
    }
    for attempt in range(1, retries+1):
        try:
            # 如果文件已存在且大小>0，跳过（断点续传的简单策略）
            if out_path.exists() and out_path.stat().st_size > 0:
                return True
            async with session.get(img_url, headers=headers, timeout=60) as resp:
                resp.raise_for_status()
                # 写入临时文件先，避免不完整文件被误判
                tmp = out_path.with_suffix(out_path.suffix + ".part")
                with tmp.open("wb") as f:
                    async for chunk in resp.content.iter_chunked(1024*16):
                        if chunk:
                            f.write(chunk)
                tmp.replace(out_path)
                return True
        except Exception as e:
            if attempt < retries:
                backoff = 0.8 * attempt + random.random() * 0.6
                await asyncio.sleep(backoff)
            else:
                print(f"[x] 下载失败：{img_url} -> {e}")
                return False

async def download_chapter_images(aio_session: ClientSession, chapter_folder: Path, imgs: List[Tuple[str, str]]):
    sem = asyncio.Semaphore(CONCURRENT_IMAGE_DOWNLOADS)
    tasks = []

    async def worker(index: int, page_url: str, img_url: str):
        async with sem:
            # 生成文件名
            ext = Path(urlparse(img_url).path).suffix or ".jpg"
            filename = f"{index:03d}{ext}"
            out_file = chapter_folder / filename
            success = await download_image_with_retries(aio_session, img_url, referer=page_url, out_path=out_file)
            return success

    for idx, (page_url, img_url) in enumerate(imgs, start=1):
        tasks.append(worker(idx, page_url, img_url))

    # tqdm 显示进度
    results = []
    for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Downloading {chapter_folder.name}"):
        res = await f
        results.append(res)
    return results

async def main(manga_home_url: str, download_all_chapters: bool = True, max_chapters: int = None):
    # 根域名（用于解析绝对链接）
    parsed = urlparse(manga_home_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        print("[i] 获取漫画主页并解析章节列表...")
        html_home = await fetch_page_content(page, manga_home_url)
        chapters = parse_chapters_from_listing(html_home, base_domain)

        if not chapters:
            print("[!] 未在主页找到章节列表，尝试查找网络请求或改用手动章节 URL 列表")
            await browser.close()
            return

        print(f"[i] 共发现 {len(chapters)} 个章节（按顺序）")
        # 选择要下载的章节子集
        if not download_all_chapters and max_chapters:
            chapters = chapters[:max_chapters]

        # 导出 cookies 并构建 aiohttp session
        cookies_list = await context.cookies()
        cookie_dict = cookies_from_playwright(cookies_list)

        # 创建 aiohttp session（共享 cookies）
        jar = aiohttp.CookieJar()
        async with ClientSession(cookie_jar=jar) as aio_sess:
            # 将 playwright 的 cookies 写入 jar
            for k, v in cookie_dict.items():
                jar.update_cookies({k: v}, response_url=base_domain)
            # 再设置默认 headers
            aio_sess.headers.update({"User-Agent": USER_AGENT})

            # 每个章节遍历
            for chap_idx, (chap_url, chap_title) in enumerate(chapters, start=1):
                pretty_title = chap_title or chap_url.split("/")[-2]
                folder_name = f"{chap_idx:03d}_{sanitize_filename(pretty_title)}"
                chapter_folder = Path(OUT_DIR) / folder_name
                chapter_folder.mkdir(parents=True, exist_ok=True)

                print(f"\n[i] [{chap_idx}/{len(chapters)}] 处理章节: {pretty_title} -> {chap_url}")
                imgs = await collect_image_urls_for_chapter(page, chap_url, base_domain)

                if not imgs:
                    print(f"[!] 未解析到图片链接，跳过章节：{chap_url}")
                    continue

                print(f"[i] 解析到 {len(imgs)} 页图片，开始并发下载 ...")
                await download_chapter_images(aio_sess, chapter_folder, imgs)

                # 章节之间休息一下，避免触发防护
                await asyncio.sleep(random.uniform(1.0, 2.2))

        await browser.close()
    print("\n[i] 全部完成。文件保存在：", Path(OUT_DIR).absolute())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="dm5 异步下载器 (Playwright + aiohttp)")
    parser.add_argument("url", help="漫画主页 URL，例如 https://m.dm5.cn/manhua-dongfangzuidiehua/")
    parser.add_argument("--out", help="输出目录 (默认 dm5_downloads)", default=OUT_DIR)
    parser.add_argument("--max", type=int, help="只下载前 N 章（可选）", default=None)
    parser.add_argument("--noall", action="store_true", help="不要下载全部章节（配合 --max 使用）")
    args = parser.parse_args()

    OUT_DIR = args.out

    # 运行主逻辑
    asyncio.run(main(args.url, download_all_chapters=not args.noall, max_chapters=args.max))
