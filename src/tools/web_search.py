from typing import List
import os
import json
import http.client
from concurrent.futures import ThreadPoolExecutor

class WebSearchTool:
    """Tool for performing web searches using Google Serper API."""
    
    name = "search"
    description = (
        "Performs batched web searches: supply an array 'query'; "
        "the tool retrieves the top 10 results for each query in one call."
    )
    parameters = [
        {
            'name': 'query',
            'type': 'array',
            'array_type': 'string',
            'description': (
                'Array of query strings. Include multiple complementary '
                'search queries in a single call.'
            ),
            'required': True
        }
    ]

    def __init__(self, top_k: int = 10, retry_times: int = 5, max_workers: int = 5):
        """
        Initialize WebSearchTool with configurable parameters.
        
        Args:
            top_k: Number of top search results to return per query (default: 10)
            retry_times: Number of retry attempts per query on failure (default: 5)
        """
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            print("Warning: SERPER_API_KEY environment variable not set")
        self.top_k = top_k
        self.retry_times = retry_times
        self.max_workers = max_workers

    def call(self, params: dict, **kwargs) -> str:
        """
        Execute web search with the given parameters.
        
        Args:
            params: Dictionary containing 'query' field (str or List[str])
            **kwargs: Additional keyword arguments
            
        Returns:
            Formatted search results as a string
        """
        try:
            query = params["query"]
        except KeyError:
            return (
                "[Search] Invalid request format: Input must be a JSON object "
                "containing 'query' field"
            )
        
        if isinstance(query, str):
            # Single query
            response = self._search_with_serp(query)
        elif isinstance(query, List):
            # Multiple queries
            responses = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._search_with_serp, q) for q in query]
                for future in futures:
                    responses.append(future.result())
            response = "\n=======\n".join(responses)
        else:
            return (
                "[Search] Invalid query type: 'query' must be a string or "
                "array of strings"
            )
            
        return response

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

    def _search_with_serp(self, query: str) -> str:
        """
        Perform a single search using Google Serper API.
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results as a string
        """
        if not self.api_key:
            return "[Search] Error: SERPER_API_KEY not configured"
        
        payload = json.dumps(self._build_search_payload(query))
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        conn = None
        try:
            conn = http.client.HTTPSConnection("google.serper.dev")
            
            # Retry logic
            res = None
            for attempt in range(self.retry_times):
                try:
                    conn.request("POST", "/search", payload, headers)
                    res = conn.getresponse()
                    if res.status == 200:
                        break
                except Exception as e:
                    print(f"Search attempt {attempt + 1} failed: {e}")
                    if attempt == self.retry_times - 1:
                        return (
                            f"[Search] Error: Failed to complete search after "
                            f"{self.retry_times} attempts. Please try again later."
                        )
            
            if res is None or res.status != 200:
                return f"[Search] Error: HTTP {res.status if res else 'Unknown'}"
            
            data = res.read()
            results = json.loads(data.decode("utf-8"))
            
            return self._format_search_results(results, query)
            
        except json.JSONDecodeError as e:
            return f"[Search] Error: Failed to parse API response: {e}"
        except Exception as e:
            return f"[Search] Error: Unexpected error occurred: {e}"
        finally:
            if conn:
                conn.close()

    def _format_search_results(self, results: dict, query: str) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: API response dictionary
            query: Original search query
            
        Returns:
            Formatted results string
        """
        if "organic" not in results or not results["organic"]:
            return (
                f"No results found for '{query}'. "
                "Try with a more general query."
            )

        web_snippets = []
        for idx, page in enumerate(results["organic"], start=1):
            date_published = ""
            if "date" in page:
                date_published = f"\nDate published: {page['date']}"

            source = ""
            if "source" in page:
                source = f"\nSource: {page['source']}"

            snippet = ""
            if "snippet" in page:
                snippet = f"\n{page['snippet']}"

            formatted_result = (
                f"{idx}. [{page.get('title', 'No title')}]"
                f"({page.get('link', '#')}){date_published}{source}\n{snippet}"
            )
            # Remove common video player error messages
            formatted_result = formatted_result.replace(
                "Your browser can't play this video.", ""
            )
            web_snippets.append(formatted_result)

        content = (
            f"A Google search for '{query}' found {len(web_snippets)} results:\n\n"
            "## Web Results\n" + "\n\n".join(web_snippets)
        )
        return content


if __name__ == '__main__':
    # Test WebSearchTool
    search_tool = WebSearchTool(top_k=10)
    
    print("=== WebSearchTool Test Cases ===\n")
    
    # Test case 1: Single query
    print("Test 1: Single query")
    result = search_tool.call({
        "query": ["Python programming tutorial"]
    })
    print(result)
    print("-" * 50)
    
    # Test case 2: Multiple queries
    print("Test 2: Multiple queries")
    result = search_tool.call({
        "query": [
            "machine learning basics",
            "deep learning frameworks"
        ]
    })
    print(result)
    print("-" * 50)
