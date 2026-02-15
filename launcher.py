# -*- coding: utf-8 -*-
"""
N.E.K.O. 统一启动器
启动所有服务器，等待它们准备就绪后启动主程序，并监控主程序状态
"""
import sys
import os
import io

# 强制 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
# 处理 PyInstaller 和 Nuitka 打包后的路径
if getattr(sys, 'frozen', False):
    # 运行在打包后的环境
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller
        bundle_dir = sys._MEIPASS
    else:
        # Nuitka 或其他
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_dir = os.path.dirname(sys.executable)
else:
    # 运行在正常 Python 环境
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = bundle_dir

sys.path.insert(0, bundle_dir)
os.chdir(bundle_dir)

import subprocess
import socket
import time
import threading
import itertools
from datetime import datetime
from typing import List, Dict
from multiprocessing import Process, freeze_support, Event
from config import MAIN_SERVER_PORT, MEMORY_SERVER_PORT, TOOL_SERVER_PORT

# 服务器配置
SERVERS = [
    {
        'name': 'Memory Server',
        'module': 'memory_server',
        'port': MEMORY_SERVER_PORT,
        'process': None,
        'ready_event': None,
    },
    {
        'name': 'Agent Server', 
        'module': 'agent_server',
        'port': TOOL_SERVER_PORT,
        'process': None,
        'ready_event': None,
    },
    {
        'name': 'Main Server',
        'module': 'main_server',
        'port': MAIN_SERVER_PORT,
        'process': None,
        'ready_event': None,
    },
    {
        'name': 'AI Control',
        'module': 'ai_control',
        'port': None,  # ai_control 不是服务器，不需要端口
        'process': None,
        'ready_event': None,
    },
]

# 不再启动主程序，用户自己启动 lanlan_frd.exe

def run_memory_server(ready_event: Event):
    """运行 Memory Server"""
    try:
        # 确保工作目录正确
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                os.chdir(sys._MEIPASS)
            else:
                # Nuitka
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            # 禁用 typeguard（子进程需要重新禁用）
            try:
                import typeguard
                def dummy_typechecked(func=None, **kwargs):
                    return func if func else (lambda f: f)
                typeguard.typechecked = dummy_typechecked
                if hasattr(typeguard, '_decorators'):
                    typeguard._decorators.typechecked = dummy_typechecked
            except: # noqa
                pass
        
        import memory_server
        import uvicorn
        
        print(f"[Memory Server] Starting on port {MEMORY_SERVER_PORT}")
        
        # 使用 Server 对象，在启动后通知父进程
        config = uvicorn.Config(
            app=memory_server.app,
            host="127.0.0.1",
            port=MEMORY_SERVER_PORT,
            log_level="error"
        )
        server = uvicorn.Server(config)
        
        # 在后台线程中运行服务器
        import asyncio
        
        async def run_with_notify():
            # 启动服务器
            await server.serve()
        
        # 启动线程来运行服务器，并在启动后通知
        def run_server():
            # 创建事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 添加启动完成的回调
            async def startup():
                print(f"[Memory Server] Running on port {MEMORY_SERVER_PORT}")
                ready_event.set()
            
            # 将 startup 添加到服务器的启动事件
            server.config.app.add_event_handler("startup", startup)
            
            # 运行服务器
            loop.run_until_complete(server.serve())
        
        run_server()
        
    except Exception as e:
        print(f"Memory Server error: {e}")
        import traceback
        traceback.print_exc()

