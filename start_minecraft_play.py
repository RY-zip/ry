from minecraft.task_manager import task_manager
from minecraft.core.client import MinecraftClient
from minecraft.core.controller import MinecraftController
import time
from datetime import datetime

print("=== Minecraft AI游玩系统启动 ===")
print(f"启动时间: {datetime.now().isoformat()}")

# 1. 初始化客户端和控制器
client = MinecraftClient()
controller = MinecraftController()

print("\n2. 检查Minecraft客户端状态")
is_running = client.is_minecraft_running()
print(f"Minecraft客户端运行状态: {is_running}")

if not is_running:
    print("警告: 未检测到Minecraft客户端运行，请先启动Minecraft游戏")
    print("系统将继续启动，但无法执行实际控制操作")
else:
    print("\n3. 聚焦到Minecraft窗口")
    focus_success = client.focus_window()
    print(f"聚焦窗口结果: {focus_success}")

print("\n4. 启动任务管理器")
task_manager.start()
print("任务管理器启动成功")

print("\n5. 执行初始游戏控制测试")
print("测试基本动作...")

# 测试基本动作
if is_running:
    try:
        print("\n测试向前移动...")
        controller.move_forward(1)
        time.sleep(0.5)
        
        print("测试跳跃...")
        controller.jump()
        time.sleep(0.5)
        
        print("测试环顾四周...")
        controller.look_around(30, 0)
        time.sleep(0.5)
        controller.look_around(-30, 0)
        time.sleep(0.5)
        
        print("测试选择快捷栏...")
        controller.select_hotbar_slot(1)
        time.sleep(0.5)
        
        print("基本动作测试完成!")
    
    except Exception as e:
        print(f"测试过程中出错: {e}")
else:
    print("跳过动作测试，因为Minecraft客户端未运行")

print("\n6. 添加游戏任务")
print("添加探索任务...")
task_manager.add_exploration_task(duration=60)

print("添加资源收集任务...")
task_manager.add_gathering_task("石头", duration=30)

print("\n7. 系统状态")
status = task_manager.get_task_status()
print(f"任务管理器状态: {status}")

print("\n=== Minecraft AI游玩系统启动完成 ===")
print("系统现在正在运行，将自动执行探索和资源收集任务")
print("按 Ctrl+C 停止系统")

# 保持系统运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n正在停止系统...")
    task_manager.stop()
    print("系统已停止")
