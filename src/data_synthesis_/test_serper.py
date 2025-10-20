import requests
import json

# 你的 Serper API 密钥
API_KEY = "YOUR_API_KEY"

# Serper 的搜索端点
SEARCH_ENDPOINT = "https://google.serper.dev/search"

# 要搜索的查询
search_query = "特斯拉最新消息"

# 准备请求数据 (JSON body)
payload = json.dumps({
  "q": search_query
})

# 准备请求头
headers = {
  'X-API-KEY': "ba84d16985e52118b112103fd7c97f5dad1db3f4",
  'Content-Type': 'application/json'
}

print(f"正在搜索: {search_query}...")

try:
    # 发送 POST 请求
    response = requests.post(SEARCH_ENDPOINT, headers=headers, data=payload)

    # 检查响应状态
    response.raise_for_status() # 如果请求失败 (例如 401, 403, 500), 会抛出异常

    # 解析 JSON 响应
    search_results = response.json()

    # 打印格式化后的结果 (美化输出)
    print(json.dumps(search_results, indent=2, ensure_ascii=False))

    # (可选) 打印第一个有机结果的标题
    if 'organic' in search_results and len(search_results['organic']) > 0:
        print("\n--- 第一个结果 ---")
        print(f"标题: {search_results['organic'][0]['title']}")
        print(f"链接: {search_results['organic'][0]['link']}")

except requests.exceptions.HTTPError as errh:
    print(f"Http 错误: {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"连接错误: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"超时错误: {errt}")
except requests.exceptions.RequestException as err:
    print(f"请求异常: {err}")