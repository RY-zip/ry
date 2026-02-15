import psutil

print("=== 列出所有运行的进程 ===")
print("进程名称包含'minecraft'或'openjdk'的进程:")
print("-" * 60)

# 遍历所有进程
for proc in psutil.process_iter(['pid', 'name']):
    try:
        process_name = proc.info['name']
        process_id = proc.info['pid']
        
        # 检查进程名称是否包含关键字
        if 'minecraft' in process_name.lower() or 'openjdk' in process_name.lower():
            print(f"PID: {process_id}, 名称: {process_name}")
    
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print("-" * 60)
print("\n=== 列出所有Java相关进程 ===")
print("-" * 60)

# 列出所有Java相关进程
for proc in psutil.process_iter(['pid', 'name']):
    try:
        process_name = proc.info['name']
        process_id = proc.info['pid']
        
        if 'java' in process_name.lower():
            print(f"PID: {process_id}, 名称: {process_name}")
    
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print("-" * 60)
print("\n=== 进程列表完成 ===")
