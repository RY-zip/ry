import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
        
        # 返回默认配置
        return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            'client': {
                'auto_focus': True,
                'input_delay': 0.1
            },
            'controller': {
                'movement_speed': 1.0,
                'mining_duration': 2.0,
                'building_mode': False
            },
            'vision': {
                'screen_capture_interval': 0.5,
                'block_detection_enabled': True,
                'show_markers': True
            },
            'language': {
                'default_language': 'zh',
                'command_timeout': 5.0
            },
            'action': {
                'plan_optimization': True,
                'max_plan_depth': 3
            },
            'multimodal': {
                'enabled': False,
                'api_key': ''
            },
            'system': {
                'debug_mode': False,
                'log_level': 'info'
            }
        }
    
    def get(self, key, default=None):
        """获取配置值"""
        # 支持嵌套键，如 'client.auto_focus'
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """设置配置值"""
        # 支持嵌套键，如 'client.auto_focus'
        keys = key.split('.')
        config = self.config
        
        # 遍历到最后一个键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存配置
        self.save()
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def reload(self):
        """重新加载配置"""
        self.config = self._load_config()
        return self.config
    
    def get_all(self):
        """获取所有配置"""
        return self.config
    
    def update(self, updates):
        """批量更新配置"""
        for key, value in updates.items():
            self.set(key, value)
        return self.save()

# 创建全局配置实例
config = ConfigManager()
