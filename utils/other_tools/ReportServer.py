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
    def __init__(self, report_path, port=9999, host='0.0.0.0', auto_serve=True):
        """
        初始化报告服务器

        Args:
            report_path: 报告目录路径
            port: 端口号，默认9999
            host: 绑定地址，默认'0.0.0.0'（所有网络接口）
            auto_serve: 是否自动判断是否需要启动服务
        """
        self.report_path = report_path
        self.port = port
        self.host = host
        self.auto_serve = auto_serve  # 修复：保存参数
        self.server = None
        self.is_jenkins = self._is_jenkins_environment()  # 修复：初始化时检查

    def _is_jenkins_environment(self):
        """检查是否为 Jenkins 环境"""
        jenkins_env_vars = ['JENKINS_URL', 'BUILD_NUMBER', 'BUILD_ID', 'BUILD_URL']
        return any(os.environ.get(var) for var in jenkins_env_vars)

    def should_serve_report(self):
        """
        判断是否应该启动报告服务
        返回: (should_serve, reason)
        """
        if not self.auto_serve:
            return False, "auto_serve 设置为 False"

        if not os.path.exists(self.report_path):
            return False, f"报告目录不存在: {self.report_path}"

        if self.is_jenkins:
            return False, "检测到 Jenkins 环境，建议使用 Allure 插件查看报告"

        return True, "本地环境，可以启动报告服务"

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

    def print_report_info(self):
        """打印报告访问信息"""
        local_ip = self.get_local_ip()
        all_ips = self.get_all_network_ips()

        print(f"\n{'=' * 60}")
        print(f"📊 测试报告信息")
        print(f"{'=' * 60}")

        if self.is_jenkins:
            print("🔧 检测到 Jenkins 环境")
            print(f"📍 报告路径: {self.report_path}")
            print(f"🌐 请通过 Jenkins Allure 插件查看报告")

            # 在 Jenkins 中，尝试生成可访问的路径
            workspace = os.environ.get('WORKSPACE', os.getcwd())
            report_relative = os.path.relpath(self.report_path, workspace)
            print(f"📁 相对工作区路径: {report_relative}")

            # 检查是否存在 index.html
            index_path = os.path.join(self.report_path, 'index.html')
            if os.path.exists(index_path):
                print(f"✅ 报告文件已生成: {index_path}")
        else:
            print("🔧 本地环境")
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

            print(f"\n🔧 详细信息:")
            print(f"   报告目录: {self.report_path}")
            print(f"   是否 Jenkins: {'是' if self.is_jenkins else '否'}")

        print(f"{'=' * 60}")

    def start_server(self):
        """启动 HTTP 服务器 - 将 start_http_server 重命名为 start_server"""
        try:
            # 切换到报告目录
            original_dir = os.getcwd()
            os.chdir(self.report_path)

            # 启动HTTP服务器
            self.server = HTTPServer((self.host, self.port), SimpleHTTPRequestHandler)

            # 在新线程中运行服务器
            def run_server():
                print(f"\n🚀 启动报告服务...")
                print(f"   绑定地址: {self.host}")
                print(f"   端口: {self.port}")
                print("   按 Ctrl+C 退出服务器\n")
                self.server.serve_forever()

            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()

            # 等待服务器启动
            time.sleep(2)

            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{self.port}')
            except:
                pass

            # 恢复原始目录
            os.chdir(original_dir)
            return True

        except Exception as e:
            print(f"启动 HTTP 服务器时出错: {e}")
            return False

    def start(self):
        """
        智能启动方法
        根据环境自动决定是否启动服务
        """
        should_serve, reason = self.should_serve_report()

        self.print_report_info()

        if not should_serve:
            print(f"\nℹ️  不启动报告服务: {reason}")
            return False

        # 检查端口是否被占用
        if self.is_port_in_use(self.port):
            print(f"⚠️  端口 {self.port} 被占用，尝试清理...")
            self.kill_process_by_port(self.port)
            time.sleep(2)

            # 再次检查
            if self.is_port_in_use(self.port):
                print(f"❌ 端口 {self.port} 仍然被占用，请手动关闭相关进程")
                return False

        # 启动服务
        if self.start_server():
            # 保持主线程运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n正在关闭服务器...")
                self.shutdown_server()
            return True
        return False

    def serve_only(self):
        """
        只启动报告服务（用于查看已有报告）
        忽略环境检测，强制启动服务
        """
        print("🔧 强制启动报告服务模式")
        self.auto_serve = True
        return self.start()

    def shutdown_server(self):
        """关闭服务器"""
        if self.server:
            self.server.shutdown()
            print("服务器已关闭")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='测试报告服务器')
    parser.add_argument('--path', '-p', type=str,
                        default=r"./report/html",
                        help='报告目录路径')
    parser.add_argument('--port', '-P', type=int,
                        default=9999,
                        help='服务器端口')
    parser.add_argument('--host', '-H', type=str,
                        default='0.0.0.0',
                        help='绑定地址')
    parser.add_argument('--serve-only', action='store_true',
                        help='强制启动服务，忽略环境检测')
    parser.add_argument('--no-auto', action='store_true',
                        help='禁用自动判断，手动控制')

    args = parser.parse_args()

    # 创建服务器实例
    server = ReportServer(
        report_path=args.path,
        port=args.port,
        host=args.host,
        auto_serve=not args.no_auto
    )

    if args.serve_only:
        # 强制启动服务模式
        server.serve_only()
    else:
        # 智能启动模式
        server.start()