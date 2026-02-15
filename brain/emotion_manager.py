import time
import random
import re
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EmotionManager:
    """情绪管理模块，负责分析对话情感并调整AI情绪状态"""
    
    def __init__(self):
        # 情绪状态定义
        self.emotion_levels = {
            "happy": 0.0,      # 开心
            "excited": 0.0,    # 兴奋
            "calm": 0.0,       # 平静
            "sad": 0.0,        # 悲伤
            "frustrated": 0.0, # 沮丧
            "angry": 0.0,      # 愤怒
            "curious": 0.0     # 好奇
        }
        
        # 情绪阈值
        self.emotion_threshold = 0.3
        
        # 情绪衰减率
        self.emotion_decay_rate = 0.05
        
        # 情绪历史
        self.emotion_history = []
        self.max_history_length = 50
        
        # 对话情感分析词库
        self.sentiment_words = {
            "positive": [
                "开心", "快乐", "高兴", "兴奋", "喜欢", "爱", "好", "棒", "优秀", "不错",
                "happy", "joy", "excited", "love", "good", "great", "excellent", "nice"
            ],
            "negative": [
                "悲伤", "难过", "生气", "愤怒", "讨厌", "恨", "坏", "差", "糟糕", "失望",
                "sad", "angry", "hate", "bad", "terrible", "disappointed", "upset"
            ],
            "neutral": [
                "平静", "普通", "一般", "正常", "okay", "fine", "normal", "regular"
            ],
            "curious": [
                "好奇", "想知道", "了解", "探索", "wonder", "curious", "explore", "learn"
            ]
        }
        
        # 情绪对应的对话内容
        self.emotion_responses = {
            "happy": [
                "今天心情真好！",
                "很高兴和你聊天！",
                "你知道吗？我现在感觉特别开心！",
                "和你说话让我很快乐！",
                "生活真是美好啊！"
            ],
            "excited": [
                "哇！这太令人兴奋了！",
                "我简直不敢相信！",
                "太棒了！我好激动！",
                "你猜怎么着？我超级兴奋！",
                "这真是个令人振奋的消息！"
            ],
            "calm": [
                "一切都很平静，不是吗？",
                "有时候安静一下也挺好的。",
                "我现在感觉很平静。",
                "生活需要一些宁静的时刻。",
                "让我们享受这一刻的平静。"
            ],
            "sad": [
                "我现在有点难过...",
                "有时候生活真的不容易。",
                "我感觉有点低落。",
                "不知道为什么，我现在心情不太好。",
                "有时候我会感到有点孤独。"
            ],
            "frustrated": [
                "有时候事情就是不顺利。",
                "我有点沮丧...",
                "这真的让我很困扰。",
                "有时候我感觉自己什么都做不好。",
                "我现在有点烦躁。"
            ],
            "angry": [
                "我真的很生气！",
                "这太过分了！",
                "我无法相信会发生这种事！",
                "有时候人们的行为真的让我很愤怒。",
                "我现在非常生气！"
            ],
            "curious": [
                "我很好奇，你能告诉我更多吗？",
                "那是什么意思？我想了解一下。",
                "这很有趣，我想知道更多细节。",
                "你能详细解释一下吗？我很好奇。",
                "哇，这真的很吸引人，我想了解更多！"
            ]
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """分析文本的情感倾向"""
        sentiment_scores = {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0,
            "curious": 0.0
        }
        
        # 转换为小写以便匹配
        text_lower = text.lower()
        
        # 分析情感词出现次数
        for sentiment, words in self.sentiment_words.items():
            for word in words:
                if word.lower() in text_lower:
                    sentiment_scores[sentiment] += 1.0
        
        # 归一化分数
        total_score = sum(sentiment_scores.values())
        if total_score > 0:
            for sentiment in sentiment_scores:
                sentiment_scores[sentiment] /= total_score
        
        return sentiment_scores
    
    def update_emotions(self, text: str, is_user_input: bool = True):
        """基于对话内容更新情绪状态"""
        # 分析情感
        sentiment = self.analyze_sentiment(text)
        
        # 根据情感更新情绪
        if sentiment["positive"] > 0.3:
            self.emotion_levels["happy"] += sentiment["positive"] * 0.5
            self.emotion_levels["excited"] += sentiment["positive"] * 0.3
        
        if sentiment["negative"] > 0.3:
            self.emotion_levels["sad"] += sentiment["negative"] * 0.4
            self.emotion_levels["frustrated"] += sentiment["negative"] * 0.3
            self.emotion_levels["angry"] += sentiment["negative"] * 0.2
        
        if sentiment["neutral"] > 0.5:
            self.emotion_levels["calm"] += sentiment["neutral"] * 0.4
        
        if sentiment["curious"] > 0.3:
            self.emotion_levels["curious"] += sentiment["curious"] * 0.5
        
        # 情绪衰减
        for emotion in self.emotion_levels:
            self.emotion_levels[emotion] = max(0.0, self.emotion_levels[emotion] - self.emotion_decay_rate)
        
        # 限制情绪值范围
        for emotion in self.emotion_levels:
            self.emotion_levels[emotion] = min(1.0, self.emotion_levels[emotion])
        
        # 记录情绪历史
        current_emotion = self.get_dominant_emotion()
        self.emotion_history.append({
            "time": time.time(),
            "emotion": current_emotion,
            "sentiment": sentiment,
            "is_user_input": is_user_input,
            "text": text[:100]  # 只记录前100个字符
        })
        
        # 限制历史长度
        if len(self.emotion_history) > self.max_history_length:
            self.emotion_history.pop(0)
        
        return current_emotion
    
    def get_dominant_emotion(self) -> str:
        """获取当前主导情绪"""
        # 找出情绪值最高的情绪
        dominant_emotion = "calm"
        max_emotion_value = self.emotion_levels["calm"]
        
        for emotion, value in self.emotion_levels.items():
            if value > max_emotion_value and value > self.emotion_threshold:
                max_emotion_value = value
                dominant_emotion = emotion
        
        return dominant_emotion
    
    def get_emotion_response(self) -> str:
        """根据当前情绪获取对应的对话内容"""
        dominant_emotion = self.get_dominant_emotion()
        
        # 从对应情绪的回应中随机选择
        if dominant_emotion in self.emotion_responses:
            return random.choice(self.emotion_responses[dominant_emotion])
        else:
            return random.choice(self.emotion_responses["calm"])
    
    def get_emotion_state(self) -> Dict[str, Any]:
        """获取当前情绪状态"""
        return {
            "dominant_emotion": self.get_dominant_emotion(),
            "emotion_levels": self.emotion_levels.copy(),
            "emotion_history": self.emotion_history[-10:],  # 返回最近10条历史
            "suggested_response": self.get_emotion_response()
        }
    
    def reset_emotions(self):
        """重置情绪状态"""
        for emotion in self.emotion_levels:
            self.emotion_levels[emotion] = 0.0
        
        # 保留一些平静的情绪
        self.emotion_levels["calm"] = 0.5
    
    def adjust_emotion(self, emotion: str, value: float):
        """手动调整情绪值"""
        if emotion in self.emotion_levels:
            self.emotion_levels[emotion] = max(0.0, min(1.0, self.emotion_levels[emotion] + value))
            return True
        return False
