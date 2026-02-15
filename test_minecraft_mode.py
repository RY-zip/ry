import requests
import json

# 测试获取 Minecraft 模式状态
def test_get_mode():
    print("测试获取 Minecraft 模式状态...")
    url = "http://localhost:48912/api/minecraft/mode"
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

# 测试启用 Minecraft 模式
def test_enable_mode():
    print("测试启用 Minecraft 模式...")
    url = "http://localhost:48912/api/minecraft/toggle"
    data = {"enabled": True}
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

# 测试禁用 Minecraft 模式
def test_disable_mode():
    print("测试禁用 Minecraft 模式...")
    url = "http://localhost:48912/api/minecraft/toggle"
    data = {"enabled": False}
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    test_get_mode()
    test_enable_mode()
    test_get_mode()
    test_disable_mode()
    test_get_mode()
