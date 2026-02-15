# -*- coding: utf-8 -*-
"""
Minecraft Router

This router handles Minecraft-related API endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging

from brain.neuro_agent import NeuroSamaAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/minecraft", tags=["minecraft"])

# 全局NeuroSamaAgent实例引用
neuro_agent_instance = None

def set_neuro_agent(agent: NeuroSamaAgent):
    """设置NeuroSamaAgent实例引用"""
    global neuro_agent_instance
    neuro_agent_instance = agent

def get_or_create_neuro_agent():
    """获取或创建NeuroSamaAgent实例"""
    global neuro_agent_instance
    if not neuro_agent_instance:
        neuro_agent_instance = NeuroSamaAgent("Neuro-Sama")
        neuro_agent_instance.start()
        logger.info("[Minecraft Router] 自动创建并启动NeuroSamaAgent实例")
    return neuro_agent_instance

@router.get("/mode")
async def get_minecraft_mode() -> Dict[str, Any]:
    """获取Minecraft模式状态"""
    try:
        agent = get_or_create_neuro_agent()
        status = agent.get_minecraft_mode_status()
        return {
            "success": True,
            "enabled": status.get("enabled", False),
            "last_activity_time": status.get("last_activity_time", 0),
            "cooldown": status.get("cooldown", 0),
            "process_status": status.get("process_status", {})
        }
    except Exception as e:
        logger.error(f"获取Minecraft模式状态失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "enabled": False,
            "process_status": {}
        }

@router.post("/toggle")
async def toggle_minecraft_mode(payload: Dict[str, bool]) -> Dict[str, Any]:
    """切换Minecraft模式"""
    try:
        enabled = payload.get("enabled")
        if enabled is None:
            return {
                "success": False,
                "error": "Missing enabled parameter",
                "enabled": False
            }
            
        agent = get_or_create_neuro_agent()
        new_status = agent.toggle_minecraft_mode(enabled)
        return {
            "success": True,
            "enabled": new_status
        }
    except Exception as e:
        logger.error(f"切换Minecraft模式失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "enabled": False
        }
