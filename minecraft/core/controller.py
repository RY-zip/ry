from .client import MinecraftClient

class MinecraftController:
    def __init__(self):
        self.client = MinecraftClient()
        self.current_action = None
    
    def move_forward(self, duration=1):
        """向前移动"""
        self.current_action = 'move_forward'
        # 实现向前移动逻辑
        try:
            success = self.client.send_input('keyboard', {'key': 'w', 'pressed': True})
            if success:
                import time
                time.sleep(duration)
                self.client.send_input('keyboard', {'key': 'w', 'pressed': False})
            else:
                print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 移动向前失败: {e}")
        finally:
            self.current_action = None
    
    def move_backward(self, duration=1):
        """向后移动"""
        self.current_action = 'move_backward'
        # 实现向后移动逻辑
        try:
            success = self.client.send_input('keyboard', {'key': 's', 'pressed': True})
            if success:
                import time
                time.sleep(duration)
                self.client.send_input('keyboard', {'key': 's', 'pressed': False})
            else:
                print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 移动向后失败: {e}")
        finally:
            self.current_action = None
    
    def move_left(self, duration=1):
        """向左移动"""
        self.current_action = 'move_left'
        # 实现向左移动逻辑
        try:
            success = self.client.send_input('keyboard', {'key': 'a', 'pressed': True})
            if success:
                import time
                time.sleep(duration)
                self.client.send_input('keyboard', {'key': 'a', 'pressed': False})
            else:
                print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 移动向左失败: {e}")
        finally:
            self.current_action = None
    
    def move_right(self, duration=1):
        """向右移动"""
        self.current_action = 'move_right'
        # 实现向右移动逻辑
        try:
            success = self.client.send_input('keyboard', {'key': 'd', 'pressed': True})
            if success:
                import time
                time.sleep(duration)
                self.client.send_input('keyboard', {'key': 'd', 'pressed': False})
            else:
                print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 移动向右失败: {e}")
        finally:
            self.current_action = None
    
    def jump(self):
        """跳跃"""
        self.current_action = 'jump'
        # 实现跳跃逻辑
        try:
            success = self.client.send_input('keyboard', {'key': 'space', 'pressed': True})
            if success:
                import time
                time.sleep(0.2)
                self.client.send_input('keyboard', {'key': 'space', 'pressed': False})
            else:
                print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 跳跃失败: {e}")
        finally:
            self.current_action = None
    
    def mine_block(self, duration=2):
        """挖掘方块"""
        self.current_action = 'mine_block'
        # 实现挖掘逻辑
        try:
            success = self.client.send_input('mouse', {'button': 'left', 'pressed': True})
            if success:
                import time
                time.sleep(duration)
                self.client.send_input('mouse', {'button': 'left', 'pressed': False})
            else:
                print("警告: 无法发送鼠标输入")
        except Exception as e:
            print(f"错误: 挖掘方块失败: {e}")
        finally:
            self.current_action = None
    
    def place_block(self):
        """放置方块"""
        self.current_action = 'place_block'
        # 实现放置方块逻辑
        try:
            success = self.client.send_input('mouse', {'button': 'right', 'pressed': True})
            if success:
                import time
                time.sleep(0.2)
                self.client.send_input('mouse', {'button': 'right', 'pressed': False})
            else:
                print("警告: 无法发送鼠标输入")
        except Exception as e:
            print(f"错误: 放置方块失败: {e}")
        finally:
            self.current_action = None
    
    def look_around(self, yaw, pitch):
        """环顾四周"""
        # 实现视角控制逻辑
        try:
            success = self.client.send_input('mouse', {'movement': {'yaw': yaw, 'pitch': pitch}})
            if not success:
                print("警告: 无法发送鼠标输入")
        except Exception as e:
            print(f"错误: 环顾四周失败: {e}")
    
    def select_hotbar_slot(self, slot):
        """选择快捷栏物品"""
        # 实现快捷栏选择逻辑
        try:
            if 1 <= slot <= 9:
                success = self.client.send_input('keyboard', {'key': str(slot), 'pressed': True})
                if success:
                    import time
                    time.sleep(0.1)
                    self.client.send_input('keyboard', {'key': str(slot), 'pressed': False})
                else:
                    print("警告: 无法发送键盘输入")
        except Exception as e:
            print(f"错误: 选择快捷栏物品失败: {e}")
    
    def get_current_action(self):
        """获取当前动作"""
        return self.current_action
    
    def stop_current_action(self):
        """停止当前动作"""
        self.current_action = None
