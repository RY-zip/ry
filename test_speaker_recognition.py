#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试说话人识别功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.speaker_recognition import SpeakerRecognition
from brain.neuro_agent import NeuroSamaAgent

def test_speaker_recognition():
    """测试说话人识别模块"""
    print("=" * 60)
    print("测试说话人识别功能")
    print("=" * 60)
    
    # 创建说话人识别模块
    speaker_recognition = SpeakerRecognition()
    
    # 模拟音频数据
    # 为了测试，我们使用字符串作为音频数据的模拟
    audio_data_a = b"This is speaker A's voice"
    audio_data_b = b"This is speaker B's voice"
    audio_data_unknown = b"This is an unknown speaker's voice"
    
    # 测试注册说话人
    print("\n测试注册说话人")
    print("-" * 40)
    
    # 注册说话人 A
    register_result_a = speaker_recognition.register_speaker("speaker_a", audio_data_a, "Speaker A")
    print(f"注册说话人 A: {register_result_a}")
    
    # 注册说话人 B
    register_result_b = speaker_recognition.register_speaker("speaker_b", audio_data_b, "Speaker B")
    print(f"注册说话人 B: {register_result_b}")
    
    # 测试获取说话人列表
    print("\n测试获取说话人列表")
    print("-" * 40)
    speakers = speaker_recognition.get_speakers()
    print(f"注册的说话人: {speakers}")
    print(f"说话人数量: {len(speakers)}")
    
    # 测试识别说话人
    print("\n测试识别说话人")
    print("-" * 40)
    
    # 识别说话人 A
    recognize_result_a = speaker_recognition.recognize_speaker(audio_data_a)
    print(f"识别说话人 A: {recognize_result_a}")
    
    # 识别说话人 B
    recognize_result_b = speaker_recognition.recognize_speaker(audio_data_b)
    print(f"识别说话人 B: {recognize_result_b}")
    
    # 识别未知说话人
    recognize_result_unknown = speaker_recognition.recognize_speaker(audio_data_unknown)
    print(f"识别未知说话人: {recognize_result_unknown}")
    
    # 测试 Neuro-Sama 智能体的说话人识别集成
    print("\n测试 Neuro-Sama 智能体的说话人识别集成")
    print("-" * 40)
    
    # 创建智能体
    agent = NeuroSamaAgent()
    
    # 测试注册说话人
    register_result = agent.register_speaker("test_speaker", audio_data_a, "Test Speaker")
    print(f"智能体注册说话人: {register_result}")
    
    # 测试识别说话人
    recognize_result = agent.recognize_speaker(audio_data_a)
    print(f"智能体识别说话人: {recognize_result}")
    
    # 测试获取说话人列表
    speakers_result = agent.get_speakers()
    print(f"智能体获取说话人列表: {speakers_result}")
    
    print("\n" + "=" * 60)
    print("说话人识别功能测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_speaker_recognition()
