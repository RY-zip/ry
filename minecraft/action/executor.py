import time
from core.controller import MinecraftController

class ActionExecutor:
    def __init__(self):
        self.controller = MinecraftController()
        self.running = False
        self.current_action = None
    
    def execute_action(self, action):
        """执行单个动作"""
        if not action:
            return False
        
        self.current_action = action
        action_type = action.get('type')
        params = action.get('params', {})
        
        try:
            # 根据动作类型执行相应操作
            if action_type == 'move_forward':
                duration = params.get('steps', 1)
                self.controller.move_forward(duration)
            
            elif action_type == 'move_backward':
                duration = params.get('steps', 1)
                self.controller.move_backward(duration)
            
            elif action_type == 'move_left':
                duration = params.get('steps', 1)
                self.controller.move_left(duration)
            
            elif action_type == 'move_right':
                duration = params.get('steps', 1)
                self.controller.move_right(duration)
            
            elif action_type == 'jump':
                self.controller.jump()
            
            elif action_type == 'mine_block':
                duration = params.get('duration', 2)
                self.controller.mine_block(duration)
            
            elif action_type == 'place_block':
                self.controller.place_block()
            
            elif action_type == 'look_around':
                yaw = params.get('yaw', 0)
                pitch = params.get('pitch', 0)
                self.controller.look_around(yaw, pitch)
            
            elif action_type == 'select_hotbar_slot':
                slot = params.get('slot', 1)
                self.controller.select_hotbar_slot(slot)
            
            elif action_type == 'stop_current_action':
                self.controller.stop_current_action()
            
            else:
                print(f"未知动作类型: {action_type}")
                return False
            
            return True
        
        except Exception as e:
            print(f"执行动作失败: {e}")
            return False
        
        finally:
            self.current_action = None
    
    def execute_sequence(self, actions):
        """执行动作序列"""
        if not actions:
            return False
        
        self.running = True
        success_count = 0
        
        try:
            for action in actions:
                if not self.running:
                    break
                
                if action.get('type') == 'sequence':
                    # 递归执行子序列
                    sub_actions = action.get('actions', [])
                    if sub_actions:
                        if self.execute_sequence(sub_actions):
                            success_count += len(sub_actions)
                
                else:
                    if self.execute_action(action):
                        success_count += 1
                
                # 动作之间添加短暂延迟
                time.sleep(0.1)
            
            return success_count > 0
        
        finally:
            self.running = False
            self.current_action = None
    
    def execute_task(self, task):
        """执行任务"""
        if not task:
            return False
        
        task_type = task.get('type')
        
        if task_type == 'action':
            action = task.get('action')
            return self.execute_action(action)
        
        elif task_type == 'sequence':
            actions = task.get('actions', [])
            return self.execute_sequence(actions)
        
        else:
            print(f"未知任务类型: {task_type}")
            return False
    
    def stop_execution(self):
        """停止执行"""
        self.running = False
        self.controller.stop_current_action()
        self.current_action = None
    
    def get_execution_status(self):
        """获取执行状态"""
        return {
            'running': self.running,
            'current_action': self.current_action,
            'controller_status': self.controller.get_current_action()
        }
    
    def execute_plan(self, plan):
        """执行任务计划"""
        if not plan:
            return False
        
        tasks = plan.get('tasks', [])
        if not tasks:
            return False
        
        print(f"开始执行任务计划，共{len(tasks)}个任务")
        
        success_count = 0
        for i, task in enumerate(tasks):
            print(f"执行任务 {i+1}/{len(tasks)}: {task.get('description', '未知任务')}")
            
            if self.execute_task(task):
                success_count += 1
                print(f"任务 {i+1} 执行成功")
            else:
                print(f"任务 {i+1} 执行失败")
            
            # 任务之间添加延迟
            time.sleep(0.5)
        
        print(f"任务计划执行完成，成功 {success_count}/{len(tasks)} 个任务")
        return success_count > 0
