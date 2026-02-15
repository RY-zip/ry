import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    return result == 0

print("检查 AI 视角端口 (3000):", "开放" if check_port(3000) else "关闭")
print("检查 UI 服务器端口 (8080):", "开放" if check_port(8080) else "关闭")
print("检查主服务器端口 (48912):", "开放" if check_port(48912) else "关闭")
