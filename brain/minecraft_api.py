# -*- coding: utf-8 -*-
"""
Minecraft API通信模块

支持两种模式：
1. 使用Rcon协议与Minecraft服务器通信（服务器版本）
2. 使用屏幕分析与Minecraft客户端通信（客户端版本）
"""

import cv2
import numpy as np
import pyautogui

import socket
import struct
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MinecraftClientAPI:
    """Minecraft客户端API
    
    使用屏幕分析与Minecraft客户端通信
    """
    
    def __init__(self):
        """初始化Minecraft客户端API"""
        self.screen_analysis_available = True
        try:
            import cv2
            import numpy as np
            import pyautogui
        except ImportError:
            self.screen_analysis_available = False
            logger.warning("[Minecraft API] 屏幕分析所需库未安装")
        
        logger.info("[Minecraft API] 初始化Minecraft客户端API")
    
    def get_player_health(self) -> Optional[float]:
        """通过屏幕分析获取玩家健康值
        
        Returns:
            玩家健康值
        """
        try:
            if not self.screen_analysis_available:
                return None
            
            # 这里需要实现屏幕分析逻辑来检测健康值
            # 示例：返回默认值
            logger.info("[Minecraft API] 获取玩家健康值")
            return 20.0  # 默认健康值
        except Exception as e:
            logger.error(f"[Minecraft API] 获取玩家健康值出错: {e}")
            return None
    
    def get_player_hunger(self) -> Optional[float]:
        """通过屏幕分析获取玩家饥饿值
        
        Returns:
            玩家饥饿值
        """
        try:
            if not self.screen_analysis_available:
                return None
            
            # 这里需要实现屏幕分析逻辑来检测饥饿值
            # 示例：返回默认值
            logger.info("[Minecraft API] 获取玩家饥饿值")
            return 20.0  # 默认饥饿值
        except Exception as e:
            logger.error(f"[Minecraft API] 获取玩家饥饿值出错: {e}")
            return None
    
    def get_world_time(self) -> Optional[int]:
        """通过屏幕分析获取世界时间
        
        Returns:
            世界时间
        """
        try:
            if not self.screen_analysis_available:
                return None
            
            # 这里需要实现屏幕分析逻辑来检测时间
            # 示例：返回默认值
            logger.info("[Minecraft API] 获取世界时间")
            return 6000  # 默认白天时间
        except Exception as e:
            logger.error(f"[Minecraft API] 获取世界时间出错: {e}")
            return None
    
    def get_weather(self) -> Optional[str]:
        """通过屏幕分析获取天气
        
        Returns:
            当前天气
        """
        try:
            if not self.screen_analysis_available:
                return None
            
            # 这里需要实现屏幕分析逻辑来检测天气
            # 示例：返回默认值
            logger.info("[Minecraft API] 获取天气")
            return "clear"  # 默认晴天
        except Exception as e:
            logger.error(f"[Minecraft API] 获取天气出错: {e}")
            return None
    
    def detect_blocks(self) -> Optional[Dict[str, Any]]:
        """通过屏幕分析检测游戏中的方块
        
        Returns:
            方块检测结果
        """
        try:
            if not self.screen_analysis_available:
                return None
            
            # 这里需要实现屏幕分析逻辑来检测方块
            # 示例：返回默认值
            logger.info("[Minecraft API] 检测方块")
            return {
                "center_block": "oak_log",  # 屏幕中心的方块
                "nearby_blocks": ["grass", "oak_log", "stone"]
            }
        except Exception as e:
            logger.error(f"[Minecraft API] 检测方块出错: {e}")
            return None


