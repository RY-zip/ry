#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于对话内容的AI控制系统
让AI能够理解用户的对话并生成相应的操作
"""
import time
import json
import os
import re
import threading
from typing import List, Dict, Any

# 设置pyautogui的参数
import pyautogui
pyautogui.PAUSE = 0.3  # 减少每个操作之间的暂停时间，使操作更流畅
pyautogui.FAILSAFE = True  # 启用安全模式，移动鼠标到左上角可以中断操作

# 添加键盘监听库
try:
    import keyboard
    keyboard_available = True
except ImportError:
    keyboard_available = False

from memory.recent import CompressedRecentHistoryManager
from utils.config_manager import get_config_manager

class AIControlSystem:
    def __init__(self):
        self.config_manager = get_config_manager()
        self.recent_history_manager = CompressedRecentHistoryManager()
        self.lanlan_name = self._get_default_lanlan_name()  # 自动获取默认角色名
        self.enabled = True  # AI控制默认启用，自动分析对话内容
        self.running = False  # 系统是否运行中
        self.last_conversation_length = 0  # 上次对话历史长度
        
        print("=" * 60)
        print("基于对话内容的AI控制系统")
        print("=" * 60)
        print(f"系统已初始化，将自动分析对话历史生成操作")
        print(f"当前使用的角色名: {self.lanlan_name}")
        print("按F12可禁用AI控制")
        print("=" * 60)
        
        # 启动键盘监听
        self._start_keyboard_listener()
        
        # 启动对话监控线程
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_conversation, daemon=True)
        self.monitor_thread.start()
    
    def _get_default_lanlan_name(self) -> str:
        """
        自动获取默认角色名
        
        Returns:
            默认角色名
        """
        try:
            # 尝试从配置中获取角色列表
            character_data = self.config_manager.load_characters()
            catgirl_names = list(character_data.get('猫娘', {}).keys())
            if catgirl_names:
                return catgirl_names[0]
            
            # 如果没有角色，尝试从memory目录获取所有recent_*.json文件
            import glob
            memory_dir = str(self.config_manager.memory_dir)
            recent_files = glob.glob(os.path.join(memory_dir, 'recent_*.json'))
            if recent_files:
                # 获取第一个文件名作为角色名
                return os.path.basename(recent_files[0]).replace('recent_', '').replace('.json', '')
        except Exception as e:
            print(f"获取默认角色名失败: {e}")
        
        # 默认角色名
        return "07"
    
    def get_recent_conversation(self, max_messages=10) -> List[Dict[str, Any]]:
        """
        获取最近的对话历史
        
        Args:
            max_messages: 最大消息数量
            
        Returns:
            对话历史列表，每条消息包含role和content
        """
        try:
            history = self.recent_history_manager.get_recent_history(self.lanlan_name)
            conversation = []
            
            for msg in history[-max_messages:]:
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    if msg.type == 'system':
                        continue  # 跳过系统消息
                    
                    role = "user" if msg.type in ['user', 'human'] else "assistant"
                    
                    # 处理消息内容
                    if isinstance(msg.content, str):
                        content = msg.content
                    elif isinstance(msg.content, list):
                        # 提取文本内容
                        text_parts = []
                        for item in msg.content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_parts.append(item.get('text', ''))
                            else:
                                text_parts.append(str(item))
                        content = "\n".join(text_parts)
                    else:
                        content = str(msg.content)
                    
                    if content.strip():
                        conversation.append({"role": role, "content": content})
            
            return conversation
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    def analyze_conversation(self, conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析对话内容，基于AI的回复来执行操作
        
        Args:
            conversation: 对话历史
            
        Returns:
            分析结果，包含action和parameters
        """
        print("分析对话内容...")
        
        # 提取最近的消息对（用户消息 + AI回复）
        if len(conversation) < 2:
            return {"action": "none", "parameters": {}, "reason": "对话历史不足"}
        
        # 找到最近的用户消息和AI回复
        user_messages = [msg for msg in conversation if msg["role"] == "user"]
        assistant_messages = [msg for msg in conversation if msg["role"] == "assistant"]
        
        if not user_messages or not assistant_messages:
            return {"action": "none", "parameters": {}, "reason": "没有完整的对话消息"}
        
        latest_user_message = user_messages[-1]["content"].lower()
        latest_assistant_message = assistant_messages[-1]["content"].lower()
        
        print(f"最近的用户消息: {latest_user_message}")
        print(f"最近的AI回复: {latest_assistant_message}")
        
        # 基于AI回复和用户输入的组合来判断操作
        combined_message = f"{latest_user_message} {latest_assistant_message}"
        
        # 简单的关键词匹配
        if any(keyword in combined_message for keyword in ["打开浏览器", "浏览器", "bilibili", "B站"]):
            # 检查是否有B站关键词
            has_bilibili = any(keyword in combined_message for keyword in ["bilibili", "B站"])
            return {
                "action": "open_browser",
                "parameters": {
                    "url": "bilibili.com" if has_bilibili else ""
                },
                "reason": "检测到打开浏览器的请求"
            }
        elif any(keyword in combined_message for keyword in ["搜索", "查找"]):
            # 提取搜索关键词
            search_match = re.search(r"搜索(.*)" , combined_message)
            if search_match:
                keyword = search_match.group(1).strip()
                return {
                    "action": "search",
                    "parameters": {
                        "keyword": keyword
                    },
                    "reason": f"检测到搜索{keyword}的请求"
                }
        
        return {"action": "none", "parameters": {}, "reason": "未检测到可执行的请求"}
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> bool:
        """
        执行操作
        
        Args:
            action: 操作类型
            parameters: 操作参数
            
        Returns:
            是否执行成功
        """
        print(f"执行操作: {action}")
        print(f"操作参数: {parameters}")
        
        try:
            if action == "open_browser":
                # 使用Win+R打开运行对话框
                print("步骤1: 使用Win+R打开运行对话框")
                pyautogui.hotkey('win', 'r')
                time.sleep(1.5)  # 增加等待时间，确保运行对话框完全打开
                
                # 输入浏览器命令
                print("步骤2: 输入浏览器命令")
                pyautogui.typewrite("msedge")
                time.sleep(1)  # 增加等待时间，确保命令完全输入
                
                # 按回车键启动浏览器
                print("步骤3: 按回车键启动浏览器")
                pyautogui.press("enter")
                time.sleep(5)  # 增加等待时间，确保浏览器完全启动
                
                # 如果指定了URL，访问该URL
                url = parameters.get("url", "")
                if url:
                    print(f"步骤4: 访问URL: {url}")
                    # 移动到地址栏并点击
                    pyautogui.moveTo(400, 100, duration=0.6)
                    pyautogui.click()
                    time.sleep(1)  # 增加等待时间
                    # 清除地址栏内容
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('backspace')
                    time.sleep(0.5)
                    # 输入URL
                    pyautogui.typewrite(url)
                    time.sleep(1)  # 增加等待时间，确保URL完全输入
                    pyautogui.press("enter")
                    time.sleep(3)  # 增加等待时间，确保页面开始加载
                
                print("浏览器已成功打开")
                return True
                
            elif action == "search":
                keyword = parameters.get("keyword", "")
                if not keyword:
                    print("搜索关键词为空")
                    return False
                
                # 检查浏览器是否已打开
                print(f"步骤1: 搜索关键词: {keyword}")
                
                # 点击搜索栏
                pyautogui.moveTo(600, 150, duration=0.6)
                pyautogui.click()
                time.sleep(1)  # 增加等待时间
                
                # 清除搜索栏内容
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                time.sleep(0.5)
                
                # 输入关键词
                pyautogui.typewrite(keyword)
                time.sleep(1)  # 增加等待时间，确保关键词完全输入
                
                # 点击搜索按钮
                pyautogui.moveTo(1000, 150, duration=0.6)
                pyautogui.click()
                time.sleep(3)  # 增加等待时间，确保搜索开始
                
                print(f"搜索已成功执行: {keyword}")
                return True
                
            else:
                print(f"未知操作: {action}")
                return False
                
        except Exception as e:
            print(f"执行操作失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _toggle_ai_control(self, enable: bool):
        """
        切换AI控制的启用状态
        
        Args:
            enable: 是否启用AI控制
        """
        self.enabled = enable
        status = "启用" if enable else "禁用"
        print(f"[AI Control] AI控制已{status}")
    
    def _on_key_press(self, event):
        """
        处理键盘按键事件
        
        Args:
            event: 键盘事件对象
        """
        if event.name == 'f11':
            self._toggle_ai_control(True)
        elif event.name == 'f12':
            self._toggle_ai_control(False)
    
    def _start_keyboard_listener(self):
        """
        启动键盘监听
        """
        if keyboard_available:
            try:
                # 监听F11和F12键
                keyboard.on_press(self._on_key_press)
                print("[Keyboard Listener] 键盘监听已启动，AI控制默认启用，按F12可关闭AI控制")
            except Exception as e:
                print(f"[Keyboard Listener] 启动键盘监听失败: {e}")
        else:
            print("[Keyboard Listener] 键盘监听库不可用，AI控制切换功能已禁用")
    
    def _monitor_conversation(self):
        """
        监控对话历史的变化，当有新的AI回复时分析并执行操作
        """
        while self.running:
            if self.enabled:
                try:
                    # 获取对话历史
                    conversation = self.get_recent_conversation()
                    
                    # 检查对话历史是否有变化
                    if len(conversation) > self.last_conversation_length:
                        # 检查是否有新的AI回复
                        assistant_messages = [msg for msg in conversation if msg["role"] == "assistant"]
                        
                        # 获取之前的AI回复数量
                        previous_assistant_count = len([msg for msg in self.get_recent_conversation(self.last_conversation_length) if msg["role"] == "assistant"])
                        
                        # 如果有新的AI回复
                        if len(assistant_messages) > previous_assistant_count:
                            self.last_conversation_length = len(conversation)
                            
                            # 打印当前检查状态
                            print(f"[监控对话] 检测到新的AI回复，正在分析对话内容...")
                            
                            # 打印对话历史
                            print("=" * 60)
                            print("检测到新的对话内容:")
                            print("=" * 60)
                            for i, msg in enumerate(conversation[-5:]):  # 只显示最近5条消息
                                role = "用户" if msg["role"] == "user" else "AI"
                                print(f"{i+1}. {role}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                            print("=" * 60)
                            
                            # 分析对话内容
                            analysis_result = self.analyze_conversation(conversation)
                            print(f"分析结果: {analysis_result}")
                            
                            # 执行操作
                            if analysis_result["action"] != "none":
                                success = self.execute_action(analysis_result["action"], analysis_result["parameters"])
                                if success:
                                    print("=" * 60)
                                    print("操作执行成功！")
                                    print("=" * 60)
                                else:
                                    print("=" * 60)
                                    print("操作执行失败！")
                                    print("=" * 60)
                            else:
                                print("没有检测到可执行的操作")
                        else:
                            # 只有用户消息，没有AI回复，不进行分析
                            self.last_conversation_length = len(conversation)
                            print(f"[监控对话] 检测到新的用户消息，等待AI回复...")
                except Exception as e:
                    print(f"监控对话历史失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            time.sleep(3)  # 每3秒检查一次，减少CPU占用
    
    def run(self):
        """
        运行AI控制系统
        """
        print("系统已启动，正在监控对话历史...")
        print("AI控制默认启用，将自动分析对话内容并执行操作")
        print("按F12可禁用AI控制，按F11可重新启用AI控制")
        print("按Ctrl+C退出系统")
        
        # 保持系统运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n退出系统...")
            self.running = False
            if keyboard_available:
                try:
                    keyboard.unhook_all()
                except Exception:
                    pass
            print("系统已退出")

def main():
    """主函数，启动AI控制系统"""
    ai_control = AIControlSystem()
    ai_control.run()

if __name__ == "__main__":
    main()
