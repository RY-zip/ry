#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Minecraft客户端API模块功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.minecraft_api import get_or_create_minecraft_api, test_minecraft_api_connection


def test_minecraft_client_api():
    """测试Minecraft客户端API模块功能"""
    print("=== 测试Minecraft客户端API模块功能 ===")
    
    # 测试1: 测试API连接
    print("\n1. 测试API连接:")
    connection_success = test_minecraft_api_connection()
    print(f"API连接状态: {connection_success}")
    
    # 获取API实例
    minecraft_api = get_or_create_minecraft_api()
    print(f"\n使用的API类型: {type(minecraft_api).__name__}")
    
    # 测试2: 获取玩家健康值
    print("\n2. 测试获取玩家健康值:")
    if hasattr(minecraft_api, 'get_player_health'):
        health = minecraft_api.get_player_health()
        print(f"玩家健康值: {health}")
    else:
        print("当前API不支持获取玩家健康值")
    
    # 测试3: 获取玩家饥饿值
    print("\n3. 测试获取玩家饥饿值:")
    if hasattr(minecraft_api, 'get_player_hunger'):
        hunger = minecraft_api.get_player_hunger()
        print(f"玩家饥饿值: {hunger}")
    else:
        print("当前API不支持获取玩家饥饿值")
    
    # 测试4: 获取世界时间
    print("\n4. 测试获取世界时间:")
    if hasattr(minecraft_api, 'get_world_time'):
        world_time = minecraft_api.get_world_time()
        print(f"世界时间: {world_time}")
        # 从世界时间判断是白天还是黑夜
        time_of_day = "day" if 0 < world_time < 12000 else "night"
        print(f"时间类型: {time_of_day}")
    else:
        print("当前API不支持获取世界时间")
    
    # 测试5: 获取天气
    print("\n5. 测试获取天气:")
    if hasattr(minecraft_api, 'get_weather'):
        weather = minecraft_api.get_weather()
        print(f"当前天气: {weather}")
    else:
        print("当前API不支持获取天气")
    
    # 测试6: 检测方块
    print("\n6. 测试检测方块:")
    if hasattr(minecraft_api, 'detect_blocks'):
        blocks = minecraft_api.detect_blocks()
        print(f"方块检测结果: {blocks}")
    else:
        print("当前API不支持检测方块")
    
    # 测试7: 发送命令（仅Rcon支持）
    print("\n7. 测试发送命令:")
    if hasattr(minecraft_api, 'send_command'):
        test_command = "say Hello from Neuro-Sama!"
        try:
            response = minecraft_api.send_command(test_command)
            print(f"命令执行结果: {response}")
        except Exception as e:
            print(f"命令执行失败: {e}")
    else:
        print("当前API不支持发送命令")
    
    print("\n=== API测试完成 ===")


if __name__ == "__main__":
    test_minecraft_client_api()
