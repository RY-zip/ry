#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试鼠标控制功能的脚本
直接使用pyautogui来模拟AI控制鼠标的过程
"""
import time
import pyautogui
import os

# 设置pyautogui的参数
pyautogui.PAUSE = 0.5  # 减少每个操作之间的暂停时间，使操作更流畅
pyautogui.FAILSAFE = True  # 启用安全模式，移动鼠标到左上角可以中断操作

print("=" * 60)
print("测试鼠标控制功能")
print("=" * 60)
print("将模拟AI控制鼠标打开浏览器并搜索B站的过程")
print("你将看到鼠标的移动和点击过程")
print("如果需要中断操作，请将鼠标移动到屏幕左上角")
print("=" * 60)
print("3秒后开始...")
time.sleep(3)

try:
    # 1. 使用Win+R打开运行对话框
    print("步骤1: 使用Win+R打开运行对话框")
    pyautogui.hotkey('win', 'r')  # 按下Win+R快捷键
    time.sleep(1)
    
    # 2. 输入浏览器命令（这里使用Edge，Windows 10/11的默认浏览器）
    print("步骤2: 输入浏览器命令")
    pyautogui.typewrite("msedge")  # 输入Edge浏览器的命令
    time.sleep(0.5)
    
    # 3. 按回车键启动浏览器
    print("步骤3: 按回车键启动浏览器")
    pyautogui.press("enter")
    time.sleep(3)  # 等待浏览器打开
    
    # 4. 点击地址栏
    print("步骤4: 点击地址栏")
    pyautogui.moveTo(400, 100, duration=0.6)  # 减少移动时间，使移动更平滑
    pyautogui.click()
    time.sleep(0.5)  # 减少等待时间
    
    # 5. 输入B站网址
    print("步骤5: 输入B站网址")
    pyautogui.typewrite("bilibili.com")
    time.sleep(0.5)  # 减少等待时间
    
    # 6. 按回车键访问
    print("步骤6: 按回车键访问B站")
    pyautogui.press("enter")
    time.sleep(3)  # 等待页面加载
    
    # 7. 点击搜索栏
    print("步骤7: 点击搜索栏")
    pyautogui.moveTo(600, 150, duration=0.6)  # 减少移动时间，使移动更平滑
    pyautogui.click()
    time.sleep(0.5)  # 减少等待时间
    
    # 8. 输入"B站"
    print("步骤8: 输入\"B站\"")
    pyautogui.typewrite("B站")
    time.sleep(0.5)  # 减少等待时间
    
    # 9. 点击搜索按钮
    print("步骤9: 点击搜索按钮")
    pyautogui.moveTo(1000, 150, duration=0.6)  # 减少移动时间，使移动更平滑
    pyautogui.click()
    time.sleep(3)  # 等待搜索结果加载
    
    # 10. 搜索nero
    print("步骤10: 搜索nero")
    pyautogui.moveTo(600, 150, duration=0.6)  # 移动到搜索栏位置
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.typewrite("nero")  # 输入"nero"
    time.sleep(0.5)
    pyautogui.moveTo(1000, 150, duration=0.6)  # 移动到搜索按钮位置
    pyautogui.click()
    time.sleep(3)  # 等待搜索结果加载
    
    print("=" * 60)
    print("测试完成！")
    print("你应该已经看到了鼠标的移动和点击过程，并且成功打开了B站并搜索了\"B站\"和\"nero\"")
    print("=" * 60)
    
except Exception as e:
    print(f"错误: {e}")
    print("测试过程中出现错误，请检查是否有其他窗口干扰")
finally:
    print("测试脚本执行完毕")
