from typing import Union, List, Dict, Any
import asyncio
# from crawl4ai import AsyncWebCrawler
from urllib.parse import urlparse
import openai
import os
import time
import requests
import tiktoken
import json

EXTRACTOR_PROMPT = """Please process the following webpage content and user goal to extract relevant information:

## **Webpage Content** 
{webpage_content}

## **User Goal**
{goal}

## **Task Guidelines**
1. **Content Scanning for Rational**: Locate the **specific sections/data** directly related to the user's goal within the webpage content
2. **Key Extraction for Evidence**: Identify and extract the **most relevant information** from the content, you never miss any important information, output the **full original context** of the content as far as possible, it can be more than three paragraphs.
3. **Summary Output for Summary**: Organize into a concise paragraph with logical flow, prioritizing clarity and judge the contribution of the information to the goal.

**Final Output Format using JSON format has "rational", "evidence", "summary" fields**
"""

def truncate_to_tokens(text: str, max_tokens: int = 95000) -> str:
    encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(text)
    if len(tokens) <= max_tokens:
        return text
    
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)


class WebVisitTool:
    name = "web_visit"
    description = 'Visit webpage(s) and return the summary of the content.'
    parameters = [
        {
            'name': 'url',
            'type': 'string',
            'description': 'The URL(s) of the webpage(s) to visit. Can be a single URL or an array of URLs.',
            'required': True
        },
        {
            'name': 'goal',
            'type': 'string',
            'description': 'The goal of the visit for webpage(s).',
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
        """
        self.summary_model = summary_model
        self.content_limit = content_limit
        self.max_tokens = max_tokens
        self.max_workers = max_workers
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.retry_max_attempts = retry_max_attempts
        self.retry_initial_delay = retry_initial_delay

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            url = params["url"]
            goal = params["goal"]
        except:
            return "[Visit] Invalid request format: Input must be a JSON object containing 'url' and 'goal' fields"

        start_time = time.time()
        
        # Create log folder if it doesn't exist
        log_folder = "log"
        os.makedirs(log_folder, exist_ok=True)

        if isinstance(url, str):
            response = self.readpage_jina(url, goal)
        else:
            response = []
            assert isinstance(url, List)
            start_time = time.time()
            for u in url: 
                if time.time() - start_time > 900:
                    cur_response = "The useful information in {url} for user goal {goal} as follows: \n\n".format(url=url, goal=goal)
                    cur_response += "Evidence in page: \n" + "The provided webpage content could not be accessed. Please check the URL or file format." + "\n\n"
                    cur_response += "Summary: \n" + "The webpage content could not be processed, and therefore, no information is available." + "\n\n"
                else:
                    try:
                        cur_response = self.readpage_jina(u, goal)
                    except Exception as e:
                        cur_response = f"Error fetching {u}: {str(e)}"
                response.append(cur_response)
            response = "\n=======\n".join(response)
        
        print(f'Summary Length {len(response)}; Summary Content {response}')
        return response.strip()
        
    def call_server(self, msgs, max_retries=2):
        client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", "")),
        )
        for attempt in range(max_retries):
            try:
                chat_response = client.chat.completions.create(
                    model=self.summary_model,
                    messages=msgs,
                    temperature=0.7
                )
                content = chat_response.choices[0].message.content
                if content:
                    try:
                        json.loads(content)
                    except:
                        # extract json from string 
                        left = content.find('{')
                        right = content.rfind('}') 
                        if left != -1 and right != -1 and left <= right: 
                            content = content[left:right+1]
                    return content
            except Exception as e:
                # print(e)
                if attempt == (max_retries - 1):
                    return ""
                continue


    def jina_readpage(self, url: str) -> str:
        """
        Read webpage content using Jina service.
        
        Args:
            url: The URL to read
            goal: The goal/purpose of reading the page
            
        Returns:
            str: The webpage content or error message
        """
        max_retries = 3
        timeout = 50
        
        for attempt in range(max_retries):
            headers = {
                "Authorization": f"Bearer {self.jina_api_key}",
            }
            try:
                response = requests.get(
                    f"https://r.jina.ai/{url}",
                    headers=headers,
                    timeout=timeout
                )
                if response.status_code == 200:
                    webpage_content = response.text
                    return webpage_content
                else:
                    print(response.text)
                    raise ValueError("jina readpage error")
            except Exception as e:
                time.sleep(0.5)
                if attempt == max_retries - 1:
                    return "[visit] Failed to read page."
                
        return "[visit] Failed to read page."

    def html_readpage_jina(self, url: str) -> str:
        max_attempts = 8
        for attempt in range(max_attempts):
            content = self.jina_readpage(url)
            service = "jina"     
            print(service)
            if content and not content.startswith("[visit] Failed to read page.") and content != "[visit] Empty content." and not content.startswith("[document_parser]"):
                return content
        return "[visit] Failed to read page."

    def readpage_jina(self, url: str, goal: str) -> str:
        """
        Attempt to read webpage content by alternating between jina and aidata services.
        
        Args:
            url: The URL to read
            goal: The goal/purpose of reading the page
            
        Returns:
            str: The webpage content or error message
        """
   
        summary_page_func = self.call_server
        max_retries = int(os.getenv('VISIT_SERVER_MAX_RETRIES', 1))

        content = self.html_readpage_jina(url)
        if content and not content.startswith("[visit] Failed to read page.") and content != "[visit] Empty content." and not content.startswith("[document_parser]"):
            # Store original content for retry truncations
            original_content = truncate_to_tokens(content, max_tokens=95000)
            content = original_content
            messages = [{"role":"user","content": EXTRACTOR_PROMPT.format(webpage_content=content, goal=goal)}]
            raw = summary_page_func(messages, max_retries=max_retries)
            print(raw)
            exit()
            summary_retries = 3
            # Check if raw is valid and has sufficient length
            while (not raw or not isinstance(raw, str) or len(raw) < 1000) and summary_retries > 0:
                truncate_length = int(0.7 * len(original_content)) if summary_retries > 1 else 25000
                status_msg = (
                    f"[visit] Summary url[{url}] " 
                    f"attempt {3 - summary_retries + 1}/3, "
                    f"content length: {len(original_content)}, "
                    f"truncating to {truncate_length} chars"
                )
                print(status_msg)
                # Truncate from original content, not the already-truncated content
                content = original_content[:truncate_length]
                extraction_prompt = EXTRACTOR_PROMPT.format(
                    webpage_content=content,
                    goal=goal
                )
                messages = [{"role": "user", "content": extraction_prompt}]
                raw = summary_page_func(messages, max_retries=max_retries)
                print(raw)
                summary_retries -= 1

            # If still no valid response after all retries, try final truncation
            if (not raw or not isinstance(raw, str) or len(raw) < 1000) and summary_retries == 0:
                print(f"[visit] Summary url[{url}] failed after 3 attempts, final truncation to 25000 chars")
                content = original_content[:25000]
                extraction_prompt = EXTRACTOR_PROMPT.format(
                    webpage_content=content,
                    goal=goal
                )
                messages = [{"role": "user", "content": extraction_prompt}]
                raw = summary_page_func(messages, max_retries=max_retries)
                print(raw)

            # Parse JSON response
            parse_retry_times = 0
            parsed_raw = None
            if isinstance(raw, str):
                raw = raw.replace("```json", "").replace("```", "").strip()
            while parse_retry_times < 3:
                try:
                    if raw and isinstance(raw, str):
                        parsed_raw = json.loads(raw)
                        break
                except Exception as e:
                    if parse_retry_times < 2:  # Only retry if we have attempts left
                        raw = summary_page_func(messages, max_retries=max_retries)
                        if isinstance(raw, str):
                            raw = raw.replace("```json", "").replace("```", "").strip()
                    parse_retry_times += 1
            
            if parse_retry_times >= 3 or parsed_raw is None:
                useful_information = "The useful information in {url} for user goal {goal} as follows: \n\n".format(url=url, goal=goal)
                useful_information += "Evidence in page: \n" + "The provided webpage content could not be accessed. Please check the URL or file format." + "\n\n"
                useful_information += "Summary: \n" + "The webpage content could not be processed, and therefore, no information is available." + "\n\n"
            else:
                useful_information = "The useful information in {url} for user goal {goal} as follows: \n\n".format(url=url, goal=goal)
                useful_information += "Evidence in page: \n" + str(parsed_raw.get("evidence", "")) + "\n\n"
                useful_information += "Summary: \n" + str(parsed_raw.get("summary", "")) + "\n\n"

            if len(useful_information) < 10:
                print("[visit] Could not generate valid summary after maximum retries")
                useful_information = "[visit] Failed to read page"
            
            return useful_information

        # If no valid content was obtained after all retries
        else:
            useful_information = "The useful information in {url} for user goal {goal} as follows: \n\n".format(url=url, goal=goal)
            useful_information += "Evidence in page: \n" + "The provided webpage content could not be accessed. Please check the URL or file format." + "\n\n"
            useful_information += "Summary: \n" + "The webpage content could not be processed, and therefore, no information is available." + "\n\n"
            return useful_information


if __name__ == '__main__':
    # 测试WebVisitTool工具
    os.environ["OPENAI_API_KEY"] = "sk-YJkQxboKmL0IBC1M0zOzZbVaVZifM5QvN4mLAtSLZ1V4yEDX"
    os.environ["OPENAI_API_URL"] = "http://123.129.219.111:3000/v1/"
    os.environ["JINA_API_KEY"] = "jina_0349f5f308d54b01ade1fa24842e044dGGlzH9kzcQxCdlNltX-3Na7EKSiW"

    print("=== Testing with Jina API ===\n")
    visit_tool_jina = WebVisitTool(
        summary_model="gpt-4o-2024-11-20"
    )
    
    result = visit_tool_jina.call({
        "url": "https://github.com/callanwu",
        "goal": "Extract main content and purpose of the page"
    })
    print(result)
    print("-" * 50)
