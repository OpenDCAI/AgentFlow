# sandbox/server/backends/tools/websearch.py
"""
WebSearch API 工具 (真实实现)

提供 search 和 visit 两个工具，使用 Serper API 和 Jina Reader API
"""

import logging
import os
import json
import http.client
import asyncio
import time
from typing import Dict, Any, List, Union, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import requests
import openai

# crawl4ai 是可选依赖
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    AsyncWebCrawler = None

from . import register_api_tool
from ..error_codes import ErrorCode
from .base_tool import BaseApiTool, ToolBusinessError

logger = logging.getLogger("WebSearch")

# =============================================================================
# Infrastructure Layers (基础设施层)
# 负责：底层 API 调用、网络请求、配置管理、通用工具函数
# =============================================================================

class SerperClient:
    """负责与 Google Serper API 进行底层交互"""
    
    def __init__(self, api_key: str, retry_times: int = 5):
        self.api_key = api_key
        self.retry_times = retry_times

    def _contains_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters."""
        return any('\u4E00' <= char <= '\u9FFF' for char in text)

    def _build_search_payload(self, query: str) -> dict:
        """Build search payload based on query language."""
        if self._contains_chinese(query):
            return {
                "q": query,
                "location": "China",
                "gl": "cn",
                "hl": "zh-cn"
            }
        else:
            return {
                "q": query,
                "location": "United States",
                "gl": "us",
                "hl": "en"
            }

    def _format_search_results(self, results: dict, query: str) -> str:
        """Format search results into a readable string."""
        if "organic" not in results or not results["organic"]:
            # 这是一个业务层面的“空结果”，但在 Infra 层我们只返回标识或空
            return f"No results found for '{query}'. Try with a more general query."

        web_snippets = []
        for idx, page in enumerate(results["organic"], start=1):
            date_published = f"\nDate published: {page['date']}" if "date" in page else ""
            source = f"\nSource: {page['source']}" if "source" in page else ""
            snippet = f"\n{page['snippet']}" if "snippet" in page else ""

            formatted_result = (
                f"{idx}. [{page.get('title', 'No title')}]"
                f"({page.get('link', '#')}){date_published}{source}\n{snippet}"
            )
            formatted_result = formatted_result.replace(
                "Your browser can't play this video.", ""
            )
            web_snippets.append(formatted_result)

        return (
            f"A Google search for '{query}' found {len(web_snippets)} results:\n\n"
            "## Web Results\n" + "\n\n".join(web_snippets)
        )

    def search_single(self, query: str) -> str:
        """执行单次搜索，成功返回格式化字符串，失败抛出异常"""
        if not self.api_key:
            raise ToolBusinessError("SERPER_API_KEY not configured", ErrorCode.EXECUTION_ERROR)

        payload = json.dumps(self._build_search_payload(query))
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        conn = None
        last_error = None
        
        try:
            for attempt in range(self.retry_times):
                try:
                    if conn:
                        try: conn.close()
                        except: pass
                    
                    conn = http.client.HTTPSConnection("google.serper.dev")
                    conn.request("POST", "/search", payload, headers)
                    res = conn.getresponse()
                    
                    if res.status == 200:
                        data = res.read()
                        results = json.loads(data.decode("utf-8"))
                        return self._format_search_results(results, query)
                    
                    last_error = f"HTTP {res.status}"
                    try: res.read()
                    except: pass
                    
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Search attempt {attempt + 1}/{self.retry_times} failed: {e}")
                    if conn:
                        try: conn.close()
                        except: pass
                        conn = None
            
            raise ToolBusinessError(
                f"Failed to complete search after {self.retry_times} attempts. Last error: {last_error}",
                ErrorCode.EXECUTION_ERROR
            )

        except json.JSONDecodeError as e:
            raise ToolBusinessError(f"Failed to parse API response: {str(e)}", ErrorCode.EXECUTION_ERROR)
        except ToolBusinessError:
            raise
        except Exception as e:
            raise ToolBusinessError(f"Unexpected error during search: {str(e)}", ErrorCode.EXECUTION_ERROR)
        finally:
            if conn:
                conn.close()


class JinaClient:
    """负责与 Jina Reader API 交互"""
    def __init__(self, api_key: str, timeout: int = 30, retry_max_attempts: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.retry_max_attempts = retry_max_attempts

    def visit(self, url: str) -> str:
        """访问页面并返回 Markdown 内容，失败抛出异常"""
        last_error_message = "Unknown error"
        retry_initial_delay = 1.0

        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                jina_url = f"https://r.jina.ai/{url}"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.get(jina_url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return response.text
                
                last_error_message = f"Jina API Status {response.status_code}, {response.text[:200]}"
            except requests.exceptions.Timeout:
                last_error_message = f"Request timeout (timeout={self.timeout}s)"
            except Exception as e:
                last_error_message = f"Jina API error: {str(e)}"

            if attempt < self.retry_max_attempts:
                delay = retry_initial_delay * (2 ** (attempt - 1))
                time.sleep(delay)

        raise ToolBusinessError(f"Failed to visit {url}: {last_error_message}", ErrorCode.EXECUTION_ERROR)


class Crawl4AiClient:
    """负责与 Crawl4AI 本地库交互"""
    def __init__(self, word_count_threshold: int = 10):
        self.word_count_threshold = word_count_threshold

    async def crawl(self, url: str) -> str:
        if not CRAWL4AI_AVAILABLE or AsyncWebCrawler is None:
            raise ToolBusinessError("crawl4ai is not available", ErrorCode.EXECUTION_ERROR)
            
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                word_count_threshold=self.word_count_threshold,
                bypass_cache=True,
                include_raw_html=False
            )

            if result.success:
                return result.markdown if result.markdown else result.cleaned_html
            else:
                raise ToolBusinessError(f"Failed to crawl page: {result.error_message}", ErrorCode.EXECUTION_ERROR)


class LLMSummarizer:
    """负责使用 LLM 总结内容"""
    def __init__(self, model: str, api_key: Optional[str], api_url: Optional[str], temperature: float = 0.3):
        self.model = model
        self.api_key = api_key
        self.api_url = api_url
        self.temperature = temperature

    def summarize(self, content: str, goal: str, url: str) -> str:
        if not self.model:
            return f"Content from {url}:\n\n{content}"

        client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)
        prompt = f"""Based on the goal: "{goal}"