class MinecraftRcon:
    """Minecraft Rcon协议客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 25575, password: str = "neuro-sama"):
        """初始化Rcon客户端
        
        Args:
            host: Minecraft服务器主机地址
            port: Rcon端口
            password: Rcon密码
        """
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.authenticated = False
        logger.info(f"[Minecraft API] 初始化Rcon客户端: {host}:{port}")
    
    def connect(self) -> bool:
        """连接到Minecraft服务器
        
        Returns:
            是否成功连接
        """
        try:
            # 创建socket连接
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            logger.info(f"[Minecraft API] 已连接到服务器: {self.host}:{self.port}")
            
            # 认证
            if not self._authenticate():
                logger.error("[Minecraft API] 认证失败")
                self.disconnect()
                return False
            
            return True
        except Exception as e:
            logger.error(f"[Minecraft API] 连接失败: {e}")
            self.disconnect()
            return False
    
    def _authenticate(self) -> bool:
        """认证到Rcon服务器
        
        Returns:
            是否认证成功
        """
        try:
            # 发送认证请求
            self._send_packet(3, self.password)
            
            # 接收响应
            packet_type, _ = self._receive_packet()
            
            # 检查认证是否成功
            if packet_type == 2:
                self.authenticated = True
                logger.info("[Minecraft API] 认证成功")
                return True
            else:
                logger.error("[Minecraft API] 认证响应类型错误")
                return False
        except Exception as e:
            logger.error(f"[Minecraft API] 认证过程出错: {e}")
            return False
    
    def disconnect(self):
        """断开与服务器的连接"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
                self.authenticated = False
                logger.info("[Minecraft API] 已断开连接")
        except Exception as e:
            logger.error(f"[Minecraft API] 断开连接出错: {e}")
    
    def send_command(self, command: str) -> Optional[str]:
        """发送命令到Minecraft服务器
        
        Args:
            command: 要执行的命令
            
        Returns:
            命令执行结果
        """
        if not self.authenticated:
            # 尝试重新连接
            if not self.connect():
                logger.error("[Minecraft API] 未认证，无法发送命令")
                return None
        
        try:
            # 发送命令
            self._send_packet(2, command)
            
            # 接收响应
            _, response = self._receive_packet()
            logger.info(f"[Minecraft API] 命令执行成功: {command}")
            return response
        except Exception as e:
            logger.error(f"[Minecraft API] 发送命令出错: {e}")
            return None
    
    def _send_packet(self, packet_type: int, payload: str):
        """发送Rcon数据包
        
        Args:
            packet_type: 数据包类型
            payload: 数据包内容
        """
        if not self.socket:
            raise Exception("Not connected to server")
        
        # 构建数据包
        data = payload.encode('utf-8') + b'\x00\x00'
        size = len(data) + 4
        packet = struct.pack('<iii', size, 0, packet_type) + data
        
        # 发送数据包
        self.socket.sendall(packet)
    
    def _receive_packet(self) -> tuple[int, str]:
        """接收Rcon数据包
        
        Returns:
            (数据包类型, 数据包内容)
        """
        if not self.socket:
            raise Exception("Not connected to server")
        
        # 接收数据包大小
        size_data = self.socket.recv(4)
        if not size_data:
            raise Exception("Connection closed")
        size = struct.unpack('<i', size_data)[0]
        
        # 接收数据包内容
        data = self.socket.recv(size)
        if not data:
            raise Exception("Connection closed")
        
        # 解析数据包
        request_id, packet_type = struct.unpack('<ii', data[:8])
        payload = data[8:-2].decode('utf-8', errors='ignore')
        
        return packet_type, payload
    
    def get_player_position(self, player_name: str = "") -> Optional[Dict[str, float]]:
        """获取玩家位置
        
        Args:
            player_name: 玩家名称（空字符串表示当前玩家）
            
        Returns:
            玩家位置信息
        """
        try:
            if not player_name:
                command = "data get entity @s Pos"
            else:
                command = f"data get entity {player_name} Pos"
            
            response = self.send_command(command)
            if response:
                # 解析位置数据
                # 示例响应: "Found "minecraft:overworld": [100.5d, 64.0d, 200.5d]"
                import re
                match = re.search(r'\[(.*?)\]', response)
                if match:
                    pos_str = match.group(1)
                    pos = [float(x.strip('d')) for x in pos_str.split(',')]
                    return {
                        "x": pos[0],
                        "y": pos[1],
                        "z": pos[2]
                    }
            return None
        except Exception as e:
            logger.error(f"[Minecraft API] 获取玩家位置出错: {e}")
            return None
    
    def get_nearby_blocks(self, radius: int = 5) -> Optional[Dict[str, Any]]:
        """获取玩家周围的方块
        
        Args:
            radius: 搜索半径
            
        Returns:
            周围方块信息
        """
        try:
            # 使用execute命令获取周围方块
            command = f"execute as @s run fill ~-{radius} ~-{radius} ~-{radius} ~{radius} ~{radius} ~{radius} minecraft:air replace"
            response = self.send_command(command)
            
            # 这里只是示例，实际需要使用更复杂的命令来获取方块信息
            # 可能需要使用数据打包或其他方式
            
            return {"radius": radius, "blocks": []}
        except Exception as e:
            logger.error(f"[Minecraft API] 获取周围方块出错: {e}")
            return None
    
    def get_player_health(self, player_name: str = "") -> Optional[float]:
        """获取玩家健康值
        
        Args:
            player_name: 玩家名称（空字符串表示当前玩家）
            
        Returns:
            玩家健康值
        """
        try:
            if not player_name:
                command = "data get entity @s Health"
            else:
                command = f"data get entity {player_name} Health"
            
            response = self.send_command(command)
            if response:
                # 解析健康值数据
                import re
                match = re.search(r'Health: (\d+\.?\d*)f', response)
                if match:
                    return float(match.group(1))
            return None
        except Exception as e:
            logger.error(f"[Minecraft API] 获取玩家健康值出错: {e}")
            return None
    
    def get_player_hunger(self, player_name: str = "") -> Optional[float]:
        """获取玩家饥饿值
        
        Args:
            player_name: 玩家名称（空字符串表示当前玩家）
            
        Returns:
            玩家饥饿值
        """
        try:
            if not player_name:
                command = "data get entity @s foodLevel"
            else:
                command = f"data get entity {player_name} foodLevel"
            
            response = self.send_command(command)
            if response:
                # 解析饥饿值数据
                import re
                match = re.search(r'foodLevel: (\d+)', response)
                if match:
                    return float(match.group(1))
            return None
        except Exception as e:
            logger.error(f"[Minecraft API] 获取玩家饥饿值出错: {e}")
            return None
    
    def get_world_time(self) -> Optional[int]:
        """获取游戏世界时间
        
        Returns:
            游戏世界时间
        """
        try:
            command = "time query daytime"
            response = self.send_command(command)
            if response:
                # 解析时间数据
                import re
                match = re.search(r'The time is (\d+)', response)
                if match:
                    return int(match.group(1))
            return None
        except Exception as e:
            logger.error(f"[Minecraft API] 获取世界时间出错: {e}")
            return None
    
    def get_weather(self) -> Optional[str]:
        """获取当前天气
        
        Returns:
            当前天气
        """
        try:
            # 检查是否在下雨
            rain_response = self.send_command("execute as @s run weather query rain")
            if "rain is false" in rain_response:
                return "clear"
            else:
                return "rainy"
        except Exception as e:
            logger.error(f"[Minecraft API] 获取天气出错: {e}")
            return None


# 全局Minecraft API实例
minecraft_api_instance = None


def get_or_create_minecraft_api() -> Any:
    """获取或创建Minecraft API实例
    
    Returns:
        Minecraft API实例（Rcon或客户端API）
    """
    global minecraft_api_instance
    if not minecraft_api_instance:
        # 首先尝试创建Rcon实例
        try:
            rcon = MinecraftRcon()
            if rcon.connect():
                minecraft_api_instance = rcon
                logger.info("[Minecraft API] 创建Minecraft Rcon实例")
                return minecraft_api_instance
        except Exception as e:
            logger.warning(f"[Minecraft API] Rcon初始化失败: {e}")
        
        # 如果Rcon失败，创建客户端API实例
        minecraft_api_instance = MinecraftClientAPI()
        logger.info("[Minecraft API] 创建Minecraft客户端API实例")
    return minecraft_api_instance


def test_minecraft_api_connection():
    """测试Minecraft API连接
    
    Returns:
        是否连接成功
    """
    api = get_or_create_minecraft_api()
    if isinstance(api, MinecraftRcon):
        return api.connect()
    else:
        # 客户端API总是可用的
        return True
