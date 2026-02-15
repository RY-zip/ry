import os
import json
import shutil
from datetime import datetime

class FileOperations:
    def __init__(self):
        self.base_dir = os.getcwd()
    
    def write_file(self, file_path, content, encoding='utf-8'):
        """写入文件"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"写入文件失败: {e}")
            return False
    
    def read_file(self, file_path, encoding='utf-8'):
        """读取文件"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None
    
    def append_file(self, file_path, content, encoding='utf-8'):
        """追加文件"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 追加文件
            with open(file_path, 'a', encoding=encoding) as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"追加文件失败: {e}")
            return False
    
    def write_json(self, file_path, data, indent=2, encoding='utf-8'):
        """写入JSON文件"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # 写入JSON
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"写入JSON文件失败: {e}")
            return False
    
    def read_json(self, file_path, encoding='utf-8'):
        """读取JSON文件"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
            return None
    
    def copy_file(self, src_path, dest_path):
        """复制文件"""
        try:
            # 确保目标目录存在
            dest_directory = os.path.dirname(dest_path)
            if dest_directory and not os.path.exists(dest_directory):
                os.makedirs(dest_directory, exist_ok=True)
            
            # 复制文件
            shutil.copy2(src_path, dest_path)
            
            return True
        except Exception as e:
            print(f"复制文件失败: {e}")
            return False
    
    def move_file(self, src_path, dest_path):
        """移动文件"""
        try:
            # 确保目标目录存在
            dest_directory = os.path.dirname(dest_path)
            if dest_directory and not os.path.exists(dest_directory):
                os.makedirs(dest_directory, exist_ok=True)
            
            # 移动文件
            shutil.move(src_path, dest_path)
            
            return True
        except Exception as e:
            print(f"移动文件失败: {e}")
            return False
    
    def delete_file(self, file_path):
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def exists(self, path):
        """检查文件或目录是否存在"""
        return os.path.exists(path)
    
    def get_file_size(self, file_path):
        """获取文件大小"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path)
            return 0
        except Exception as e:
            print(f"获取文件大小失败: {e}")
            return 0
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'mode': stat.st_mode
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    def list_files(self, directory, pattern=None):
        """列出目录中的文件"""
        try:
            files = []
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if pattern:
                        if pattern in filename:
                            files.append(os.path.join(root, filename))
                    else:
                        files.append(os.path.join(root, filename))
            return files
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []

# 创建全局文件操作实例
file_ops = FileOperations()
