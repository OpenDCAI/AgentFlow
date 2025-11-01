from openai import OpenAI
from typing import List, Optional, Dict, Any, Union
import time
import threading
import requests

class RequestCounter:
    """线程安全的请求计数器"""
    
    def __init__(self):
        self._counter = 0
        self._lock = threading.Lock()
    
    def get_next_id(self) -> int:
        """获取下一个请求ID"""
        with self._lock:
            self._counter += 1
            return self._counter

def call_openrouter(messages: List[Dict], temperature: float = 0.6, 
                        top_p: float = 0.95, timeout: int = 120) -> Optional[str]:
    """调用OpenRouter服务"""

    request_counter=RequestCounter()
    request_id = request_counter.get_next_id()
        
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p
    }
        
    openrouter_key = "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"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        }
        
    start_time = time.time()
        
    try:
        # print(f"OpenRouter请求#{request_id} 开始发送...")
            
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=timeout
        )

        print(response)
            
        elapsed_time = time.time() - start_time
            
        if response.status_code != 200:
            print(f"OpenRouter请求#{request_id} 失败: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
            
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']
            print(f"OpenRouter请求#{request_id} 成功 ({elapsed_time:.2f}s)")
            # print(f"回复内容: {content[:150]}...")
            # print("-" * 80)
            return content
        else:
            print(f"OpenRouter请求#{request_id} 响应格式异常: {result}")
            return None
                
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"OpenRouter请求#{request_id} 超时 ({elapsed_time:.2f}s)")
        return None
    except requests.exceptions.RequestException as e:
        elapsed_time = time.time() - start_time
        print(f"OpenRouter请求#{request_id} 网络异常 ({elapsed_time:.2f}s): {e}")
        return None
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"OpenRouter请求#{request_id} 其他异常 ({elapsed_time:.2f}s): {e}")
        return None

print(call_openrouter([{"role": "user", "content": "你好"}]))