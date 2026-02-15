#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试情绪管理系统
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.emotion_manager import EmotionManager
from brain.neuro_agent import NeuroSamaAgent

def test_emotion_manager():
    """测试情绪管理模块"""
    print("=" * 60)
    print("测试情绪管理系统")
    print("=" * 60)
    
    # 创建情绪管理器
    emotion_manager = EmotionManager()
    
    # 测试情感分析
    test_messages = [
        "今天天气真好，我很开心！",
        "我今天感觉特别难过，一切都不顺利。",
        "你知道吗？我对这个问题很好奇。",
        "生活真是平静，没有什么特别的事情发生。",
        "我真的很生气，为什么会这样？"
    ]
    
    for message in test_messages:
        print(f"\n测试消息: {message}")
        dominant_emotion = emotion_manager.update_emotions(message, is_user_input=True)
        emotion_state = emotion_manager.get_emotion_state()
        print(f"主导情绪: {dominant_emotion}")
        print(f"情绪水平: {emotion_state['emotion_levels']}")
        print(f"建议回应: {emotion_state['suggested_response']}")
    
    print("\n" + "=" * 60)
    print("情绪管理模块测试完成！")
    print("=" * 60)

def test_neuro_agent_emotion():
    """测试Neuro-Sama智能体的情绪管理功能"""
    print("\n" + "=" * 60)
    print("测试Neuro-Sama智能体的情绪管理功能")
    print("=" * 60)
    
    # 创建智能体
    agent = NeuroSamaAgent()
    
    # 测试添加聊天消息
    test_messages = [
        "你好，很高兴认识你！",
        "我今天心情不太好，感觉有点难过。",
        "你能告诉我一些有趣的事情吗？",
        "今天真是糟糕的一天，什么都不顺利。",
        "谢谢你，你真的很贴心！"
    ]
    
    for i, message in enumerate(test_messages):
        print(f"\n消息 {i+1}: {message}")
        agent.add_chat_message(message)
        
        # 获取状态
        status = agent.get_status()
        print(f"智能体状态:")
        print(f"  内部情绪: {status['internal_emotion']}")
        print(f"  能量: {status['energy']:.2f}")
        print(f"  好奇心: {status['curiosity']:.2f}")
        print(f"  情绪管理状态:")
        print(f"    主导情绪: {status['emotion_state']['dominant_emotion']}")
        print(f"    建议回应: {status['emotion_state']['suggested_response']}")
    
    print("\n" + "=" * 60)
    print("Neuro-Sama智能体情绪管理功能测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_emotion_manager()
    test_neuro_agent_emotion()
