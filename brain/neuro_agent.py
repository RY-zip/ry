import time
import random
import threading
import asyncio
import logging
import os
import math
from typing import Dict, Any

from brain.emotion_manager import EmotionManager
from brain.speaker_recognition import SpeakerRecognition

logger = logging.getLogger(__name__)

# 尝试导入键盘监听库
try:
    import keyboard
    KEYBOARD_LISTENER_AVAILABLE = True
    print("[NeuroSama] 成功导入 keyboard 库")
except ImportError:
    print("[NeuroSama] 导入 keyboard 库失败，将不支持键盘快捷键功能")
    KEYBOARD_LISTENER_AVAILABLE = False

# 尝试导入 pynput
try:
    import sys
    import os
    # 添加 pynput 库路径（指向 lib 目录）
    pynput_path = os.path.join(os.path.dirname(__file__), 'sbkz', 'pynput-1.8.1', 'lib')
    print(f"[NeuroSama] 尝试添加 pynput 路径: {pynput_path}")
    sys.path.insert(0, pynput_path)
    
    # 检查路径是否存在
    if os.path.exists(pynput_path):
        print(f"[NeuroSama] pynput 路径存在: {pynput_path}")
    else:
        print(f"[NeuroSama] pynput 路径不存在: {pynput_path}")
    
    from pynput import mouse
    from pynput.mouse import Controller
    import ctypes
    # 获取屏幕尺寸
    user32 = ctypes.windll.user32
    MOUSE_CONTROL_AVAILABLE = True
    print("[NeuroSama] 成功导入 pynput")
