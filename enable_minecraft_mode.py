import requests
import json

# 启用 Minecraft 模式
def enable_minecraft_mode():
    print("启用 Minecraft 模式...")
    url = "http://localhost:48911/api/minecraft/toggle"
    data = {"enabled": True}
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

# 获取 Minecraft 模式状态
def get_minecraft_mode():
    print("获取 Minecraft 模式状态...")
    url = "http://localhost:48911/api/minecraft/mode"
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    enable_minecraft_mode()
    get_minecraft_mode()
