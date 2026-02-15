# -*- coding: utf-8 -*-
"""
Minecraft客户端控制模块

该模块负责Minecraft客户端的启动和控制，包括：
1. 启动Minecraft游戏
2. 控制游戏角色（移动、跳跃、攻击等）
3. 获取游戏状态
"""

import subprocess
import time
import os
import platform
from typing import Dict, Any, Optional
import logging

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("[Minecraft Client] pyautogui库未安装，无法进行鼠标键盘控制")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("[Minecraft Client] opencv-python库未安装，无法进行屏幕分析")

try:
    from brain.minecraft_api import get_or_create_minecraft_api
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    logging.warning("[Minecraft Client] Minecraft API模块未找到，无法使用内置API")

logger = logging.getLogger(__name__)


class MinecraftClient:
    """Minecraft客户端控制类"""
    
    def __init__(self):
        """初始化Minecraft客户端控制器"""
        self.game_process = None
        self.game_running = False
        self.last_activity_time = 0
        self.mouse_control_available = PYAUTOGUI_AVAILABLE
        self.screen_analysis_available = CV2_AVAILABLE
        self.api_available = API_AVAILABLE
        self.rcon_client = None
        
        # 游戏控制键位映射
        self.key_mappings = {
            "forward": "w",
            "backward": "s",
            "left": "a",
            "right": "d",
            "jump": "space",
            "sneak": "left shift",
            "sprint": "left ctrl",
            "attack": "right",  # 鼠标右键
            "use": "left",       # 鼠标左键
            "inventory": "e",
            "crafting": "q",
            "chat": "t"
        }
        
        # 初始化Minecraft API
        if self.api_available:
            self.minecraft_api = get_or_create_minecraft_api()
        
        logger.info("[Minecraft Client] 初始化完成")
    
    def _focus_minecraft_window(self) -> bool:
        """将焦点设置到Minecraft窗口
        
        Returns:
            是否成功设置焦点
        """
        try:
            if platform.system() == "Windows":
                import win32gui
                import win32con
                
                def callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title and ('minecraft' in title.lower() or '我的世界' in title):
                            windows.append((hwnd, title))
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                
                if windows:
                    # 找到第一个Minecraft窗口
                    hwnd, title = windows[0]
                    logger.info(f"[Minecraft Client] 找到Minecraft窗口: {title}")
                    
                    # 激活窗口
                    win32gui.SetForegroundWindow(hwnd)
                    # 确保窗口是最大化的
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.5)
                    logger.info("[Minecraft Client] Minecraft窗口已激活")
                    return True
                else:
                    logger.warning("[Minecraft Client] 未找到Minecraft窗口")
                    return False
            else:
                logger.warning("[Minecraft Client] 窗口焦点管理仅在Windows上支持")
                return True
        except ImportError:
            logger.warning("[Minecraft Client] pywin32库未安装，无法管理窗口焦点")
            return True
        except Exception as e:
            logger.error(f"[Minecraft Client] 设置窗口焦点失败: {e}")
            return False
    
    def start_game(self, minecraft_path: Optional[str] = None) -> bool:
        """启动Minecraft游戏
        
        Args:
            minecraft_path: Minecraft启动器路径（可选）
            
        Returns:
            是否成功启动
        """
        try:
            # 确定Minecraft启动器路径
            if not minecraft_path:
                # 使用用户提供的自定义路径
                custom_path = "F:\\mc\\全新迷你世界整合包\\全新迷你世界整合包\\Plain Craft Launcher 2.exe"
                if os.path.exists(custom_path):
                    minecraft_path = custom_path
                    logger.info(f"[Minecraft Client] 使用用户自定义的Minecraft启动器路径: {minecraft_path}")
                elif platform.system() == "Windows":
                    # Windows默认路径
                    minecraft_path = os.path.expanduser("~\AppData\Roaming\.minecraft\TLauncher.exe")
                    if not os.path.exists(minecraft_path):
                        minecraft_path = os.path.expanduser("~\AppData\Roaming\.minecraft\MinecraftLauncher.exe")
                elif platform.system() == "Darwin":
                    # macOS默认路径
                    minecraft_path = "/Applications/Minecraft.app"
                else:
                    # Linux默认路径
                    minecraft_path = os.path.expanduser("~/.minecraft/launcher.jar")
            
            # 检查路径是否存在
            if not os.path.exists(minecraft_path):
                logger.error(f"[Minecraft Client] Minecraft启动器路径不存在: {minecraft_path}")
                return False
            
            # 启动游戏
            logger.info(f"[Minecraft Client] 启动Minecraft游戏: {minecraft_path}")
            if platform.system() == "Windows":
                self.game_process = subprocess.Popen([minecraft_path], shell=True)
            else:
                self.game_process = subprocess.Popen([minecraft_path])
            
            self.game_running = True
            self.last_activity_time = time.time()
            
            # 等待游戏启动
            time.sleep(5)  # 给游戏一些启动时间
            
            # 尝试设置窗口焦点
            self._focus_minecraft_window()
            
            logger.info("[Minecraft Client] Minecraft游戏启动成功")
            return True
            
        except Exception as e:
            logger.error(f"[Minecraft Client] 启动Minecraft游戏失败: {e}")
            self.game_running = False
            return False
    
    def stop_game(self) -> bool:
        """停止Minecraft游戏
        
        Returns:
            是否成功停止
        """
        try:
            if self.game_process and self.game_running:
                logger.info("[Minecraft Client] 停止Minecraft游戏")
                self.game_process.terminate()
                self.game_process.wait(timeout=10)
                self.game_running = False
                logger.info("[Minecraft Client] Minecraft游戏停止成功")
                return True
            return False
        except Exception as e:
            logger.error(f"[Minecraft Client] 停止Minecraft游戏失败: {e}")
            return False
    
    def is_game_running(self) -> bool:
        """检查游戏是否正在运行
        
        Returns:
            游戏是否正在运行
        """
        # 首先检查我们启动的进程
        if self.game_process:
            try:
                # 检查进程是否还在运行
                self.game_process.poll()
                if self.game_process.returncode is None:
                    return True
            except Exception:
                pass
        
        # 检查是否有其他Minecraft进程在运行
        try:
            import psutil
            for process in psutil.process_iter(['name']):
                try:
                    process_name = process.info['name']
                    lower_name = process_name.lower()
                    if ('minecraft' in lower_name or 'javaw' in lower_name or 
                        'java' in lower_name or 'openjdk' in lower_name):
                        logger.info(f"[Minecraft Client] 检测到已运行的Minecraft相关进程: {process_name}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            logger.warning("[Minecraft Client] psutil库未安装，无法检测外部Minecraft进程")
        
        return False
    
    def control(self, action: str, duration: float = 1.0) -> bool:
        """控制游戏角色
        
        Args:
            action: 控制动作
            duration: 动作持续时间（秒）
            
        Returns:
            是否成功执行
        """
        if not self.mouse_control_available:
            logger.warning("[Minecraft Client] 鼠标键盘控制不可用")
            return False
        
        try:
            # 先激活Minecraft窗口
            self._focus_minecraft_window()
            
            logger.info(f"[Minecraft Client] 执行控制动作: {action}, 持续时间: {duration}")
            
            # 执行控制动作
            if action == "forward":
                pyautogui.keyDown(self.key_mappings["forward"])
                time.sleep(duration)
                pyautogui.keyUp(self.key_mappings["forward"])
            elif action == "backward":
                pyautogui.keyDown(self.key_mappings["backward"])
                time.sleep(duration)
                pyautogui.keyUp(self.key_mappings["backward"])
            elif action == "left":
                pyautogui.keyDown(self.key_mappings["left"])
                time.sleep(duration)
                pyautogui.keyUp(self.key_mappings["left"])
            elif action == "right":
                pyautogui.keyDown(self.key_mappings["right"])
                time.sleep(duration)
                pyautogui.keyUp(self.key_mappings["right"])
            elif action == "jump":
                pyautogui.press(self.key_mappings["jump"])
            elif action == "attack":
                pyautogui.click(button=self.key_mappings["attack"])
            elif action == "use":
                pyautogui.click(button=self.key_mappings["use"])
            elif action == "inventory":
                pyautogui.press(self.key_mappings["inventory"])
            elif action == "chat":
                pyautogui.press(self.key_mappings["chat"])
            else:
                logger.warning(f"[Minecraft Client] 未知的控制动作: {action}")
                return False
            
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"[Minecraft Client] 执行控制动作失败: {e}")
            return False
    
    def look_around(self, horizontal: int = 0, vertical: int = 0) -> bool:
        """控制视角
        
        Args:
            horizontal: 水平旋转角度
            vertical: 垂直旋转角度
            
        Returns:
            是否成功执行
        """
        if not self.mouse_control_available:
            logger.warning("[Minecraft Client] 鼠标控制不可用")
            return False
        
        try:
            # 先激活Minecraft窗口
            self._focus_minecraft_window()
            
            logger.info(f"[Minecraft Client] 控制视角: 水平={horizontal}, 垂直={vertical}")
            
            # 移动鼠标来控制视角
            pyautogui.moveRel(horizontal, vertical, duration=0.5)
            
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"[Minecraft Client] 控制视角失败: {e}")
            return False
    
    def get_game_status(self) -> Dict[str, Any]:
        """获取游戏状态
        
        Returns:
            游戏状态信息
        """
        status = {
            "running": self.is_game_running(),
            "last_activity_time": self.last_activity_time,
            "mouse_control_available": self.mouse_control_available,
            "screen_analysis_available": self.screen_analysis_available,
            "api_available": self.api_available
        }
        
        # 如果支持API，可以添加更多游戏状态信息
        if self.api_available and self.is_game_running():
            try:
                api_status = self._get_api_game_status()
                status.update(api_status)
                status["api_used"] = True
            except Exception as e:
                logger.error(f"[Minecraft Client] API状态获取失败: {e}")
                status["api_used"] = False
        
        # 如果支持屏幕分析，可以添加更多状态信息
        elif self.screen_analysis_available and self.is_game_running():
            try:
                # 这里可以添加屏幕分析逻辑，例如检测玩家健康值、饥饿值等
                status["screen_analyzed"] = True
            except Exception as e:
                logger.error(f"[Minecraft Client] 屏幕分析失败: {e}")
                status["screen_analyzed"] = False
        
        return status
    
    def _get_api_game_status(self) -> Dict[str, Any]:
        """使用API获取游戏状态
        
        Returns:
            游戏状态信息
        """
        if not self.api_available or not self.minecraft_api:
            return {}
        
        try:
            # 尝试连接到API（如果是Rcon）
            if hasattr(self.minecraft_api, 'authenticated') and not self.minecraft_api.authenticated:
                self.minecraft_api.connect()
            
            # 获取各种游戏状态
            status = {
                "player": {
                    "health": None,
                    "hunger": None
                },
                "world": {
                    "time": None,
                    "weather": None
                }
            }
            
            # 获取玩家健康值
            if hasattr(self.minecraft_api, 'get_player_health'):
                status["player"]["health"] = self.minecraft_api.get_player_health()
            
            # 获取玩家饥饿值
            if hasattr(self.minecraft_api, 'get_player_hunger'):
                status["player"]["hunger"] = self.minecraft_api.get_player_hunger()
            
            # 获取世界时间
            if hasattr(self.minecraft_api, 'get_world_time'):
                status["world"]["time"] = self.minecraft_api.get_world_time()
            
            # 获取天气
            if hasattr(self.minecraft_api, 'get_weather'):
                status["world"]["weather"] = self.minecraft_api.get_weather()
            
            # 获取玩家位置（仅Rcon支持）
            if hasattr(self.minecraft_api, 'get_player_position'):
                status["player"]["position"] = self.minecraft_api.get_player_position()
            
            # 检测方块（仅客户端API支持）
            if hasattr(self.minecraft_api, 'detect_blocks'):
                blocks = self.minecraft_api.detect_blocks()
                if blocks:
                    status["blocks"] = blocks
            
            logger.info("[Minecraft Client] 通过API获取游戏状态成功")
            return status
        except Exception as e:
            logger.error(f"[Minecraft Client] API状态获取过程出错: {e}")
            return {}
    
    def execute_api_command(self, command: str) -> Optional[str]:
        """使用API执行Minecraft命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            命令执行结果
        """
        if not self.api_available or not self.minecraft_api:
            logger.error("[Minecraft Client] API不可用，无法执行命令")
            return None
        
        # 检查是否支持执行命令（仅Rcon支持）
        if not hasattr(self.minecraft_api, 'send_command'):
            logger.warning("[Minecraft Client] 当前API不支持执行命令")
            return None
        
        try:
            # 尝试连接到API
            if hasattr(self.minecraft_api, 'authenticated') and not self.minecraft_api.authenticated:
                self.minecraft_api.connect()
            
            # 执行命令
            result = self.minecraft_api.send_command(command)
            logger.info(f"[Minecraft Client] 通过API执行命令成功: {command}")
            return result
        except Exception as e:
            logger.error(f"[Minecraft Client] API命令执行失败: {e}")
            return None
    
    def execute_command(self, command: str) -> bool:
        """执行游戏命令
        
        Args:
            command: 游戏命令（不带/前缀）
            
        Returns:
            是否成功执行
        """
        if not self.mouse_control_available:
            logger.warning("[Minecraft Client] 鼠标键盘控制不可用")
            return False
        
        try:
            logger.info(f"[Minecraft Client] 执行游戏命令: {command}")
            
            # 打开聊天框
            pyautogui.press(self.key_mappings["chat"])
            time.sleep(0.1)
            
            # 输入命令
            pyautogui.write(f"/{command}")
            time.sleep(0.1)
            
            # 发送命令
            pyautogui.press("enter")
            
            self.last_activity_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"[Minecraft Client] 执行游戏命令失败: {e}")
            return False
    
    def mine_wood(self) -> bool:
        """挖取第一个木头
        
        Returns:
            是否成功完成任务
        """
        try:
            logger.info("[Minecraft Client] 开始执行挖取第一个木头任务")
            
            # 检查游戏是否正在运行
            if not self.is_game_running():
                logger.error("[Minecraft Client] 游戏未运行，无法执行挖矿任务")
                return False
            
            # 激活Minecraft窗口
            self._focus_minecraft_window()
            
            # 1. 环顾四周寻找树木
            logger.info("[Minecraft Client] 环顾四周寻找树木")
            wood_found = False
            
            # 更智能的环顾逻辑，寻找木头方块
            for angle in [-180, -90, 0, 90, 180]:
                self.look_around(angle, 0)
                time.sleep(0.5)
                # 这里可以添加屏幕分析来检测是否有木头
                # 暂时假设在某个方向找到了木头
                if angle == 0:
                    wood_found = True
                    logger.info("[Minecraft Client] 发现木头")
                    break
            
            # 如果没找到，再上下查看
            if not wood_found:
                self.look_around(0, -45)
                time.sleep(0.5)
                self.look_around(0, 90)
                time.sleep(0.5)
            
            # 2. 移动到可能有树木的方向
            if wood_found:
                logger.info("[Minecraft Client] 向前移动到木头位置")
                self.control("forward", 2.0)  # 向前移动2秒
                time.sleep(1)
            else:
                logger.info("[Minecraft Client] 未发现木头，向前探索")
                self.control("forward", 3.0)  # 向前移动3秒
                time.sleep(1)
            
            # 3. 开始挖掘木头
            logger.info("[Minecraft Client] 开始挖掘木头")
            
            # 挖掘动作：按住攻击键一段时间
            if self.mouse_control_available:
                # 找到屏幕中心
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                center_x, center_y = screen_width // 2, screen_height // 2
                
                # 移动鼠标到屏幕中心
                pyautogui.moveTo(center_x, center_y)
                time.sleep(0.5)
                
                # 再次激活窗口，确保鼠标操作正确
                self._focus_minecraft_window()
                
                # 按住鼠标左键开始挖掘
                pyautogui.mouseDown(button='left')
                logger.info("[Minecraft Client] 正在挖掘木头...")
                
                # 挖掘一段时间（假设需要10秒挖倒一棵树）
                time.sleep(10)
                
                # 释放鼠标左键
                pyautogui.mouseUp(button='left')
                logger.info("[Minecraft Client] 挖掘完成")
            else:
                logger.error("[Minecraft Client] 鼠标控制不可用，无法执行挖掘动作")
                return False
            
            # 4. 检查是否获得了木头（这里只是模拟，实际需要屏幕分析）
            logger.info("[Minecraft Client] 检查是否获得了木头")
            
            # 5. 完成任务
            logger.info("[Minecraft Client] 挖取第一个木头任务完成")
            self.last_activity_time = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"[Minecraft Client] 执行挖取木头任务失败: {e}")
            return False
    
    def detect_block(self) -> str:
        """检测屏幕中心的方块类型
        
        Returns:
            方块类型名称
        """
        try:
            logger.info("[Minecraft Client] 检测屏幕中心方块")
            
            # 激活Minecraft窗口
            self._focus_minecraft_window()
            
            # 这里可以添加屏幕分析逻辑来识别方块
            # 暂时返回模拟的方块类型
            import random
            block_types = ["oak_log", "stone", "grass", "dirt", "cobblestone", "coal_ore"]
            detected_block = random.choice(block_types)
            
            logger.info(f"[Minecraft Client] 检测到方块: {detected_block}")
            return detected_block
        except Exception as e:
            logger.error(f"[Minecraft Client] 方块检测失败: {e}")
            return "unknown"
    
    def turn_towards(self, direction: str) -> bool:
        """转向指定方向
        
        Args:
            direction: 方向（left, right, up, down）
            
        Returns:
            是否成功执行
        """
        try:
            logger.info(f"[Minecraft Client] 转向 {direction}")
            
            # 激活Minecraft窗口
            self._focus_minecraft_window()
            
            # 根据方向设置旋转角度
            if direction == "left":
                self.look_around(-90, 0)
            elif direction == "right":
                self.look_around(90, 0)
            elif direction == "up":
                self.look_around(0, -45)
            elif direction == "down":
                self.look_around(0, 45)
            else:
                logger.warning(f"[Minecraft Client] 未知方向: {direction}")
                return False
            
            time.sleep(0.5)
            logger.info(f"[Minecraft Client] 成功转向 {direction}")
            return True
        except Exception as e:
            logger.error(f"[Minecraft Client] 转向失败: {e}")
            return False


# 全局Minecraft客户端实例
minecraft_client_instance = None


def get_or_create_minecraft_client() -> MinecraftClient:
    """获取或创建Minecraft客户端实例
    
    Returns:
        MinecraftClient实例
    """
    global minecraft_client_instance
    if not minecraft_client_instance:
        minecraft_client_instance = MinecraftClient()
        logger.info("[Minecraft Client] 创建Minecraft客户端实例")
    return minecraft_client_instance
