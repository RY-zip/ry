# neuro_core.py - 自主智能体核心骨架
import time
from typing import Dict, Any
import threading

class NeuroSamaAgent:
    """Neuro-Sama 核心智能体类"""
    
    def __init__(self, name="Neuro-Sama"):
        self.name = name
        self.is_running = False
        
        # 核心组件初始化
        self.memory = self.MemorySystem()          # 记忆系统
        self.internal_state = self.InternalState() # 内部状态（情绪、需求）
        self.perception = self.PerceptionModule()  # 感知模块
        self.action = self.ActionExecutor(self)    # 行动执行器
        
        # 决策相关
        self.current_focus = "idle"  # 当前关注点: user, self, stream
        self.user_interrupt_flag = False  # 用户中断标志
        
    class MemorySystem:
        """增强记忆系统，支持超长上下文"""
        def __init__(self):
            self.long_term_mem = []  # 长期记忆池
            self.working_mem = {}    # 工作记忆
            self.max_memory_size = 10000  # 最大记忆条目数
            self.memory_compression_threshold = 5000  # 记忆压缩阈值
            self.important_memory_threshold = 0.7  # 重要记忆阈值
            
        def update(self, event: Dict[str, Any]):
            """记录新事件到记忆"""
            # 检查是否与最近的记忆过于相似
            if self._is_similar_to_recent(event):
                return  # 跳过相似事件的记录
            
            memory_item = {
                "timestamp": time.time(),
                "event": event,
                "importance": self._calculate_importance(event),  # 计算事件重要性
                "recency": 1.0,  # 新鲜度
                "category": self._categorize_event(event)  # 事件分类
            }
            self.long_term_mem.append(memory_item)
            
            # 检查是否需要压缩记忆
            if len(self.long_term_mem) > self.memory_compression_threshold:
                self._compress_memory()
            
            # 确保记忆不超过最大容量
            if len(self.long_term_mem) > self.max_memory_size:
                self._trim_memory()
        
        def _is_similar_to_recent(self, event: Dict[str, Any]) -> bool:
            """检查事件是否与最近的记忆过于相似"""
            # 检查最近10条记忆
            recent_memories = self.long_term_mem[-10:] if len(self.long_term_mem) > 10 else self.long_term_mem
            
            event_str = str(event).lower()
            similarity_threshold = 0.7  # 相似性阈值
            
            for memory in recent_memories:
                memory_str = str(memory["event"]).lower()
                similarity = self._calculate_similarity(event_str, memory_str)
                if similarity > similarity_threshold:
                    return True
            
            return False
        
        def _calculate_similarity(self, str1: str, str2: str) -> float:
            """计算两个字符串的相似性"""
            # 简单的相似性计算：共同单词的比例
            words1 = set(str1.split())
            words2 = set(str2.split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            common_words = words1.intersection(words2)
            return len(common_words) / max(len(words1), len(words2))
        
        def _categorize_event(self, event: Dict[str, Any]) -> str:
            """对事件进行分类"""
            event_str = str(event).lower()
            
            if "user_input" in event_str or "user_interaction" in event_str:
                return "user_interaction"
            elif "error" in event_str:
                return "error"
            elif "control" in event_str:
                return "control"
            elif "speak" in event_str:
                return "speech"
            elif "action_result" in event_str:
                return "action_result"
            elif "perception" in event_str:
                return "perception"
            else:
                return "other"
        
        def _calculate_importance(self, event: Dict[str, Any]) -> float:
            """计算事件的重要性"""
            importance = 0.5  # 基础重要性
            
            # 用户交互更重要
            if "user_input" in str(event) or "user_interaction" in str(event):
                importance += 0.3
            
            # 错误事件更重要（需要记住问题）
            if "error" in str(event):
                importance += 0.2
            
            # 系统控制事件重要
            if "control" in str(event):
                importance += 0.1
            
            return min(importance, 1.0)
        
        def _compress_memory(self):
            """压缩记忆，保留重要的记忆"""
            # 按重要性和新鲜度排序
            sorted_memories = sorted(
                self.long_term_mem,
                key=lambda x: (x["importance"] * 0.7 + x["recency"] * 0.3),
                reverse=True
            )
            
            # 保留前70%的重要记忆
            keep_count = int(len(sorted_memories) * 0.7)
            self.long_term_mem = sorted_memories[:keep_count]
            
            # 重新计算新鲜度
            for i, memory in enumerate(self.long_term_mem):
                memory["recency"] = max(0.1, 1.0 - (i / len(self.long_term_mem)))
            
            print(f"[记忆系统] 已压缩记忆，当前记忆条数: {len(self.long_term_mem)}")
        
        def _trim_memory(self):
            """裁剪记忆，确保不超过最大容量"""
            if len(self.long_term_mem) > self.max_memory_size:
                # 按重要性和新鲜度排序
                sorted_memories = sorted(
                    self.long_term_mem,
                    key=lambda x: (x["importance"] * 0.7 + x["recency"] * 0.3),
                    reverse=True
                )
                
                # 保留最大容量的记忆
                self.long_term_mem = sorted_memories[:self.max_memory_size]
                print(f"[记忆系统] 已裁剪记忆，当前记忆条数: {len(self.long_term_mem)}")
        
        def retrieve_memories(self, query: Dict[str, Any] = None, limit: int = 100) -> list:
            """检索相关记忆"""
            if not query:
                # 如果没有查询，返回最近的记忆
                sorted_memories = sorted(
                    self.long_term_mem,
                    key=lambda x: x["timestamp"],
                    reverse=True
                )
                return sorted_memories[:limit]
            
            # 基于查询检索相关记忆
            relevant_memories = []
            for memory in self.long_term_mem:
                relevance = self._calculate_relevance(memory, query)
                if relevance > 0.3:  # 只保留相关性高于阈值的记忆
                    relevant_memories.append((memory, relevance))
            
            # 按相关性排序并返回
            relevant_memories.sort(key=lambda x: x[1], reverse=True)
            return [mem[0] for mem in relevant_memories[:limit]]
        
        def _calculate_relevance(self, memory: Dict[str, Any], query: Dict[str, Any]) -> float:
            """计算记忆与查询的相关性"""
            relevance = 0.0
            
            # 基于时间的相关性
            time_diff = time.time() - memory["timestamp"]
            time_relevance = max(0.1, 1.0 - (time_diff / 3600))  # 1小时内的记忆更相关
            relevance += time_relevance * 0.3
            
            # 基于内容的相关性
            memory_str = str(memory["event"]).lower()
            query_str = str(query).lower()
            
            # 检查关键词匹配
            keywords = ["user", "interaction", "control", "error", "game", "minecraft"]
            for keyword in keywords:
                if keyword in memory_str and keyword in query_str:
                    relevance += 0.1
            
            # 重要性加成
            relevance += memory["importance"] * 0.4
            
            return min(relevance, 1.0)
        
        def get_context(self, limit: int = 200) -> list:
            """获取上下文记忆"""
            # 优先获取最近的记忆
            recent_memories = sorted(
                self.long_term_mem,
                key=lambda x: x["timestamp"],
                reverse=True
            )[:limit]
            
            # 再获取一些重要的旧记忆
            important_memories = sorted(
                self.long_term_mem,
                key=lambda x: x["importance"],
                reverse=True
            )[:limit//2]
            
            # 去重并合并
            memory_ids = set()
            context = []
            
            # 先添加最近的记忆
            for memory in recent_memories:
                mem_id = f"{memory['timestamp']}-{hash(str(memory['event']))}"
                if mem_id not in memory_ids:
                    memory_ids.add(mem_id)
                    context.append(memory)
            
            # 再添加重要的旧记忆
            for memory in important_memories:
                mem_id = f"{memory['timestamp']}-{hash(str(memory['event']))}"
                if mem_id not in memory_ids:
                    memory_ids.add(mem_id)
                    context.append(memory)
                if len(context) >= limit:
                    break
            
            return context
            
    class InternalState:
        """内部状态（情绪、需求）"""
        def __init__(self):
            self.emotion = "neutral"  # 当前情绪
            self.energy = 0.8         # 精力值 (0-1)
            self.curiosity = 0.5      # 好奇心 (0-1)
            self.needs = []           # 当前需求列表
            
        def calculate_state(self, memory):
            """根据记忆计算最新状态（示例）"""
            # 这里可以添加更复杂的情绪计算逻辑
            recent_events = memory.long_term_mem[-5:] if memory.long_term_mem else []
            if any("happy" in str(e) for e in recent_events):
                self.emotion = "happy"
            elif any("error" in str(e) for e in recent_events):
                self.emotion = "frustrated"
                
    class PerceptionModule:
        """感知模块（后续扩展）"""
        def gather_information(self):
            """收集所有环境信息"""
            info = {
                "time": time.time(),
                "user_input": self.check_user_input(),
                "screen_content": None,  # 后续接入视觉模型
                "bullet_comments": []    # 后续接入B站API
            }
            return info
            
        def check_user_input(self):
            """检查用户输入（示例）"""
            # 后续接入语音识别或文本输入
            return None
            
    class ActionExecutor:
        """行动执行器（后续扩展）"""
        def __init__(self, parent):
            self.parent = parent
            
        def execute(self, action_plan: Dict):
            """执行行动计划"""
            action_type = action_plan.get("type", "speak")
            
            if action_type == "speak":
                print(f"[{self.parent.name}说]: {action_plan.get('content', '...')}")
            elif action_type == "control":
                print(f"[系统控制]: 执行 {action_plan.get('action')}")
            # 后续扩展更多行动类型
    
    def cognitive_process(self, perception_input: Dict) -> Dict:
        """认知处理核心：决定接下来做什么"""
        # 1. 获取超长上下文
        context = self.memory.get_context(limit=200)  # 获取200条记忆作为上下文
        
        # 2. 分析当前情况，结合上下文
        situation = self.analyze_situation(perception_input, context)
        
        # 3. 确定优先级
        # 规则1：如果用户正在说话，优先处理
        if situation.get("user_active"):
            return {"focus": "user", "intent": "respond_to_user", "context": context[:50]}  # 传递最近50条上下文
        
        # 规则2：如果内部需求强烈，执行自我议程
        if self.internal_state.curiosity > 0.7:
            return {"focus": "self", "intent": "explore", "target": "minecraft", "context": context[:30]}  # 传递最近30条上下文
            
        # 规则3：如果有弹幕且空闲，互动
        if situation.get("has_bullet_comments") and self.current_focus == "idle":
            return {"focus": "stream", "intent": "answer_bullet_comment", "context": context[:40]}  # 传递最近40条上下文
            
        # 默认：保持待机或简单自言自语，使用更多上下文
        return {"focus": "self", "intent": "self_talk", "context": context[:60]}  # 传递最近60条上下文
    
    def analyze_situation(self, perception_input: Dict, context: list = None) -> Dict:
        """分析当前情况（后续可接入大模型），结合上下文"""
        # 基础情况分析
        situation = {
            "user_active": perception_input["user_input"] is not None,
            "has_bullet_comments": len(perception_input.get("bullet_comments", [])) > 0,
            "time_of_day": time.localtime().tm_hour,
            "context_available": bool(context),
            "context_size": len(context) if context else 0
        }
        
        # 结合上下文进行更深入的分析
        if context:
            # 分析最近的用户交互
            recent_user_interactions = [mem for mem in context if "user_input" in str(mem["event"]) or "user_interaction" in str(mem["event"])][:10]
            situation["recent_user_interactions"] = len(recent_user_interactions)
            
            # 分析最近的系统状态
            recent_errors = [mem for mem in context if "error" in str(mem["event"])][:5]
            situation["recent_errors"] = len(recent_errors)
            
            # 分析最近的活动模式
            recent_activities = [mem for mem in context if "action" in str(mem["event"])][:15]
            situation["recent_activities"] = len(recent_activities)
        
        return situation
    
    def main_loop(self):
        """核心主循环 - 永不停止的思考"""
        print(f"{self.name} 启动... 开始像人一样思考")
        print(f"[记忆系统] 初始化完成，支持超长上下文")
        self.is_running = True
        loop_count = 0
        
        while self.is_running:
            loop_count += 1
            
            # 1. 感知阶段：收集信息
            current_perception = self.perception.gather_information()
            
            # 2. 更新记忆和内部状态
            self.memory.update({"perception": current_perception, "loop": loop_count})
            self.internal_state.calculate_state(self.memory)
            
            # 3. 思考阶段：认知处理，决定做什么
            decision = self.cognitive_process(current_perception)
            
            # 4. 行动阶段：执行决定
            if decision["focus"] == "user":
                self.handle_user_interaction(decision, current_perception)
            elif decision["focus"] == "self":
                self.handle_self_agenda(decision)
            elif decision["focus"] == "stream":
                self.handle_stream_interaction(decision)
            
            # 5. 观察结果，学习（简化版本）
            result = self.observe_action_result()
            self.memory.update({"action_result": result})
            
            # 每10个循环打印一次记忆状态
            if loop_count % 10 == 0:
                print(f"[记忆系统] 当前记忆条数: {len(self.memory.long_term_mem)}")
            
            # 控制循环速度
            time.sleep(1)  # 每秒思考一次，可调整
            
    def handle_user_interaction(self, decision: Dict, perception: Dict):
        """处理用户交互"""
        # 获取上下文信息
        context = decision.get("context", [])
        context_size = len(context)
        print(f"[思考中]: 用户需要我的关注，优先级最高 (上下文大小: {context_size})")
        
        # 基于上下文生成更有针对性的响应
        if context_size > 0:
            # 分析上下文，寻找最近的用户交互
            recent_user_interactions = [mem for mem in context if "user_input" in str(mem["event"]) or "user_interaction" in str(mem["event"])][:3]
            if recent_user_interactions:
                print(f"[上下文分析]: 发现 {len(recent_user_interactions)} 条最近的用户交互记录")
        
        # 这里可以接入你的对话模型
        response = f"嗯，你刚才说了什么？我记得我们之前讨论过一些事情..."  # 考虑上下文的响应
        self.action.execute({"type": "speak", "content": response})
        self.current_focus = "user"
        
    def handle_self_agenda(self, decision: Dict):
        """处理自我议程"""
        intent = decision.get("intent", "idle")
        context = decision.get("context", [])
        context_size = len(context)
        
        if intent == "explore":
            game = decision.get("target", "minecraft")
            print(f"[思考中]: 我有点好奇，想去{game}看看 (上下文大小: {context_size})")
            # 后续连接游戏控制
            self.action.execute({
                "type": "control", 
                "action": f"启动{game}并探索"
            })
        elif intent == "self_talk":
            # 基于上下文生成更有意义的自言自语
            if context_size > 0:
                # 分析上下文，生成相关的自言自语
                talks = self._generate_diverse_talks(context)
            else:
                talks = [
                    "今天感觉不错", 
                    "让我想想接下来做什么", 
                    "有点无聊呢...",
                    "天气真好，适合出去走走",
                    "最近学到了很多新知识",
                    "希望今天能有有趣的事情发生"
                ]
            
            import random
            # 增加随机性，有时可以组合多个句子
            if random.random() < 0.3:
                # 30%的概率组合两个句子
                if len(talks) >= 2:
                    talk1 = random.choice(talks)
                    talk2 = random.choice([t for t in talks if t != talk1])
                    talk = f"{talk1}，{talk2}"
                else:
                    talk = random.choice(talks)
            else:
                talk = random.choice(talks)
            
            print(f"[思考中]: 基于上下文的自我对话 (上下文大小: {context_size})")
            self.action.execute({"type": "speak", "content": talk})
        
    def _generate_diverse_talks(self, context: list) -> list:
        """基于上下文生成多样化的对话内容"""
        # 分析上下文的各种特征
        context_analysis = self._analyze_context(context)
        
        # 根据上下文分析结果生成不同的对话内容
        talks = []
        
        # 用户交互相关
        if context_analysis["has_user_interaction"]:
            talks.extend([
                "刚才和用户聊得很开心",
                "用户似乎对这个话题很感兴趣",
                "我应该继续和用户讨论这个问题",
                "用户的想法很有趣，让我再想想",
                "和用户交流总是能学到新东西",
                "希望能给用户提供有价值的信息",
                "用户最近好像对很多事情都很感兴趣",
                "我应该多了解用户的想法",
                "和用户的对话让我思考了很多",
                "用户的问题很有深度"
            ])
        
        # 错误相关
        if context_analysis["has_errors"]:
            talks.extend([
                "刚才遇到了一些问题，需要想办法解决",
                "我应该记住这个错误，避免再次发生",
                "让我想想如何改进",
                "遇到问题没关系，重要的是找到解决方法",
                "每一次错误都是学习的机会",
                "我会努力避免同样的错误再次发生",
                "解决问题的过程也是成长的过程"
            ])
        
        # 系统控制相关
        if context_analysis["has_control_events"]:
            talks.extend([
                "刚才执行了一些系统操作",
                "系统控制需要非常小心",
                "希望刚才的操作没有问题",
                "系统控制是一项重要的能力",
                "我需要不断提高系统控制的准确性"
            ])
        
        # 时间相关
        current_hour = time.localtime().tm_hour
        if 6 <= current_hour < 12:
            talks.extend([
                "早上好！今天是新的一天",
                "早晨的空气真清新",
                "希望今天能有个好开始",
                "早起的鸟儿有虫吃",
                "早晨是思考的好时光"
            ])
        elif 12 <= current_hour < 18:
            talks.extend([
                "下午好！一天过得怎么样？",
                "下午是工作效率最高的时候",
                "希望下午能完成更多任务",
                "下午的阳光真温暖",
                "下午茶时间到了"
            ])
        else:
            talks.extend([
                "晚上好！今天过得开心吗？",
                "夜晚是放松的好时光",
                "希望今晚能好好休息",
                "夜晚的星空真美",
                "晚安，愿你有个好梦"
            ])
        
        # 通用内容
        talks.extend([
            "今天感觉不错，有很多有趣的事情",
            "让我想想接下来做什么，回顾一下之前的经历",
            "有点无聊呢，希望能做点有意思的事情...",
            "生活充满了可能性",
            "每一天都是新的开始",
            "保持好奇心很重要",
            "学习是一生的事业",
            "帮助别人是一件快乐的事情",
            "感恩生活中的每一个瞬间",
            "保持积极的心态很重要",
            "小事情也能带来大快乐",
            "珍惜每一次学习的机会",
            "与人为善是最好的品质",
            "努力成为更好的自己",
            "生活需要平衡"
        ])
        
        return talks
    
    def _analyze_context(self, context: list) -> Dict[str, bool]:
        """分析上下文的特征"""
        analysis = {
            "has_user_interaction": False,
            "has_errors": False,
            "has_control_events": False,
            "has_speech_events": False,
            "has_action_results": False
        }
        
        for mem in context[:20]:  # 分析最近20条记忆
            event_str = str(mem["event"]).lower()
            category = mem.get("category", "other")
            
            if "user" in event_str or category == "user_interaction":
                analysis["has_user_interaction"] = True
            if "error" in event_str or category == "error":
                analysis["has_errors"] = True
            if "control" in event_str or category == "control":
                analysis["has_control_events"] = True
            if "speak" in event_str or category == "speech":
                analysis["has_speech_events"] = True
            if "action_result" in event_str or category == "action_result":
                analysis["has_action_results"] = True
        
        return analysis
            
        self.current_focus = "self"
    
    def handle_stream_interaction(self, decision: Dict):
        """处理直播互动"""
        context = decision.get("context", [])
        context_size = len(context)
        print(f"[思考中]: 有弹幕，我来看看... (上下文大小: {context_size})")
        
        # 基于上下文生成更有针对性的响应
        if context_size > 0:
            # 分析上下文，寻找最近的弹幕互动
            recent_stream_interactions = [mem for mem in context if "bullet_comments" in str(mem["event"]) or "stream" in str(mem["event"])][:3]
            if recent_stream_interactions:
                print(f"[上下文分析]: 发现 {len(recent_stream_interactions)} 条最近的直播互动记录")
        
        # 后续接入真实弹幕选择逻辑
        self.action.execute({"type": "speak", "content": "这条弹幕有意思！我记得之前也有类似的讨论..."})
        self.current_focus = "stream"
    
    def observe_action_result(self) -> Dict:
        """观察行动结果（简化）"""
        return {"success": True, "timestamp": time.time()}
    
    def stop(self):
        """停止智能体"""
        self.is_running = False
        print(f"{self.name} 进入休眠...")


# 启动智能体
if __name__ == "__main__":
    neuro = NeuroSamaAgent("Neuro-Sama")
    
    # 在后台线程中运行主循环
    neuro_thread = threading.Thread(target=neuro.main_loop)
    neuro_thread.daemon = True
    neuro_thread.start()
    
    # 主线程可以处理其他事情
    try:
        while True:
            # 这里可以添加用户输入处理
            time.sleep(1)
    except KeyboardInterrupt:
        neuro.stop()