import re

class CommandParser:
    def __init__(self):
        # 命令模式
        self.command_patterns = {
            'move': [
                r'向前移动(\d+)?步?',
                r'向后移动(\d+)?步?',
                r'向左移动(\d+)?步?',
                r'向右移动(\d+)?步?',
                r'移动到(\d+),(\d+),(\d+)'
            ],
            'jump': [
                r'跳(跃)?',
                r'向上跳'
            ],
            'mine': [
                r'挖(掘)?(\w+)?方块?',
                r'破坏(\w+)?方块?'
            ],
            'place': [
                r'放置(\w+)?方块?',
                r'放(\w+)?方块?'
            ],
            'look': [
                r'看向(\w+)',
                r'环顾四周'
            ],
            'select': [
                r'选择第(\d+)个物品',
                r'切换到第(\d+)格'
            ],
            'stop': [
                r'停止',
                r'暂停'
            ],
            'status': [
                r'状态',
                r'系统状态'
            ]
        }
    
    def parse_command(self, input_text):
        """解析用户输入命令"""
        if not input_text:
            return None
        
        input_text = input_text.lower().strip()
        
        # 遍历所有命令模式
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, input_text)
                if match:
                    return {
                        'type': command_type,
                        'params': match.groups(),
                        'raw': input_text
                    }
        
        # 尝试解析复合命令
        return self.parse_complex_command(input_text)
    
    def parse_complex_command(self, input_text):
        """解析复合命令"""
        # 示例：解析"向前移动两步然后跳跃"这样的复合命令
        parts = re.split(r'然后|接着|再', input_text)
        if len(parts) > 1:
            commands = []
            for part in parts:
                part = part.strip()
                if part:
                    cmd = self.parse_command(part)
                    if cmd:
                        commands.append(cmd)
            if commands:
                return {
                    'type': 'sequence',
                    'commands': commands,
                    'raw': input_text
                }
        
        return None
    
    def extract_parameters(self, command):
        """从命令中提取参数"""
        if not command:
            return {}
        
        params = {}
        command_type = command.get('type')
        raw_params = command.get('params', ())
        
        if command_type == 'move':
            if len(raw_params) == 1 and raw_params[0]:
                params['steps'] = int(raw_params[0])
            elif len(raw_params) == 3:
                params['x'] = int(raw_params[0])
                params['y'] = int(raw_params[1])
                params['z'] = int(raw_params[2])
        
        elif command_type == 'mine':
            if len(raw_params) > 0 and raw_params[1]:
                params['block_type'] = raw_params[1]
        
        elif command_type == 'place':
            if len(raw_params) > 0 and raw_params[0]:
                params['block_type'] = raw_params[0]
        
        elif command_type == 'look':
            if len(raw_params) > 0 and raw_params[0]:
                params['direction'] = raw_params[0]
        
        elif command_type == 'select':
            if len(raw_params) > 0 and raw_params[0]:
                params['slot'] = int(raw_params[0])
        
        return params
    
    def validate_command(self, command):
        """验证命令是否有效"""
        if not command:
            return False
        
        command_type = command.get('type')
        
        # 验证命令类型
        valid_types = list(self.command_patterns.keys()) + ['sequence']
        if command_type not in valid_types:
            return False
        
        # 验证参数
        if command_type == 'select':
            params = self.extract_parameters(command)
            slot = params.get('slot')
            if slot and not (1 <= slot <= 9):
                return False
        
        return True
    
    def get_command_action(self, command):
        """获取命令对应的动作"""
        if not command or not self.validate_command(command):
            return None
        
        command_type = command.get('type')
        params = self.extract_parameters(command)
        
        action_map = {
            'move': 'move_forward',  # 默认向前移动
            'jump': 'jump',
            'mine': 'mine_block',
            'place': 'place_block',
            'look': 'look_around',
            'select': 'select_hotbar_slot',
            'stop': 'stop_current_action',
            'status': 'get_status'
        }
        
        if command_type == 'sequence':
            return {
                'type': 'sequence',
                'actions': [self.get_command_action(cmd) for cmd in command.get('commands', [])]
            }
        
        action = action_map.get(command_type)
        if action:
            return {
                'type': action,
                'params': params
            }
        
        return None
