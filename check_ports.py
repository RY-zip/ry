import socket
import time

def check_port(host, port):
    """检查指定端口是否开放"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()

def check_ports():
    """检查所有相关端口"""
    ports = [
        ("localhost", 3000, "AI 视角"),
        ("localhost", 8080, "UI 服务器"),
        ("localhost", 48912, "主服务器")
    ]
    
    print("检查端口状态...")
    for host, port, description in ports:
        try:
            is_open = check_port(host, port)
            status = "✅ 开放" if is_open else "❌ 关闭"
            print(f"{description} ({host}:{port}): {status}")
        except Exception as e:
            print(f"{description} ({host}:{port}): 检查失败: {str(e)}")

if __name__ == "__main__":
    check_ports()
