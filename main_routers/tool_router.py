# tool_router.py - 工具调用路由器（中继器/中转站）
import asyncio
import uuid
from typing import Dict, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import time

class ToolStatus(Enum):
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"        # 失败

@dataclass
class ToolCall:
    """一次工具调用的完整记录"""
    id: str                  # 唯一ID
    tool_name: str           # 工具名称
    parameters: Dict         # 调用参数
    status: ToolStatus       # 当前状态
    created_at: float        # 创建时间
    completed_at: float = None  # 完成时间
    result: Any = None       # 执行结果
    error: str = None       # 错误信息

class ToolRouter:
    """工具调用路由器 - AI大脑和所有工具之间的唯一桥梁"""
    
    def __init__(self):
        # 1. 工具注册表：存储所有可用的工具
        self.tools = {}
        
        # 2. 任务队列：待执行的工具调用
        self.task_queue = asyncio.Queue()
        
        # 3. 任务状态表：跟踪所有进行中的调用
        self.tasks: Dict[str, ToolCall] = {}
        
        # 4. AI大脑的回调函数（由主程序设置）
        self.ai_callback = None
        
        # 5. 运行标志
        self.is_running = False
        
    def register_tool(self, name: str, handler: Callable[[Dict], Awaitable[Any]], description: str = ""):
        """注册一个工具到路由器"""
        self.tools[name] = {
            "handler": handler,
            "description": description
        }
        print(f"✅ 工具已注册: {name}")
    
    def set_ai_callback(self, callback: Callable[[ToolCall], None]):
        """设置AI大脑的回调函数 - 当工具执行完成时，通过此回调通知AI"""
        self.ai_callback = callback
    
    async def call_tool(self, tool_name: str, parameters: Dict) -> str:
        """
        AI大脑调用的方法 - 非阻塞
        返回任务ID，AI可以继续做其他事
        """
        # 1. 检查工具是否存在
        if tool_name not in self.tools:
            raise ValueError(f"未知工具: {tool_name}")
        
        # 2. 创建任务记录
        task_id = str(uuid.uuid4())
        tool_call = ToolCall(
            id=task_id,
            tool_name=tool_name,
            parameters=parameters,
            status=ToolStatus.PENDING,
            created_at=time.time()
        )
        
        # 3. 存储任务状态
        self.tasks[task_id] = tool_call
        
        # 4. 放入任务队列（异步执行，不阻塞AI）
        await self.task_queue.put(tool_call)
        
        # 5. 立即返回任务ID，AI继续思考
        return task_id
    
    async def get_task_status(self, task_id: str) -> ToolCall:
        """查询任务状态（AI可以随时调用）"""
        return self.tasks.get(task_id)
    
    async def _worker(self):
        """后台工作线程：持续执行任务队列中的工具调用"""
        while self.is_running:
            try:
                # 1. 从队列获取一个任务（等待直到有任务）
                tool_call = await self.task_queue.get()
                
                # 2. 更新状态为运行中
                tool_call.status = ToolStatus.RUNNING
                self.tasks[tool_call.id] = tool_call
                
                # 3. 获取工具处理器
                handler = self.tools[tool_call.tool_name]["handler"]
                
                # 4. 异步执行工具（不阻塞这个worker）
                asyncio.create_task(self._execute_tool(tool_call, handler))
                
            except Exception as e:
                print(f"工作线程错误: {e}")
                await asyncio.sleep(0.1)
    
    async def _execute_tool(self, tool_call: ToolCall, handler: Callable):
        """实际执行工具（异步）"""
        try:
            # 1. 执行工具
            result = await handler(tool_call.parameters)
            
            # 2. 更新任务状态
            tool_call.status = ToolStatus.COMPLETED
            tool_call.completed_at = time.time()
            tool_call.result = result
            self.tasks[tool_call.id] = tool_call
            
            # 3. 通过回调通知AI大脑
            if self.ai_callback:
                self.ai_callback(tool_call)
                
        except Exception as e:
            # 4. 处理失败
            tool_call.status = ToolStatus.FAILED
            tool_call.completed_at = time.time()
            tool_call.error = str(e)
            self.tasks[tool_call.id] = tool_call
            
            if self.ai_callback:
                self.ai_callback(tool_call)
    
    def start(self):
        """启动路由器"""
        self.is_running = True
        asyncio.create_task(self._worker())
        print("🚀 工具调用路由器已启动")
    
    def stop(self):
        """停止路由器"""
        self.is_running = False
        print("🛑 工具调用路由器已停止")