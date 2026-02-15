from minecraft.utils.config import config
from minecraft.utils.logger import logger
from minecraft.language.command_parser import CommandParser
from minecraft.language.goal_extractor import GoalExtractor
from minecraft.multimodal.adapter import multimodal_adapter
from minecraft.mindcraft_integration import mindcraft_integration

print("=== 测试配置管理 ===")
print(f"默认语言: {config.get('language.default_language')}")
print(f"调试模式: {config.get('system.debug_mode')}")

# 测试修改配置
config.set('system.debug_mode', True)
print(f"修改后的调试模式: {config.get('system.debug_mode')}")

print("\n=== 测试日志系统 ===")
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")

print("\n=== 测试命令解析 ===")
parser = CommandParser()
test_commands = [
    "向前移动两步",
    "跳跃",
    "挖掘石头",
    "放置方块",
    "选择第一个物品"
]

for cmd in test_commands:
    result = parser.parse_command(cmd)
    print(f"命令: {cmd}")
    print(f"解析结果: {result}")
    print(f"对应的动作: {parser.get_command_action(result)}")
    print()

print("\n=== 测试目标提取 ===")
extractor = GoalExtractor()
test_goals = [
    "探索森林",
    "建造房子",
    "收集石头",
    "生存模式"
]

for goal in test_goals:
    result = extractor.extract_goal(goal)
    print(f"目标: {goal}")
    print(f"提取结果: {result}")
    print(f"生成的任务: {extractor.generate_tasks(result)}")
    print()

print("\n=== 测试多模态适配器 ===")
print(f"多模态状态: {multimodal_adapter.get_status()}")

# 测试多模态处理
response = multimodal_adapter.process_multimodal_input(text="你好，测试多模态功能")
print(f"多模态响应: {response}")

print("\n=== 测试mindcraft集成 ===")
print(f"mindcraft状态: {mindcraft_integration.get_status()}")
print(f"mindcraft可用: {mindcraft_integration.is_mindcraft_available()}")

print("\n=== 测试完成 ===")
