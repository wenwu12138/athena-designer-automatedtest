#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/11/19 09:01  
# @Author  : wenwu        
# @Desc    : 智能报告服务器，封装所有逻辑，主函数只需简单调用
# @File    : ReportServer.py
# @Software: PyCharm

import os
import socket
import webbrowser
import threading
import time
import psutil
import signal
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from enum import Enum


class ServerMode(Enum):
    """服务器运行模式"""
    AUTO = "auto"  # 自动判断
    FOREGROUND = "fg"  # 前台阻塞模式
    BACKGROUND = "bg"  # 后台非阻塞模式
    INFO_ONLY = "info"  # 只显示信息，不启动服务


class ReportServer:
    def __init__(self, report_path, port=9999, host='0.0.0.0', mode=ServerMode.AUTO):
        """
        初始化报告服务器 - 所有逻辑封装在此类中

        Args:
            report_path: 报告目录路径
            port: 端口号，默认9999
            host: 绑定地址，默认'0.0.0.0'
            mode: 运行模式，默认自动判断
        """
        self.report_path = report_path
        self.port = port
        self.host = host
        self.mode = mode if isinstance(mode, ServerMode) else ServerMode(mode)
        self.server = None
        self.server_thread = None
        self.is_running = False

        # 环境检测
        self.env_info = self._detect_environment()
        print(f"📋 环境检测: {self.env_info['type']} - {self.env_info['description']}")

    @staticmethod
    def get_local_ip():
        """
        获取本机IP地址（兼容旧版本）
        注意：建议使用实例方法 _get_network_ips() 替代
        """
        try:
            # 方法1: 通过UDP连接获取
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            try:
                # 方法2: 通过主机名获取
                hostname = socket.gethostname()
                return socket.gethostbyname(hostname)
            except:
                return "127.0.0.1"

    def _detect_environment(self):
        """检测运行环境"""
        env_vars = os.environ

        # 检测CI/CD环境
        if env_vars.get('JENKINS_URL'):
            # Jenkins环境
            jenkins_url = env_vars.get('JENKINS_URL', '').lower()
            is_cloud = self._is_cloud_deployment(jenkins_url, env_vars)

            return {
                'type': 'jenkins_cloud' if is_cloud else 'jenkins_local',
                'description': '云端Jenkins' if is_cloud else '本地Jenkins',
                'is_ci': True,
                'is_jenkins': True,
                'is_cloud': is_cloud,
                'should_serve': is_cloud  # 云端Jenkins需要服务
            }
        elif env_vars.get('GITLAB_CI'):
            return {
                'type': 'gitlab',
                'description': 'GitLab CI',
                'is_ci': True,
                'is_jenkins': False,
                'is_cloud': True,
                'should_serve': True
            }
        elif env_vars.get('GITHUB_ACTIONS'):
            return {
                'type': 'github',
                'description': 'GitHub Actions',
                'is_ci': True,
                'is_jenkins': False,
                'is_cloud': True,
                'should_serve': True
            }
        else:
            # 本地环境
            return {
                'type': 'local',
                'description': '本地开发环境',
                'is_ci': False,
                'is_jenkins': False,
                'is_cloud': False,
                'should_serve': True
            }

    def _is_cloud_deployment(self, jenkins_url, env_vars):
        """判断是否为云端部署"""
        # 云端关键词
        cloud_keywords = ['cloud', 'aliyun', 'tencent', 'aws', 'azure',
                          'k8s', 'kubernetes', 'docker', 'ec2', 'ecs']

        # 检查URL
        if any(keyword in jenkins_url for keyword in cloud_keywords):
            return True

        # 检查节点名
        node_name = env_vars.get('NODE_NAME', '').lower()
        if node_name and node_name not in ['built-in', 'master', 'main']:
            return True

        # 默认：非本地部署都认为是云端
        return 'localhost' not in jenkins_url and '127.0.0.1' not in jenkins_url

    def _should_start_server(self):
        """判断是否应该启动服务器"""
        # 如果指定了模式，按模式执行
        if self.mode == ServerMode.FOREGROUND:
            return True, "前台模式强制启动"
        elif self.mode == ServerMode.BACKGROUND:
            return True, "后台模式启动"
        elif self.mode == ServerMode.INFO_ONLY:
            return False, "信息模式，不启动服务"

        # AUTO模式：根据环境判断
        if not os.path.exists(self.report_path):
            return False, f"报告目录不存在: {self.report_path}"

        if self.env_info['should_serve']:
            return True, f"{self.env_info['description']}需要报告服务"
        else:
            return False, f"{self.env_info['description']}建议使用CI工具查看报告"

    def _check_port(self):
        """检查端口占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((self.host, self.port)) == 0

    def _kill_port_process(self):
        """清理占用端口的进程"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn.laddr, 'port') and conn.laddr.port == self.port:
                            print(f"🔪 清理占用端口 {self.port} 的进程: {proc.info['name']} (PID: {proc.info['pid']})")
                            os.kill(proc.info['pid'], signal.SIGTERM)
                            time.sleep(2)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"⚠️  清理端口时出错: {e}")

    def _get_network_ips(self):
        """获取所有网络IP地址"""
        ips = []
        try:
            # 获取主机名
            hostname = socket.gethostname()

            # 获取所有IP地址
            all_ips = set()

            # 方法1: socket.getaddrinfo
            try:
                addr_info = socket.getaddrinfo(hostname, None)
                for info in addr_info:
                    ip = info[4][0]
                    if ip != '127.0.0.1':
                        all_ips.add(ip)
            except:
                pass

            # 方法2: 通过UDP连接获取本地IP
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    if local_ip != '127.0.0.1':
                        all_ips.add(local_ip)
            except:
                pass

            # 排序：公网IP优先
            for ip in sorted(all_ips, key=lambda x: (x.startswith('192.168.'), x.startswith('10.'), x)):
                ips.append(ip)

        except Exception as e:
            print(f"⚠️  获取网络IP时出错: {e}")

        return ips

    def _print_access_info(self, ips):
        """打印访问信息"""
        print(f"\n{'=' * 60}")
        print(f"📊 测试报告访问信息")
        print(f"{'=' * 60}")

        print(f"📍 报告目录: {self.report_path}")
        print(f"🔧 运行模式: {self.mode.value}")
        print(f"🌍 环境类型: {self.env_info['description']}")

        if self.is_running:
            print(f"\n✅ 报告服务运行中:")
            print(f"   本地访问:")
            print(f"   → http://localhost:{self.port}")
            print(f"   → http://127.0.0.1:{self.port}")

            if ips:
                print(f"\n🌐 网络访问:")
                for ip in ips:
                    print(f"   → http://{ip}:{self.port}")

            if self.env_info['is_jenkins']:
                print(f"\n🔗 Jenkins报告:")
                build_url = os.environ.get('BUILD_URL', '')
                if build_url:
                    print(f"   Allure插件: {build_url}allure")

                # 显示节点信息
                node_name = os.environ.get('NODE_NAME', '未知')
                print(f"   执行节点: {node_name}")
        else:
            print(f"\nℹ️  报告服务未启动")
            print(f"   原因: {self._should_start_server()[1]}")

            if self.env_info['is_ci']:
                print(f"\n💡 CI环境建议:")
                print(f"   1. 使用CI平台的Allure插件")
                print(f"   2. 下载报告文件到本地查看")
                print(f"   3. 如需远程访问，请设置 mode='background'")

        print(f"{'=' * 60}\n")

    def _run_server(self):
        """运行HTTP服务器（内部方法）"""
        try:
            # 切换到报告目录
            original_dir = os.getcwd()
            os.chdir(self.report_path)

            # 启动HTTP服务器
            self.server = HTTPServer((self.host, self.port), SimpleHTTPRequestHandler)
            print(f"🚀 报告服务器启动成功!")
            print(f"   📍 绑定地址: {self.host}")
            print(f"   🔌 端口: {self.port}")
            print(f"   📂 服务目录: {self.report_path}")

            # 标记为运行中
            self.is_running = True

            # 运行服务器
            self.server.serve_forever()

            # 恢复原始目录
            os.chdir(original_dir)

        except Exception as e:
            print(f"❌ 服务器运行出错: {e}")
            self.is_running = False
            # 恢复原始目录
            try:
                os.chdir(original_dir)
            except:
                pass

    def _start_in_background(self):
        """在后台启动服务器"""
        print("🔄 在后台启动报告服务...")

        # 创建并启动线程
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True  # 设置为守护线程
        self.server_thread.start()

        # 等待服务器启动
        for i in range(10):
            if self.is_running:
                break
            time.sleep(0.5)

        if self.is_running:
            print("✅ 报告服务已在后台启动")
        else:
            print("⚠️  报告服务启动可能失败")

    def _start_in_foreground(self):
        """在前台启动服务器（阻塞）"""
        print("🔄 在前台启动报告服务...")
        print("💡 按 Ctrl+C 停止服务器\n")

        try:
            self._run_server()
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，关闭服务器...")
            self.stop()
        except Exception as e:
            print(f"❌ 服务器异常: {e}")
            self.stop()

    def start(self):
        """
        智能启动报告服务器

        根据环境和模式自动决策：
        1. 判断是否需要启动
        2. 清理端口占用
        3. 按模式启动服务
        4. 打印访问信息
        5. 自动打开浏览器（本地环境）

        Returns:
            bool: 是否成功启动
        """
        # 1. 判断是否需要启动
        should_start, reason = self._should_start_server()
        if not should_start:
            print(f"ℹ️  {reason}")
            self._print_access_info([])
            return False

        # 2. 检查并清理端口
        if self._check_port():
            print(f"⚠️  端口 {self.port} 被占用，尝试清理...")
            self._kill_port_process()
            time.sleep(2)

            if self._check_port():
                print(f"❌ 端口 {self.port} 仍然被占用，请手动处理")
                return False

        # 3. 获取网络IP（用于信息显示）
        network_ips = self._get_network_ips()

        # 4. 根据模式启动
        if self.mode == ServerMode.BACKGROUND or (self.mode == ServerMode.AUTO and self.env_info['is_ci']):
            # CI环境或后台模式：非阻塞启动
            self._start_in_background()

            # CI环境不需要自动打开浏览器
            if not self.env_info['is_ci'] and not self.env_info['is_jenkins']:
                try:
                    webbrowser.open(f'http://localhost:{self.port}')
                except:
                    pass

        else:
            # 前台模式：阻塞启动
            self._start_in_foreground()

            # 本地环境自动打开浏览器
            if not self.env_info['is_ci']:
                try:
                    webbrowser.open(f'http://localhost:{self.port}')
                except:
                    pass

        # 5. 打印访问信息
        self._print_access_info(network_ips)

        return self.is_running

    def stop(self):
        """停止报告服务器"""
        if self.server:
            print("🛑 正在停止报告服务器...")
            self.server.shutdown()
            self.is_running = False
            print("✅ 报告服务器已停止")
        else:
            print("ℹ️  报告服务器未运行")

    def serve_only(self):
        """只启动服务（简化调用）"""
        self.mode = ServerMode.BACKGROUND
        return self.start()

    def info_only(self):
        """只显示信息（简化调用）"""
        self.mode = ServerMode.INFO_ONLY
        network_ips = self._get_network_ips()
        self._print_access_info(network_ips)
        return True


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='智能测试报告服务器')
    parser.add_argument('--path', '-p', type=str,
                        default="./report/html",
                        help='报告目录路径')
    parser.add_argument('--port', '-P', type=int,
                        default=9999,
                        help='服务器端口')
    parser.add_argument('--host', '-H', type=str,
                        default='0.0.0.0',
                        help='绑定地址')
    parser.add_argument('--mode', '-m', type=str,
                        choices=['auto', 'fg', 'bg', 'info'],
                        default='auto',
                        help='运行模式: auto(自动), fg(前台), bg(后台), info(仅信息)')

    args = parser.parse_args()

    # 创建并启动服务器
    server = ReportServer(
        report_path=args.path,
        port=args.port,
        host=args.host,
        mode=ServerMode(args.mode)
    )

    server.start()