Please summarize the following content from {url}, focusing only on information relevant to the goal. Keep the summary concise but informative. Only output the summary, no other text.

+++Content:
{content}

+++Summary:"""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5000,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise ToolBusinessError(f"LLM summarization failed: {str(e)}", ErrorCode.EXECUTION_ERROR)


# =============================================================================
# Business Logic Layers (业务逻辑层)
# 负责：流程编排、逻辑判断、异常转换为业务码、参数校验
# =============================================================================

class SearchTool(BaseApiTool):
    def __init__(self):
        super().__init__(tool_name="search", resource_type="websearch")

    async def execute(self, query: Union[str, List[str]], **kwargs) -> Any:
        # 1. 准备配置和客户端（从实例内部获取配置）
        api_key = self.get_config('serper_api_key') or os.getenv('SERPER_API_KEY')
        if not api_key:
            raise ToolBusinessError("SERPER_API_KEY not configured", ErrorCode.EXECUTION_ERROR)
            
        max_workers = self.get_config('max_workers', 5)
        retry_times = self.get_config('retry_times', 5)
        
        client = SerperClient(api_key=api_key, retry_times=retry_times)

        # 2. 执行搜索逻辑
        if isinstance(query, str):
            return client.search_single(query)
            
        elif isinstance(query, list):
            results = []
            errors = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(client.search_single, q): q for q in query}
                for future in futures:
                    try:
                        results.append(future.result())
                    except Exception as e:
                        q = futures[future]
                        errors.append(f"Query '{q}' failed: {str(e)}")

            if not results and errors:
                raise ToolBusinessError(f"All queries failed. Errors: {'; '.join(errors)}", ErrorCode.EXECUTION_ERROR)
            
            combined_result = "\n=======\n".join(results)
            if errors:
                combined_result += "\n\nErrors encountered:\n" + "\n".join(errors)
                
            return combined_result
        else:  # type: ignore[unreachable]
            # 参数类型错误也视为执行错误（运行时保护，虽然类型注解理论上不会到达这里）
            raise ToolBusinessError("Invalid query type: must be string or list of strings", ErrorCode.EXECUTION_ERROR)


class VisitTool(BaseApiTool):
    def __init__(self):
        super().__init__(tool_name="visit", resource_type="websearch")

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    async def execute(self, urls: Union[str, List[str]], goal: str, **kwargs) -> Any:
        # 1. 参数标准化
        if isinstance(urls, str):
            urls = [urls]
        if not urls:
            raise ToolBusinessError("No URLs provided", ErrorCode.EXECUTION_ERROR)

        # 2. 准备配置和客户端（从实例内部获取配置）
        visit_method = self.get_config('visit_method', 'jina')
        max_workers = self.get_config('max_workers', 5)
        
        # Jina Client
        jina_key = self.get_config('jina_api_key') or os.getenv('JINA_API_KEY')
        jina_client = None
        if visit_method == 'jina':
            if not jina_key:
                 raise ToolBusinessError("JINA_API_KEY required for jina method", ErrorCode.EXECUTION_ERROR)
            jina_client = JinaClient(api_key=str(jina_key))
        
        # Crawl4Ai Client
        crawl_client = Crawl4AiClient() if visit_method == 'crawl4ai' else None
        
        # Summarizer
        enable_llm_summary = self.get_config('enable_llm_summary', False)
        summary_model = self.get_config('summary_model')
        summarizer = None
        if enable_llm_summary and summary_model:
            summarizer = LLMSummarizer(
                model=summary_model,
                api_key=self.get_config('openai_api_key') or os.getenv('OPENAI_API_KEY'),
                api_url=self.get_config('openai_api_url') or os.getenv('OPENAI_API_URL')
            )
            
        # 传递 content_limit 给内部函数
        content_limit = self.get_config('content_limit', 50000)

        # 3. 定义单URL处理逻辑 (包含 抓取 -> 总结)
        def process_url_sync(url):
            try:
                if not self._is_valid_url(url):
                    return {"success": False, "url": url, "error": "Invalid URL"}
                
                # Fetch
                content = ""
                if visit_method == 'jina' and jina_client:
                    content = jina_client.visit(url)
                elif visit_method == 'crawl4ai' and crawl_client:
                    # Async call in sync context hack if needed, or separate logic
                    # Since we are in ThreadPool, we need new loop for async crawl4ai
                    # For simplicity, let's assume jina is primary. 
                    # If crawl4ai is needed, we need proper async handling.
                    # Given the original code used asyncio.run for crawl4ai inside thread pool, we replicate:
                    content = asyncio.run(crawl_client.crawl(url))
                else:
                     raise Exception(f"Visit method {visit_method} not initialized correctly")

                # Summarize
                if summarizer:
                    # Truncate for safety
                    if len(content) > content_limit:
                        content = content[:content_limit] + "\n...[Truncated]"
                    content = summarizer.summarize(content, goal, url)
                else:
                    content = f"Content from {url}:\n\n{content}"

                return {"success": True, "url": url, "result": content}
            except Exception as e:
                return {"success": False, "url": url, "error": str(e)}

        # 4. 并行执行
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = executor.map(process_url_sync, urls)
            results = list(futures)

        # 5. 结果聚合
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        output = ""
        for i, res in enumerate(successful, 1):
            output += f"{i}. {res['result']}\n\n"
            
        if failed:
            output += "**Failed URLs:**\n"
            for res in failed:
                output += f"- {res['url']}: {res['error']}\n"

        if not successful:
            raise ToolBusinessError(f"All URLs failed to process. Details: {output}", ErrorCode.EXECUTION_ERROR)
        
        # Return dict to include warning if needed, or just string if BaseApiTool handles it.
        # BaseApiTool handles dicts nicely.
        return {
            "result": output.strip(),
            "warning": f"{len(failed)}/{len(urls)} URLs failed" if failed else None
        }


# =============================================================================
# Tool Registration (工具注册)
# =============================================================================

# 实例化并注册工具
# 注意：register_api_tool 装饰器会注册传入的可调用对象。
# 由于 BaseApiTool 实现了 __call__，实例本身就是可调用的。

search = register_api_tool(
    name="web:search", 
    config_key="websearch", 
    description="搜索网页 (Serper API)"
)(SearchTool())

visit = register_api_tool(
    name="web:visit", 
    config_key="websearch", 
    description="访问网页并提取内容 (Jina API)"
)(VisitTool())
