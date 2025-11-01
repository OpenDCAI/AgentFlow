from typing import Union, List, Dict, Any
import asyncio
from crawl4ai import AsyncWebCrawler
from urllib.parse import urlparse
import openai
import os
import time
import pdb
import bdb
import requests

# os.environ["OPENAI_API_KEY"] = ""
# os.environ["OPENAI_API_BASE"] = ""


class WebVisitTool:
    name = "web_visit"
    description = (
        "A web page visiting and content extraction tool. "
        "Supports Crawl4AI and Jina Reader API for content extraction. "
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

    def __init__(self, summary_model=None, content_limit=50000, max_tokens=1000, max_workers=5, 
                 visit_method='jina', jina_api_key=None, retry_max_attempts=3, retry_initial_delay=1.0):
        """Initialize WebVisitTool
        
        Args:
            summary_model: Model name for LLM summarization (default: None, returns raw markdown)
            content_limit: Maximum content length for LLM summarization (default: 8000)
            max_tokens: Maximum tokens for LLM response (default: 500)
            max_workers: Maximum number of concurrent workers for parallel requests (default: 5)
            visit_method: Method to visit web pages, 'crawl4ai' or 'jina' (default: 'crawl4ai')
            jina_api_key: API key for Jina Reader API (required if visit_method='jina')
        """
        self.summary_model = summary_model
        self.content_limit = content_limit
        self.max_tokens = max_tokens
        self.max_workers = max_workers
        self.visit_method = visit_method
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.retry_max_attempts = retry_max_attempts
        self.retry_initial_delay = retry_initial_delay
        
        # Validate configuration
        if self.visit_method == 'jina' and not self.jina_api_key:
            raise ValueError("Jina API key is required when visit_method='jina'. "
                           "Set JINA_API_KEY environment variable or pass jina_api_key parameter.")

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
                
                # Step 1: Get markdown content using selected method
                if self.visit_method == 'jina':
                    markdown_content = self._visit_page_with_jina(url)
                else:  # crawl4ai
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
                    if isinstance(content, str) and (content.startswith('[WebVisit] Error') or content.startswith('[WebVisit] Failed')):
                        return {
                            'url': url,
                            'success': False,
                            'summary': content
                        }
                
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

    def _visit_page_with_jina(self, url: str) -> str:
        """Visit a page using Jina Reader API and get markdown content"""
        last_error_message = None
        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                jina_url = f"https://r.jina.ai/{url}"
                headers = {
                    "Authorization": f"Bearer {self.jina_api_key}"
                }
                response = requests.get(jina_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response.text
                last_error_message = f"Jina API Status {response.status_code}, {response.text[:200]}"
            except requests.exceptions.Timeout:
                last_error_message = "Request timeout when accessing Jina API"
            except Exception as e:
                last_error_message = f"Jina API error: {str(e)}"

            if attempt < self.retry_max_attempts:
                delay = self.retry_initial_delay * (2 ** (attempt - 1))
                time.sleep(delay)

        return f"[WebVisit] Failed: {last_error_message} after {self.retry_max_attempts} attempts"

    def _summarize_with_llm(self, markdown_content: str, goal: str, url: str) -> str:
        """Summarize markdown content using LLM based on goal"""
        # Skip LLM summarization if no model is specified

        if self.summary_model is None:
            return f"Content from {url}:\n\n{markdown_content}"
            
        last_error_message = None
        # Limit content length for API
        if len(markdown_content) > self.content_limit:
            markdown_content = markdown_content[:self.content_limit] + "\n\n[Content truncated for summarization]"

        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    base_url=os.getenv("OPENAI_API_URL")
                )

                prompt = f"""Based on the goal: "{goal}"
            
Please summarize the following content from {url}, focusing only on information relevant to the goal. Keep the summary concise but informative. Only output the summary, no other text.

+++Content:
{markdown_content}

+++Summary:"""

                response = client.chat.completions.create(
                    # model=self.summary_model,
                    model='gpt-oss-20b',
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=0.3
                )

                summary = response.choices[0].message.content.strip()
                return summary
            except Exception as e:
                last_error_message = str(e)
                if attempt < self.retry_max_attempts:
                    delay = self.retry_initial_delay * (2 ** (attempt - 1))
                    time.sleep(delay)

        return f"[WebVisit] Failed: LLM summarization failed after {self.retry_max_attempts} attempts. Last error: {last_error_message}"

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
    
    print("=== Testing with Jina API ===\n")
    visit_tool_jina = WebVisitTool(
        summary_model="gpt-4o-2024-11-20",
        visit_method='jina'
    )
    
    result = visit_tool_jina.call({
        "urls": ["https://github.com/callanwu"],
        "goal": "Extract main content and purpose of the page"
    })
    print(result)
    print("-" * 50)
    
