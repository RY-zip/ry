from minecraft.mindcraft_integration import mindcraft_integration
from minecraft.core.client import MinecraftClient
import time
from datetime import datetime

print("=== 使用mindcraft-develop控制Minecraft ===")
print(f"启动时间: {datetime.now().isoformat()}")

# 1. 检查mindcraft-develop状态
print("\n1. 检查mindcraft-develop状态")
mindcraft_status = mindcraft_integration.get_status()
print(f"mindcraft-develop状态: {mindcraft_status}")

# 2. 检查Minecraft客户端状态
print("\n2. 检查Minecraft客户端状态")
client = MinecraftClient()
is_minecraft_running = client.is_minecraft_running()
print(f"Minecraft客户端运行状态: {is_minecraft_running}")

if is_minecraft_running:
    process = client.get_minecraft_process()
    print(f"进程ID: {process.pid}")
    print(f"进程名称: {process.name()}")

# 3. 启动mindcraft-develop（如果未运行）
print("\n3. 启动mindcraft-develop")
if not mindcraft_status['running']:
    print("mindcraft-develop未运行，正在启动...")
    start_success = mindcraft_integration.start_mindcraft()
    print(f"启动结果: {start_success}")
else:
    print("mindcraft-develop已经在运行")

# 4. 检查启动后的状态
print("\n4. 检查启动后的状态")
mindcraft_status = mindcraft_integration.get_status()
print(f"启动后状态: {mindcraft_status}")

if mindcraft_status['running']:
    print("\n5. mindcraft-develop启动成功！")
    print("\n系统现在通过mindcraft-develop控制Minecraft")
    print("mindcraft-develop具有以下功能:")
    print("- 智能移动和视角控制")
    print("- 自动探索和资源收集")
    print("- 背包管理和物品合成")
    print("- 更高级的游戏交互能力")
    print("\n控制界面可访问: http://localhost:8080")
    print("机器人视角可访问: http://localhost:3000")
else:
    print("\n5. mindcraft-develop启动失败")
    print("将使用基本控制系统")

print("\n=== 系统启动完成 ===")
print("按 Ctrl+C 停止系统")

# 保持系统运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n正在停止系统...")
    if mindcraft_status['running']:
        mindcraft_integration.stop_mindcraft()
    print("系统已停止")
