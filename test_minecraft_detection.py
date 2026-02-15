from minecraft.core.client import MinecraftClient
import time

print("=== 测试Minecraft进程检测 ===")

# 初始化客户端
client = MinecraftClient()

print("\n1. 检查Minecraft进程是否运行")
is_running = client.is_minecraft_running()
print(f"Minecraft进程运行状态: {is_running}")

print("\n2. 获取Minecraft进程信息")
process = client.get_minecraft_process()
if process:
    print(f"进程ID: {process.pid}")
    print(f"进程名称: {process.name()}")
else:
    print("未找到Minecraft进程")

print("\n3. 获取客户端信息")
client_info = client.get_client_info()
print(f"客户端信息: {client_info}")

print("\n4. 测试窗口聚焦")
if is_running:
    focus_success = client.focus_window()
    print(f"聚焦窗口结果: {focus_success}")
else:
    print("跳过窗口聚焦测试，因为Minecraft进程未运行")

print("\n=== 测试完成 ===")