def run_agent_server(ready_event: Event):
    """运行 Agent Server (不需要等待初始化)"""
    try:
        # 确保工作目录正确
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                os.chdir(sys._MEIPASS)
            else:
                # Nuitka
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
            # 禁用 typeguard（子进程需要重新禁用）
            try:
                import typeguard
                def dummy_typechecked(func=None, **kwargs):
                    return func if func else (lambda f: f)
                typeguard.typechecked = dummy_typechecked
                if hasattr(typeguard, '_decorators'):
                    typeguard._decorators.typechecked = dummy_typechecked
            except: # noqa
                pass
        
        import agent_server
        import uvicorn
        
        print(f"[Agent Server] Starting on port {TOOL_SERVER_PORT}")
        
        # Agent Server 不需要等待，立即通知就绪
        ready_event.set()
        
        uvicorn.run(agent_server.app, host="127.0.0.1", port=TOOL_SERVER_PORT, log_level="error")
    except Exception as e:
        print(f"Agent Server error: {e}")
        import traceback
        traceback.print_exc()

def run_main_server(ready_event: Event):
    """运行 Main Server"""
    try:
        # 确保工作目录正确
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                os.chdir(sys._MEIPASS)
            else:
                # Nuitka
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("[Main Server] Importing main_server module...")
        import main_server
        import uvicorn
        
        print(f"[Main Server] Starting on port {MAIN_SERVER_PORT}")
        
        # 直接运行 FastAPI app，不依赖 main_server 的 __main__ 块
        config = uvicorn.Config(
            app=main_server.app,
            host="127.0.0.1",
            port=MAIN_SERVER_PORT,
            log_level="error",
            loop="asyncio",
            reload=False,
        )
        server = uvicorn.Server(config)
        
        # 添加启动完成的回调
        async def startup():
            print(f"[Main Server] Running on port {MAIN_SERVER_PORT}")
            ready_event.set()
        
        # 将 startup 添加到服务器的启动事件
        main_server.app.add_event_handler("startup", startup)
        
        # 运行服务器
        server.run()
    except Exception as e:
        print(f"Main Server error: {e}")
        import traceback
        traceback.print_exc()

def run_ai_control(ready_event: Event):
    """运行 AI Control 程序"""
    try:
        # 确保工作目录正确
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                os.chdir(sys._MEIPASS)
            else:
                # Nuitka
                os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        print("[AI Control] Starting AI Control program...")
        
        # 立即通知就绪，因为 ai_control 是一个后台程序
        ready_event.set()
        
        # 导入并运行 ai_control
        import ai_control
        
        # 调用 ai_control 的主函数
        ai_control.main()
    except Exception as e:
        print(f"AI Control error: {e}")
        import traceback
        traceback.print_exc()

