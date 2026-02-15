import subprocess
import time
import os
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class MindcraftProcessManager:
    """Mindcraft Develop 进程管理器"""
    
    def __init__(self):
        self.process = None
        self.process_path = "f:\\5\\ry\\mindcraft-develop"
        self.main_script = "main.js"
        self.is_running = False
        self.start_time = 0
    
    def start(self) -> bool:
        """启动 mindcraft-develop 进程
        
        Returns:
            bool: 启动是否成功
        """
        if self.is_running:
            logger.info("[Mindcraft] 进程已经在运行中")
            return True
        
        try:
            logger.info("[Mindcraft] 正在启动 mindcraft-develop 进程...")
            
            # 构建启动命令
            cmd = ["node", self.main_script]
            cwd = self.process_path
            
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # 启动线程读取进程输出
            def read_output():
                while self.process and self.process.poll() is None:
                    try:
                        line = self.process.stdout.readline()
                        if line:
                            print(f"[Mindcraft] {line.strip()}")
                    except:
                        break
            
            import threading
            output_thread = threading.Thread(target=read_output)
            output_thread.daemon = True
            output_thread.start()
            
            self.is_running = True
            self.start_time = time.time()
            
            logger.info(f"[Mindcraft] 进程已启动，PID: {self.process.pid}")
            return True
        
        except Exception as e:
            logger.error(f"[Mindcraft] 启动进程失败: {str(e)}")
            self.is_running = False
            self.process = None
            return False
    
    def stop(self) -> bool:
        """停止 mindcraft-develop 进程
        
        Returns:
            bool: 停止是否成功
        """
        if not self.is_running or not self.process:
            logger.info("[Mindcraft] 进程未运行")
            return True
        
        try:
            logger.info(f"[Mindcraft] 正在停止进程，PID: {self.process.pid}")
            
            # 终止进程
            self.process.terminate()
            
            # 等待进程结束
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("[Mindcraft] 进程终止超时，强制杀死")
                self.process.kill()
                self.process.wait(timeout=2)
            
            self.is_running = False
            self.process = None
            logger.info("[Mindcraft] 进程已停止")
            return True
        
        except Exception as e:
            logger.error(f"[Mindcraft] 停止进程失败: {str(e)}")
            self.is_running = False
            self.process = None
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取进程状态
        
        Returns:
            Dict[str, Any]: 进程状态
        """
        status = {
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.is_running else 0,
            "process_path": self.process_path,
            "main_script": self.main_script
        }
        
        if self.process:
            status["pid"] = self.process.pid
        
        return status
    
    def check_status(self) -> bool:
        """检查进程是否仍在运行
        
        Returns:
            bool: 进程是否在运行
        """
        if not self.is_running or not self.process:
            return False
        
        try:
            # 检查进程状态
            self.process.poll()
            if self.process.returncode is None:
                # 进程仍在运行
                return True
            else:
                # 进程已退出
                self.is_running = False
                self.process = None
                logger.warning(f"[Mindcraft] 进程已退出，返回码: {self.process.returncode}")
                return False
        
        except Exception as e:
            logger.error(f"[Mindcraft] 检查进程状态失败: {str(e)}")
            self.is_running = False
            self.process = None
            return False

# 全局进程管理器实例
_mindcraft_process_manager = None

def get_mindcraft_process_manager() -> MindcraftProcessManager:
    """获取 mindcraft 进程管理器实例
    
    Returns:
        MindcraftProcessManager: 进程管理器实例
    """
    global _mindcraft_process_manager
    if _mindcraft_process_manager is None:
        _mindcraft_process_manager = MindcraftProcessManager()
    return _mindcraft_process_manager