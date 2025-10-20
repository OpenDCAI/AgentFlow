from typing import Union, List, Dict, Any
import asyncio
from crawl4ai import AsyncWebCrawler
from urllib.parse import urlparse
import openai
import os
import pdb
import bdb

# os.environ["OPENAI_API_KEY"] = ""
# os.environ["OPENAI_API_BASE"] = ""


class WebVisitTool:
    name = "web_visit"
    description = (
        "A web page visiting and content extraction tool powered by Crawl4AI. "
        "Can visit web pages, extract content, perform semantic analysis, and extract specific information based on schemas or patterns."
    )
    parameters = [
        {
            'name': 'urls',
            'type': 'array',
            'array_type': 'string',
            'description': 'Array of URLs to visit and extract content from. Can process multiple URLs in parallel.',
            'required': True
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': 'The goal or purpose for content extraction. Used to guide LLM summarization of markdown content.',
            'required': True
        }
    ]

    def __init__(self, summary_model=None, content_limit=8000, max_tokens=500, max_workers=5):
        """Initialize WebVisitTool
        
        Args:
            summary_model: Model name for LLM summarization (default: None, returns raw markdown)
            content_limit: Maximum content length for LLM summarization (default: 8000)
            max_tokens: Maximum tokens for LLM response (default: 500)
            max_workers: Maximum number of concurrent workers for parallel requests (default: 5)
        """
        self.summary_model = summary_model
        self.content_limit = content_limit
        self.max_tokens = max_tokens
        self.max_workers = max_workers

    def call(self, params: Union[str, dict]) -> str:
        try:
            urls = params.get("urls")
            if not urls:
                return "[WebVisit] Error: URLs parameter is required"
            
            goal = params.get("goal")
            if not goal:
                return "[WebVisit] Error: Goal parameter is required"
            
            # Handle single URL as string
            if isinstance(urls, str):
                urls = [urls]
            elif not isinstance(urls, list):
                return "[WebVisit] Error: URLs must be a string or array of strings"
            
            # Process all URLs with goal-based summarization
            return self._crawl_and_summarize_urls(urls, goal)
                
        except Exception as e:
            return f"[WebVisit] Error: {str(e)}"

    def _crawl_and_summarize_urls(self, urls: List[str], goal: str) -> str:
        """Crawl URLs and summarize content based on goal"""
        import concurrent.futures
        
        def process_single_url(url):
            try:
                if not self._is_valid_url(url):
                    return {
                        'url': url,
                        'success': False,
                        'summary': '[WebVisit] Error: Invalid URL format'
                    }
                
                # Step 1: Get markdown content
                markdown_content = asyncio.run(self._crawl_page_for_markdown(url))
                
                if markdown_content.startswith('[WebVisit] Error') or markdown_content.startswith('[WebVisit] Failed'):
                    return {
                        'url': url,
                        'success': False,
                        'summary': markdown_content
                    }
                
                # Step 2: Summarize based on goal using LLM or return raw markdown
                if self.summary_model is None:
                    # Return raw markdown content with URL info
                    content = f"Content from {url}:\n\n{markdown_content}"
                else:
                    # Summarize using LLM
                    content = self._summarize_with_llm(markdown_content, goal, url)
                
                return {
                    'url': url,
                    'success': True,
                    'summary': content
                }
            except Exception as e:
                return {
                    'url': url,
                    'success': False,
                    'summary': f'[WebVisit] Error: {str(e)}'
                }
        
        # Process URLs in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(process_single_url, urls))
        
        # Combine summaries
        return self._combine_summaries(results)

    async def _crawl_page_for_markdown(self, url: str) -> str:
        """Crawl a single page and extract markdown content"""
        async with AsyncWebCrawler(verbose=True) as crawler:
            try:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    bypass_cache=True,
                    include_raw_html=False
                )
                
                if result.success:
                    # Return markdown content
                    return result.markdown if result.markdown else result.cleaned_html
                else:
                    return f"[WebVisit] Failed to crawl page: {result.error_message}"
                    
            except Exception as e:
                return f"[WebVisit] Crawling error: {str(e)}"

    def _summarize_with_llm(self, markdown_content: str, goal: str, url: str) -> str:
        """Summarize markdown content using LLM based on goal"""
        # Skip LLM summarization if no model is specified
        if self.summary_model is None:
            return f"Content from {url}:\n\n{markdown_content}"
            
        try:
            # Get OpenAI configuration from environment or use defaults
            
            client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE")
            )
            
            # Limit content length for API
            if len(markdown_content) > self.content_limit:
                markdown_content = markdown_content[:self.content_limit] + "\n\n[Content truncated for summarization]"
            
            prompt = f"""Based on the goal: "{goal}"
            
Please summarize the following content from {url}, focusing only on information relevant to the goal. Keep the summary concise but informative:

Content:
{markdown_content}

Summary:"""
            
            response = client.chat.completions.create(
                model=self.summary_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            # Fallback to truncated content if LLM fails
            return f"Content from {url}:\n\n{markdown_content[:2000]}...\n[Note: LLM summarization failed: {str(e)}]"

    def _combine_summaries(self, results: List[Dict]) -> str:
        """Combine multiple URL summaries"""
        if not results:
            return "[WebVisit] No URLs processed"
        
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        output = ""
        
        # Combine successful summaries
        for i, result in enumerate(successful_results, 1):
            summary = result['summary']
            output += f"{i}. {summary}\n\n"
        
        # Show failed URLs
        if failed_results:
            output += "**Failed URLs:**\n"
            for result in failed_results:
                url = result['url']
                error = result['summary'][:200] if result['summary'] else "Unknown error"
                output += f"- {url}: {error}...\n"
        
        return output.strip()

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False


if __name__ == '__main__':
    # 测试WebVisitTool工具
    os.environ["OPENAI_API_KEY"] = "sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX"
    os.environ["OPENAI_API_BASE"] = "http://123.129.219.111:3000/v1/"

    visit_tool = WebVisitTool(summary_model="gpt-4.1-2025-04-14")
    
    print("=== WebVisitTool Test Cases ===\n")
    
    # 测试用例1: 单个URL访问
    print("Test 1: Single URL visit with goal")
    result = visit_tool.call({
        "urls": ["https://httpbin.org/html"],
        "goal": "Extract any HTML content and structure information"
    })
    print(result)
    print("-" * 50)
    
    # 测试用例2: 多个URL并行访问
    print("Test 2: Multiple URLs parallel visit with specific goal")
    result = visit_tool.call({
        "urls": [
            "https://httpbin.org/html", 
            "https://example.com"
        ],
        "goal": "Find information about web services and example content"
    })
    print(result)
    print("-" * 50)
    
    # # 测试用例3: 参数验证
    # print("Test 3: Parameter validation")
    # result = visit_tool.call({})  # 缺少URLs和goal
    # print(result)
    # print("-" * 50)
    
    # # 测试用例4: 单个URL作为字符串
    # print("Test 4: Single URL as string with goal")
    # result = visit_tool.call({
    #     "urls": "https://httpbin.org/html",
    #     "goal": "Extract technical documentation or API information"
    # })
    # success = "Content from" in result or len(result) > 100
    # print("Success: Single URL processed" if success else f"Result: {result}")
    # print("-" * 50)
    
    # print("Note: For full functionality, install: pip install crawl4ai openai")