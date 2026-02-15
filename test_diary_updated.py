#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新后的日记生成功能
"""

import sys
import os
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.neuro_agent import NeuroSamaAgent

def test_updated_diary_generation():
    """测试更新后的日记生成功能"""
    print("=" * 60)
    print("测试更新后的日记生成功能")
    print("=" * 60)
    
    # 创建 Neuro-Sama 智能体实例
    agent = NeuroSamaAgent()
    
    # 等待一段时间，模拟使用时间
    print("1. 等待 2 秒，模拟使用时间...")
    time.sleep(2)
    
    print("2. 测试生成包含使用时间和学习内容的日记...")
    result = agent.generate_diary("general", "测试更新后的日记功能")
    print(f"   结果: {'成功' if result else '失败'}")
    
    # 添加一些记忆和任务，以便测试学习内容
    print("3. 添加一些记忆和任务，测试学习内容...")
    agent.memory.update({"event": "user_interaction", "details": "测试用户交互"})
    agent.add_task("test", "测试任务")
    agent.current_task = {"id": "test", "type": "test", "description": "测试任务", "started_at": time.time()}
    agent.complete_task()
    
    # 等待一段时间
    time.sleep(1)
    
    print("4. 再次测试生成日记，验证学习内容...")
    result = agent.generate_diary("user_interaction", "与用户进行了测试交流")
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("5. 测试生成每日总结...")
    result = agent.generate_daily_summary()
    print(f"   结果: {'成功' if result else '失败'}")
    
    print("\n" + "=" * 60)
    print("更新后的日记生成功能测试完成")
    print("=" * 60)
    print("请检查 F:\日记 目录下的日记文件，确认包含以下内容：")
    print("1. 使用时间（从启动到现在）")
    print("2. 学习到的内容")
    print("3. 详细的情绪和状态信息")

if __name__ == "__main__":
    test_updated_diary_generation()
