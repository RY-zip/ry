# main.py - 整合AI大脑和工具
import asyncio
from tool_router import ToolRouter, ToolCall

# ============ 1. 定义各种工具 ============

async def screen_analyzer(params: dict):
    """屏幕识别工具"""
    print(f"🔍 [屏幕工具] 开始分析: {params.get('prompt', '')}")
    # 这里调用GLM-4.6V的视觉API
    await asyncio.sleep(2)  # 模拟耗时操作
    return {"description": "屏幕上有一个Chrome浏览器图标和任务栏"}

async def mouse_controller(params: dict):
    """鼠标控制工具"""
    print(f"🖱️ [鼠标工具] 执行: {params.get('action')} 在 {params.get('position')}")
    # 这里调用PyAutoGUI
    await asyncio.sleep(0.5)
    return {"success": True}

async def tts_generator(params: dict):
    """语音合成工具"""
    print(f"🔊 [语音工具] 合成: {params.get('text')[:20]}...")
    # 这里调用GPT-SoVITS
    await asyncio.sleep(0.8)
    return {"audio_path": "output.wav"}

async def bullet_comment_reader(params: dict):
    """B站弹幕工具"""
    print(f"💬 [弹幕工具] 获取最新弹幕")
    # 这里调用B站API
    await asyncio.sleep(1)
    return {"comments": ["主播好可爱", "2333", "再来一首"]}

# ============ 2. AI大脑的回调函数 ============

def on_tool_completed(tool_call: ToolCall):
    """当工具执行完成时，路由器会调用这个函数"""
    print(f"\n📨 [AI收到工具结果] 任务ID: {tool_call.id}")
    print(f"   工具: {tool_call.tool_name}")
    print(f"   状态: {tool_call.status.value}")
    
    if tool_call.status.value == "completed":
        print(f"   结果: {tool_call.result}")
        # 这里你可以：
        # 1. 将结果存入记忆系统
        # 2. 让AI基于结果继续思考
        # 3. 触发新的对话或行动
    else:
        print(f"   错误: {tool_call.error}")

# ============ 3. 主程序 ============

async def main():
    # 1. 创建路由器
    router = ToolRouter()
    
    # 2. 注册所有工具
    router.register_tool(
        "analyze_screen", 
        screen_analyzer, 
        "分析屏幕内容，返回文字描述"
    )
    router.register_tool(
        "control_mouse", 
        mouse_controller, 
        "控制鼠标移动和点击"
    )
    router.register_tool(
        "generate_speech", 
        tts_generator, 
        "将文本合成为语音"
    )
    router.register_tool(
        "get_bullet_comments", 
        bullet_comment_reader, 
        "获取B站直播间的最新弹幕"
    )
    
    # 3. 设置AI回调
    router.set_ai_callback(on_tool_completed)
    
    # 4. 启动路由器
    router.start()
    
    # 5. 模拟AI大脑永不停止的思考循环
    print("\n🧠 AI大脑开始永不停止的思考...\n")
    
    # 模拟AI连续调用多个工具，不等结果
    task_ids = []
    
    # 第1个指令：分析屏幕
    task1 = await router.call_tool("analyze_screen", {
        "prompt": "描述当前屏幕内容"
    })
    task_ids.append(task1)
    print(f"🤖 AI发出指令1: 分析屏幕 (任务ID: {task1})")
    
    # AI继续思考，立即发出第2个指令
    task2 = await router.call_tool("get_bullet_comments", {})
    task_ids.append(task2)
    print(f"🤖 AI发出指令2: 获取弹幕 (任务ID: {task2})")
    
    # AI继续思考，发出第3个指令
    task3 = await router.call_tool("control_mouse", {
        "action": "click",
        "position": [100, 200]
    })
    task_ids.append(task3)
    print(f"🤖 AI发出指令3: 点击鼠标 (任务ID: {task3})")
    
    # AI可以随时查询任务状态
    await asyncio.sleep(1)
    for task_id in task_ids:
        status = await router.get_task_status(task_id)
        print(f"📊 任务 {task_id[:8]}... 状态: {status.status.value}")
    
    # 保持程序运行，等待所有工具完成
    await asyncio.sleep(5)
    
    # 停止路由器
    router.stop()

# 运行
if __name__ == "__main__":
    asyncio.run(main())