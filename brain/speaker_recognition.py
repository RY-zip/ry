import time
import random
import numpy as np
import logging
import os
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SpeakerRecognition:
    """说话人识别模块，负责识别声音是谁发出的"""
    
    def __init__(self):
        # 说话人数据库
        self.speakers = {}
        self.speakers_file = "speakers.json"
        
        # 加载已保存的说话人数据
        self._load_speakers()
        
        # 特征提取参数
        self.feature_dim = 128
        
        # 相似度阈值
        self.similarity_threshold = 0.7
        
        # 识别历史
        self.recognition_history = []
        self.max_history_length = 100
        
        logger.info("[SpeakerRecognition] 说话人识别模块初始化完成")
    
    def _load_speakers(self):
        """加载已保存的说话人数据"""
        try:
            if os.path.exists(self.speakers_file):
                with open(self.speakers_file, 'r', encoding='utf-8') as f:
                    self.speakers = json.load(f)
                logger.info(f"[SpeakerRecognition] 加载了 {len(self.speakers)} 个说话人")
            else:
                logger.info("[SpeakerRecognition] 未找到说话人数据文件，将创建新的")
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 加载说话人数据失败: {e}")
            self.speakers = {}
    
    def _save_speakers(self):
        """保存说话人数据"""
        try:
            with open(self.speakers_file, 'w', encoding='utf-8') as f:
                json.dump(self.speakers, f, ensure_ascii=False, indent=2)
            logger.info(f"[SpeakerRecognition] 保存了 {len(self.speakers)} 个说话人")
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 保存说话人数据失败: {e}")
    
    def extract_features(self, audio_data: bytes) -> np.ndarray:
        """提取音频特征
        
        Args:
            audio_data: 音频数据
            
        Returns:
            特征向量
        """
        # 这里使用简单的特征提取方法
        # 实际应用中应该使用更复杂的特征提取算法，如MFCC、x-vector等
        # 为了演示，我们使用基于音频数据的哈希值生成特征向量
        
        # 将音频数据转换为特征向量
        # 1. 计算音频数据的哈希值
        hash_value = hash(audio_data)
        
        # 2. 使用哈希值生成特征向量，确保种子在有效范围内
        seed = abs(hash_value) % (2**32)
        np.random.seed(seed)
        features = np.random.rand(self.feature_dim)
        
        # 3. 归一化特征向量
        features = features / np.linalg.norm(features)
        
        return features
    
    def register_speaker(self, speaker_id: str, audio_data: bytes, speaker_name: str = None) -> bool:
        """注册新的说话人
        
        Args:
            speaker_id: 说话人ID
            audio_data: 音频数据
            speaker_name: 说话人名称
            
        Returns:
            是否注册成功
        """
        try:
            # 提取特征
            features = self.extract_features(audio_data)
            
            # 保存说话人信息
            self.speakers[speaker_id] = {
                "name": speaker_name or speaker_id,
                "features": features.tolist(),
                "registered_at": time.time(),
                "last_seen": time.time()
            }
            
            # 保存数据
            self._save_speakers()
            
            logger.info(f"[SpeakerRecognition] 注册了新说话人: {speaker_id} ({speaker_name})")
            return True
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 注册说话人失败: {e}")
            return False
    
    def recognize_speaker(self, audio_data: bytes) -> Dict[str, Any]:
        """识别说话人
        
        Args:
            audio_data: 音频数据
            
        Returns:
            识别结果，包含说话人ID、名称、相似度等
        """
        try:
            # 提取特征
            features = self.extract_features(audio_data)
            
            # 如果没有注册的说话人，返回未知
            if not self.speakers:
                result = {
                    "speaker_id": "unknown",
                    "name": "未知",
                    "similarity": 0.0,
                    "recognized": False
                }
                
                # 记录识别历史
                self._record_recognition(result, audio_data)
                return result
            
            # 计算与每个注册说话人的相似度
            best_speaker = None
            best_similarity = 0.0
            
            for speaker_id, speaker_info in self.speakers.items():
                speaker_features = np.array(speaker_info["features"])
                similarity = np.dot(features, speaker_features)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_speaker = speaker_id
            
            # 判断是否识别成功
            if best_speaker and best_similarity >= self.similarity_threshold:
                result = {
                    "speaker_id": best_speaker,
                    "name": self.speakers[best_speaker]["name"],
                    "similarity": float(best_similarity),
                    "recognized": True
                }
                
                # 更新说话人最后 seen 时间
                self.speakers[best_speaker]["last_seen"] = time.time()
                self._save_speakers()
            else:
                result = {
                    "speaker_id": "unknown",
                    "name": "未知",
                    "similarity": float(best_similarity),
                    "recognized": False
                }
            
            # 记录识别历史
            self._record_recognition(result, audio_data)
            
            return result
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 识别说话人失败: {e}")
            return {
                "speaker_id": "unknown",
                "name": "未知",
                "similarity": 0.0,
                "recognized": False,
                "error": str(e)
            }
    
    def _record_recognition(self, result: Dict[str, Any], audio_data: bytes):
        """记录识别历史"""
        self.recognition_history.append({
            "time": time.time(),
            "result": result,
            "audio_length": len(audio_data)
        })
        
        # 限制历史长度
        if len(self.recognition_history) > self.max_history_length:
            self.recognition_history.pop(0)
    
    def get_speakers(self) -> Dict[str, Any]:
        """获取所有注册的说话人
        
        Returns:
            说话人字典
        """
        return self.speakers
    
    def get_recognition_history(self) -> List[Dict[str, Any]]:
        """获取识别历史
        
        Returns:
            识别历史列表
        """
        return self.recognition_history[-20:]  # 返回最近20条历史
    
    def update_speaker(self, speaker_id: str, audio_data: bytes) -> bool:
        """更新说话人的特征
        
        Args:
            speaker_id: 说话人ID
            audio_data: 音频数据
            
        Returns:
            是否更新成功
        """
        if speaker_id not in self.speakers:
            logger.error(f"[SpeakerRecognition] 说话人不存在: {speaker_id}")
            return False
        
        try:
            # 提取新特征
            features = self.extract_features(audio_data)
            
            # 更新特征
            self.speakers[speaker_id]["features"] = features.tolist()
            self.speakers[speaker_id]["last_seen"] = time.time()
            
            # 保存数据
            self._save_speakers()
            
            logger.info(f"[SpeakerRecognition] 更新了说话人的特征: {speaker_id}")
            return True
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 更新说话人特征失败: {e}")
            return False
    
    def delete_speaker(self, speaker_id: str) -> bool:
        """删除说话人
        
        Args:
            speaker_id: 说话人ID
            
        Returns:
            是否删除成功
        """
        if speaker_id not in self.speakers:
            logger.error(f"[SpeakerRecognition] 说话人不存在: {speaker_id}")
            return False
        
        try:
            del self.speakers[speaker_id]
            self._save_speakers()
            logger.info(f"[SpeakerRecognition] 删除了说话人: {speaker_id}")
            return True
        except Exception as e:
            logger.error(f"[SpeakerRecognition] 删除说话人失败: {e}")
            return False
