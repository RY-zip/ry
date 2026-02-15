from ..utils.config import config
from ..utils.logger import logger

class MultimodalAdapter:
    def __init__(self):
        self.enabled = config.get('multimodal.enabled', False)
        self.api_key = config.get('multimodal.api_key', '')
        self.model = config.get('multimodal.model', 'gpt-4o')
        self.client = None
        
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化多模态客户端"""
        try:
            # 这里可以根据不同的AI服务提供商实现不同的客户端
            # 示例：使用OpenAI API
            if self.api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info(f"多模态客户端初始化成功，使用模型: {self.model}")
                except ImportError:
                    logger.error("OpenAI库未安装")
                except Exception as e:
                    logger.error(f"初始化多模态客户端失败: {e}")
            else:
                logger.warning("未配置API密钥，多模态功能将被禁用")
                self.enabled = False
        
        except Exception as e:
            logger.error(f"初始化多模态客户端时出错: {e}")
            self.enabled = False
    
    def process_multimodal_input(self, text=None, image=None, audio=None):
        """处理多模态输入"""
        if not self.enabled or not self.client:
            return self._process_fallback(text, image, audio)
        
        try:
            # 根据输入类型构建请求
            messages = []
            
            # 添加文本输入
            if text:
                messages.append({
                    'role': 'user',
                    'content': text
                })
            
            # 添加图像输入（如果支持）
            if image:
                # 这里需要根据具体的API要求处理图像
                # 示例：使用OpenAI的图像输入格式
                messages.append({
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': '分析这张图像'},
                        {'type': 'image_url', 'image_url': {'url': image}}
                    ]
                })
            
            # 添加音频输入（如果支持）
            if audio:
                # 这里需要根据具体的API要求处理音频
                pass
            
            # 发送请求到AI模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            
            # 处理响应
            if response.choices and len(response.choices) > 0:
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'model': self.model
                }
            
        except Exception as e:
            logger.error(f"处理多模态输入失败: {e}")
        
        # 失败时使用回退方案
        return self._process_fallback(text, image, audio)
    
    def _process_fallback(self, text=None, image=None, audio=None):
        """回退处理方案"""
        logger.info("使用回退方案处理输入")
        
        if text:
            return {
                'success': True,
                'content': f"收到文本输入: {text}",
                'model': 'fallback'
            }
        elif image:
            return {
                'success': True,
                'content': "收到图像输入",
                'model': 'fallback'
            }
        elif audio:
            return {
                'success': True,
                'content': "收到音频输入",
                'model': 'fallback'
            }
        else:
            return {
                'success': False,
                'content': "无输入提供",
                'model': 'fallback'
            }
    
    def analyze_minecraft_screen(self, screen_image):
        """分析Minecraft屏幕"""
        prompt = "分析这张Minecraft游戏截图，描述：1. 玩家所处的环境 2. 玩家周围的方块 3. 玩家可能正在进行的活动 4. 建议的下一步行动"
        
        return self.process_multimodal_input(
            text=prompt,
            image=screen_image
        )
    
    def generate_action_plan(self, goal, context=None):
        """根据目标和上下文生成行动计划"""
        prompt = f"根据以下目标和上下文，为Minecraft游戏生成详细的行动计划：\n目标：{goal}\n上下文：{context or '无'}\n\n行动计划应包括：1. 具体步骤 2. 所需资源 3. 可能的挑战 4. 最佳路径"
        
        return self.process_multimodal_input(text=prompt)
    
    def get_status(self):
        """获取多模态适配器状态"""
        return {
            'enabled': self.enabled,
            'model': self.model,
            'client_connected': self.client is not None,
            'api_key_configured': bool(self.api_key)
        }
    
    def enable(self, api_key=None):
        """启用多模态功能"""
        if api_key:
            self.api_key = api_key
            config.set('multimodal.api_key', api_key)
        
        self.enabled = True
        config.set('multimodal.enabled', True)
        self._initialize_client()
        
        return self.enabled
    
    def disable(self):
        """禁用多模态功能"""
        self.enabled = False
        config.set('multimodal.enabled', False)
        self.client = None
        
        return True
    
    def set_model(self, model):
        """设置多模态模型"""
        self.model = model
        config.set('multimodal.model', model)
        
        # 如果客户端已初始化，可能需要重新初始化
        if self.enabled and self.client:
            self._initialize_client()
        
        return True

# 创建全局多模态适配器实例
multimodal_adapter = MultimodalAdapter()
