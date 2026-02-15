from .executor import ActionExecutor
from language.goal_extractor import GoalExtractor

class ActionPlanner:
    def __init__(self):
        self.executor = ActionExecutor()
        self.goal_extractor = GoalExtractor()
        self.current_plan = None
    
    def create_plan(self, goal_input):
        """创建任务计划"""
        # 提取目标
        goal = self.goal_extractor.extract_goal(goal_input)
        if not goal:
            return {
                'error': '无法理解目标',
                'raw': goal_input
            }
        
        # 生成任务计划
        plan = self.goal_extractor.create_task_plan(goal_input)
        self.current_plan = plan
        
        return plan
    
    def optimize_plan(self, plan):
        """优化任务计划"""
        if not plan or 'tasks' not in plan:
            return plan
        
        tasks = plan['tasks']
        optimized_tasks = []
        
        # 合并相同类型的连续任务
        last_task = None
        for task in tasks:
            if last_task and task['type'] == last_task['type']:
                # 合并相同类型的任务
                # 这里可以根据具体任务类型实现合并逻辑
                optimized_tasks.append(task)
            else:
                optimized_tasks.append(task)
            last_task = task
        
        plan['tasks'] = optimized_tasks
        plan['optimized'] = True
        
        return plan
    
    def execute_plan(self, plan=None):
        """执行任务计划"""
        if plan:
            self.current_plan = plan
        elif not self.current_plan:
            return False
        
        # 优化计划
        optimized_plan = self.optimize_plan(self.current_plan)
        
        # 执行计划
        return self.executor.execute_plan(optimized_plan)
    
    def get_plan_status(self):
        """获取计划状态"""
        if not self.current_plan:
            return {
                'status': 'no_plan',
                'message': '没有当前计划'
            }
        
        execution_status = self.executor.get_execution_status()
        
        return {
            'status': 'running' if execution_status['running'] else 'idle',
            'current_plan': self.current_plan,
            'execution_status': execution_status
        }
    
    def cancel_plan(self):
        """取消当前计划"""
        self.executor.stop_execution()
        self.current_plan = None
        return True
    
    def create_exploration_plan(self, area_size=100):
        """创建探索计划"""
        # 创建探索任务序列
        tasks = [
            {
                'type': 'action',
                'action': {
                    'type': 'move_forward',
                    'params': {'steps': 5}
                },
                'description': '向前探索',
                'priority': 'high'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'look_around',
                    'params': {'yaw': 90, 'pitch': 0}
                },
                'description': '向左观察',
                'priority': 'medium'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'look_around',
                    'params': {'yaw': -180, 'pitch': 0}
                },
                'description': '向右观察',
                'priority': 'medium'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'move_forward',
                    'params': {'steps': 5}
                },
                'description': '继续向前探索',
                'priority': 'high'
            }
        ]
        
        plan = {
            'type': 'exploration',
            'area_size': area_size,
            'tasks': tasks,
            'created_at': self._get_current_time()
        }
        
        self.current_plan = plan
        return plan
    
    def create_gathering_plan(self, resource_type):
        """创建资源收集计划"""
        tasks = [
            {
                'type': 'action',
                'action': {
                    'type': 'move_forward',
                    'params': {'steps': 10}
                },
                'description': '寻找资源',
                'priority': 'high'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'mine_block',
                    'params': {'duration': 3}
                },
                'description': f'开采{resource_type}',
                'priority': 'high'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'move_forward',
                    'params': {'steps': 5}
                },
                'description': '继续寻找资源',
                'priority': 'medium'
            }
        ]
        
        plan = {
            'type': 'gathering',
            'resource_type': resource_type,
            'tasks': tasks,
            'created_at': self._get_current_time()
        }
        
        self.current_plan = plan
        return plan
    
    def create_building_plan(self, structure_type):
        """创建建筑计划"""
        tasks = [
            {
                'type': 'action',
                'action': {
                    'type': 'select_hotbar_slot',
                    'params': {'slot': 1}
                },
                'description': '选择建筑材料',
                'priority': 'high'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'place_block',
                    'params': {}
                },
                'description': f'开始建造{structure_type}',
                'priority': 'high'
            },
            {
                'type': 'action',
                'action': {
                    'type': 'move_forward',
                    'params': {'steps': 1}
                },
                'description': '移动到下一个位置',
                'priority': 'medium'
            }
        ]
        
        plan = {
            'type': 'building',
            'structure_type': structure_type,
            'tasks': tasks,
            'created_at': self._get_current_time()
        }
        
        self.current_plan = plan
        return plan
    
    def _get_current_time(self):
        """获取当前时间"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S')
