import subprocess
import time
import os
import json
from .utils.logger import logger
from .utils.config import config

class MindcraftIntegration:
    def __init__(self):
        self.mindcraft_dir = '../mindcraft-develop'
        self.process = None
        self.running = False
        self.port = 8080
        self.bot_view_port = 3000
    
    def is_mindcraft_available(self):
        """检查mindcraft-develop是否可用"""
        return os.path.exists(os.path.join(self.mindcraft_dir, 'package.json'))
    
    def start_mindcraft(self):
        """启动mindcraft-develop"""
        if not self.is_mindcraft_available():
            logger.error('mindcraft-develop目录不存在')
            return False
        
        if self.running:
            logger.warning('mindcraft-develop已经在运行')
            return True
        
        try:
            # 检查端口是否被占用
            if self._is_port_in_use(self.port):
                logger.warning(f'端口 {self.port} 已被占用，尝试停止占用进程')
                self._stop_process_on_port(self.port)
            
            # 启动mindcraft-develop
            logger.info('启动mindcraft-develop...')
            
            # 构建启动命令
            if os.name == 'nt':  # Windows
                command = 'npm start'
            else:  # Linux/macOS
                command = 'npm start'
            
            # 启动进程
            self.process = subprocess.Popen(
                command, 
                cwd=self.mindcraft_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待启动完成
            time.sleep(5)
            
            # 检查进程是否运行
            if self.process.poll() is None:
                self.running = True
                logger.info('mindcraft-develop启动成功')
                return True
            else:
                # 读取错误输出
                stderr = self.process.stderr.read()
                logger.error(f'mindcraft-develop启动失败: {stderr}')
                return False
        
        except Exception as e:
            logger.error(f'启动mindcraft-develop时出错: {e}')
            return False
    
    def stop_mindcraft(self):
        """停止mindcraft-develop"""
        if not self.running:
            logger.warning('mindcraft-develop未在运行')
            return True
        
        try:
            logger.info('停止mindcraft-develop...')
            
            if self.process:
                # 尝试优雅停止
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/PID', str(self.process.pid)], shell=True)
                else:  # Linux/macOS
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
            
            # 检查端口是否仍被占用
            if self._is_port_in_use(self.port):
                self._stop_process_on_port(self.port)
            
            self.running = False
            self.process = None
            logger.info('mindcraft-develop停止成功')
            return True
        
        except Exception as e:
            logger.error(f'停止mindcraft-develop时出错: {e}')
            return False
    
    def get_status(self):
        """获取mindcraft-develop状态"""
        status = {
            'running': self.running,
            'available': self.is_mindcraft_available(),
            'port': self.port,
            'bot_view_port': self.bot_view_port,
            'port_in_use': self._is_port_in_use(self.port)
        }
        
        if self.running and self.process:
            status['pid'] = self.process.pid
        
        return status
    
    def update_settings(self, settings):
        """更新mindcraft-develop设置"""
        settings_file = os.path.join(self.mindcraft_dir, 'settings.js')
        
        try:
            # 读取现有设置
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析设置（假设是JSON格式）
            # 注意：实际的settings.js可能是CommonJS模块格式，需要适当处理
            # 这里简化处理，假设是纯JSON格式
            current_settings = json.loads(content)
            
            # 更新设置
            current_settings.update(settings)
            
            # 写回设置
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, indent=2, ensure_ascii=False)
            
            logger.info('mindcraft-develop设置更新成功')
            return True
        
        except Exception as e:
            logger.error(f'更新mindcraft-develop设置时出错: {e}')
            return False
    
    def get_settings(self):
        """获取mindcraft-develop设置"""
        settings_file = os.path.join(self.mindcraft_dir, 'settings.js')
        
        try:
            # 读取设置文件
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析设置（假设是JSON格式）
            # 注意：实际的settings.js可能是CommonJS模块格式，需要适当处理
            # 这里简化处理，假设是纯JSON格式
            settings = json.loads(content)
            
            return settings
        
        except Exception as e:
            logger.error(f'获取mindcraft-develop设置时出错: {e}')
            return {}
    
    def _is_port_in_use(self, port):
        """检查端口是否被占用"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def _stop_process_on_port(self, port):
        """停止占用指定端口的进程"""
        try:
            if os.name == 'nt':  # Windows
                # 使用netstat命令查找占用端口的进程
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                # 解析输出，获取PID
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        logger.info(f'停止占用端口 {port} 的进程 {pid}')
                        subprocess.run(['taskkill', '/F', '/PID', pid], shell=True)
            
            else:  # Linux/macOS
                # 使用lsof命令查找占用端口的进程
                result = subprocess.run(
                    f'lsof -t -i:{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                # 解析输出，获取PID
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        logger.info(f'停止占用端口 {port} 的进程 {pid}')
                        subprocess.run(['kill', '-9', pid], shell=True)
        
        except Exception as e:
            logger.error(f'停止占用端口的进程时出错: {e}')
    
    def restart_mindcraft(self):
        """重启mindcraft-develop"""
        logger.info('重启mindcraft-develop...')
        
        # 停止
        stop_success = self.stop_mindcraft()
        if not stop_success:
            logger.error('停止mindcraft-develop失败')
            return False
        
        # 等待一秒
        time.sleep(1)
        
        # 启动
        start_success = self.start_mindcraft()
        if not start_success:
            logger.error('启动mindcraft-develop失败')
            return False
        
        logger.info('mindcraft-develop重启成功')
        return True
    
    def is_bot_view_available(self):
        """检查bot视图是否可用"""
        return self._is_port_in_use(self.bot_view_port)

# 创建全局集成实例
mindcraft_integration = MindcraftIntegration()
