# -*- coding: utf-8 -*-
"""
Neuro-Sama 智能体集成模块
将 Neuro-Sama 智能体集成到 agent_server 中
"""
import logging
from typing import Dict, Any
from brain.neuro_core import NeuroSamaAgent, get_neuro_agent, start_neuro_agent, stop_neuro_agent, get_neuro_agent_status

logger = logging.getLogger(__name__)


class NeuroAgentIntegrator:
    """Neuro-Sama 智能体集成器"""
    
    def __init__(self):
        self.agent: NeuroSamaAgent = None
        self.enabled = False
        
    def initialize(self) -> bool:
        """初始化 Neuro-Sama 智能体"""
        try:
            self.agent = get_neuro_agent()
            success = start_neuro_agent()
            if success:
                self.enabled = True
                logger.info("[Neuro-Sama] ✅ 智能体已启动")
            else:
                logger.warning("[Neuro-Sama] ⚠️ 智能体启动失败")
            return success
        except Exception as e:
            logger.error(f"[Neuro-Sama] ❌ 初始化失败: {e}", exc_info=True)
            return False
    
    def shutdown(self):
        """关闭 Neuro-Sama 智能体"""
        try:
            stop_neuro_agent()
            self.enabled = False
            logger.info("[Neuro-Sama] ✅ 智能体已关闭")
        except Exception as e:
            logger.error(f"[Neuro-Sama] ❌ 关闭失败: {e}", exc_info=True)
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        try:
            status = get_neuro_agent_status()
            status["enabled"] = self.enabled
            return status
        except Exception as e:
            logger.error(f"[Neuro-Sama] ❌ 获取状态失败: {e}", exc_info=True)
            return {
                "error": str(e),
                "enabled": False
            }


# 全局集成器实例
_neuro_integrator: NeuroAgentIntegrator = None


def get_neuro_integrator() -> NeuroAgentIntegrator:
    """获取 Neuro-Sama 集成器单例"""
    global _neuro_integrator
    if _neuro_integrator is None:
        _neuro_integrator = NeuroAgentIntegrator()
    return _neuro_integrator