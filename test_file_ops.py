from minecraft.utils.file_operations import file_ops

print("=== 测试文件操作模块 ===")

# 测试文件路径
test_file = "test_file.txt"
test_json = "test_data.json"
test_dir = "test_directory"

print("\n1. 测试写入文件")
content = "Hello, Minecraft!\nThis is a test file."
success = file_ops.write_file(test_file, content)
print(f"写入文件结果: {success}")

print("\n2. 测试读取文件")
read_content = file_ops.read_file(test_file)
print(f"读取文件内容: {read_content}")

print("\n3. 测试追加文件")
append_content = "\nAppended content."
success = file_ops.append_file(test_file, append_content)
print(f"追加文件结果: {success}")

print("\n4. 测试读取追加后的文件")
read_content = file_ops.read_file(test_file)
print(f"读取追加后内容: {read_content}")

print("\n5. 测试写入JSON文件")
test_data = {
    "name": "Minecraft System",
    "version": "1.0",
    "features": ["vision", "language", "action", "multimodal"],
    "settings": {
        "debug": True,
        "language": "zh"
    }
}
success = file_ops.write_json(test_json, test_data)
print(f"写入JSON结果: {success}")

print("\n6. 测试读取JSON文件")
read_data = file_ops.read_json(test_json)
print(f"读取JSON数据: {read_data}")

print("\n7. 测试文件信息")
file_info = file_ops.get_file_info(test_file)
print(f"文件信息: {file_info}")

print("\n8. 测试文件大小")
file_size = file_ops.get_file_size(test_file)
print(f"文件大小: {file_size} bytes")

print("\n9. 测试目录操作")
# 创建测试目录
test_subdir = f"{test_dir}/subdir"
test_subfile = f"{test_subdir}/subfile.txt"

# 写入子目录文件
success = file_ops.write_file(test_subfile, "Subdirectory file content")
print(f"写入子目录文件结果: {success}")

print("\n10. 测试列出文件")
files = file_ops.list_files(test_dir)
print(f"目录中的文件: {files}")

print("\n11. 测试复制文件")
copy_file = "test_file_copy.txt"
success = file_ops.copy_file(test_file, copy_file)
print(f"复制文件结果: {success}")

print("\n12. 测试移动文件")
move_file = f"{test_dir}/moved_file.txt"
success = file_ops.move_file(copy_file, move_file)
print(f"移动文件结果: {success}")

print("\n13. 测试删除文件")
success = file_ops.delete_file(test_file)
print(f"删除文件结果: {success}")

print("\n14. 测试删除JSON文件")
success = file_ops.delete_file(test_json)
print(f"删除JSON文件结果: {success}")

print("\n15. 测试清理测试目录")
import shutil
try:
    if file_ops.exists(test_dir):
        shutil.rmtree(test_dir)
        print("测试目录清理成功")
except Exception as e:
    print(f"清理目录失败: {e}")

print("\n=== 测试完成 ===")
