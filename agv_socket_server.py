# coding=utf-8
import socket
import json
import threading
import sys

import time
from pymycobot.myagvplus import MyAGVPlus

# 初始化实例
agv = MyAGVPlus("/dev/myagvplus_controller", 921600, "/dev/ttyACM0", 115200)

class AGVSocketServer:
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.server = None
        self.is_running = False
        self.server_thread = None

    def start(self):
        if self.is_running: return
        self.is_running = True
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.server.settimeout(1.0)
        self.server_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.server_thread.start()
        print("[Daemon] Socket 网络服务启动成功！正在监听 9000 端口...")

    def stop(self):
        if not self.is_running: return
        self.is_running = False
        if self.server:
            self.server.close()
            self.server = None
        print("[Daemon] Socket 网络服务已关闭（仅允许本地串口/手柄控制）。")

    def _accept_loop(self):
        while self.is_running:
            try:
                conn, addr = self.server.accept()
                print(f"[Daemon] 接受来自 {addr} 的连接")
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                break

    def _handle_client(self, conn, addr):
        buffer = ""
        try:
            while self.is_running:
                data = conn.recv(1024)
                if not data: break
                buffer += data.decode('utf-8')
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip(): continue
                    
                    try:
                        req = json.loads(line)
                        func_name = req.get("func")
                        args = req.get("args", [])
                        
                        # 打印当前执行的指令（生产环境可注释以减少刷屏）
                        # print(f"[Daemon] 执行指令 -> {func_name}{tuple(args)}")
                        
                        target_func = getattr(agv, func_name)
                        result = target_func(*args)
                        
                        resp = json.dumps({"result": result}) + "\n"
                        conn.sendall(resp.encode('utf-8'))
                    except Exception as e:
                        print(f"[Daemon] 处理请求时出错: {e}")
                        error_resp = json.dumps({"error": str(e)}) + "\n"
                        conn.sendall(error_resp.encode('utf-8'))
        finally:
            print(f"[Daemon] 客户端 {addr} 断开连接")
            conn.close()

if __name__ == '__main__':
    print("="*50)
    print(" MyAGV Plus 终极系统守护进程 (Daemon)")
    print("="*50)
    print("[Daemon] 正在初始化底层控制模块...")
    
    socket_server = AGVSocketServer()
    
    print("[Daemon] 守护进程启动！开始监控硬件 Communication State...")
    print("[Daemon] 提示: 请使用 myagvplus.py 的 set_communication_state(1) 开启网络控制。")
    
    last_state = -1
    while True:
        try:
            state = agv.get_communication_state()
            
            # 如果状态发生变化，或者脚本刚启动
            if state != last_state:
                if state == 1:
                    print("\n[Daemon] 检测到通信模式切换为: 1 (Socket Mode)")
                    socket_server.start()
                elif state == 0:
                    print("\n[Daemon] 检测到通信模式切换为: 0 (Serial Mode)")
                    socket_server.stop()
                elif state == 2:
                    print("\n[Daemon] 检测到通信模式切换为: 2 (Bluetooth Mode)")
                    socket_server.stop()
                    # 预留蓝牙启动代码位置
                    
                last_state = state
                
            time.sleep(1.0) # 每秒轮询一次
            
        except KeyboardInterrupt:
            print("\n[Daemon] 收到终止信号，退出程序。")
            socket_server.stop()
            break
        except Exception as e:
            print(f"[Daemon] 监控报错: {e}")
            time.sleep(1)
            
    sys.exit(0)
