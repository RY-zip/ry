#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日记生成功能
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.neuro_agent import NeuroSamaAgent

def test_diary_generation():
    """测试日记生成功能"""
    print("=" * 60)
    print("测试日记生成功能")
    print("=" * 60)
    
    # 创建 Neuro-Sama 智能体实例
    agent = NeuroSamaAgent()
    
    print("1. 测试生成一般日记...")
    result = agent.generate_diary("general", "这是一条测试日记")
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("2. 测试生成用户交互日记...")
    result = agent.generate_diary("user_interaction", "与用户进行了测试交流")
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("3. 测试生成自我对话日记...")
    result = agent.generate_diary("self_talk", "进行了自我测试对话")
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("4. 测试生成探索日记...")
    result = agent.generate_diary("exploration", "测试探索了新环境")
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("5. 测试生成每日总结...")
    result = agent.generate_daily_summary()
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("6. 测试智能体启动时的日记初始化...")
    # 启动智能体（这会初始化日记文件列表）
    agent.start()
    print(f"   日记文件数量: {len(agent.diary_files)}")
    if agent.diary_files:
        print(f"   第一个日记文件: {agent.diary_files[0]}")
    
    # 等待一段时间，让智能体有机会运行
    time.sleep(2)
    
    # 停止智能体
    agent.stop()
    
    print("\n" + "=" * 60)
    print("日记生成功能测试完成")
    print("=" * 60)
    print("请检查 F:\日记 目录下是否生成了日记文件")

if __name__ == "__main__":
    test_diary_generation()
