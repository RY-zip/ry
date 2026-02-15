from minecraft.utils.task_scheduler import task_scheduler
from minecraft.utils.logger import logger
from minecraft.utils.file_operations import file_ops
from minecraft.vision.screen_capture import ScreenCapture
from minecraft.vision.block_detector import BlockDetector
import time
from datetime import datetime

class MinecraftTaskManager:
    def __init__(self):
        self.scheduler = task_scheduler
        self.screen_capture = ScreenCapture()
        self.block_detector = BlockDetector()
        self.running_tasks = {}
    
    def start(self):
        """启动任务管理器"""
        if not self.scheduler.start():
            logger.error("任务调度器启动失败")
            return False
        
        # 添加系统默认任务
        self._add_default_tasks()
        logger.info("Minecraft任务管理器启动成功")
        return True
    
    def stop(self):
        """停止任务管理器"""
        if not self.scheduler.stop():
            logger.error("任务调度器停止失败")
            return False
        
        self.running_tasks.clear()
        logger.info("Minecraft任务管理器停止成功")
        return True
    
    def _add_default_tasks(self):
        """添加默认任务"""
        # 添加状态检查任务
        status_task_id = self.scheduler.schedule_repeating(
            self.check_system_status,
            interval=10,
            task_name="系统状态检查"
        )
        self.running_tasks['status'] = status_task_id
        
        # 添加屏幕捕获任务
        capture_task_id = self.scheduler.schedule_repeating(
            self.capture_screen,
            interval=5,
            task_name="屏幕捕获"
        )
        self.running_tasks['capture'] = capture_task_id
    
    def check_system_status(self):
        """检查系统状态"""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'scheduler_status': self.scheduler.get_status(),
                'running_tasks': list(self.running_tasks.keys())
            }
            
            # 保存状态到文件
            file_ops.write_json("system_status.json", status)
            logger.info("系统状态检查完成")
        except Exception as e:
            logger.error(f"系统状态检查失败: {e}")
    
    def capture_screen(self):
        """捕获屏幕"""
        try:
            # 捕获Minecraft窗口
            frame = self.screen_capture.capture_minecraft_window()
            if frame is not None:
                # 检测方块
                blocks = self.block_detector.detect_blocks(frame)
                
                # 保存捕获结果
                capture_data = {
                    'timestamp': datetime.now().isoformat(),
                    'blocks_detected': len(blocks),
                    'detected_blocks': [b['type'] for b in blocks[:5]]  # 只保存前5个方块
                }
                
                file_ops.write_json("latest_capture.json", capture_data)
                logger.info(f"屏幕捕获完成，检测到 {len(blocks)} 个方块")
        except Exception as e:
            logger.error(f"屏幕捕获失败: {e}")
    
    def add_exploration_task(self, duration=60):
        """添加探索任务"""
        def exploration_task():
            logger.info("执行探索任务")
            # 这里可以添加具体的探索逻辑
        
        task_id = self.scheduler.add_task(
            exploration_task,
            delay=0,
            interval=5,
            max_runs=duration // 5,
            task_name="探索任务"
        )
        
        self.running_tasks['exploration'] = task_id
        logger.info(f"添加探索任务，持续 {duration} 秒")
        return task_id
    
    def add_gathering_task(self, resource_type, duration=30):
        """添加资源收集任务"""
        def gathering_task():
            logger.info(f"执行资源收集任务: {resource_type}")
            # 这里可以添加具体的资源收集逻辑
        
        task_id = self.scheduler.add_task(
            gathering_task,
            delay=0,
            interval=3,
            max_runs=duration // 3,
            task_name=f"收集{resource_type}"
        )
        
        self.running_tasks['gathering'] = task_id
        logger.info(f"添加资源收集任务: {resource_type}，持续 {duration} 秒")
        return task_id
    
    def add_building_task(self, structure_type):
        """添加建筑任务"""
        def building_task():
            logger.info(f"执行建筑任务: {structure_type}")
            # 这里可以添加具体的建筑逻辑
        
        task_id = self.scheduler.add_task(
            building_task,
            delay=0,
            task_name=f"建造{structure_type}"
        )
        
        self.running_tasks['building'] = task_id
        logger.info(f"添加建筑任务: {structure_type}")
        return task_id
    
    def cancel_task(self, task_name):
        """取消指定任务"""
        if task_name in self.running_tasks:
            task_id = self.running_tasks[task_name]
            self.scheduler.remove_task(task_id)
            del self.running_tasks[task_name]
            logger.info(f"取消任务: {task_name}")
            return True
        return False
    
    def get_task_status(self):
        """获取任务状态"""
        status = {
            'manager_status': 'running' if self.scheduler.get_status()['running'] else 'stopped',
            'running_tasks': self.running_tasks,
            'scheduler_status': self.scheduler.get_status()
        }
        return status
    
    def optimize_tasks(self):
        """优化任务执行"""
        try:
            # 分析当前任务执行情况
            tasks = self.scheduler.get_tasks()
            
            # 统计任务执行时间
            execution_times = {}
            for task in tasks:
                if task['runs'] > 0:
                    execution_times[task['id']] = task['runs']
            
            # 调整任务执行间隔
            for task in tasks:
                if task['interval'] > 0:
                    # 根据执行情况动态调整间隔
                    if task['runs'] > 5:
                        # 执行次数多的任务可以适当延长间隔
                        new_interval = min(task['interval'] * 1.2, 30)  # 最大间隔30秒
                        # 这里可以添加调整间隔的逻辑
            
            logger.info("任务优化完成")
            return True
        except Exception as e:
            logger.error(f"任务优化失败: {e}")
            return False

# 创建全局任务管理器实例
task_manager = MinecraftTaskManager()
