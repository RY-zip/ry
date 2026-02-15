# Minecraft控制管理器 - 让用户选择不同的控制模式
import time
import os
import subprocess
from datetime import datetime
from minecraft.core.client import MinecraftClient
from minecraft.core.controller import MinecraftController
from minecraft.mindcraft_integration import mindcraft_integration

print("=== Minecraft控制管理器 ===")
print(f"启动时间: {datetime.now().isoformat()}")

# AI控制类
class AIController:
    def __init__(self):
        self.client = MinecraftClient()
        self.controller = MinecraftController()
        self.running = False
    
    def start_ai_control(self):
        """开始AI控制"""
        self.running = True
        print("\n=== AI控制已启动 ===")
        print("AI正在控制Minecraft...")
        
        try:
            while self.running:
                # AI决策逻辑 - 这里可以根据需要扩展
                # 示例：基本的探索行为
                print("AI正在探索周围环境...")
                
                # 向前移动
                print("AI执行动作: 向前移动")
                self.controller.move_forward(2)
                time.sleep(1)
                
                # 跳跃
                print("AI执行动作: 跳跃")
                self.controller.jump()
                time.sleep(1)
                
                # 环顾四周
                print("AI执行动作: 环顾四周")
                self.controller.look_around(30, 0)  # 向右看
                time.sleep(1)
                self.controller.look_around(-30, 0)  # 向左看
                time.sleep(1)
                
                # 挖掘方块
                print("AI执行动作: 挖掘方块")
                self.controller.mine_block(2)
                time.sleep(1)
                
                # 放置方块
                print("AI执行动作: 放置方块")
                self.controller.place_block()
                time.sleep(1)
                
                # 随机选择一个方向移动
                import random
                direction = random.choice(['forward', 'left', 'right'])
                print(f"AI执行动作: 随机移动 ({direction})")
                
                if direction == 'forward':
                    self.controller.move_forward(1)
                elif direction == 'left':
                    self.controller.move_left(1)
                elif direction == 'right':
                    self.controller.move_right(1)
                
                time.sleep(2)
                
                # 检查Minecraft是否仍在运行
                if not self.client.is_minecraft_running():
                    print("\n错误: Minecraft已停止运行")
                    self.running = False
                    break
                    
        except KeyboardInterrupt:
            print("\nAI控制已停止")
        except Exception as e:
            print(f"\nAI控制出错: {e}")
        finally:
            self.running = False
    
    def stop_ai_control(self):
        """停止AI控制"""
        self.running = False

# 主菜单
while True:
    print("\n请选择控制模式:")
    print("1. AI直接控制桌面Minecraft应用")
    print("2. 通过mindcraft-develop AI控制")
    print("3. 退出")
    
    choice = input("请输入选择 (1-3): ")
    
    if choice == "1":
        print("\n=== 启动AI直接控制模式 ===")
        print("此模式将让AI直接控制桌面Minecraft应用，无需浏览器")
        print("正在初始化AI控制器...")
        
        # 检查Minecraft是否正在运行
        client = MinecraftClient()
        if not client.is_minecraft_running():
            print("错误: Minecraft未在运行，请先启动Minecraft游戏")
            continue
        
        # 聚焦到Minecraft窗口
        if client.focus_window():
            print("成功聚焦到Minecraft窗口")
        else:
            print("警告: 无法聚焦到Minecraft窗口，可能需要手动聚焦")
        
        # 启动AI控制
        ai_controller = AIController()
        ai_controller.start_ai_control()
        
    elif choice == "2":
        print("\n=== 启动mindcraft-develop AI控制模式 ===")
        print("此模式通过mindcraft-develop AI控制，需要浏览器访问控制界面")
        print("正在启动mindcraft-develop...")
        
        # 使用现有的mindcraft_integration模块启动
        try:
            from minecraft.mindcraft_integration import mindcraft_integration
            
            if mindcraft_integration.start_mindcraft():
                print("\nmindcraft-develop AI控制已启动")
                print(f"控制界面可访问: http://localhost:{mindcraft_integration.port}")
                print(f"机器人视角可访问: http://localhost:{mindcraft_integration.bot_view_port}")
                print("\n按 Enter 停止系统")
                input()
                mindcraft_integration.stop_mindcraft()
            else:
                print("错误: 无法启动mindcraft-develop")
        except Exception as e:
            print(f"错误: {e}")
        
    elif choice == "3":
        print("\n退出系统...")
        break
    
    else:
        print("无效选择，请重新输入")

print("\n=== 系统已退出 ===")
