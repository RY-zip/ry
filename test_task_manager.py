from minecraft.task_manager import task_manager
import time
from datetime import datetime

print("=== 测试Minecraft任务管理器 ===")

print("\n1. 启动任务管理器")
success = task_manager.start()
print(f"启动结果: {success}")

print("\n2. 查看初始任务状态")
status = task_manager.get_task_status()
print(f"任务管理器状态: {status}")

print("\n3. 添加探索任务")
exploration_task_id = task_manager.add_exploration_task(duration=15)
print(f"添加的探索任务ID: {exploration_task_id}")

print("\n4. 添加资源收集任务")
gathering_task_id = task_manager.add_gathering_task("石头", duration=10)
print(f"添加的资源收集任务ID: {gathering_task_id}")

print("\n5. 添加建筑任务")
building_task_id = task_manager.add_building_task("房子")
print(f"添加的建筑任务ID: {building_task_id}")

print("\n6. 查看添加任务后的状态")
status = task_manager.get_task_status()
print(f"任务管理器状态: {status}")

print("\n7. 等待任务执行...")
time.sleep(20)

print("\n8. 查看任务执行状态")
status = task_manager.get_task_status()
print(f"任务管理器状态: {status}")

print("\n9. 测试任务优化")
optimize_result = task_manager.optimize_tasks()
print(f"任务优化结果: {optimize_result}")

print("\n10. 取消探索任务")
cancel_result = task_manager.cancel_task('exploration')
print(f"取消探索任务结果: {cancel_result}")

print("\n11. 查看取消任务后的状态")
status = task_manager.get_task_status()
print(f"任务管理器状态: {status}")

print("\n12. 停止任务管理器")
success = task_manager.stop()
print(f"停止结果: {success}")

print("\n=== 测试完成 ===")
