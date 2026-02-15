import re
from .command_parser import CommandParser

class GoalExtractor:
    def __init__(self):
        self.parser = CommandParser()
        
        # 目标模式
        self.goal_patterns = {
            'explore': [
                r'探索(\w+)',
                r'去(\w+)看看',
                r'寻找(\w+)'
            ],
            'build': [
                r'建造(\w+)',
                r'制作(\w+)',
                r'创建(\w+)'
            ],
            'gather': [
                r'收集(\w+)',
                r'获取(\w+)',
                r'开采(\w+)'
            ],
            'survive': [
                r'生存模式',
                r'活下去',
                r'保持生存'
            ],
            'craft': [
                r'合成(\w+)',
                r'制作(\w+)工具',
                r'打造(\w+)'
            ]
        }
        
        # 任务模板
        self.task_templates = {
            'explore': [
                '向前移动探索',
                '观察周围环境',
                '寻找标志性建筑'
            ],
            'build': [
                '收集建筑材料',
                '规划建筑结构',
                '开始建造'
            ],
            'gather': [
                '寻找资源',
                '开采资源',
                '收集资源'
            ],
            'survive': [
                '寻找食物',
                '建造庇护所',
                '防御怪物'
            ],
            'craft': [
                '收集合成材料',
                '打开合成界面',
                '合成物品'
            ]
        }
    
    def extract_goal(self, input_text):
        """从用户输入中提取目标"""
        if not input_text:
            return None
        
        input_text = input_text.lower().strip()
        
        # 首先尝试解析为命令
        command = self.parser.parse_command(input_text)
        if command:
            return {
                'type': 'command',
                'command': command,
                'raw': input_text
            }
        
        # 尝试提取目标
        for goal_type, patterns in self.goal_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, input_text)
                if match:
                    target = match.group(1) if len(match.groups()) > 0 else None
                    return {
                        'type': 'goal',
                        'goal_type': goal_type,
                        'target': target,
                        'raw': input_text
                    }
        
        # 尝试提取隐含目标
        return self.extract_implicit_goal(input_text)
    
    def extract_implicit_goal(self, input_text):
        """提取隐含目标"""
        keywords = {
            'explore': ['探索', '看看', '发现', '寻找'],
            'build': ['建造', '制作', '创建', '搭建'],
            'gather': ['收集', '获取', '开采', '挖掘'],
            'survive': ['生存', '活着', '安全'],
            'craft': ['合成', '制作', '打造', '加工']
        }
        
        for goal_type, goal_keywords in keywords.items():
            for keyword in goal_keywords:
                if keyword in input_text:
                    return {
                        'type': 'goal',
                        'goal_type': goal_type,
                        'target': None,
                        'raw': input_text
                    }
        
        return None
    
    def generate_tasks(self, goal):
        """根据目标生成任务列表"""
        if not goal:
            return []
        
        if goal['type'] == 'command':
            # 对于命令类型，直接返回命令对应的任务
            action = self.parser.get_command_action(goal['command'])
            if action:
                return [{
                    'type': 'action',
                    'action': action,
                    'priority': 'high'
                }]
        
        elif goal['type'] == 'goal':
            goal_type = goal.get('goal_type')
            target = goal.get('target')
            
            # 根据目标类型生成任务
            tasks = []
            templates = self.task_templates.get(goal_type, [])
            
            for i, template in enumerate(templates):
                # 如果有目标，替换模板中的占位符
                if target:
                    task_description = template.replace(r'(\w+)', target)
                else:
                    task_description = template
                
                # 解析任务描述为命令
                command = self.parser.parse_command(task_description)
                if command:
                    action = self.parser.get_command_action(command)
                    if action:
                        tasks.append({
                            'type': 'action',
                            'action': action,
                            'description': task_description,
                            'priority': 'high' if i == 0 else 'medium'
                        })
            
            return tasks
        
        return []
    
    def prioritize_tasks(self, tasks):
        """对任务进行优先级排序"""
        if not tasks:
            return []
        
        # 优先级顺序：high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t.get('priority', 'medium'), 1))
        return sorted_tasks
    
    def create_task_plan(self, input_text):
        """创建任务计划"""
        # 提取目标
        goal = self.extract_goal(input_text)
        if not goal:
            return {
                'error': '无法理解输入',
                'raw': input_text
            }
        
        # 生成任务
        tasks = self.generate_tasks(goal)
        
        # 优先级排序
        prioritized_tasks = self.prioritize_tasks(tasks)
        
        return {
            'goal': goal,
            'tasks': prioritized_tasks,
            'raw': input_text
        }
    
    def evaluate_progress(self, goal, completed_tasks):
        """评估目标完成进度"""
        if not goal:
            return 0.0
        
        total_tasks = len(self.generate_tasks(goal))
        if total_tasks == 0:
            return 0.0
        
        completed_count = len(completed_tasks)
        progress = min(completed_count / total_tasks, 1.0)
        
        return progress
    
    def get_goal_status(self, goal):
        """获取目标状态"""
        if not goal:
            return None
        
        tasks = self.generate_tasks(goal)
        
        return {
            'goal': goal,
            'total_tasks': len(tasks),
            'task_descriptions': [t.get('description', '') for t in tasks]
        }