def check_port(port: int, timeout: float = 0.5) -> bool:
    """检查端口是否已开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except: # noqa
        return False

def show_spinner(stop_event: threading.Event, message: str = "正在启动服务器"):
    """显示转圈圈动画"""
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message}... {next(spinner)} ')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 60 + '\r')  # 清除动画行
    sys.stdout.write('\n')  # 换行，确保后续输出在新行
    sys.stdout.flush()

def start_server(server: Dict) -> bool:
    """启动单个服务器"""
    try:
        # 根据模块名选择启动函数
        if server['module'] == 'memory_server':
            target_func = run_memory_server
        elif server['module'] == 'agent_server':
            target_func = run_agent_server
        elif server['module'] == 'main_server':
            target_func = run_main_server
        elif server['module'] == 'ai_control':
            target_func = run_ai_control
        else:
            print(f"✗ {server['name']} 未知模块", flush=True)
            return False
        
        # 创建进程间同步事件
        server['ready_event'] = Event()
        
        # 使用 multiprocessing 启动服务器
        # 注意：不能设置 daemon=True，因为 main_server 自己会创建子进程
        server['process'] = Process(target=target_func, args=(server['ready_event'],), daemon=False)
        server['process'].start()
        
        print(f"✓ {server['name']} 已启动 (PID: {server['process'].pid})", flush=True)
        return True
    except Exception as e:
        print(f"✗ {server['name']} 启动失败: {e}", flush=True)
        return False

def wait_for_servers(timeout: int = 60) -> bool:
    """等待所有服务器启动完成"""
    print("\n等待服务器准备就绪...", flush=True)
    
    # 启动动画线程
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=show_spinner, args=(stop_spinner, "检查服务器状态"))
    spinner_thread.daemon = True
    spinner_thread.start()
    
    start_time = time.time()
    all_ready = False
    
    # 第一步：等待所有端口就绪
    while time.time() - start_time < timeout:
        ready_count = 0
        for server in SERVERS:
            if server['port'] is None:
                # ai_control 没有端口，直接视为就绪
                ready_count += 1
            elif check_port(server['port']) or server['port']==TOOL_SERVER_PORT:
                ready_count += 1
        
        if ready_count == len(SERVERS):
            break
        
        time.sleep(0.5)
    
    # 第二步：等待所有服务器的 ready_event（同步初始化完成）
    if ready_count == len(SERVERS):
        for server in SERVERS:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time > 0:
                if server['ready_event'].wait(timeout=remaining_time):
                    continue
                else:
                    # 超时
                    break
        else:
            # 所有服务器都就绪了
            all_ready = True
    
    # 停止动画
    stop_spinner.set()
    spinner_thread.join()
    
    if all_ready:
        print("\n", flush=True)
        print("=" * 60, flush=True)
        print("✓✓✓  所有服务器已准备就绪！  ✓✓✓", flush=True)
        print("=" * 60, flush=True)
        print("\n", flush=True)
        return True
    else:
        print("\n", flush=True)
        print("=" * 60, flush=True)
        print("✗ 服务器启动超时，请检查日志文件", flush=True)
        print("=" * 60, flush=True)
        print("\n", flush=True)
        # 显示未就绪的服务器
        for server in SERVERS:
            if not server['ready_event'].is_set():
                print(f"  - {server['name']} 初始化未完成", flush=True)
            elif not check_port(server['port']):
                print(f"  - {server['name']} 端口 {server['port']} 未就绪", flush=True)
        return False


def cleanup_servers():
    """清理所有服务器进程"""
    print("\n正在关闭服务器...", flush=True)
    for server in SERVERS:
        if server['process'] and server['process'].is_alive():
            try:
                # 先尝试温和地终止
                server['process'].terminate()
                server['process'].join(timeout=3)
                if not server['process'].is_alive():
                    print(f"✓ {server['name']} 已关闭", flush=True)
                else:
                    # 如果还活着，强制杀死
                    server['process'].kill()
                    server['process'].join(timeout=2)
                    print(f"✓ {server['name']} 已强制关闭", flush=True)
            except Exception as e:
                print(f"✗ {server['name']} 关闭失败: {e}", flush=True)

def main():
    """主函数"""
    # 支持 multiprocessing 在 Windows 上的打包
    freeze_support()
    
    # 记录程序启动时间
    start_time = time.time()
    start_datetime = datetime.now()
    
    print("=" * 60, flush=True)
    print("N.E.K.O. 服务器启动器", flush=True)
    print("=" * 60, flush=True)
    
    # 记录发生的事情
    events = [
        f"程序启动于: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    
    try:
        # 1. 启动所有服务器
        print("\n正在启动服务器...\n", flush=True)
        events.append("开始启动所有服务器")
        all_started = True
        for server in SERVERS:
            if not start_server(server):
                all_started = False
                events.append(f"❌ {server['name']} 启动失败")
                break
            events.append(f"✅ {server['name']} 已启动")
        
        if not all_started:
            print("\n启动失败，正在清理...", flush=True)
            events.append("启动失败，开始清理")
            cleanup_servers()
            return 1
        
        # 2. 等待服务器准备就绪
        events.append("等待服务器准备就绪")
        if not wait_for_servers():
            print("\n启动失败，正在清理...", flush=True)
            events.append("服务器准备超时，启动失败")
            cleanup_servers()
            return 1
        events.append("✅ 所有服务器已准备就绪")
        
        # 3. 服务器已启动，等待用户操作
        print("", flush=True)
        print("=" * 60, flush=True)
        print("  🎉 所有服务器已启动完成！", flush=True)
        print("\n  现在你可以：", flush=True)
        print("  1. 启动 lanlan_frd.exe 使用系统", flush=True)
        print("  2. 在浏览器访问 http://localhost:48911", flush=True)
        print("\n  AI Control 已自动启动，功能如下：", flush=True)
        print("  - 按 F11 启用 AI 控制鼠标和键盘", flush=True)
        print("  - 按 F12 禁用 AI 控制鼠标和键盘", flush=True)
        print("  - 默认已启用自动对话分析", flush=True)
        print("\n  按 Ctrl+C 关闭所有服务器", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
        events.append("服务器已准备就绪，等待用户操作")
        
        # 持续运行，监控服务器状态
        while True:
            time.sleep(1)
            # 检查服务器是否还活着
            all_alive = all(
                server['process'] and server['process'].is_alive() 
                for server in SERVERS
            )
            if not all_alive:
                print("\n检测到服务器异常退出！", flush=True)
                events.append("⚠️ 检测到服务器异常退出")
                break
        
    except KeyboardInterrupt:
        print("\n\n收到中断信号，正在关闭...", flush=True)
        events.append("收到中断信号，开始关闭服务器")
    except Exception as e:
        error_msg = f"\n发生错误: {e}"
        print(error_msg, flush=True)
        events.append(f"❌ 发生错误: {e}")
    finally:
        cleanup_servers()
        print("\n所有服务器已关闭", flush=True)
        print("再见！\n", flush=True)
        
        # 记录程序退出时间
        end_time = time.time()
        end_datetime = datetime.now()
        run_duration = end_time - start_time
        events.append(f"程序退出于: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        events.append(f"总运行时间: {time.strftime('%H:%M:%S', time.gmtime(run_duration))}")
        
        # 调用独立的日记生成函数
        generate_diary(start_datetime, events, end_datetime, run_duration)
    
    return 0

def generate_diary(start_datetime, events, end_datetime, run_duration):
    """生成日记的独立函数"""
    try:
        # 确保日记目录存在
        diary_dir = "F:\\日记"
        if not os.path.exists(diary_dir):
            os.makedirs(diary_dir)
        
        # 生成日记文件名（格式：2024-01-01_21-30-45_日记.txt）
        # 使用日期+时间格式命名，确保当天的日记都写入同一个文件
        diary_filename = os.path.join(diary_dir, f"{start_datetime.strftime('%Y-%m-%d')}_日记.txt")
        
        # 生成日记内容
        diary_content = [
            "=" * 50,
            "N.E.K.O. 系统运行日记",
            "=" * 50,
            f"日期: {start_datetime.strftime('%Y-%m-%d')}",
            f"启动时间: {start_datetime.strftime('%H:%M:%S')}",
            f"退出时间: {end_datetime.strftime('%H:%M:%S')}",
            f"运行时长: {time.strftime('%H:%M:%S', time.gmtime(run_duration))}",
            "\n今日发生的事情：",
            "-" * 30
        ]
        
        # 添加事件记录
        for event in events:
            diary_content.append(f"• {event}")
        
        # 添加对话内容
        diary_content.extend([
            "",
            "\n今日对话内容：",
            "-" * 30
        ])
        
        # 获取对话历史
        try:
            from memory.recent import CompressedRecentHistoryManager
            from utils.config_manager import get_config_manager
            
            # 初始化配置管理器和历史记录管理器
            _config_manager = get_config_manager()
            recent_history_manager = CompressedRecentHistoryManager()
            
            # 获取所有角色
            try:
                character_data = _config_manager.load_characters()
                catgirl_names = list(character_data.get('猫娘', {}).keys())
            except Exception as e:
                catgirl_names = []
                print(f"\n⚠️ 获取角色列表失败: {e}")
            
            # 如果没有角色，添加默认角色
            if not catgirl_names:
                # 尝试从memory目录获取所有recent_*.json文件
                import glob
                memory_dir = str(_config_manager.memory_dir)
                recent_files = glob.glob(os.path.join(memory_dir, 'recent_*.json'))
                catgirl_names = [os.path.basename(f).replace('recent_', '').replace('.json', '') for f in recent_files]
            
            # 为每个角色添加对话历史
            for lanlan_name in catgirl_names:
                try:
                    # 获取最近的对话历史
                    history = recent_history_manager.get_recent_history(lanlan_name)
                    if history:
                        diary_content.append(f"\n【{lanlan_name}的对话记录】")
                        
                        # 遍历历史记录，只添加最近的10条对话
                        for msg in history[-10:]:  # 只显示最近10条
                            # 处理不同类型的消息
                            if hasattr(msg, 'type'):
                                if msg.type == 'system':
                                    # 跳过系统消息
                                    continue
                                elif msg.type == 'ai' or msg.type == 'assistant':
                                    role = lanlan_name
                                elif msg.type == 'user' or msg.type == 'human':
                                    role = "主人"
                                else:
                                    role = msg.type
                            else:
                                role = "未知"
                            
                            # 处理消息内容
                            if hasattr(msg, 'content'):
                                if isinstance(msg.content, str):
                                    content = msg.content
                                elif isinstance(msg.content, list):
                                    # 提取文本内容
                                    text_parts = []
                                    for item in msg.content:
                                        if isinstance(item, dict):
                                            if item.get('type') == 'text':
                                                text_parts.append(item.get('text', ''))
                                        else:
                                            text_parts.append(str(item))
                                    content = "\n".join(text_parts)
                                else:
                                    content = str(msg.content)
                            else:
                                content = str(msg)
                            
                            # 只添加非空内容
                            if content.strip():
                                diary_content.append(f"{role}: {content}")
                except Exception as e:
                    print(f"\n⚠️ 获取{lanlan_name}的对话历史失败: {e}")
        except Exception as e:
            diary_content.append("⚠️ 无法获取对话历史")
            print(f"\n⚠️ 获取对话历史失败: {e}")
        
        # 添加学习到的内容
        diary_content.extend([
            "",
            "\n今日学习内容：",
            "-" * 30
        ])
        
        # 尝试获取学习内容（设置、重要信息等）
        try:
            from memory.important_settings import ImportantSettingsManager
            
            settings_manager = ImportantSettingsManager()
            
            for lanlan_name in catgirl_names:
                try:
                    settings = settings_manager.get_settings(lanlan_name)
                    if settings:
                        diary_content.append(f"\n【{lanlan_name}学习到的内容】")
                        for key, value in settings.items():
                            diary_content.append(f"• {key}: {value}")
                except Exception as e:
                    print(f"\n⚠️ 获取{lanlan_name}的学习内容失败: {e}")
        except Exception as e:
            diary_content.append("⚠️ 无法获取学习内容")
            print(f"\n⚠️ 获取学习内容失败: {e}")
        
        # 如果没有学习内容，添加提示
        if "今日学习内容：" in diary_content and "⚠️ 无法获取学习内容" not in diary_content:
            # 检查是否有实际的学习内容
            has_learning_content = False
            for line in diary_content:
                if line.startswith("• ") and "今日学习内容：" in diary_content[:diary_content.index(line)]:
                    has_learning_content = True
                    break
            if not has_learning_content:
                diary_content.append("• 今日没有学习到新内容")
        
        # 添加结束语
        diary_content.extend([
            "",
            "-" * 30,
            "日记结束",
            "=" * 50
        ])
        
        # 写入日记文件
        with open(diary_filename, "a", encoding="utf-8") as f:
            f.write("\n".join(diary_content))
            f.write("\n\n")  # 空两行作为分隔
        
        print(f"\n📝 日记已生成：{diary_filename}", flush=True)
    except Exception as e:
        print(f"\n⚠️ 生成日记失败: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sys.exit(main())

