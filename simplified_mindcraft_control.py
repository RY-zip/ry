# 简化版脚本，只使用mindcraft_integration
import subprocess
import time
import os
from datetime import datetime

print("=== 使用mindcraft-develop控制Minecraft ===")
print(f"启动时间: {datetime.now().isoformat()}")

# mindcraft-develop目录
MINDCRAFT_DIR = "f:\\5\\ry\\mindcraft-develop"

print("\n1. 检查mindcraft-develop目录")
if not os.path.exists(MINDCRAFT_DIR):
    print(f"错误: 未找到mindcraft-develop目录: {MINDCRAFT_DIR}")
    exit(1)
else:
    print(f"找到mindcraft-develop目录: {MINDCRAFT_DIR}")

print("\n2. 检查package.json文件")
package_json = os.path.join(MINDCRAFT_DIR, "package.json")
if not os.path.exists(package_json):
    print(f"错误: 未找到package.json文件: {package_json}")
    exit(1)
else:
    print("找到package.json文件，mindcraft-develop安装正确")

print("\n3. 启动mindcraft-develop")
print("正在启动mindcraft-develop...")

# 启动mindcraft-develop
process = subprocess.Popen(
    "npm start",
    cwd=MINDCRAFT_DIR,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print(f"mindcraft-develop已启动，进程ID: {process.pid}")

# 等待启动完成
print("\n4. 等待启动完成...")
time.sleep(10)  # 给足够的时间启动

# 检查进程是否仍在运行
if process.poll() is None:
    print("\n5. mindcraft-develop启动成功！")
    print("\n系统现在通过mindcraft-develop控制Minecraft")
    print("mindcraft-develop具有以下功能:")
    print("- 智能移动和视角控制")
    print("- 自动探索和资源收集")
    print("- 背包管理和物品合成")
    print("- 更高级的游戏交互能力")
    print("\n控制界面可访问: http://localhost:8080")
    print("机器人视角可访问: http://localhost:3000")
    print("\n=== 系统启动完成 ===")
    print("按 Ctrl+C 停止系统")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止系统...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("系统已停止")
else:
    # 读取错误输出
    stderr = process.stderr.read()
    print(f"\n5. mindcraft-develop启动失败: {stderr}")
    print("请检查mindcraft-develop的安装和配置")
