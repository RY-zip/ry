import os

# 原文件路径
old_path = r"c:\Users\admin\Desktop\新建文本文档 (2).py"
# 新文件路径
new_path = r"c:\Users\admin\Desktop\neuro_core.py"

print(f"重命名文件: {old_path} -> {new_path}")

try:
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print("文件重命名成功!")
    else:
        print("原文件不存在!")
except Exception as e:
    print(f"重命名失败: {e}")
