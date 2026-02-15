import subprocess
import time

class MinecraftClient:
    def __init__(self):
        self.process = None
        self.window_id = None
    
    def is_minecraft_running(self):
        """检查Minecraft是否正在运行"""
        try:
            # 尝试使用psutil
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    process_name = proc.info['name'].lower()
                    # 检查常见的Minecraft进程名
                    if 'minecraft' in process_name or 'openjdk platform binary' in process_name or 'java.exe' in process_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            # 如果psutil不存在，使用tasklist命令
            try:
                result = subprocess.run(
                    'tasklist',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                output = result.stdout.lower()
                # 检查常见的Minecraft进程名
                if 'minecraft' in output or 'openjdk platform binary' in output or 'java.exe' in output:
                    return True
            except Exception:
                pass
        return False
    
    def get_minecraft_process(self):
        """获取Minecraft进程"""
        try:
            # 尝试使用psutil
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    process_name = proc.info['name'].lower()
                    # 检查常见的Minecraft进程名
                    if 'minecraft' in process_name or 'openjdk platform binary' in process_name or 'java.exe' in process_name:
                        return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            # 如果psutil不存在，返回None
            pass
        return None
    
    def focus_window(self):
        """聚焦到Minecraft窗口"""
        # 这里需要根据操作系统实现窗口聚焦
        # Windows示例：使用pygetwindow或win32gui
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('Minecraft')
            if windows:
                window = windows[0]
                window.activate()
                return True
        except ImportError:
            # 如果pygetwindow不存在，尝试使用win32gui
            try:
                import win32gui
                def callback(hwnd, windows):
                    if 'minecraft' in win32gui.GetWindowText(hwnd).lower():
                        windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                if windows:
                    win32gui.SetForegroundWindow(windows[0])
                    return True
            except ImportError:
                pass
        except Exception:
            pass
        return False
    
    def send_input(self, input_type, value):
        """发送输入到Minecraft"""
        try:
            if input_type == 'keyboard':
                from pynput.keyboard import Controller as KeyboardController, Key
                keyboard = KeyboardController()
                
                key = value.get('key')
                pressed = value.get('pressed', True)
                
                # 处理特殊键
                key_map = {
                    'space': Key.space,
                    'enter': Key.enter,
                    'tab': Key.tab,
                    'shift': Key.shift,
                    'ctrl': Key.ctrl,
                    'alt': Key.alt
                }
                
                # 获取实际的键对象
                actual_key = key_map.get(key, key)
                
                if pressed:
                    keyboard.press(actual_key)
                else:
                    keyboard.release(actual_key)
            
            elif input_type == 'mouse':
                from pynput.mouse import Controller as MouseController
                mouse = MouseController()
                
                if 'button' in value:
                    from pynput.mouse import Button
                    button_map = {
                        'left': Button.left,
                        'right': Button.right,
                        'middle': Button.middle
                    }
                    button = button_map.get(value.get('button'))
                    pressed = value.get('pressed', True)
                    
                    if button:
                        if pressed:
                            mouse.press(button)
                        else:
                            mouse.release(button)
                
                elif 'movement' in value:
                    movement = value.get('movement')
                    yaw = movement.get('yaw', 0)
                    pitch = movement.get('pitch', 0)
                    mouse.move(yaw, pitch)
            
            return True
        
        except ImportError:
            print("pynput库未安装，无法发送输入")
            return False
        except Exception as e:
            print(f"发送输入失败: {e}")
            return False
    
    def get_client_info(self):
        """获取客户端信息"""
        return {
            'running': self.is_minecraft_running(),
            'process': self.get_minecraft_process(),
            'window_id': self.window_id
        }
