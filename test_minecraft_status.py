#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Minecraft模式状态和进程状态
"""

from brain.neuro_agent import get_or_create_neuro_agent

def test_minecraft_status():
    print("测试Minecraft模式状态...")
    
    try:
        # 获取Neuro-Sama智能体
        agent = get_or_create_neuro_agent()
        
        # 检查Minecraft模式状态
        print(f"Minecraft模式启用状态: {agent.minecraft_mode_enabled}")
        
        # 检查mindcraft-develop进程状态
        process_status = agent.mindcraft_process_manager.get_status()
        print(f"进程运行状态: {process_status.get('is_running', False)}")
        print(f"进程路径: {process_status.get('process_path', 'N/A')}")
        print(f"进程PID: {process_status.get('pid', 'N/A')}")
        print(f"运行时间: {process_status.get('uptime', 0):.2f}秒")
        
        # 尝试获取详细状态
        try:
            status = agent.get_minecraft_mode_status()
            print(f"\n详细状态:")
            print(f"启用状态: {status.get('enabled', False)}")
            print(f"最后活动时间: {status.get('last_activity_time', 0)}")
            print(f"冷却时间: {status.get('cooldown', 0)}")
        except Exception as e:
            print(f"获取详细状态失败: {e}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_minecraft_status()
