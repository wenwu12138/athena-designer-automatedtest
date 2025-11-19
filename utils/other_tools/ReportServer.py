#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/11/19 09:01  
# @Author  : wenwu        
# @Desc    : 修复服务器绑定问题，支持通过IP地址访问
# @File    : ReportServer.py
# @Software: PyCharm

import os
import socket
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time
import psutil
import signal


class ReportServer:
    def __init__(self, report_path, port=9999, host='0.0.0.0'):
        """
        初始化报告服务器

        Args:
            report_path: 报告目录路径
            port: 端口号，默认9999
            host: 绑定地址，默认'0.0.0.0'（所有网络接口）
        """
        self.report_path = report_path
        self.port = port
        self.host = host  # 新增host参数
        self.server = None

    def is_port_in_use(self, port, host='localhost'):
        """检查端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0

    def kill_process_by_port(self, port):
        """杀死占用指定端口的进程"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                            print(f"杀死占用端口 {port} 的进程: {proc.info['name']} (PID: {proc.info['pid']})")
                            os.kill(proc.info['pid'], signal.SIGTERM)
                            time.sleep(2)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"清理端口进程时出错: {e}")

    @staticmethod
    def get_local_ip():
        """获取本机局域网IP地址（更可靠的方法）"""
        try:
            # 方法1: 通过连接外部地址获取
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
                    return ip
        except:
            pass

        try:
            # 方法2: 获取主机名对应的IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip and local_ip != '127.0.0.1':
                return local_ip
        except:
            pass

        try:
            # 方法3: 遍历所有网络接口
            import netifaces
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info['addr']
                        if ip.startswith('192.168') or ip.startswith('10.') or ip.startswith('172.'):
                            if ip != '127.0.0.1':
                                return ip
        except:
            pass

        # 方法4: 最后尝试获取所有IP
        try:
            hostname = socket.gethostname()
            ip_list = socket.getaddrinfo(hostname, None)
            for ip in ip_list:
                ip_addr = ip[4][0]
                if ip_addr.startswith('192.168') or ip_addr.startswith('10.') or ip_addr.startswith('172.'):
                    return ip_addr
        except:
            pass

        return "无法获取局域网IP"

    def get_all_network_ips(self):
        """获取所有网络IP地址"""
        ips = []
        try:
            # 获取主机名
            hostname = socket.gethostname()

            # 获取所有IP地址
            ip_list = socket.getaddrinfo(hostname, None)
            for ip in ip_list:
                ip_addr = ip[4][0]
                if ip_addr != '127.0.0.1' and not ip_addr.startswith('169.254'):
                    ips.append(ip_addr)

            # 去重
            ips = list(set(ips))
        except Exception as e:
            print(f"获取网络IP时出错: {e}")

        return ips

    def start_server(self):
        """启动本地服务器"""
        # 确保报告目录存在
        if not os.path.exists(self.report_path):
            print(f"报告目录不存在: {self.report_path}")
            return False

        # 检查端口是否被占用
        if self.is_port_in_use(self.port):
            print(f"端口 {self.port} 被占用，尝试清理...")
            self.kill_process_by_port(self.port)
            time.sleep(2)

            # 再次检查
            if self.is_port_in_use(self.port):
                print(f"端口 {self.port} 仍然被占用，请手动关闭相关进程")
                return False

        try:
            # 切换到报告目录
            original_dir = os.getcwd()  # 保存原始目录
            os.chdir(self.report_path)

            # 启动HTTP服务器 - 关键修改：使用 self.host 而不是 'localhost'
            self.server = HTTPServer((self.host, self.port), SimpleHTTPRequestHandler)

            # 获取所有网络IP
            local_ip = self.get_local_ip()
            all_ips = self.get_all_network_ips()

            # 在新线程中运行服务器
            def run_server():
                print(f"\n{'=' * 60}")
                print(f"📊 测试报告服务已启动!")
                print(f"{'=' * 60}")
                print(f"📍 本地访问:")
                print(f"   http://localhost:{self.port}")
                print(f"   http://127.0.0.1:{self.port}")

                print(f"\n🌐 网络访问:")
                if local_ip != "无法获取局域网IP":
                    print(f"   http://{local_ip}:{self.port}  ← 推荐")

                # 显示所有找到的IP地址
                for ip in all_ips:
                    if ip != local_ip and ip != '127.0.0.1':
                        print(f"   http://{ip}:{self.port}")

                print(f"\n🔧 服务器信息:")
                print(f"   绑定地址: {self.host}")
                print(f"   端口: {self.port}")
                print(f"   目录: {self.report_path}")
                print(f"{'=' * 60}")
                print("按 Ctrl+C 退出服务器\n")

                self.server.serve_forever()

            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()

            # 等待服务器启动
            time.sleep(2)

            # 自动打开浏览器（使用localhost）
            webbrowser.open(f'http://localhost:{self.port}')

            # 保持主线程运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在关闭服务器...")
                self.shutdown_server()

            # 恢复原始目录
            os.chdir(original_dir)

        except Exception as e:
            print(f"启动服务器时出错: {e}")
            return False

        return True

    def shutdown_server(self):
        """关闭服务器"""
        if self.server:
            self.server.shutdown()
            print("服务器已关闭")


if __name__ == "__main__":
    # 配置报告路径和端口
    report_path = r"D:\sort\athena-designer-automatedtest\report\html"
    port = 9999

    # 关键修改：使用 '0.0.0.0' 而不是 'localhost'
    host = '0.0.0.0'  # 绑定到所有网络接口
    print("测试本地ip"+ReportServer.get_local_ip())

    # 启动服务器
    server = ReportServer(report_path, port, host)
    server.start_server()
