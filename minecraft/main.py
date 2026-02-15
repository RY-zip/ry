from core.registry import registry
from core.client import MinecraftClient
from core.controller import MinecraftController

class MinecraftSystem:
    def __init__(self):
        self.client = MinecraftClient()
        self.controller = MinecraftController()
        self.initialize_modules()
    
    def initialize_modules(self):
        """初始化所有模块"""
        # 注册核心模块
        registry.register_module('client', self.client)
        registry.register_module('controller', self.controller)
        
        # 注册功能
        registry.register_feature('move_forward', self.controller.move_forward)
        registry.register_feature('move_backward', self.controller.move_backward)
        registry.register_feature('move_left', self.controller.move_left)
        registry.register_feature('move_right', self.controller.move_right)
        registry.register_feature('jump', self.controller.jump)
        registry.register_feature('mine_block', self.controller.mine_block)
        registry.register_feature('place_block', self.controller.place_block)
        registry.register_feature('look_around', self.controller.look_around)
        registry.register_feature('select_hotbar_slot', self.controller.select_hotbar_slot)
    
    def start(self):
        """启动系统"""
        print("Minecraft系统启动中...")
        
        # 检查Minecraft客户端状态
        if self.client.is_minecraft_running():
            print("检测到Minecraft客户端正在运行")
        else:
            print("未检测到Minecraft客户端运行")
        
        # 打印注册的模块和功能
        print(f"注册的模块: {registry.list_modules()}")
        print(f"注册的功能: {registry.list_features()}")
        
        print("Minecraft系统启动完成！")
    
    def stop(self):
        """停止系统"""
        print("Minecraft系统停止中...")
        # 执行清理操作
        print("Minecraft系统已停止")
    
    def get_status(self):
        """获取系统状态"""
        return {
            'client_running': self.client.is_minecraft_running(),
            'registered_modules': registry.list_modules(),
            'registered_features': registry.list_features(),
            'current_action': self.controller.get_current_action()
        }

def main():
    """主函数"""
    system = MinecraftSystem()
    system.start()
    
    # 示例：使用系统功能
    print("\n示例操作:")
    print("1. 向前移动")
    # system.controller.move_forward(1)
    
    print("2. 跳跃")
    # system.controller.jump()
    
    print("3. 挖掘方块")
    # system.controller.mine_block(2)
    
    print("\n系统状态:")
    print(system.get_status())
    
    system.stop()

if __name__ == "__main__":
    main()
