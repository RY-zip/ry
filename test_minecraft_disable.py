#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Minecraft模式禁用功能
"""

import httpx
import json

async def test_minecraft_disable():
    print("测试Minecraft模式禁用功能...")
    
    try:
        # 检查当前状态
        async with httpx.AsyncClient() as client:
            # 检查当前状态
            print("1. 检查当前Minecraft模式状态...")
            response = await client.get("http://localhost:48911/api/minecraft/mode")
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.json()}")
            
            # 禁用Minecraft模式
            print("\n2. 尝试禁用Minecraft模式...")
            disable_response = await client.post(
                "http://localhost:48911/api/minecraft/toggle",
                json={"enabled": False},
                headers={"Content-Type": "application/json"}
            )
            print(f"状态码: {disable_response.status_code}")
            print(f"响应内容: {disable_response.json()}")
            
            # 再次检查状态
            print("\n3. 再次检查Minecraft模式状态...")
            final_response = await client.get("http://localhost:48911/api/minecraft/mode")
            print(f"状态码: {final_response.status_code}")
            print(f"响应内容: {final_response.json()}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_minecraft_disable())
