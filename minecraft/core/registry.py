class ModuleRegistry:
    def __init__(self):
        self.modules = {}
        self.features = {}
    
    def register_module(self, module_name, module_instance):
        """注册模块"""
        self.modules[module_name] = module_instance
    
    def get_module(self, module_name):
        """获取模块实例"""
        return self.modules.get(module_name)
    
    def register_feature(self, feature_name, feature_callback):
        """注册功能"""
        self.features[feature_name] = feature_callback
    
    def get_feature(self, feature_name):
        """获取功能回调"""
        return self.features.get(feature_name)
    
    def list_modules(self):
        """列出所有注册的模块"""
        return list(self.modules.keys())
    
    def list_features(self):
        """列出所有注册的功能"""
        return list(self.features.keys())
    
    def has_module(self, module_name):
        """检查模块是否已注册"""
        return module_name in self.modules
    
    def has_feature(self, feature_name):
        """检查功能是否已注册"""
        return feature_name in self.features

# 创建全局注册表实例
registry = ModuleRegistry()
