from typing import Union, List, Dict, Any
import requests
import os
import pdb
import bdb
import time
import random

# os.environ['SERPER_API_KEY'] = ''

class ImageSearchTool:
    name = "image_search"
    description = (
        "A reverse image search tool powered by Serper API that can search the internet for visually similar images and related webpages. "
        "Provide an image URL, and this tool will find the top-k most visually relevant webpages, returning thumbnails and titles."
    )
    parameters = [
        {
            'name': 'image_urls',
            'type': 'array',
            'array_type': 'string',
            'description': 'Array of image URLs to search. Each URL will be processed to find visually similar content.',
            'required': True
        }
    ]

    def __init__(self, top_k=10, max_workers=5, retry_times=5, retry_backoff=1.0):
        """
        Initialize ImageSearchTool with configurable parameters

        Args:
            top_k: Number of top search results to return per image query (default: 10)
            max_workers: Maximum number of concurrent workers for parallel requests (default: 5)
            retry_times: Number of retry attempts per query on failure (default: 5)
            retry_backoff: Base seconds for exponential backoff between retries (default: 1.0)
        """
        self.api_key = os.getenv('SERPER_API_KEY')
        if not self.api_key:
            print("Warning: SERPER_API_KEY environment variable not set")
        self.top_k = min(top_k, 10)
        self.max_workers = max_workers
        self.retry_times = max(1, int(retry_times))
        self.retry_backoff = float(retry_backoff)

    def call(self, params: Union[str, dict]) -> str:
        try:
            image_urls = params.get("image_urls")
            if not image_urls:
                return "[ImageSearch] Error: image_urls parameter is required"

            # Handle single URL as string
            if isinstance(image_urls, str):
                image_urls = [image_urls]
            elif not isinstance(image_urls, list):
                return "[ImageSearch] Error: image_urls must be a string or array of strings"

            # Validate URLs
            for url in image_urls:
                if not isinstance(url, str) or not url.strip():
                    return "[ImageSearch] Error: All image URLs must be non-empty strings"

            if not self.api_key:
                return "[ImageSearch] Error: SERPER_API_KEY not configured"

            # Process all image queries in parallel
            return self._search_images(image_urls)

        except Exception as e:
            return f"[ImageSearch] Error: {str(e)}"

    def _search_images(self, image_urls: List[str]) -> str:
        """Search multiple images in parallel"""
        import concurrent.futures

        def search_single_image(image_url):
            last_error = None
            for attempt in range(1, self.retry_times + 1):
                try:
                    # Make API request to Serper Lens API
                    url = "https://google.serper.dev/lens"
                    headers = {
                        'X-API-KEY': self.api_key,
                        'Content-Type': 'application/json'
                    }

                    payload = {
                        'url': image_url
                    }

                    response = requests.post(url, headers=headers, json=payload, timeout=30)

                    status_code = response.status_code
                    if 200 <= status_code < 300:
                        try:
                            data = response.json()
                        except Exception:
                            data = {}
                        results = self._format_results(data, image_url)
                        return {
                            'image_url': image_url,
                            'success': True,
                            'results': results
                        }

                    # build error message
                    try:
                        err_json = response.json()
                        err_detail = err_json.get('message') if isinstance(err_json, dict) else err_json
                    except Exception:
                        err_detail = response.text or ''
                    err_detail = str(err_detail)[:1000] if err_detail else f"HTTP {status_code}"
                    err_msg = f"HTTP {status_code}: {err_detail}"

                    last_error = err_msg
                    if attempt < self.retry_times:
                        sleep_seconds = self.retry_backoff * (2 ** (attempt - 1))
                        sleep_seconds += random.uniform(0, 0.25 * max(self.retry_backoff, 0.001))
                        time.sleep(sleep_seconds)
                        continue

                    # Non-retriable or retries exhausted
                    return {
                        'image_url': image_url,
                        'success': False,
                        'results': err_msg
                    }

                except requests.exceptions.RequestException as e:
                    # Network/timeout errors -> retriable
                    last_error = e
                    if attempt < self.retry_times:
                        sleep_seconds = self.retry_backoff * (2 ** (attempt - 1))
                        sleep_seconds += random.uniform(0, 0.25 * max(self.retry_backoff, 0.001))
                        time.sleep(sleep_seconds)
                        continue
                    return {
                        'image_url': image_url,
                        'success': False,
                        'results': str(last_error)
                    }
                except Exception as e:
                    if isinstance(e, bdb.BdbQuit):
                        raise e
                    last_error = e
                    if attempt < self.retry_times:
                        sleep_seconds = self.retry_backoff * (2 ** (attempt - 1))
                        sleep_seconds += random.uniform(0, 0.25 * max(self.retry_backoff, 0.001))
                        time.sleep(sleep_seconds)
                        continue
                    return {
                        'image_url': image_url,
                        'success': False,
                        'results': str(last_error)
                    }

        # Process image queries in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            search_results = list(executor.map(search_single_image, image_urls))

        # Format combined results as string
        return self._format_combined_results(search_results)

    def _format_results(self, data: Dict[str, Any], image_url: str) -> List[Dict[str, str]]:
        """Format the reverse image search results as a list of dictionaries"""

        results = []
        
        # Extract visual matches (similar images found on web)
        visual_matches = data.get('organic', [])
        for idx, match in enumerate(visual_matches[:self.top_k]):
            result_item = {
                'image_url': image_url,
                'rank': idx + 1,
                'title': match.get('title', ''),
                'link': match.get('link', ''),
                'source': match.get('source', ''),
                'thumbnailUrl': match.get('thumbnailUrl', ''),
                'imageUrl': match.get('imageUrl', '')
            }
            results.append(result_item)

        # Also check for knowledge graph results (often provides context)
        knowledge_graph = data.get('knowledgeGraph', {})
        if knowledge_graph:
            kg_result = {
                'image_url': image_url,
                'rank': 0,  # Priority result
                'title': knowledge_graph.get('title', ''),
                'link': knowledge_graph.get('website', ''),
                'source': 'Knowledge Graph',
                'thumbnail': knowledge_graph.get('imageUrl', ''),
                'snippet': knowledge_graph.get('description', '')
            }
            # Insert knowledge graph at the beginning if it has content
            if kg_result['title'] or kg_result['snippet']:
                results.insert(0, kg_result)

        return results

    def _format_combined_results(self, search_results: List[Dict]) -> str:
        """Format all image search results into a single string with thumbnails and titles"""
        if not search_results:
            return "[ImageSearch] No image queries processed"

        output = ""
        successful_queries = [r for r in search_results if r['success']]

        if successful_queries:
            output += "[ImageSearch] Reverse image search results:\n\n"

        # Process each image query
        for query_idx, query_result in enumerate(successful_queries, 1):
            image_url = query_result.get('image_url', '')
            results = query_result.get('results', [])

            if results:
                output += f"=== Results for image: {image_url} ===\n\n"

                for item in results:
                    rank = item.get('rank', '')
                    title = item.get('title', 'No title')
                    link = item.get('link', '')
                    source = item.get('source', '')
                    thumbnail = item.get('thumbnail', '')
                    snippet = item.get('snippet', '')

                    if rank == 0:
                        output += f"[Knowledge Graph Result]\n"
                    else:
                        output += f"{rank}. "

                    output += f"Title: {title}\n"

                    if link:
                        output += f"URL: {link}\n"

                    if source:
                        output += f"Source: {source}\n"

                    if thumbnail:
                        output += f"Thumbnail: {thumbnail}\n"

                    if snippet:
                        output += f"Description: {snippet}\n"

                    output += "\n"

                # Add separator between different image queries
                if query_idx < len(successful_queries):
                    output += "-" * 60 + "\n\n"

        # If there are no successful formatted results, include failure reasons
        if not output.strip():
            failed_queries = [r for r in search_results if not r.get('success')]
            if failed_queries:
                output = "[ImageSearch] Failed queries:\n"
                for fail in failed_queries:
                    image_url = fail.get('image_url', '')
                    reason = str(fail.get('results', 'Unknown error'))
                    output += f"Image URL: {image_url}\nError: {reason}\n\n"
            # If still empty for any reason, provide a generic message
            if not output.strip():
                output = "[ImageSearch] Search failed with no results or error details"

        return output


if __name__ == '__main__':
    # Test ImageSearchTool
    search_tool = ImageSearchTool(top_k=5)

    print("=== ImageSearchTool Test Cases ===\n")

    # Test case 1: Single image URL
    print("Test 1: Single image reverse search")
    result = search_tool.call({
        "image_urls": ["https://youke1.picui.cn/s1/2025/10/27/68ff3e07492f5.png"]
    })
    print(result)
    print("-" * 50)

    # Test case 2: Multiple image URLs parallel search
    print("\nTest 2: Multiple images parallel search")
    result = search_tool.call({
        "image_urls": [
            "https://youke1.picui.cn/s1/2025/10/27/68ff3e07492f5.png",
            "https://youke1.picui.cn/s1/2025/10/27/68ff606d337a3.png"
        ]
    })
    print(result)
    print("-" * 50)

    # Test case 3: Parameter validation
    print("\nTest 3: Parameter validation")
    result = search_tool.call({})  # Missing image_urls
    print(result)

    print(f"\nTool configuration: top_k={search_tool.top_k}, max_workers={search_tool.max_workers}")
