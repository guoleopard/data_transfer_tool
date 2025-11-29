import requests

# 测试GET请求
response = requests.get('http://localhost:8100/api/data_sources/')

print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")

# 如果响应状态码是200，尝试解析JSON
if response.status_code == 200:
    try:
        data = response.json()
        print(f"解析后的JSON数据: {data}")
    except Exception as e:
        print(f"解析JSON失败: {e}")
