import threading
import time
from datetime import datetime, timedelta
from minecraft.utils.logger import logger
from minecraft.utils.file_operations import file_ops

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
        self.thread = None
        self.task_id_counter = 0
    
    def start(self):
        """启动任务调度器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info("任务调度器启动成功")
        return self.running
    
    def stop(self):
        """停止任务调度器"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2)
            logger.info("任务调度器停止成功")
        return not self.running
    
    def add_task(self, task_func, delay=0, interval=0, max_runs=1, task_name=""):
        """添加任务
        
        Args:
            task_func: 任务函数
            delay: 延迟执行时间（秒）
            interval: 执行间隔（秒），0表示只执行一次
            max_runs: 最大执行次数，0表示无限次
            task_name: 任务名称
        """
        self.task_id_counter += 1
        task_id = self.task_id_counter
        
        task = {
            'id': task_id,
            'name': task_name or f"Task_{task_id}",
            'func': task_func,
            'delay': delay,
            'interval': interval,
            'max_runs': max_runs,
            'runs': 0,
            'next_run': time.time() + delay,
            'status': 'pending'
        }
        
        self.tasks.append(task)
        logger.info(f"添加任务: {task['name']} (ID: {task_id})")
        return task_id
    
    def remove_task(self, task_id):
        """移除任务"""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        logger.info(f"移除任务: {task_id}")
        return True
    
    def get_tasks(self):
        """获取所有任务"""
        return self.tasks
    
    def get_task(self, task_id):
        """获取指定任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def _run(self):
        """任务调度器运行循环"""
        while self.running:
            current_time = time.time()
            
            # 执行到期的任务
            for task in self.tasks:
                if task['status'] == 'pending' and current_time >= task['next_run']:
                    self._execute_task(task)
            
            # 清理已完成的任务
            self.tasks = [task for task in self.tasks if not (task['status'] == 'completed' and task['max_runs'] > 0 and task['runs'] >= task['max_runs'])]
            
            time.sleep(0.1)  # 避免CPU占用过高
    
    def _execute_task(self, task):
        """执行任务"""
        try:
            task['status'] = 'running'
            logger.info(f"开始执行任务: {task['name']} (ID: {task['id']})")
            
            # 执行任务函数
            task['func']()
            
            task['runs'] += 1
            task['status'] = 'completed'
            logger.info(f"任务执行完成: {task['name']} (ID: {task['id']}), 已执行 {task['runs']}/{task['max_runs']} 次")
            
            # 计算下一次执行时间
            if task['interval'] > 0 and (task['max_runs'] == 0 or task['runs'] < task['max_runs']):
                task['next_run'] = time.time() + task['interval']
                task['status'] = 'pending'
            elif task['max_runs'] > 0 and task['runs'] >= task['max_runs']:
                logger.info(f"任务达到最大执行次数: {task['name']} (ID: {task['id']})")
            
        except Exception as e:
            task['status'] = 'error'
            logger.error(f"任务执行失败: {task['name']} (ID: {task['id']}), 错误: {e}")
    
    def schedule_at(self, task_func, scheduled_time, task_name=""):
        """在指定时间执行任务
        
        Args:
            task_func: 任务函数
            scheduled_time: 执行时间（datetime对象）
            task_name: 任务名称
        """
        delay = (scheduled_time - datetime.now()).total_seconds()
        if delay < 0:
            delay = 0
        return self.add_task(task_func, delay=delay, task_name=task_name)
    
    def schedule_repeating(self, task_func, interval, start_delay=0, max_runs=0, task_name=""):
        """添加重复执行的任务
        
        Args:
            task_func: 任务函数
            interval: 执行间隔（秒）
            start_delay: 开始延迟（秒）
            max_runs: 最大执行次数，0表示无限次
            task_name: 任务名称
        """
        return self.add_task(
            task_func,
            delay=start_delay,
            interval=interval,
            max_runs=max_runs,
            task_name=task_name
        )
    
    def get_status(self):
        """获取调度器状态"""
        return {
            'running': self.running,
            'task_count': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks if t['status'] == 'pending']),
            'running_tasks': len([t for t in self.tasks if t['status'] == 'running']),
            'completed_tasks': len([t for t in self.tasks if t['status'] == 'completed']),
            'error_tasks': len([t for t in self.tasks if t['status'] == 'error'])
        }

# 创建全局任务调度器实例
task_scheduler = TaskScheduler()
