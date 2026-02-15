# 直接控制桌面Minecraft应用的脚本
import time
import os
from datetime import datetime
from minecraft.core.client import MinecraftClient
from minecraft.core.controller import MinecraftController

print("=== 直接控制桌面Minecraft应用 ===")
print(f"启动时间: {datetime.now().isoformat()}")

# 初始化Minecraft客户端和控制器
client = MinecraftClient()
controller = MinecraftController()

print("\n1. 检查Minecraft是否正在运行")
if not client.is_minecraft_running():
    print("错误: Minecraft未在运行，请先启动Minecraft游戏")
    exit(1)
else:
    print("Minecraft已在运行")

print("\n2. 聚焦到Minecraft窗口")
if client.focus_window():
    print("成功聚焦到Minecraft窗口")
else:
    print("警告: 无法聚焦到Minecraft窗口，可能需要手动聚焦")

print("\n3. 初始化控制器")
print("控制器已初始化，准备开始控制")

print("\n4. 开始控制Minecraft")
print("按 Ctrl+C 停止系统")

# 基本控制示例
try:
    while True:
        # 示例1: 向前移动2秒
        print("\n执行动作: 向前移动")
        controller.move_forward(2)
        time.sleep(1)
        
        # 示例2: 跳跃
        print("执行动作: 跳跃")
        controller.jump()
        time.sleep(1)
        
        # 示例3: 向左移动1秒
        print("执行动作: 向左移动")
        controller.move_left(1)
        time.sleep(1)
        
        # 示例4: 向右移动1秒
        print("执行动作: 向右移动")
        controller.move_right(1)
        time.sleep(1)
        
        # 示例5: 向后移动1秒
        print("执行动作: 向后移动")
        controller.move_backward(1)
        time.sleep(1)
        
        # 示例6: 环顾四周
        print("执行动作: 环顾四周")
        controller.look_around(50, 0)  # 向右看
        time.sleep(1)
        controller.look_around(-50, 0)  # 向左看
        time.sleep(1)
        
        # 示例7: 挖掘方块
        print("执行动作: 挖掘方块")
        controller.mine_block(3)
        time.sleep(1)
        
        # 示例8: 放置方块
        print("执行动作: 放置方块")
        controller.place_block()
        time.sleep(1)
        
        # 示例9: 选择快捷栏物品
        print("执行动作: 选择快捷栏物品")
        controller.select_hotbar_slot(1)
        time.sleep(1)
        
        # 等待一段时间再重复
        print("\n等待3秒后重复动作...")
        time.sleep(3)
        
        # 检查Minecraft是否仍在运行
        if not client.is_minecraft_running():
            print("\n错误: Minecraft已停止运行")
            break
            
except KeyboardInterrupt:
    print("\n正在停止系统...")
    print("系统已停止")
except Exception as e:
    print(f"\n错误: {e}")
    print("系统已停止")

print("\n=== 控制结束 ===")