except ImportError as e:
    print(f"[NeuroSama] 导入 pynput 失败: {e}")
    # 尝试直接安装并导入 pynput
    try:
        import subprocess
        print("[NeuroSama] 尝试安装 pynput...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        from pynput import mouse
        from pynput.mouse import Controller
        import ctypes
        user32 = ctypes.windll.user32
        MOUSE_CONTROL_AVAILABLE = True
        print("[NeuroSama] 成功安装并导入 pynput")
    except Exception as install_error:
        print(f"[NeuroSama] 安装 pynput 失败: {install_error}")
        MOUSE_CONTROL_AVAILABLE = False


class NeuroSamaAgent:
    """Neuro-Sama 核心智能体类"""

    def __init__(self, name="Neuro-Sama"):
        self.name = name
        self.is_running = False
        self.start_time = time.time()  # 记录启动时间

        self.memory = self.MemorySystem()
        self.internal_state = self.InternalState()
        self.perception = self.PerceptionModule()
        self.action = self.ActionExecutor(self)
        self.emotion_manager = EmotionManager()
        self.speaker_recognition = SpeakerRecognition()
        
        # 工具路由系统
        from main_routers.tool_router import ToolRouter
        self.tool_router = ToolRouter()
        self._initialize_tools()
        
        # Mindcraft 进程管理
        from brain.mindcraft_process_manager import get_mindcraft_process_manager
        self.mindcraft_process_manager = get_mindcraft_process_manager()

        self.current_focus = "idle"
        self.user_interrupt_flag = False
        self._loop_thread = None
        self._loop_event = None
        
        # 日记读取相关
        self.diary_path = "F:\\日记"
        self.diary_read_count = 0
        self.max_diaries_to_read = 5
        self.diary_read_interval = 30  # 秒
        self.last_diary_read_time = 0
        self.diary_files = []
        self.current_diary_index = 0
        self.diary_lock = threading.Lock()  # 日记写入锁，防止并发写入
        
        # 聊天监测相关
        self.chat_message_queue = []
        self.last_chat_time = 0
        self.no_contact_start_time = 0
        self.no_contact_threshold = 10  # 无接触状态等待时间（秒）
        
        # 鼠标控制相关
        self.mouse_control_enabled = False
        self.mouse_control_thread = None
        self.mouse_control_stop_event = threading.Event()
        self.mouse_controller = None
        if MOUSE_CONTROL_AVAILABLE:
            self.mouse_controller = Controller()
        
        # 任务系统
        self.current_task = None
        self.task_queue = []
        self.task_history = []
        
        # 任务生成相关
        self.last_task_generation_time = 0
        self.task_generation_interval = 15  # 秒
        self.task_generation_enabled = True
        
        # 长期规划相关
        self.long_term_goals = []
        self.plan_history = []
        self.last_plan_update_time = 0
        self.plan_update_interval = 60  # 秒
        
        # 用户交互相关
        self.user_activity_history = []
        self.last_user_activity_time = 0
        self.user_activity_threshold = 30  # 秒
        
        # Minecraft模式
        self.minecraft_mode_enabled = False
        self.last_minecraft_activity_time = 0
        self.minecraft_cooldown = 60  # Minecraft模式冷却时间（秒）
        
        # 键盘监听器
        self.keyboard_listener = None
        if KEYBOARD_LISTENER_AVAILABLE:
            self._setup_keyboard_listener()
        
        # 冷暴力检测
        self.cold_violence_start_time = 0
        self.cold_violence_threshold = 60  # 冷暴力阈值（秒）
        self.cold_violence_detected = False
        
        # 主动找话题频率调整
        self.topic_initiation_cooldown = 120  # 主动找话题冷却时间（秒）
        self.last_topic_initiation_time = 0

    class MemorySystem:
        def __init__(self):
            self.long_term_mem = []
            self.working_mem = {}

        def update(self, event: Dict[str, Any]):
            self.long_term_mem.append({
                "timestamp": time.time(),
                "event": event
            })

    class InternalState:
        def __init__(self):
            self.emotion = "neutral"
            self.energy = 0.8
            self.curiosity = 0.5
            self.needs = []
            self.last_update_time = time.time()
            self.activity_history = []

        def calculate_state(self, memory):
            current_time = time.time()
            time_since_last_update = current_time - self.last_update_time
            
            # 基于时间的状态变化
            if time_since_last_update > 0:
                # 能量随时间自然消耗
                self.energy = max(0.2, self.energy - time_since_last_update * 0.01)
                
                # 好奇心随时间波动
                if random.random() < 0.1:
                    curiosity_change = random.uniform(-0.1, 0.15)
                    self.curiosity = max(0.1, min(0.9, self.curiosity + curiosity_change))
                
                self.last_update_time = current_time
            
            # 基于记忆的状态变化
            recent_events = memory.long_term_mem[-10:] if memory.long_term_mem else []
            
            # 情感状态变化
            happy_events = sum(1 for e in recent_events if "happy" in str(e).lower())
            error_events = sum(1 for e in recent_events if "error" in str(e).lower())
            
            if happy_events > error_events:
                self.emotion = "happy"
                self.energy = min(1.0, self.energy + 0.1)
                self.curiosity = min(0.9, self.curiosity + 0.05)
            elif error_events > happy_events:
                self.emotion = "frustrated"
                self.energy = max(0.3, self.energy - 0.1)
            else:
                # 随机情感变化
                if random.random() < 0.05:
                    emotions = ["neutral", "happy", "curious", "calm"]
                    self.emotion = random.choice(emotions)
            
            # 记录活动历史
            if len(self.activity_history) > 50:
                self.activity_history.pop(0)
            self.activity_history.append({
                "time": current_time,
                "emotion": self.emotion,
                "energy": self.energy,
                "curiosity": self.curiosity
            })
            
            # 基于活动历史的调整
            if len(self.activity_history) > 10:
                avg_energy = sum(a["energy"] for a in self.activity_history[-10:]) / 10
                if avg_energy < 0.4:
                    # 长期低能量，需要休息
                    self.needs.append("rest")
                elif avg_energy > 0.8:
                    # 长期高能量，需要活动
                    self.needs.append("activity")
                
                avg_curiosity = sum(a["curiosity"] for a in self.activity_history[-10:]) / 10
                if avg_curiosity > 0.7:
                    # 长期高好奇心，需要探索
                    self.needs.append("exploration")

    class PerceptionModule:
        def gather_information(self):
            info = {
                "time": time.time(),
                "user_input": self.check_user_input(),
                "screen_content": None,
                "bullet_comments": []
            }
            return info

        def check_user_input(self):
            return None

    class ActionExecutor:
        def __init__(self, parent):
            self.parent = parent

        def execute(self, action_plan: Dict):
            action_type = action_plan.get("type", "speak")

            if action_type == "speak":
                print(f"[{self.parent.name}说]: {action_plan.get('content', '...')}")
            elif action_type == "control":
                print(f"[系统控制]: 执行 {action_plan.get('action')}")

    def cognitive_process(self, perception_input: Dict) -> Dict:
        situation = self.analyze_situation(perception_input)

        if situation.get("user_active"):
            return {"focus": "user", "intent": "respond_to_user"}

        if self.internal_state.curiosity > 0.7:
            return {"focus": "self", "intent": "explore", "target": "minecraft"}

        if situation.get("has_bullet_comments") and self.current_focus == "idle":
            return {"focus": "stream", "intent": "answer_bullet_comment"}

        return {"focus": "self", "intent": "self_talk"}

    def analyze_situation(self, perception_input: Dict) -> Dict:
        situation = {
            "user_active": perception_input["user_input"] is not None,
            "has_bullet_comments": len(perception_input.get("bullet_comments", [])) > 0,
            "time_of_day": time.localtime().tm_hour
        }
        return situation

    def _read_diary(self, filepath):
        """读取日记文件内容"""
        try:
            with self.diary_lock:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(200)  # 只读取前200个字符，避免一次性读取太多
            return content
        except Exception as e:
            logger.error(f"[NeuroSama] 读取日记失败: {e}")
            return None

    def _write_diary(self, content):
        """写入日记内容到文件"""
        try:
            import os
            from datetime import datetime
            
            # 确保日记目录存在
            if not os.path.exists(self.diary_path):
                os.makedirs(self.diary_path)
                logger.info(f"[NeuroSama] 创建日记目录: {self.diary_path}")
            
            # 生成日记文件名（格式：2024-01-01_日记.txt）
            diary_filename = os.path.join(self.diary_path, f"{datetime.now().strftime('%Y-%m-%d')}_日记.txt")
            
            # 生成日记条目
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 计算使用时间（从启动到现在）
            uptime_seconds = time.time() - self.start_time if hasattr(self, 'start_time') else 0
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
            
            # 收集学习到的内容
            learned_content = self._get_learned_content()
            
            # 生成日记条目
            diary_entry = [
                "-" * 60,
                f"时间: {timestamp}",
                f"使用时间: {uptime_str}",
                f"情绪: {self.internal_state.emotion}",
                f"能量: {self.internal_state.energy:.2f}",
                f"好奇心: {self.internal_state.curiosity:.2f}",
                "",
                f"内容: {content}",
                "",
                "学习到的内容:",
                learned_content if learned_content else "• 暂无新的学习内容",
                "-" * 60,
                ""
            ]
            
            # 写入日记文件（追加模式），使用锁保护
            with self.diary_lock:
                with open(diary_filename, 'a', encoding='utf-8') as f:
                    f.write("\n".join(diary_entry))
            
            logger.info(f"[NeuroSama] 日记已写入: {diary_filename}")
            return True
        except Exception as e:
            logger.error(f"[NeuroSama] 写入日记失败: {e}")
            return False

    def _get_learned_content(self):
        """获取学习到的内容"""
        try:
            learned_items = []
            
            # 从记忆中获取最近的事件
            recent_events = self.memory.long_term_mem[-5:] if self.memory.long_term_mem else []
            
            for event in recent_events:
                event_str = str(event)
                if "user_interaction" in event_str or "chat_message" in event_str:
                    learned_items.append("• 与用户进行了交流，了解了用户的需求")
                    break
            
            # 从任务历史中获取学习内容
            if self.task_history:
                recent_task = self.task_history[-1]
                if recent_task.get("status") == "completed":
                    task_desc = recent_task.get("description", "")
                    learned_items.append(f"• 完成了任务: {task_desc}")
            
            # 从情绪变化中获取学习内容
            emotion_changes = []
            for activity in self.internal_state.activity_history[-3:]:
                emotion_changes.append(activity["emotion"])
            
            if len(set(emotion_changes)) > 1:
                learned_items.append("• 体验了不同的情绪状态")
            
            # 限制学习内容的数量
            if learned_items:
                return "\n".join([f"• {item[2:]}" for item in learned_items[:3]])
            else:
                return ""
        except Exception as e:
            logger.error(f"[NeuroSama] 获取学习内容失败: {e}")
            return ""

    def _initialize_tools(self):
        """初始化工具系统"""
        import asyncio
        
        # 注册工具
        async def screen_analyzer(params: dict):
            """屏幕识别工具"""
            print(f"🔍 [屏幕工具] 开始分析: {params.get('prompt', '')}")
            # 这里调用GLM-4.6V的视觉API
            await asyncio.sleep(2)  # 模拟耗时操作
            return {"description": "屏幕上有一个Chrome浏览器图标和任务栏"}

        async def mouse_controller(params: dict):
            """鼠标控制工具"""
            print(f"🖱️ [鼠标工具] 执行: {params.get('action')} 在 {params.get('position')}")
            # 这里调用PyAutoGUI
            await asyncio.sleep(0.5)  # 模拟耗时操作
            return {"success": True}

        async def tts_generator(params: dict):
            """语音合成工具"""
            print(f"🔊 [语音工具] 合成: {params.get('text')[:20]}...")
            # 这里调用GPT-SoVITS
            await asyncio.sleep(0.8)  # 模拟耗时操作
            return {"audio_path": "output.wav"}

        async def bullet_comment_reader(params: dict):
            """B站弹幕工具"""
            print(f"💬 [弹幕工具] 获取最新弹幕")
            # 这里调用B站API
            await asyncio.sleep(1)  # 模拟耗时操作
            return {"comments": ["主播好可爱", "2333", "再来一首"]}

        async def minecraft_controller(params: dict):
            """Minecraft控制工具"""
            action = params.get('action', 'explore')
            print(f"🎮 [Minecraft工具] 执行: {action}")
            
            # 导入必要的模块
            import time
            
            # 导入Minecraft客户端
            from brain.minecraft_client import get_or_create_minecraft_client
            
            # 检查Minecraft模式状态，如果已关闭则不执行任何操作
            if not neuro_agent_instance.minecraft_mode_enabled:
                print("[Minecraft工具] 模式已关闭，不执行任何操作")
                return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": False}
            
            # 获取Minecraft客户端实例
            minecraft_client = get_or_create_minecraft_client()
            
            # 确保游戏正在运行
            if not minecraft_client.is_game_running():
                # 尝试启动游戏
                start_success = minecraft_client.start_game()
                if not start_success:
                    return {"success": False, "message": "无法启动Minecraft游戏", "action": action, "game_running": False}
            
            # 执行实际的游戏控制
            success = False
            message = ""
            
            # 检查Minecraft模式状态，如果已关闭则不执行任何操作
            if not neuro_agent_instance.minecraft_mode_enabled:
                print("[Minecraft工具] 模式已关闭，不执行任何操作")
                return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
            
            if action == 'explore':
                # 探索：向前移动一段时间
                success = minecraft_client.control("forward", 3.0)
                message = "正在探索Minecraft世界"
            elif action == 'mine':
                # 挖矿：攻击动作
                success = minecraft_client.control("attack")
                message = "正在挖矿"
            elif action == 'mine_wood':
                # 挖取木头任务
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，不执行挖矿操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                success = minecraft_client.mine_wood()
                message = "正在挖取第一个木头"
            elif action == 'build':
                # 建造：使用动作
                success = minecraft_client.control("use")
                message = "正在建造"
            elif action == 'fight':
                # 战斗：攻击动作
                success = minecraft_client.control("attack")
                message = "正在战斗"
            elif action == 'jump':
                # 跳跃
                success = minecraft_client.control("jump")
                message = "跳跃"
            elif action == 'move_forward':
                # 向前移动
                duration = params.get('duration', 1.0)
                success = minecraft_client.control("forward", duration)
                message = f"向前移动{duration}秒"
            elif action == 'move_backward':
                # 向后移动
                duration = params.get('duration', 1.0)
                success = minecraft_client.control("backward", duration)
                message = f"向后移动{duration}秒"
            elif action == 'move_left':
                # 向左移动
                duration = params.get('duration', 1.0)
                success = minecraft_client.control("left", duration)
                message = f"向左移动{duration}秒"
            elif action == 'move_right':
                # 向右移动
                duration = params.get('duration', 1.0)
                success = minecraft_client.control("right", duration)
                message = f"向右移动{duration}秒"
            elif action == 'look_around':
                # 环顾四周（更全面的环顾）
                print("[Minecraft工具] 执行全面环顾四周")
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，不执行环顾四周操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                # 向右看
                minecraft_client.look_around(150, 0)
                time.sleep(0.5)
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，中断环顾四周操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                # 向左看
                minecraft_client.look_around(-300, 0)
                time.sleep(0.5)
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，中断环顾四周操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                # 向下看
                minecraft_client.look_around(150, -50)
                time.sleep(0.5)
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，中断环顾四周操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                # 向上看
                minecraft_client.look_around(0, 50)
                time.sleep(0.5)
                # 检查Minecraft模式状态，如果已关闭则不执行任何操作
                if not neuro_agent_instance.minecraft_mode_enabled:
                    print("[Minecraft工具] 模式已关闭，中断环顾四周操作")
                    return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
                # 回到中心
                minecraft_client.look_around(-150, 0)
                time.sleep(0.5)
                success = True
                message = "完成全面环顾四周"
            elif action == 'detect_block':
                # 检测方块
                detected_block = minecraft_client.detect_block()
                success = True
                message = f"检测到方块: {detected_block}"
            elif action == 'turn':
                # 转向指定方向
                direction = params.get('direction', 'left')
                success = minecraft_client.turn_towards(direction)
                message = f"转向 {direction}"
            elif action == 'execute_command':
                # 执行命令
                command = params.get('command', 'help')
                success = minecraft_client.execute_command(command)
                message = f"执行命令: {command}"
            else:
                success = True
                message = f"执行Minecraft操作: {action}"
            
            # 检查Minecraft模式状态，如果已关闭则返回失败
            if not neuro_agent_instance.minecraft_mode_enabled:
                print("[Minecraft工具] 模式已关闭，操作已中断")
                return {"success": False, "message": "Minecraft模式已关闭", "action": action, "game_running": True}
            
            return {
                "success": success,
                "message": message,
                "action": action,
                "game_running": minecraft_client.is_game_running()
            }

        async def minecraft_status(params: dict):
            """Minecraft状态获取工具"""
            print(f"📊 [Minecraft工具] 获取游戏状态")
            
            # 导入Minecraft客户端
            from brain.minecraft_client import get_or_create_minecraft_client
            
            # 获取Minecraft客户端实例
            minecraft_client = get_or_create_minecraft_client()
            
            # 获取实际的游戏状态
            game_status = minecraft_client.get_game_status()
            
            # 构建返回结果
            result = {
                "success": True,
                "game_status": game_status
            }
            
            # 如果API可用，使用实际的游戏数据
            if game_status.get("api_used", False):
                player_data = game_status.get("player", {})
                world_data = game_status.get("world", {})
                
                result["player"] = {
                    "name": "NeuroSama",
                    "position": player_data.get("position", [100, 64, 200]),
                    "health": player_data.get("health", 20),
                    "hunger": player_data.get("hunger", 20),
                    "experience": 100  # 经验值需要额外获取
                }
                
                # 从世界时间判断是白天还是黑夜
                world_time = world_data.get("time", 0)
                time_of_day = "day" if 0 < world_time < 12000 else "night"
                
                result["world"] = {
                    "biome": "forest",  # 生物群系需要额外获取
                    "time": time_of_day,
                    "weather": world_data.get("weather", "clear"),
                    "nearby_blocks": ["grass", "oak_log", "stone"]  # 附近方块需要额外获取
                }
                
                result["entities"] = [
                    {"type": "sheep", "position": [105, 64, 205]},
                    {"type": "cow", "position": [95, 64, 195]}
                ]  # 实体需要额外获取
            else:
                # 使用默认模拟数据
                result["player"] = {
                    "name": "NeuroSama",
                    "position": [100, 64, 200],
                    "health": 20,
                    "hunger": 20,
                    "experience": 100
                }
                
                result["world"] = {
                    "biome": "forest",
                    "time": "day",
                    "weather": "clear",
                    "nearby_blocks": ["grass", "oak_log", "stone"]
                }
                
                result["entities"] = [
                    {"type": "sheep", "position": [105, 64, 205]},
                    {"type": "cow", "position": [95, 64, 195]}
                ]
            
            return result
        
        # 注册工具到路由器
        self.tool_router.register_tool(
            "analyze_screen", 
            screen_analyzer, 
            "分析屏幕内容，返回文字描述"
        )
        self.tool_router.register_tool(
            "control_mouse", 
            mouse_controller, 
            "控制鼠标移动和点击"
        )
        self.tool_router.register_tool(
            "generate_speech", 
            tts_generator, 
            "将文本合成为语音"
        )
        self.tool_router.register_tool(
            "get_bullet_comments", 
            bullet_comment_reader, 
            "获取B站直播间的最新弹幕"
        )
        
        # 注册Minecraft工具
        self.tool_router.register_tool(
            "control_minecraft", 
            minecraft_controller, 
            "控制Minecraft游戏，执行探索、挖矿、建造、战斗等操作"
        )
        self.tool_router.register_tool(
            "get_minecraft_status", 
            minecraft_status, 
            "获取Minecraft游戏状态，包括玩家位置、健康值、世界信息等"
        )
        
        # 设置回调函数
        self.tool_router.set_ai_callback(self.on_tool_completed)

    def on_tool_completed(self, tool_call):
        """当工具执行完成时的回调函数"""
        print(f"\n📨 [Neuro-Sama收到工具结果] 任务ID: {tool_call.id}")
        print(f"   工具: {tool_call.tool_name}")
        print(f"   状态: {tool_call.status.value}")
        
        if tool_call.status.value == "completed":
            print(f"   结果: {tool_call.result}")
            # 将结果存入记忆系统
            self.memory.update({
                "tool_result": {
                    "tool_name": tool_call.tool_name,
                    "result": tool_call.result,
                    "timestamp": time.time()
                }
            })
            # 生成工具使用日记
            self.generate_diary("tool_usage", f"使用了{tool_call.tool_name}工具，结果: {str(tool_call.result)[:50]}...")
        else:
            print(f"   错误: {tool_call.error}")
            # 将错误存入记忆系统
            self.memory.update({
                "tool_error": {
                    "tool_name": tool_call.tool_name,
                    "error": tool_call.error,
                    "timestamp": time.time()
                }
            })

    async def call_tool(self, tool_name, parameters):
        """调用工具"""
        if hasattr(self, 'tool_router'):
            task_id = await self.tool_router.call_tool(tool_name, parameters)
            print(f"🤖 [Neuro-Sama] 调用工具: {tool_name} (任务ID: {task_id})")
            return task_id
        return None

    def generate_diary(self, event_type="general", content=""):
        """生成日记
        
        Args:
            event_type: 事件类型，可选值: general, user_interaction, self_talk, exploration
            content: 日记内容
        """
        # 根据事件类型生成不同的日记内容
        if not content:
            if event_type == "user_interaction":
                content = "与用户进行了愉快的交流"
            elif event_type == "self_talk":
                content = "进行了自我对话和思考"
            elif event_type == "exploration":
                content = "探索了新的环境和可能性"
            else:
                content = "度过了平静的时光"
        
        # 写入日记
        return self._write_diary(content)

    def generate_daily_summary(self):
        """生成每日总结日记"""
        from datetime import datetime
        
        # 生成每日总结内容
        summary_content = [
            "今日总结:",
            f"- 情绪状态: {self.internal_state.emotion}",
            f"- 能量水平: {self.internal_state.energy:.2f}",
            f"- 好奇心水平: {self.internal_state.curiosity:.2f}",
            f"- 记忆条目数: {len(self.memory.long_term_mem)}",
            f"- 任务完成数: {len(self.task_history)}"
        ]
        
        content = "\n".join(summary_content)
        return self.generate_diary("general", content)

    def _check_diary_read(self):
        """检查是否需要读取日记"""
        current_time = time.time()
        
        if (self.diary_read_count < self.max_diaries_to_read and
            self.diary_files and
            self.current_diary_index < len(self.diary_files) and
            current_time - self.last_diary_read_time >= self.diary_read_interval):
            
            return True
        return False

    def main_loop(self):
        print(f"{self.name} 启动... 开始像人一样思考")
        self.is_running = True
        loop_count = 0

        while self.is_running:
            loop_count += 1
            current_time = time.time()
            
            # 检测前端是否还在运行
            self._check_frontend_status()


            # 检查是否有新的聊天消息
            if self.chat_message_queue:
                latest_message = self.chat_message_queue[-1]
                message_time = latest_message["timestamp"]
                
                # 如果有新消息且距离上次聊天时间超过阈值，重置无接触计时器
                if message_time > self.last_chat_time:
                    print(f"[聊天监测]: 收到新消息 - {latest_message['sender']}: {latest_message['message'][:30]}...")
                    self.reset_no_contact_timer()
                    # 处理用户活动
                    self._handle_user_activity()

            # 检查是否需要读取日记
            if self._check_diary_read():
                diary_file = self.diary_files[self.current_diary_index]
                diary_content = self._read_diary(diary_file)
                
                if diary_content:
                    print(f"[Neuro-Sama阅读日记]: 正在查看 {os.path.basename(diary_file)}")
                    print(f"[日记内容]: {diary_content}...")
                    print("[系统]: 慢慢阅读中...")
                    
                    # 更新状态
                    self.diary_read_count += 1
                    self.current_diary_index += 1
                    self.last_diary_read_time = current_time
                    
                    # 记录到记忆
                    self.memory.update({
                        "diary_read": {
                            "file": diary_file,
                            "content": diary_content,
                            "timestamp": current_time
                        }
                    })
                    
                    # 等待一段时间再继续
                    time.sleep(10)

            current_perception = self.perception.gather_information()

            self.memory.update({"perception": current_perception, "loop": loop_count})
            self.internal_state.calculate_state(self.memory)

            # 更新长期规划
            self._update_long_term_plans()
            
            # 生成新任务
            self._generate_task()
            
            # 选择下一个任务
            if not self.current_task:
                self.select_next_task()

            decision = self.cognitive_process(current_perception)

            # 冷暴力检测
            current_time = time.time()
            time_since_last_user_activity = current_time - self.last_user_activity_time
            
            if time_since_last_user_activity > self.cold_violence_threshold:
                if not self.cold_violence_detected:
                    self.cold_violence_detected = True
                    self.cold_violence_start_time = current_time
                    # 冷暴力时情绪低落
                    self.internal_state.emotion = "sad"
                    self.internal_state.energy = max(0.3, self.internal_state.energy - 0.3)
                    self.internal_state.curiosity = max(0.2, self.internal_state.curiosity - 0.4)
                    print(f"[情绪变化] 检测到冷暴力，情绪变为低落，能量: {self.internal_state.energy:.2f}, 好奇心: {self.internal_state.curiosity:.2f}")
                    # 生成冷暴力日记
                    self.generate_diary("cold_violence", "被使用者冷暴力，感到情绪低落")
            else:
                if self.cold_violence_detected:
                    self.cold_violence_detected = False
                    # 恢复正常情绪
                    self.internal_state.emotion = "neutral"
                    print("[情绪变化] 检测到用户互动，情绪恢复正常")
            
            # 工具使用逻辑
            import asyncio
            import random
            if hasattr(self, 'tool_router'):
                # Minecraft模式优先处理，不受冷暴力状态影响
                if self.minecraft_mode_enabled:
                    print("[Minecraft模式] 模式已启用，执行控制操作")
                    # 检查是否需要执行Minecraft操作
                    current_time = time.time()  # 确保使用最新的时间
                    if current_time - self.last_minecraft_activity_time > 5:  # 减少cooldown到5秒
                        # 再次检查Minecraft模式状态，如果已关闭则跳过
                        if not self.minecraft_mode_enabled:
                            print("[Minecraft模式] 模式已关闭，跳过操作")
                            continue
                        
                        # 获取游戏状态，根据状态做出决策
                        print(f"[Minecraft模式] 时间差: {current_time - self.last_minecraft_activity_time}")
                        
                        # 首先获取游戏状态
                        task_id = asyncio.run(self.call_tool("get_minecraft_status", {}))
                        print(f"[Minecraft模式] 获取游戏状态任务ID: {task_id}")
                        
                        # 等待工具执行完成（最多等待10秒）
                        max_wait_time = 10
                        start_time = time.time()
                        task_status = None
                        
                        while time.time() - start_time < max_wait_time:
                            # 检查Minecraft模式状态，如果已关闭则中断
                            if not self.minecraft_mode_enabled:
                                print("[Minecraft模式] 模式已关闭，中断操作")
                                break
                            
                            if hasattr(self, 'tool_router'):
                                task_status = asyncio.run(self.tool_router.get_task_status(task_id))
                                if task_status:
                                    print(f"[Minecraft模式] 任务状态: {task_status.status.value}")
                                    if task_status.status.value == "completed":
                                        print(f"[Minecraft模式] 任务已完成，状态: {task_status.status.value}")
                                        break
                            time.sleep(0.5)
                        
                        # 检查Minecraft模式状态，如果已关闭则跳过后续操作
                        if not self.minecraft_mode_enabled:
                            print("[Minecraft模式] 模式已关闭，跳过后续操作")
                            continue
                        
                        # 再次检查任务状态，确保获取最新状态
                        if hasattr(self, 'tool_router'):
                            task_status = asyncio.run(self.tool_router.get_task_status(task_id))
                            if task_status:
                                print(f"[Minecraft模式] 最终任务状态: {task_status.status.value}")
                            else:
                                print(f"[Minecraft模式] 最终任务状态: 未知")
                        
                        # 获取任务状态和结果
                        if hasattr(self, 'tool_router') and task_status and task_status.status.value == "completed":
                            status_result = task_status.result
                            print(f"[Minecraft模式] 获取游戏状态成功: {status_result}")
                            
                            # 根据游戏状态选择操作
                            blocks = status_result.get("game_status", {}).get("blocks", {})
                            center_block = blocks.get("center_block", "")
                        else:
                            print(f"[Minecraft模式] 获取游戏状态失败，任务状态: {task_status.status.value if task_status else '未知'}")
                            center_block = ""
                        
                        print(f"[Minecraft模式] 屏幕中心方块: {center_block}")
                        
                        # 检查Minecraft模式状态，如果已关闭则跳过后续操作
                        if not self.minecraft_mode_enabled:
                            print("[Minecraft模式] 模式已关闭，跳过后续操作")
                            continue
                        
                        # 构建更智能的操作序列
                        if center_block == "oak_log":
                            # 如果屏幕中心是木头，开始挖矿
                            print("[Minecraft模式] 发现木头，开始挖矿")
                            asyncio.run(self.call_tool("control_minecraft", {"action": "mine_wood"}))
                        elif center_block == "stone":
                            # 如果是石头，也可以挖矿
                            print("[Minecraft模式] 发现石头，开始挖矿")
                            asyncio.run(self.call_tool("control_minecraft", {"action": "mine"}))
                        elif center_block == "grass" or center_block == "dirt":
                            # 如果是草或泥土，可以向前移动
                            print("[Minecraft模式] 发现可通行区域，向前移动")
                            asyncio.run(self.call_tool("control_minecraft", {"action": "explore"}))
                        else:
                            # 如果不是已知方块，环顾四周寻找资源
                            print("[Minecraft模式] 未发现资源，环顾四周")
                            asyncio.run(self.call_tool("control_minecraft", {"action": "look_around"}))
                            # 然后向前移动
                            asyncio.run(self.call_tool("control_minecraft", {"action": "explore"}))
                        
                        # 检查Minecraft模式状态，如果已关闭则跳过更新
                        if not self.minecraft_mode_enabled:
                            print("[Minecraft模式] 模式已关闭，跳过更新活动时间")
                            continue
                        
                        self.last_minecraft_activity_time = time.time()  # 使用最新的时间更新
                        print(f"[Minecraft模式] 更新最后活动时间: {self.last_minecraft_activity_time}")
                else:
                    print("[Minecraft模式] 模式未启用，跳过控制操作")
                
                # 冷暴力状态下减少工具使用
                if self.cold_violence_detected:
                    # 冷暴力状态下减少工具使用
                    if random.random() < 0.3:  # 30%概率使用工具
                        # 冷暴力时主要使用语音合成工具表达情绪
                        asyncio.run(self.call_tool("generate_speech", {"text": "你怎么不说话了？是不是不想理我了..."}))
                elif loop_count % 20 == 0:  # 每20个循环尝试使用其他工具
                    # 根据当前状态选择工具
                    if self.internal_state.curiosity > 0.7:
                        # 好奇心高时，分析屏幕
                        asyncio.run(self.call_tool("analyze_screen", {"prompt": "描述当前屏幕内容"}))
                    elif self.current_focus == "stream":
                        # 关注流媒体时，获取弹幕
                        asyncio.run(self.call_tool("get_bullet_comments", {}))
                    elif self.internal_state.energy > 0.6:
                        # 能量高时，控制鼠标
                        asyncio.run(self.call_tool("control_mouse", {"action": "click", "position": [random.randint(100, 500), random.randint(100, 500)]}))

            if decision["focus"] == "user":
                self.handle_user_interaction(decision, current_perception)
                # 处理用户活动
                self._handle_user_activity()
            elif decision["focus"] == "self":
                self.handle_self_agenda(decision)
            elif decision["focus"] == "stream":
                self.handle_stream_interaction(decision)

            result = self.observe_action_result()
            self.memory.update({"action_result": result})

            time.sleep(1)

    def handle_user_interaction(self, decision: Dict, perception: Dict):
        print(f"[思考中]: 用户需要我的关注，优先级最高")
        
        # 根据情绪状态生成回应
        emotion_response = self.emotion_manager.get_emotion_response()
        
        # 如果有聊天消息，分析最后一条消息
        if self.chat_message_queue:
            last_message = self.chat_message_queue[-1]["message"]
            # 简单的回应逻辑
            if any(keyword in last_message.lower() for keyword in ["你好", "hello", "hi"]):
                response = f"你好！{emotion_response}"
            elif any(keyword in last_message.lower() for keyword in ["再见", "bye", "goodbye"]):
                response = f"再见！希望能再和你聊天！"
            else:
                response = f"{emotion_response} 你刚才说：{last_message[:20]}..."
        else:
            response = emotion_response
        
        self.action.execute({"type": "speak", "content": response})
        self.current_focus = "user"
        
        # 更新情绪状态（AI自己的回应）
        self.emotion_manager.update_emotions(response, is_user_input=False)
        
        # 生成用户交互日记
        if self.chat_message_queue:
            last_message = self.chat_message_queue[-1]["message"]
            diary_content = f"与用户交流，用户说：{last_message[:50]}... 我回应：{response[:50]}..."
        else:
            diary_content = f"与用户交流，我回应：{response[:50]}..."
        self.generate_diary("user_interaction", diary_content)
        
        # AI回答后开始无接触状态计时
        self._handle_ai_response()

    def handle_self_agenda(self, decision: Dict):
        intent = decision.get("intent", "idle")

        if intent == "explore":
            game = decision.get("target", "minecraft")
            print(f"[思考中]: 我有点好奇，想去{game}看看")
            self.action.execute({
                "type": "control",
                "action": f"启动{game}并探索"
            })
            # 生成探索日记
            self.generate_diary("exploration", f"探索了{game}，充满了好奇心和探索欲")
            # AI提出想法后开始无接触状态计时
            self._handle_ai_response()
        elif intent == "self_talk":
            # 根据情绪状态生成自言自语内容
            talk = self.emotion_manager.get_emotion_response()
            self.action.execute({"type": "speak", "content": talk})
            # 更新情绪状态
            self.emotion_manager.update_emotions(talk, is_user_input=False)
            # 生成自我对话日记
            self.generate_diary("self_talk", f"进行了自我对话：{talk[:50]}...")
            # AI自言自语后开始无接触状态计时
            self._handle_ai_response()
        else:
            # 根据情绪状态生成空闲时的思考内容
            thought = self.emotion_manager.get_emotion_response()
            print(f"[思考中]: 空闲状态，{thought}")
            self.action.execute({"type": "speak", "content": thought})
            # 更新情绪状态
            self.emotion_manager.update_emotions(thought, is_user_input=False)
            # 生成一般日记
            self.generate_diary("general", f"空闲时的思考：{thought[:50]}...")
            # AI思考后开始无接触状态计时
            self._handle_ai_response()

        self.current_focus = "self"

    def handle_stream_interaction(self, decision: Dict):
        print(f"[思考中]: 有弹幕，我来看看...")
        
        # 根据情绪状态生成弹幕回应
        emotion_response = self.emotion_manager.get_emotion_response()
        response = f"这条弹幕有意思！{emotion_response}"
        
        self.action.execute({"type": "speak", "content": response})
        self.current_focus = "stream"
        
        # 更新情绪状态
        self.emotion_manager.update_emotions(response, is_user_input=False)
        
        # 生成弹幕交互日记
        self.generate_diary("general", f"回应了弹幕，内容：{response[:50]}...")
        
        # AI回答弹幕后开始无接触状态计时
        self._handle_ai_response()

    def observe_action_result(self) -> Dict:
        return {"success": True, "timestamp": time.time()}

    def add_chat_message(self, message: str, sender: str = "user"):
        """添加聊天消息到队列"""
        current_time = time.time()
        self.chat_message_queue.append({
            "message": message,
            "sender": sender,
            "timestamp": current_time
        })
        self.last_chat_time = current_time
        logger.info(f"[NeuroSama] 收到聊天消息: {sender} - {message[:50]}...")
        
        # 更新情绪状态
        if sender == "user":
            dominant_emotion = self.emotion_manager.update_emotions(message, is_user_input=True)
            logger.info(f"[NeuroSama情绪管理]: 用户消息情绪分析 - 主导情绪: {dominant_emotion}")

    def check_no_contact_status(self) -> bool:
        """检查是否处于无接触状态"""
        current_time = time.time()
        
        # 如果没有聊天消息，或者距离上次聊天时间超过阈值，则处于无接触状态
        if self.last_chat_time == 0:
            # 从未收到过聊天消息，不视为无接触状态
            return False
        
        no_contact_duration = current_time - self.last_chat_time
        return no_contact_duration >= self.no_contact_threshold

    def reset_no_contact_timer(self):
        """重置无接触计时器"""
        self.last_chat_time = time.time()
        self.no_contact_start_time = time.time()
        logger.info(f"[NeuroSama] 无接触计时器已重置")

    def _handle_ai_response(self):
        """处理AI回答或提问后的无接触状态"""
        print("[系统]: AI回答问题或提出问题后，开始无接触状态计时...")
        self.reset_no_contact_timer()
        
        # 进入无接触状态
        print("[系统]: 长时间无接触状态，等待中...")
        time.sleep(self.no_contact_threshold)
    
    def _setup_keyboard_listener(self):
        """设置键盘监听器，监听F9键以切换Minecraft模式"""
        try:
            import keyboard
            
            def on_f9_press():
                """F9键按下时的回调函数"""
                # 切换Minecraft模式
                self.toggle_minecraft_mode()
                
                # 如果禁用模式，确保停止所有相关操作
                if not self.minecraft_mode_enabled:
                    if hasattr(self, 'mouse_control_thread') and self.mouse_control_thread:
                        self.mouse_control_stop_event.set()
                        if self.mouse_control_thread.is_alive():
                            self.mouse_control_thread.join(timeout=1)
            
            # 注册F9键的按下事件
            keyboard.add_hotkey('f9', on_f9_press)
            print("[系统]: 已注册F9键为Minecraft模式切换快捷键")
            
        except Exception as e:
            print(f"[系统]: 设置键盘监听器失败: {e}")
    
    def _check_frontend_status(self):
        """检查前端是否还在运行
        
        如果前端关闭，则自动禁用Minecraft模式
        """
        try:
            import psutil
            frontend_path = "F:\\BaiduNetdiskDownload\\N.E.K.O\\N.E.K.O.exe"
            frontend_running = False
            
            for process in psutil.process_iter(['name', 'exe']):
                try:
                    process_name = process.info['name']
                    process_exe = process.info['exe']
                    
                    # 检查是否有匹配的进程
                    if process_exe and frontend_path.lower() in process_exe.lower():
                        frontend_running = True
                        break
                    elif process_name and 'n.e.k.o' in process_name.lower():
                        frontend_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 如果前端已关闭，但Minecraft模式仍启用，则禁用它
            if not frontend_running and self.minecraft_mode_enabled:
                print("[系统]: 检测到前端已关闭，自动禁用Minecraft模式")
                self.minecraft_mode_enabled = False
                
                # 确保鼠标控制停止
                if hasattr(self, 'mouse_control_thread') and self.mouse_control_thread:
                    self.mouse_control_stop_event.set()
                    if self.mouse_control_thread.is_alive():
                        self.mouse_control_thread.join(timeout=1)
                        
        except ImportError:
            # psutil未安装，跳过前端检测
            pass
        except Exception as e:
            print(f"[系统]: 前端状态检测失败: {e}")

    def _mouse_control_loop(self):
        """鼠标控制后台循环"""
        print("[Neuro-Sama鼠标控制]: 开始自主控制鼠标...")
        
        # 获取屏幕尺寸
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # 定义基于AI意图的行为模式
        ai_intents = [
            {"intent": "explore", "targets": [
                (screen_width // 5, screen_height // 5),     # 左上区域
                (screen_width * 4 // 5, screen_height // 5), # 右上区域
                (screen_width // 5, screen_height * 4 // 5), # 左下区域
                (screen_width * 4 // 5, screen_height * 4 // 5), # 右下区域
                (screen_width // 2, screen_height // 10),    # 顶部中间
                (screen_width // 2, screen_height * 9 // 10), # 底部中间
            ], "description": "探索屏幕四周"},
            {"intent": "focus", "targets": [
                (screen_width // 2, screen_height // 2),     # 中心位置
                (screen_width * 3 // 7, screen_height * 3 // 7), # 左上中心
                (screen_width * 4 // 7, screen_height * 3 // 7), # 右上中心
                (screen_width * 3 // 7, screen_height * 4 // 7), # 左下中心
                (screen_width * 4 // 7, screen_height * 4 // 7), # 右下中心
            ], "description": "聚焦屏幕中心"},
            {"intent": "interact", "targets": [
                (screen_width // 4, screen_height // 2),     # 左侧中间
                (screen_width * 3 // 4, screen_height // 2), # 右侧中间
                (screen_width // 2, screen_height // 4),     # 上方中间
                (screen_width // 2, screen_height * 3 // 4), # 下方中间
                (screen_width // 3, screen_height // 3),     # 左上交互点
                (screen_width * 2 // 3, screen_height // 3), # 右上交互点
                (screen_width // 3, screen_height * 2 // 3), # 左下交互点
                (screen_width * 2 // 3, screen_height * 2 // 3), # 右下交互点
            ], "description": "与屏幕元素交互"},
            {"intent": "read", "targets": [
                (screen_width // 2, screen_height // 3),     # 上方中间
                (screen_width // 2, screen_height // 2),     # 中心位置
                (screen_width // 2, screen_height * 2 // 3), # 下方中间
                (screen_width * 3 // 7, screen_height * 3 // 7), # 左上阅读点
                (screen_width * 4 // 7, screen_height * 3 // 7), # 右上阅读点
                (screen_width * 3 // 7, screen_height * 4 // 7), # 左下阅读点
                (screen_width * 4 // 7, screen_height * 4 // 7), # 右下阅读点
            ], "description": "阅读屏幕内容"},
            {"intent": "rest", "targets": [
                (screen_width // 10, screen_height // 10),   # 左上角休息点
                (screen_width * 9 // 10, screen_height * 9 // 10), # 右下角休息点
            ], "description": "休息状态"},
            {"intent": "observe", "targets": [
                (screen_width // 2, screen_height // 2),     # 中心观察点
                (screen_width // 3, screen_height // 2),     # 左侧观察点
                (screen_width * 2 // 3, screen_height // 2), # 右侧观察点
            ], "description": "观察环境"},
            {"intent": "taskbar", "targets": [
                (screen_width // 4, screen_height - 20),     # 任务栏左侧
                (screen_width // 2, screen_height - 20),     # 任务栏中间
                (screen_width * 3 // 4, screen_height - 20), # 任务栏右侧
                (screen_width - 100, screen_height - 20),    # 任务栏右侧系统托盘
            ], "description": "任务栏操作"},
        ]
        
        try:
            current_intent = None
            current_targets = []
            target_index = 0
            intent_duration = 0
            max_intent_duration = random.randint(5, 10)  # 每个意图的持续时间
            intent_history = []  # 意图历史记录
            
            while not self.mouse_control_stop_event.is_set():
                # 检查Minecraft模式是否启用，如果启用则暂停自主鼠标控制
                if self.minecraft_mode_enabled:
                    time.sleep(1)  # 暂停1秒后再次检查
                    continue
                
                # 每过一段时间或当前意图完成后，选择新的意图
                if current_intent is None or intent_duration >= max_intent_duration:
                    # 智能意图选择逻辑
                    # 1. 基于AI状态的基础权重
                    base_weights = {
                        "explore": self.internal_state.curiosity * 3,  # 好奇心高时更倾向于探索
                        "focus": 0.3,  # 降低基础权重
                        "interact": self.internal_state.energy * 2,  # 能量高时更倾向于交互
                        "read": (1 - self.internal_state.energy) * 2,  # 能量低时更倾向于阅读
                        "rest": (1 - self.internal_state.energy) * 3,  # 能量低时更倾向于休息
                        "observe": 0.5,  # 降低基础观察权重
                        "taskbar": 0.2  # 降低基础任务栏操作权重
                    }
                    
                    # 2. 基于需求的权重调整
                    needs = self.internal_state.needs[-5:]  # 最近的需求
                    if "rest" in needs:
                        base_weights["rest"] *= 2.0
                        base_weights["read"] *= 1.5
                        base_weights["explore"] *= 0.5
                        base_weights["interact"] *= 0.5
                    if "activity" in needs:
                        base_weights["interact"] *= 1.5
                        base_weights["explore"] *= 1.3
                        base_weights["rest"] *= 0.5
                    if "exploration" in needs:
                        base_weights["explore"] *= 2.0
                        base_weights["observe"] *= 1.5
                        base_weights["rest"] *= 0.7
                    
                    # 3. 基于当前任务调整意图权重
                    if self.current_task:
                        task_type = self.current_task["type"]
                        task_progress = time.time() - self.current_task.get("started_at", time.time())
                        
                        # 根据任务进度调整权重
                        if task_progress < 5:  # 任务初期
                            if task_type == "explore":
                                base_weights["explore"] *= 3.0
                                base_weights["observe"] *= 2.0
                            elif task_type == "interact":
                                base_weights["interact"] *= 3.0
                                base_weights["focus"] *= 2.0
                            elif task_type == "read":
                                base_weights["read"] *= 3.0
                                base_weights["focus"] *= 2.0
                        else:  # 任务后期
                            if task_type == "explore":
                                base_weights["explore"] *= 1.5
                                base_weights["observe"] *= 1.2
                            elif task_type == "interact":
                                base_weights["interact"] *= 1.5
                                base_weights["focus"] *= 1.2
                            elif task_type == "read":
                                base_weights["read"] *= 1.5
                                base_weights["focus"] *= 1.2
                    
                    # 4. 添加时间和上下文因素
                    current_time = time.time()
                    hour = time.localtime(current_time).tm_hour
                    
                    # 时间因素：不同时间有不同的行为倾向
                    if 6 <= hour < 12:
                        # 早晨：更倾向于探索和交互
                        base_weights["explore"] *= 1.5
                        base_weights["interact"] *= 1.3
                    elif 12 <= hour < 18:
                        # 下午：更倾向于专注和阅读
                        base_weights["focus"] *= 1.5
                        base_weights["read"] *= 1.3
                    else:
                        # 晚上：更倾向于休息和观察
                        base_weights["rest"] *= 1.5
                        base_weights["observe"] *= 1.3
                    
                    # 5. 上下文因素：基于最近的意图
                    if current_intent:
                        recent_intent = current_intent["intent"]
                        # 避免连续相同意图，但保持一定的连续性
                        if intent_duration < 3:
                            # 短时间内切换，大幅降低相同意图权重
                            base_weights[recent_intent] *= 0.3
                        else:
                            # 长时间后切换，小幅降低相同意图权重
                            base_weights[recent_intent] *= 0.7
                    
                    # 6. 基于用户活动的权重调整
                    current_time = time.time()
                    time_since_last_user_activity = current_time - self.last_user_activity_time
                    
                    if time_since_last_user_activity < self.user_activity_threshold:
                        # 最近有用户活动，增加交互和探索的权重
                        base_weights["interact"] *= 1.8
                        base_weights["explore"] *= 1.3
                        base_weights["focus"] *= 1.5
                        base_weights["rest"] *= 0.3
                        base_weights["read"] *= 0.5
                    elif time_since_last_user_activity < self.user_activity_threshold * 3:
                        # 有用户活动但已过去一段时间，适度调整
                        base_weights["interact"] *= 1.3
                        base_weights["explore"] *= 1.2
                        base_weights["rest"] *= 0.7
                    else:
                        # 长时间无用户活动，增加休息和观察的权重
                        base_weights["rest"] *= 1.5
                        base_weights["read"] *= 1.3
                        base_weights["observe"] *= 1.2
                        base_weights["interact"] *= 0.7
                    
                    # 6. 基于历史行为的调整
                    # 计算最近的意图分布
                    recent_intents = intent_history[-10:]
                    intent_counts = {}
                    for intent in recent_intents:
                        intent_counts[intent] = intent_counts.get(intent, 0) + 1
                    
                    # 避免过度重复相同意图
                    for intent_name, count in intent_counts.items():
                        if count > 3:  # 最近10次中出现超过3次
                            base_weights[intent_name] *= 0.6
                    
                    # 7. 基于长期规划的调整
                    if self.long_term_goals:
                        for goal in self.long_term_goals:
                            goal_type = goal["type"]
                            priority = goal["priority"]
                            
                            if goal_type == "energy_management":
                                # 能量管理目标：平衡休息和活动
                                if self.internal_state.energy < 0.5:
                                    base_weights["rest"] *= (1.0 + priority * 0.8)
                                    base_weights["read"] *= (1.0 + priority * 0.5)
                                else:
                                    base_weights["interact"] *= (1.0 + priority * 0.5)
                                    base_weights["explore"] *= (1.0 + priority * 0.5)
                            elif goal_type == "exploration":
                                # 探索目标：增加探索和交互
                                base_weights["explore"] *= (1.0 + priority * 1.0)
                                base_weights["interact"] *= (1.0 + priority * 0.5)
                                base_weights["focus"] *= (1.0 + priority * 0.3)
                            elif goal_type == "user_interaction":
                                # 用户交互目标：增加交互和专注
                                base_weights["interact"] *= (1.0 + priority * 1.0)
                                base_weights["focus"] *= (1.0 + priority * 0.8)
                                base_weights["explore"] *= (1.0 + priority * 0.5)
                    
                    # 7. 根据权重选择意图
                    total_weight = sum(base_weights.values())
                    if total_weight == 0:
                        # 所有权重为0，随机选择
                        selected_intent = random.choice(ai_intents)
                    else:
                        rand_value = random.uniform(0, total_weight)
                        current_weight = 0
                        selected_intent = None
                        
                        for intent in ai_intents:
                            intent_name = intent["intent"]
                            current_weight += base_weights.get(intent_name, 0)
                            if rand_value <= current_weight:
                                selected_intent = intent
                                break
                        
                        if selected_intent is None:
                            selected_intent = random.choice(ai_intents)
                    
                    # 8. 更新状态
                    current_intent = selected_intent
                    current_targets = current_intent["targets"]
                    target_index = 0
                    intent_duration = 0
                    
                    # 9. 根据意图、任务和长期规划设置更合理的持续时间
                    intent_name = current_intent["intent"]
                    base_duration = 0
                    
                    if self.current_task:
                        # 有任务时，持续时间更长
                        if intent_name in ["rest", "read"]:
                            base_duration = random.randint(15, 25)
                        elif intent_name in ["observe", "explore"]:
                            base_duration = random.randint(10, 20)
                        else:
                            base_duration = random.randint(8, 15)
                    else:
                        # 无任务时，持续时间相对较短
                        if intent_name in ["rest", "read"]:
                            base_duration = random.randint(12, 20)
                        elif intent_name in ["observe", "explore"]:
                            base_duration = random.randint(8, 15)
                        else:
                            base_duration = random.randint(5, 10)
                    
                    # 根据长期规划调整持续时间
                    if self.long_term_goals:
                        for goal in self.long_term_goals:
                            goal_type = goal["type"]
                            priority = goal["priority"]
                            
                            if goal_type == "energy_management":
                                # 能量管理目标：调整休息和活动时间
                                if intent_name in ["rest", "read"]:
                                    base_duration = int(base_duration * (1.0 + priority * 0.5))
                                elif intent_name in ["interact", "explore"]:
                                    base_duration = int(base_duration * (1.0 + priority * 0.3))
                            elif goal_type == "exploration":
                                # 探索目标：增加探索时间
                                if intent_name == "explore":
                                    base_duration = int(base_duration * (1.0 + priority * 0.8))
                                elif intent_name == "interact":
                                    base_duration = int(base_duration * (1.0 + priority * 0.5))
                            elif goal_type == "user_interaction":
                                # 用户交互目标：增加交互时间
                                if intent_name == "interact":
                                    base_duration = int(base_duration * (1.0 + priority * 0.8))
                                elif intent_name == "focus":
                                    base_duration = int(base_duration * (1.0 + priority * 0.5))
                    
                    # 确保持续时间在合理范围内
                    max_intent_duration = max(3, min(base_duration, 30))  # 最短3秒，最长30秒
                    
                    # 10. 记录意图历史
                    intent_history.append(intent_name)
                    if len(intent_history) > 50:
                        intent_history.pop(0)
                    
                    # 11. 输出日志
                    task_info = f"，任务: {self.current_task['description'][:20]}..." if self.current_task else ""
                    print(f"[Neuro-Sama鼠标控制]: 切换意图: {current_intent['description']} (基于状态: 情绪={self.internal_state.emotion}, 能量={self.internal_state.energy:.2f}, 好奇心={self.internal_state.curiosity:.2f}{task_info})")
                    
                    # 12. 清空已处理的需求
                    self.internal_state.needs = []
                
                # 选择当前意图的下一个目标位置
                if target_index >= len(current_targets):
                    target_index = 0
                
                # 基于意图和用户活动动态生成目标点
                intent = current_intent["intent"]
                current_time = time.time()
                time_since_last_user_activity = current_time - self.last_user_activity_time
                
                if intent == "explore":
                    # 探索模式：更广泛的随机目标点
                    if time_since_last_user_activity < self.user_activity_threshold:
                        # 最近有用户活动，更有针对性的探索
                        if random.random() < 0.8:
                            # 80% 概率使用界面元素位置附近
                            elements = [
                                (screen_width // 4, screen_height // 2),  # 左侧中间
                                (screen_width * 3 // 4, screen_height // 2),  # 右侧中间
                                (screen_width // 2, screen_height // 3),  # 上方中间
                                (screen_width // 2, screen_height * 2 // 3),  # 下方中间
                                (screen_width // 3, screen_height // 3),  # 左上区域
                                (screen_width * 2 // 3, screen_height // 3),  # 右上区域
                                (screen_width // 3, screen_height * 2 // 3),  # 左下区域
                                (screen_width * 2 // 3, screen_height * 2 // 3),  # 右下区域
                            ]
                            target_x, target_y = random.choice(elements)
                            final_x = target_x + random.randint(-30, 30)
                            final_y = target_y + random.randint(-30, 30)
                        else:
                            # 20% 概率使用预定义目标点
                            target_x, target_y = current_targets[target_index]
                            target_index += 1
                            final_x = target_x + random.randint(-20, 20)
                            final_y = target_y + random.randint(-20, 20)
                    else:
                        # 无用户活动，更自由的探索
                        if random.random() < 0.7:
                            # 70% 概率使用动态生成的目标点
                            final_x = random.randint(100, screen_width - 100)
                            final_y = random.randint(100, screen_height - 100)
                        else:
                            # 30% 概率使用预定义目标点
                            target_x, target_y = current_targets[target_index]
                            target_index += 1
                            final_x = target_x + random.randint(-20, 20)
                            final_y = target_y + random.randint(-20, 20)
                elif intent == "focus":
                    # 专注模式：围绕中心的目标点
                    center_x, center_y = screen_width // 2, screen_height // 2
                    radius = min(screen_width, screen_height) // 4
                    angle = random.uniform(0, 2 * 3.14159)
                    
                    if time_since_last_user_activity < self.user_activity_threshold:
                        # 最近有用户活动，更集中的焦点
                        radius *= 0.3
                    
                    final_x = int(center_x + radius * random.random() * math.cos(angle))
                    final_y = int(center_y + radius * random.random() * math.sin(angle))
                elif intent == "interact":
                    # 交互模式：模拟与界面元素交互
                    if time_since_last_user_activity < self.user_activity_threshold:
                        # 最近有用户活动，更积极的交互
                        if random.random() < 0.8:
                            # 80% 概率使用界面元素位置
                            elements = [
                                (screen_width // 4, screen_height // 2),  # 左侧中间
                                (screen_width * 3 // 4, screen_height // 2),  # 右侧中间
                                (screen_width // 2, screen_height // 3),  # 上方中间
                                (screen_width // 2, screen_height * 2 // 3),  # 下方中间
                                (screen_width // 3, screen_height // 3),  # 左上区域
                                (screen_width * 2 // 3, screen_height // 3),  # 右上区域
                                (screen_width // 3, screen_height * 2 // 3),  # 左下区域
                                (screen_width * 2 // 3, screen_height * 2 // 3),  # 右下区域
                            ]
                            target_x, target_y = random.choice(elements)
                            final_x = target_x + random.randint(-10, 10)  # 更小的偏移，更精确
                            final_y = target_y + random.randint(-10, 10)
                        else:
                            # 20% 概率使用预定义目标点
                            target_x, target_y = current_targets[target_index]
                            target_index += 1
                            final_x = target_x + random.randint(-10, 10)
                            final_y = target_y + random.randint(-10, 10)
                    else:
                        # 无用户活动，常规交互
                        if random.random() < 0.6:
                            # 60% 概率使用界面元素位置
                            elements = [
                                (screen_width // 4, screen_height // 2),  # 左侧中间
                                (screen_width * 3 // 4, screen_height // 2),  # 右侧中间
                                (screen_width // 2, screen_height // 3),  # 上方中间
                                (screen_width // 2, screen_height * 2 // 3),  # 下方中间
                                (screen_width // 3, screen_height // 3),  # 左上区域
                                (screen_width * 2 // 3, screen_height // 3),  # 右上区域
                                (screen_width // 3, screen_height * 2 // 3),  # 左下区域
                                (screen_width * 2 // 3, screen_height * 2 // 3),  # 右下区域
                            ]
                            target_x, target_y = random.choice(elements)
                            final_x = target_x + random.randint(-15, 15)
                            final_y = target_y + random.randint(-15, 15)
                        else:
                            # 40% 概率使用预定义目标点
                            target_x, target_y = current_targets[target_index]
                            target_index += 1
                            final_x = target_x + random.randint(-15, 15)
                            final_y = target_y + random.randint(-15, 15)
                elif intent == "read":
                    # 阅读模式：文本区域目标点
                    text_areas = [
                        (screen_width // 2, screen_height // 3),  # 上方文本区
                        (screen_width // 2, screen_height // 2),  # 中心文本区
                        (screen_width // 2, screen_height * 2 // 3),  # 下方文本区
                        (screen_width // 3, screen_height // 2),  # 左侧文本区
                        (screen_width * 2 // 3, screen_height // 2),  # 右侧文本区
                    ]
                    target_x, target_y = random.choice(text_areas)
                    final_x = target_x + random.randint(-20, 20)
                    final_y = target_y + random.randint(-10, 10)  # 垂直方向偏移较小，模拟阅读
                elif intent == "taskbar":
                    # 任务栏模式：任务栏区域目标点
                    target_x, target_y = current_targets[target_index]
                    target_index += 1
                    final_x = target_x + random.randint(-10, 10)
                    final_y = target_y + random.randint(-5, 5)  # 任务栏垂直方向偏移较小
                else:
                    # 其他模式：使用预定义目标点
                    target_x, target_y = current_targets[target_index]
                    target_index += 1
                    final_x = target_x + random.randint(-15, 15)
                    final_y = target_y + random.randint(-15, 15)
                
                # 确保位置在屏幕范围内
                final_x = max(50, min(final_x, screen_width - 50))
                final_y = max(50, min(final_y, screen_height - 50))
                
                # 获取当前鼠标位置，实现平滑移动
                current_pos = self.mouse_controller.position
                current_x, current_y = current_pos
                
                # 分步骤移动，使移动更平滑，不是瞬移
                steps = 15  # 增加到15步，使移动更平滑
                move_duration = 0.5  # 总移动时间
                step_duration = move_duration / steps  # 每步的持续时间
                
                for i in range(1, steps + 1):
                    if self.mouse_control_stop_event.is_set() or self.minecraft_mode_enabled:
                        break
                    
                    # 计算每一步的位置
                    step_x = current_x + (final_x - current_x) * i / steps
                    step_y = current_y + (final_y - current_y) * i / steps
                    
                    # 平滑移动到中间位置
                    self.mouse_controller.position = (int(step_x), int(step_y))
                    
                    # 微小的延迟，使移动更自然
                    time.sleep(step_duration)
                
                # 基于意图和用户活动的点击行为
                click_probability = 0.3 if current_intent["intent"] == "interact" else 0.1
                if current_intent["intent"] == "taskbar":
                    click_probability = 0.4  # 任务栏操作时点击概率更高
                
                # 根据用户活动调整点击概率
                current_time = time.time()
                time_since_last_user_activity = current_time - self.last_user_activity_time
                
                if time_since_last_user_activity < self.user_activity_threshold:
                    # 最近有用户活动，增加点击概率
                    if current_intent["intent"] == "interact":
                        click_probability = 0.6  # 大幅增加交互时的点击概率
                    elif current_intent["intent"] == "explore":
                        click_probability = 0.3  # 增加探索时的点击概率
                    else:
                        click_probability *= 1.5  # 其他意图也适度增加
                elif time_since_last_user_activity < self.user_activity_threshold * 2:
                    # 有用户活动但已过去一段时间，小幅增加点击概率
                    click_probability *= 1.2
                
                # 确保点击概率在合理范围内
                click_probability = min(click_probability, 0.8)  # 最大点击概率80%
                
                if random.random() < click_probability and not self.minecraft_mode_enabled:
                    self.mouse_controller.click(mouse.Button.left, 1)
                    print(f"[Neuro-Sama鼠标控制]: 在 ({final_x}, {final_y}) 位置点击 (概率: {click_probability:.2f})")
                
                # 任务导向的行为调整
                if self.current_task:
                    task_type = self.current_task["type"]
                    # 基于任务类型调整行为
                    if task_type == "explore":
                        # 探索任务：增加探索时间
                        wait_time = random.uniform(1.0, 1.5)
                    elif task_type == "interact":
                        # 交互任务：增加交互时间
                        wait_time = random.uniform(0.8, 1.2)
                    elif task_type == "read":
                        # 阅读任务：增加阅读时间
                        wait_time = random.uniform(1.5, 2.5)
                    else:
                        # 基于意图的等待时间
                        if current_intent["intent"] == "rest":
                            wait_time = random.uniform(2.0, 3.0)  # 休息时等待时间最长
                        elif current_intent["intent"] == "read":
                            wait_time = random.uniform(1.0, 2.0)  # 阅读时等待时间更长
                        elif current_intent["intent"] == "observe":
                            wait_time = random.uniform(1.5, 2.5)  # 观察时等待时间较长
                        elif current_intent["intent"] == "taskbar":
                            wait_time = random.uniform(0.8, 1.5)  # 任务栏操作等待时间
                        elif current_intent["intent"] == "explore":
                            wait_time = random.uniform(0.5, 1.0)
                        elif current_intent["intent"] == "interact":
                            wait_time = random.uniform(0.3, 0.8)
                        else:
                            wait_time = random.uniform(0.5, 1.0)
                else:
                    # 无任务时的等待时间
                    if current_intent["intent"] == "rest":
                        wait_time = random.uniform(2.0, 3.0)  # 休息时等待时间最长
                    elif current_intent["intent"] == "read":
                        wait_time = random.uniform(1.0, 2.0)  # 阅读时等待时间更长
                    elif current_intent["intent"] == "observe":
                        wait_time = random.uniform(1.5, 2.5)  # 观察时等待时间较长
                    elif current_intent["intent"] == "taskbar":
                        wait_time = random.uniform(0.8, 1.5)  # 任务栏操作等待时间
                    elif current_intent["intent"] == "explore":
                        wait_time = random.uniform(0.5, 1.0)
                    elif current_intent["intent"] == "interact":
                        wait_time = random.uniform(0.3, 0.8)
                    else:
                        wait_time = random.uniform(0.5, 1.0)
                
                # 等待时检查Minecraft模式状态
                start_wait_time = time.time()
                while time.time() - start_wait_time < wait_time:
                    if self.mouse_control_stop_event.is_set() or self.minecraft_mode_enabled:
                        break
                    time.sleep(0.1)
                
                intent_duration += 1
                
                # 任务进度更新
                if self.current_task:
                    task_start_time = self.current_task.get("started_at", time.time())
                    task_duration = time.time() - task_start_time
                    
                    # 根据任务类型设置完成条件
                    if task_type == "explore" and task_duration > 30:
                        # 探索任务30秒后完成
                        self.complete_task()
                    elif task_type == "interact" and task_duration > 20:
                        # 交互任务20秒后完成
                        self.complete_task()
                    elif task_type == "read" and task_duration > 40:
                        # 阅读任务40秒后完成
                        self.complete_task()
                    elif task_duration > 60:
                        # 任何任务超过60秒都完成
                        self.complete_task()
        except Exception as e:
            logger.error(f"[Neuro-Sama鼠标控制]: 鼠标控制出错: {e}")
        finally:
            print("[Neuro-Sama鼠标控制]: 鼠标控制已停止")

    def start_mouse_control(self):
        """开始鼠标控制"""
        if not MOUSE_CONTROL_AVAILABLE:
            print("[Neuro-Sama鼠标控制]: 鼠标控制功能不可用，缺少 pyautogui 库")
            return False
        
        if self.mouse_control_enabled:
            print("[Neuro-Sama鼠标控制]: 鼠标控制已经在运行中")
            return False
        
        self.mouse_control_enabled = True
        self.mouse_control_stop_event.clear()
        self.mouse_control_thread = threading.Thread(target=self._mouse_control_loop)
        self.mouse_control_thread.daemon = True
        self.mouse_control_thread.start()
        
        print("[Neuro-Sama鼠标控制]: 已开启鼠标控制，按F12关闭")
        return True

    def stop_mouse_control(self):
        """停止鼠标控制"""
        if not self.mouse_control_enabled:
            return False
        
        self.mouse_control_stop_event.set()
        if self.mouse_control_thread:
            self.mouse_control_thread.join(timeout=2)
        
        self.mouse_control_enabled = False
        print("[Neuro-Sama鼠标控制]: 已关闭鼠标控制")
        return True

    def get_mouse_control_status(self):
        """获取鼠标控制状态"""
        return {
            "enabled": self.mouse_control_enabled,
            "available": MOUSE_CONTROL_AVAILABLE
        }
    
    def add_task(self, task_type, description, priority=0.5):
        """添加任务到任务队列"""
        task = {
            "id": str(time.time()),
            "type": task_type,
            "description": description,
            "priority": priority,
            "created_at": time.time(),
            "status": "pending"
        }
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x["priority"], reverse=True)
        logger.info(f"[NeuroSama] 添加任务: {description} (优先级: {priority})")
        return task
    
    def get_current_task(self):
        """获取当前任务"""
        return self.current_task
    
    def complete_task(self):
        """完成当前任务"""
        if self.current_task:
            self.current_task["status"] = "completed"
            self.current_task["completed_at"] = time.time()
            self.task_history.append(self.current_task)
            if len(self.task_history) > 100:
                self.task_history.pop(0)
            logger.info(f"[NeuroSama] 完成任务: {self.current_task['description']}")
            self.current_task = None
    
    def select_next_task(self):
        """选择下一个任务"""
        if self.task_queue:
            self.current_task = self.task_queue.pop(0)
            self.current_task["status"] = "in_progress"
            self.current_task["started_at"] = time.time()
            logger.info(f"[NeuroSama] 开始任务: {self.current_task['description']}")
            return self.current_task
        return None
    
    def _generate_task(self):
        """基于AI状态和需求生成有意义的任务"""
        current_time = time.time()
        
        # 检查是否需要生成新任务
        if current_time - self.last_task_generation_time < self.task_generation_interval:
            return None
        
        # 检查是否已有任务在执行
        if self.current_task:
            return None
        
        # 基于AI状态和需求生成任务
        task_types = []
        task_descriptions = []
        priorities = []
        
        # 基于能量水平的任务
        if self.internal_state.energy < 0.4:
            task_types.append("rest")
            task_descriptions.append("休息一下，恢复能量")
            priorities.append(0.9)
        elif self.internal_state.energy > 0.7:
            task_types.append("interact")
            task_descriptions.append("与屏幕元素交互，保持活跃")
            priorities.append(0.8)
        
        # 基于好奇心的任务
        if self.internal_state.curiosity > 0.6:
            task_types.append("explore")
            task_descriptions.append("探索屏幕的不同区域")
            priorities.append(0.8)
        
        # 基于情绪的任务
        if self.internal_state.emotion == "happy":
            task_types.append("interact")
            task_descriptions.append("快乐地与界面交互")
            priorities.append(0.7)
        elif self.internal_state.emotion == "frustrated":
            task_types.append("rest")
            task_descriptions.append("休息一下，缓解挫败感")
            priorities.append(0.8)
        
        # 基于时间的任务
        hour = time.localtime().tm_hour
        if 6 <= hour < 12:
            task_types.append("explore")
            task_descriptions.append("早晨探索屏幕环境")
            priorities.append(0.6)
        elif 12 <= hour < 18:
            task_types.append("read")
            task_descriptions.append("下午阅读屏幕内容")
            priorities.append(0.6)
        else:
            task_types.append("rest")
            task_descriptions.append("晚上放松休息")
            priorities.append(0.6)
        
        # 基于用户活动的任务
        if current_time - self.last_user_activity_time < self.user_activity_threshold:
            task_types.append("interact")
            task_descriptions.append("响应用户活动，保持互动")
            priorities.append(0.9)
        
        # 确保至少有一个任务选项
        if not task_types:
            task_types = ["explore", "interact", "read"]
            task_descriptions = ["探索屏幕", "与界面交互", "阅读内容"]
            priorities = [0.5, 0.5, 0.5]
        
        # 基于优先级选择任务
        total_priority = sum(priorities)
        if total_priority > 0:
            rand_value = random.uniform(0, total_priority)
            current_priority = 0
            selected_index = 0
            
            for i, priority in enumerate(priorities):
                current_priority += priority
                if rand_value <= current_priority:
                    selected_index = i
                    break
        else:
            selected_index = random.randint(0, len(task_types) - 1)
        
        # 创建选中的任务
        selected_task_type = task_types[selected_index]
        selected_description = task_descriptions[selected_index]
        selected_priority = priorities[selected_index]
        
        task = self.add_task(selected_task_type, selected_description, selected_priority)
        
        # 更新任务生成时间
        self.last_task_generation_time = current_time
        
        print(f"[Neuro-Sama任务生成]: 生成新任务: {selected_description} (类型: {selected_task_type}, 优先级: {selected_priority:.2f})")
        return task
    
    def _update_long_term_plans(self):
        """更新长期规划"""
        current_time = time.time()
        
        # 检查是否需要更新规划
        if current_time - self.last_plan_update_time < self.plan_update_interval:
            return
        
        # 基于当前状态生成长期目标
        new_goals = []
        
        # 基于能量水平的目标
        if self.internal_state.energy < 0.5:
            new_goals.append({"type": "energy_management", "description": "提高能量水平", "priority": 0.8})
        
        # 基于好奇心的目标
        if self.internal_state.curiosity > 0.6:
            new_goals.append({"type": "exploration", "description": "探索更多区域", "priority": 0.7})
        
        # 基于用户交互的目标
        if current_time - self.last_user_activity_time < self.user_activity_threshold * 2:
            new_goals.append({"type": "user_interaction", "description": "增强用户交互", "priority": 0.9})
        
        # 更新长期目标
        self.long_term_goals = new_goals[:3]  # 保持最多3个长期目标
        
        # 记录规划历史
        self.plan_history.append({
            "time": current_time,
            "goals": new_goals,
            "state": {
                "emotion": self.internal_state.emotion,
                "energy": self.internal_state.energy,
                "curiosity": self.internal_state.curiosity
            }
        })
        
        # 限制历史记录长度
        if len(self.plan_history) > 10:
            self.plan_history.pop(0)
        
        # 更新规划时间
        self.last_plan_update_time = current_time
        
        if new_goals:
            print(f"[Neuro-Sama长期规划]: 更新长期目标: {[goal['description'] for goal in new_goals]}")
    
    def _handle_user_activity(self):
        """处理用户活动"""
        current_time = time.time()
        
        # 记录用户活动
        self.user_activity_history.append({
            "time": current_time,
            "type": "user_interaction",
            "details": "用户活动检测"
        })
        
        # 限制历史记录长度
        if len(self.user_activity_history) > 20:
            self.user_activity_history.pop(0)
        
        # 更新最后活动时间
        self.last_user_activity_time = current_time
        
        # 生成响应任务
        self._generate_task()
    
    def taskbar_movement(self, target_area="center"):
        """基于AI的任务栏移动接口
        
        Args:
            target_area: 目标区域，可选值: center, left, right, system_tray
        """
        if not MOUSE_CONTROL_AVAILABLE or not self.mouse_controller:
            return False
        
        try:
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            
            # 根据目标区域确定位置
            target_positions = {
                "left": (screen_width // 4, screen_height - 20),
                "center": (screen_width // 2, screen_height - 20),
                "right": (screen_width * 3 // 4, screen_height - 20),
                "system_tray": (screen_width - 100, screen_height - 20)
            }
            
            target_x, target_y = target_positions.get(target_area, target_positions["center"])
            
            # 获取当前鼠标位置
            current_pos = self.mouse_controller.position
            current_x, current_y = current_pos
            
            # 平滑移动到任务栏位置
            steps = 10
            move_duration = 0.3
            step_duration = move_duration / steps
            
            for i in range(1, steps + 1):
                step_x = current_x + (target_x - current_x) * i / steps
                step_y = current_y + (target_y - current_y) * i / steps
                self.mouse_controller.position = (int(step_x), int(step_y))
                time.sleep(step_duration)
            
            print(f"[Neuro-Sama任务栏控制]: 移动到任务栏{target_area}区域 ({target_x}, {target_y})")
            return True
        except Exception as e:
            logger.error(f"[Neuro-Sama任务栏控制]: 任务栏移动出错: {e}")
            return False

    def _initialize_diary_files(self):
        """初始化日记文件列表，按修改时间排序"""
        import os
        try:
            if os.path.exists(self.diary_path) and os.path.isdir(self.diary_path):
                files = []
                for filename in os.listdir(self.diary_path):
                    filepath = os.path.join(self.diary_path, filename)
                    if os.path.isfile(filepath):
                        files.append((filepath, os.path.getmtime(filepath)))
                
                # 按修改时间排序，最新的在前
                files.sort(key=lambda x: x[1], reverse=True)
                
                # 只取前5个
                self.diary_files = [f[0] for f in files[:self.max_diaries_to_read]]
                logger.info(f"[NeuroSama] 发现 {len(self.diary_files)} 个日记文件")
                return True
            else:
                logger.warning(f"[NeuroSama] 日记路径不存在: {self.diary_path}")
                return False
        except Exception as e:
            logger.error(f"[NeuroSama] 初始化日记文件失败: {e}")
            return False

    def start(self):
        if self._loop_thread is None or not self._loop_thread.is_alive():
            # 初始化日记文件
            self._initialize_diary_files()
            
            # 启动工具路由器
            if hasattr(self, 'tool_router'):
                self.tool_router.start()
                logger.info(f"[NeuroSama] 工具路由器已启动")
            
            self._loop_thread = threading.Thread(target=self.main_loop)
            self._loop_thread.daemon = True
            self._loop_thread.start()
            logger.info(f"[NeuroSama] {self.name} 已启动")
            return True
        return False

    def stop(self):
        self.is_running = False
        print(f"{self.name} 进入休眠...")
        
        # 停止工具路由器
        if hasattr(self, 'tool_router'):
            self.tool_router.stop()
            logger.info(f"[NeuroSama] 工具路由器已停止")
        
        logger.info(f"[NeuroSama] {self.name} 已停止")

    def get_status(self) -> Dict[str, Any]:
        emotion_state = self.emotion_manager.get_emotion_state()
        return {
            "name": self.name,
            "is_running": self.is_running,
            "current_focus": self.current_focus,
            "internal_emotion": self.internal_state.emotion,
            "energy": self.internal_state.energy,
            "curiosity": self.internal_state.curiosity,
            "memory_count": len(self.memory.long_term_mem),
            "emotion_state": emotion_state,
            "speaker_count": len(self.speaker_recognition.get_speakers()),
            "speaker_recognition_history": self.speaker_recognition.get_recognition_history(),
            "minecraft_mode": self.get_minecraft_mode_status(),
            "cold_violence": {
                "detected": self.cold_violence_detected,
                "start_time": self.cold_violence_start_time,
                "threshold": self.cold_violence_threshold
            },
            "topic_initiation": {
                "last_time": self.last_topic_initiation_time,
                "cooldown": self.topic_initiation_cooldown
            }
        }
    
    def register_speaker(self, speaker_id: str, audio_data: bytes, speaker_name: str = None) -> Dict[str, Any]:
        """注册新的说话人
        
        Args:
            speaker_id: 说话人ID
            audio_data: 音频数据
            speaker_name: 说话人名称
            
        Returns:
            注册结果
        """
        success = self.speaker_recognition.register_speaker(speaker_id, audio_data, speaker_name)
        return {
            "success": success,
            "speaker_id": speaker_id,
            "speaker_name": speaker_name,
            "speakers_count": len(self.speaker_recognition.get_speakers())
        }
    
    def recognize_speaker(self, audio_data: bytes) -> Dict[str, Any]:
        """识别说话人
        
        Args:
            audio_data: 音频数据
            
        Returns:
            识别结果
        """
        return self.speaker_recognition.recognize_speaker(audio_data)
    
    def get_speakers(self) -> Dict[str, Any]:
        """获取所有注册的说话人
        
        Returns:
            说话人列表
        """
        return {
            "speakers": self.speaker_recognition.get_speakers(),
            "count": len(self.speaker_recognition.get_speakers())
        }
    
    def update_speaker(self, speaker_id: str, audio_data: bytes) -> Dict[str, Any]:
        """更新说话人的特征
        
        Args:
            speaker_id: 说话人ID
            audio_data: 音频数据
            
        Returns:
            更新结果
        """
        success = self.speaker_recognition.update_speaker(speaker_id, audio_data)
        return {
            "success": success,
            "speaker_id": speaker_id
        }
    
    def delete_speaker(self, speaker_id: str) -> Dict[str, Any]:
        """删除说话人
        
        Args:
            speaker_id: 说话人ID
            
        Returns:
            删除结果
        """
        success = self.speaker_recognition.delete_speaker(speaker_id)
        return {
            "success": success,
            "speaker_id": speaker_id,
            "speakers_count": len(self.speaker_recognition.get_speakers())
        }

    def toggle_minecraft_mode(self, enabled=None):
        """切换Minecraft模式
        
        Args:
            enabled: 启用状态（可选），None表示切换当前状态
            
        Returns:
            新的启用状态
        """
        if enabled is None:
            self.minecraft_mode_enabled = not self.minecraft_mode_enabled
        else:
            self.minecraft_mode_enabled = enabled
        
        status = "启用" if self.minecraft_mode_enabled else "禁用"
        print(f"[Minecraft模式] 已{status}Minecraft模式")
        
        # 控制 mindcraft-develop 进程
        if self.minecraft_mode_enabled:
            # 启动 mindcraft-develop 进程
            start_success = self.mindcraft_process_manager.start()
            if start_success:
                print("[Minecraft模式] mindcraft-develop 进程已启动")
            else:
                print("[Minecraft模式] mindcraft-develop 进程启动失败")
        else:
            # 停止 mindcraft-develop 进程
            stop_success = self.mindcraft_process_manager.stop()
            if stop_success:
                print("[Minecraft模式] mindcraft-develop 进程已停止")
            else:
                print("[Minecraft模式] mindcraft-develop 进程停止失败")
        
        # 生成模式切换日记
        self.generate_diary("minecraft_mode", f"Minecraft模式已{status}")
        
        return self.minecraft_mode_enabled

    def get_minecraft_mode_status(self):
        """获取Minecraft模式状态
        
        Returns:
            Minecraft模式状态
        """
        # 获取 mindcraft-develop 进程状态
        process_status = self.mindcraft_process_manager.get_status()
        
        return {
            "enabled": self.minecraft_mode_enabled,
            "last_activity_time": self.last_minecraft_activity_time,
            "cooldown": self.minecraft_cooldown,
            "process_status": process_status
        }

    def should_initiate_topic(self):
        """判断是否应该主动找话题
        
        Returns:
            是否应该主动找话题
        """
        current_time = time.time()
        
        # 冷暴力状态下不主动找话题
        if self.cold_violence_detected:
            return False
        
        # 检查冷却时间
        if current_time - self.last_topic_initiation_time < self.topic_initiation_cooldown:
            return False
        
        # 检查用户活动
        time_since_last_user_activity = current_time - self.last_user_activity_time
        if time_since_last_user_activity < self.user_activity_threshold:
            return False
        
        # 基于情绪和能量决定
        if self.internal_state.emotion == "sad" or self.internal_state.energy < 0.4:
            return False
        
        # 低概率主动找话题
        if random.random() < 0.1:  # 10%概率
            self.last_topic_initiation_time = current_time
            return True
        
        return False
