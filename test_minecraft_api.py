import requests
import json

# 测试获取Minecraft模式状态
print("测试获取Minecraft模式状态...")
try:
    response = requests.get("http://localhost:48911/api/minecraft/mode")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {str(e)}")

# 测试启用Minecraft模式
print("\n测试启用Minecraft模式...")
try:
    payload = {"enabled": True}
    response = requests.post("http://localhost:48911/api/minecraft/toggle", json=payload)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {str(e)}")

# 再次获取状态确认
print("\n再次获取Minecraft模式状态...")
try:
    response = requests.get("http://localhost:48911/api/minecraft/mode")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {str(e)}")

# 最后获取状态确认
print("\n最后获取Minecraft模式状态...")
try:
    response = requests.get("http://localhost:48911/api/minecraft/mode")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {str(e)}")
