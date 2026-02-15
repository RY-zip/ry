from minecraft.utils.task_scheduler import task_scheduler
from datetime import datetime, timedelta
import time

print("=== 测试任务调度器 ===")

# 测试任务函数
def test_task_1():
    print(f"[{datetime.now()}] 执行测试任务 1")

def test_task_2():
    print(f"[{datetime.now()}] 执行测试任务 2")

def test_task_3():
    print(f"[{datetime.now()}] 执行测试任务 3")

def error_task():
    print(f"[{datetime.now()}] 执行错误任务")
    raise Exception("测试错误")

print("\n1. 启动任务调度器")
success = task_scheduler.start()
print(f"启动结果: {success}")

print("\n2. 添加延迟任务")
task1_id = task_scheduler.add_task(test_task_1, delay=2, task_name="延迟任务")
print(f"添加的任务ID: {task1_id}")

print("\n3. 添加重复任务")
task2_id = task_scheduler.schedule_repeating(test_task_2, interval=1, max_runs=3, task_name="重复任务")
print(f"添加的任务ID: {task2_id}")

print("\n4. 添加定时任务")
scheduled_time = datetime.now() + timedelta(seconds=3)
task3_id = task_scheduler.schedule_at(test_task_3, scheduled_time, task_name="定时任务")
print(f"添加的任务ID: {task3_id}")

print("\n5. 添加错误任务")
task4_id = task_scheduler.add_task(error_task, delay=1, task_name="错误任务")
print(f"添加的任务ID: {task4_id}")

print("\n6. 查看任务状态")
print(f"调度器状态: {task_scheduler.get_status()}")

print("\n7. 等待任务执行...")
time.sleep(5)

print("\n8. 查看任务执行结果")
tasks = task_scheduler.get_tasks()
for task in tasks:
    print(f"任务 {task['id']} ({task['name']}): 状态={task['status']}, 执行次数={task['runs']}")

print("\n9. 移除任务")
task_scheduler.remove_task(task2_id)
print(f"移除任务 {task2_id}")

print("\n10. 查看剩余任务")
remaining_tasks = task_scheduler.get_tasks()
print(f"剩余任务数量: {len(remaining_tasks)}")
for task in remaining_tasks:
    print(f"任务 {task['id']} ({task['name']})")

print("\n11. 停止任务调度器")
success = task_scheduler.stop()
print(f"停止结果: {success}")

print("\n=== 测试完成 ===")
