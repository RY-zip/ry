import logging
import os
from datetime import datetime
from .config import config

class Logger:
    def __init__(self, name='minecraft_system'):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """设置日志器"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self._get_log_level())
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self._get_log_level())
        
        # 创建文件处理器
        file_handler = self._create_file_handler()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 设置格式化器
        console_handler.setFormatter(formatter)
        if file_handler:
            file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
        if file_handler:
            logger.addHandler(file_handler)
        
        # 禁用传播
        logger.propagate = False
        
        return logger
    
    def _get_log_level(self):
        """获取日志级别"""
        log_level = config.get('system.log_level', 'info').upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(log_level, logging.INFO)
    
    def _create_file_handler(self):
        """创建文件处理器"""
        try:
            # 创建logs目录
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 创建日志文件
            log_file = os.path.join(log_dir, f"minecraft_{datetime.now().strftime('%Y%m%d')}.log")
            
            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            return file_handler
        
        except Exception as e:
            print(f"创建文件处理器失败: {e}")
            return None
    
    def debug(self, message, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
    
    def log(self, level, message, *args, **kwargs):
        """通用日志方法"""
        self.logger.log(level, message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        """异常日志"""
        self.logger.exception(message, *args, **kwargs)
    
    def is_debug(self):
        """检查是否为调试模式"""
        return config.get('system.debug_mode', False)
    
    def get_logger(self):
        """获取原始日志器"""
        return self.logger

# 创建全局日志实例
logger = Logger()

# 导出常用日志方法
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
log = logger.log
exception = logger.exception
