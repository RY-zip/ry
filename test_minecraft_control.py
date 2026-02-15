from minecraft.core.client import MinecraftClient
from minecraft.core.controller import MinecraftController
import time
import pygetwindow as gw

print("=== 测试Minecraft控制功能 ===")

# 初始化客户端和控制器
client = MinecraftClient()
controller = MinecraftController()

print("\n1. 列出所有窗口，查找Minecraft窗口")
windows = gw.getAllTitles()
minecraft_windows = [title for title in windows if 'minecraft' in title.lower()]

print(f"找到的窗口总数: {len(windows)}")
print(f"包含'minecraft'的窗口: {minecraft_windows}")

print("\n2. 检查Minecraft进程状态")
is_running = client.is_minecraft_running()
print(f"Minecraft进程运行状态: {is_running}")

if is_running:
    process = client.get_minecraft_process()
    print(f"进程ID: {process.pid}")
    print(f"进程名称: {process.name()}")

print("\n3. 测试窗口聚焦")
if is_running:
    print("尝试聚焦到Minecraft窗口...")
    focus_success = client.focus_window()
    print(f"聚焦窗口结果: {focus_success}")
    
    # 再次检查当前聚焦的窗口
    current_window = gw.getActiveWindow()
    if current_window:
        print(f"当前聚焦的窗口: {current_window.title}")
    else:
        print("未找到当前聚焦的窗口")
else:
    print("跳过窗口聚焦测试，因为Minecraft进程未运行")

print("\n4. 测试输入控制")
if is_running:
    print("\n测试键盘输入...")
    print("测试W键按下和释放...")
    
    # 直接测试客户端的send_input方法
    print("发送W键按下...")
    client.send_input('keyboard', {'key': 'w', 'pressed': True})
    time.sleep(2)  # 按住2秒
    
    print("发送W键释放...")
    client.send_input('keyboard', {'key': 'w', 'pressed': False})
    time.sleep(1)
    
    print("\n测试跳跃...")
    print("发送空格键按下和释放...")
    client.send_input('keyboard', {'key': 'space', 'pressed': True})
    time.sleep(0.2)
    client.send_input('keyboard', {'key': 'space', 'pressed': False})
    time.sleep(1)
    
    print("\n测试鼠标移动...")
    print("发送鼠标移动...")
    client.send_input('mouse', {'movement': {'yaw': 50, 'pitch': 0}})
    time.sleep(0.5)
    client.send_input('mouse', {'movement': {'yaw': -50, 'pitch': 0}})
    time.sleep(1)
    
    print("\n测试鼠标点击...")
    print("发送鼠标左键点击...")
    client.send_input('mouse', {'button': 'left', 'pressed': True})
    time.sleep(0.5)
    client.send_input('mouse', {'button': 'left', 'pressed': False})
    time.sleep(1)
    
    print("\n输入控制测试完成!")
else:
    print("跳过输入控制测试，因为Minecraft进程未运行")

print("\n5. 测试控制器高级功能")
if is_running:
    print("\n测试控制器的move_forward方法...")
    controller.move_forward(1)
    time.sleep(1)
    
    print("测试控制器的jump方法...")
    controller.jump()
    time.sleep(1)
    
    print("测试控制器的look_around方法...")
    controller.look_around(30, 0)
    time.sleep(0.5)
    controller.look_around(-30, 0)
    time.sleep(0.5)
    
    print("\n控制器功能测试完成!")
else:
    print("跳过控制器功能测试，因为Minecraft进程未运行")

print("\n=== 测试完成 ===")
print("\n如果Minecraft未被控制，请检查:")
print("1. Minecraft窗口是否真正打开并在前台")
print("2. 窗口标题是否包含'Minecraft'")
print("3. pynput库是否正确安装")
print("4. 是否有其他程序干扰窗口聚焦")
