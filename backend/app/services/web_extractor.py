from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass
import hashlib
import asyncio
from urllib.parse import urlparse

import httpx
from trafilatura import extract, extract_metadata
from trafilatura.settings import use_config

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("extractor")


@dataclass
class ExtractedContent:
    """提取的内容"""
    url: str
    title: str
    author: Optional[str]
    date: Optional[datetime]
    site_name: Optional[str]
    content: str
    text_content: str
    excerpt: Optional[str]
    content_hash: str
    word_count: int


@dataclass
class BatchResult:
    """批量处理结果"""
    total: int
    success: int
    failed: int
    results: List[dict]


class WebExtractor:
    """网页内容提取器"""

    def __init__(
        self,
        timeout: int = None,
        max_retries: int = None,
        user_agent: str = None
    ):
        self.timeout = timeout or settings.TRAFILATURA_TIMEOUT
        self.max_retries = max_retries or settings.TRAFILATURA_MAX_RETRIES
        self.user_agent = user_agent or settings.DEFAULT_USER_AGENT
        self._config = use_config()

    def _validate_url(self, url: str) -> bool:
        """验证 URL 格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _strip_markdown(self, text: str) -> str:
        """去除 Markdown 格式"""
        import re
        # 移除链接，保留文本
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除 Markdown 符号
        text = re.sub(r'[*_#>`~]', '', text)
        # 压缩多余空行
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    async def _download_html(
        self,
        url: str,
        retry_count: int = 0
    ) -> str:
        """下载网页内容（带重试）"""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=headers,
                verify=False
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP 错误 {e.response.status_code}: {url}")
            raise
        except httpx.RequestError as e:
            if retry_count < self.max_retries:
                logger.warning(f"请求失败，重试 {retry_count + 1}/{self.max_retries}: {url}")
                await asyncio.sleep(1 * (retry_count + 1))
                return await self._download_html(url, retry_count + 1)
            raise

    async def extract_content(self, url: str) -> ExtractedContent:
        """提取网页内容"""
        logger.info(f"开始提取 URL: {url}")

        # 验证 URL 格式
        if not self._validate_url(url):
            logger.warning(f"无效的 URL 格式：{url}")
            raise ValueError(f"无效的 URL: {url}")

        # 下载网页
        html = await self._download_html(url)

        # 提取元数据
        metadata = extract_metadata(html) or {}

        # 提取正文内容
        text = extract(
            html,
            output_format="markdown",
            with_metadata=True,
            include_images=False,
            include_tables=True,
            favor_precision=True,
            config=self._config
        )

        if not text:
            logger.error(f"无法从 {url} 提取内容")
            raise ValueError(f"无法从 {url} 提取内容")

        # 处理文本
        text_content = self._strip_markdown(text)
        content_hash = hashlib.sha256(text.encode()).hexdigest()

        logger.info(f"成功提取 URL: {url}, 字数：{len(text_content)}")

        return ExtractedContent(
            url=url,
            title=metadata.get("title", "") or "",
            author=metadata.get("author"),
            date=metadata.get("date"),
            site_name=metadata.get("sitename", "") or "",
            content=text,
            text_content=text_content,
            excerpt=metadata.get("description"),
            content_hash=content_hash,
            word_count=len(text_content)
        )

    async def extract_batch(
        self,
        urls: List[str],
        concurrency: int = 5,
        rate_limit: float = 0.5
    ) -> dict:
        """批量提取网页内容"""
        semaphore = asyncio.Semaphore(concurrency)

        async def extract_with_limit(url: str):
            async with semaphore:
                await asyncio.sleep(rate_limit)
                try:
                    result = await self.extract_content(url)
                    return {"url": url, "success": True, "data": result}
                except Exception as e:
                    logger.error(f"批量提取失败 {url}: {e}")
                    return {"url": url, "success": False, "error": str(e)}

        tasks = [extract_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks)

        return {
            "total": len(urls),
            "success": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }

    async def check_url_status(self, url: str) -> dict:
        """检查 URL 可访问性"""
        try:
            if not self._validate_url(url):
                return {"accessible": False, "error": "无效的 URL 格式"}

            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml"
            }

            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                headers=headers,
                verify=False
            ) as client:
                response = await client.head(url)
                if response.status_code >= 400:
                    response = await client.get(url)
                return {
                    "accessible": response.status_code < 400,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"accessible": False, "error": str(e)}
