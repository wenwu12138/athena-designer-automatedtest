#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 15:01
# @Author : 闻武
import os
import sys
import traceback
import pytest
from utils.other_tools.models import NotificationType
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.logging_tool.log_control import INFO
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from utils import config
from utils.other_tools.ReportServer import ReportServer
from common.setting import ensure_path_sep


def run():
    # 从配置文件中获取项目名称
    try:
        INFO.logger.info(
            """
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             (◍●ᴗ●◍)  ʚ♡ɞ  (◍●ᴗ●◍)            ┃
                                  ┃                                            ┃
                                  ┃         ╭━━━━━━━━━━━━━━━━━━━━━━━━━╮          ┃
                                  ┃         ┃                         ┃          ┃
                                  ┃         ┃     (｡•̀ᴗ-)✧ 准备就绪！    ┃          ┃
                                  ┃         ┃                         ┃          ┃
                                  ┃         ╰━━━━━━━━━━━━━━━━━━━━━━━━━╯          ┃
                                  ┃                                            ┃
                                  ┃        ｡◕‿◕｡  ｡◕‿◕｡  ｡◕‿◕｡  ｡◕‿◕｡         ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             「{}」项目启动啦！                ┃
                                  ┃                                            ┃
                                  ┃         ʕ•̀ω•́ʔ✧  冲鸭冲鸭～ 加油加油～  ʕ•̀ω•́ʔ✧      ┃
                                  ┃                                            ┃
                                  ┃         一定会顺顺利利，没有BUG的！(*╹▽╹*)     ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃        (✧∇✧)  (✧∇✧)  (✧∇✧)  (✧∇✧)         ┃
                                  ┃                                            ┃
                                  ┃        ╭───╮  ╭───╮  ╭───╮  ╭───╮          ┃
                                  ┃        │♡♡│  │♡♡│  │♡♡│  │♡♡│          ┃
                                  ┃        ╰───╯  ╰───╯  ╰───╯  ╰───╯          ┃
                                  ┃                                            ┃
                                  ┃        (✧∇✧)  (✧∇✧)  (✧∇✧)  (✧∇✧)         ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                                  ╭╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╮
                                  ┃                                            ┃
                                  ┃             启动流程开始～ (๑＞ڡ＜)☆            ┃
                                  ┃                                            ┃
                                  ┃         ʚ(◜𖥦◝ )ɞ  祝一切顺利哦～  ʚ(◜𖥦◝ )ɞ        ┃
                                  ┃                                            ┃
                                  ╰╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╼╯
                """.format(config.project_name)
        )

        # 判断现有的测试用例，如果未生成测试代码，则自动生成
        # TestCaseAutomaticGeneration().get_case_automatic()

        pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning',
                     '--alluredir', './report/tmp', "--clean-alluredir"])

        """
                   --reruns: 失败重跑次数
                   --count: 重复执行次数
                   -v: 显示错误位置以及错误的详细信息
                   -s: 等价于 pytest --capture=no 可以捕获print函数的输出
                   -q: 简化输出信息
                   -m: 运行指定标签的测试用例
                   -x: 一旦错误，则停止运行
                   --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
                    "--reruns=3", "--reruns-delay=2"
                   """

        # 1. 先打印当前工作目录（确认 Jenkins 路径）
        current_dir = os.getcwd()
        print(f"当前工作目录：{current_dir}")

        # 2. 执行 allure generate 并打印详细信息
        allure_cmd = "allure generate ./report/tmp -o ./report/html --clean"
        print(f"\n=== 执行 Allure 命令 ===")
        print(f"命令内容：{allure_cmd}")
        # 执行命令并获取退出码
        cmd_exit_code = os.system(allure_cmd)
        print(f"命令退出码：{cmd_exit_code}（0=成功，非0=失败）")

        # 3. 检查 tmp 目录（pytest 生成的原始数据）
        print(f"\n=== 检查 ./report/tmp 目录 ===")
        tmp_dir = os.path.join(current_dir, "report", "tmp")
        if os.path.exists(tmp_dir):
            print(f"tmp 目录存在：{tmp_dir}")
            # 列出 tmp 目录下所有文件
            tmp_files = os.listdir(tmp_dir)
            print(f"tmp 目录下的文件：{tmp_files}")
            if not tmp_files:
                print(f"⚠️  tmp 目录为空！pytest 未生成 Allure 原始数据")
        else:
            print(f"❌ tmp 目录不存在：{tmp_dir}（pytest 执行失败）")

        # 4. 检查 html 目录和 summary.json
        print(f"\n=== 检查 ./report/html 目录 ===")
        summary_json_path = os.path.join(current_dir, "report", "html", "widgets", "summary.json")
        html_dir = os.path.dirname(os.path.dirname(summary_json_path))
        if os.path.exists(html_dir):
            print(f"html 目录存在：{html_dir}")
            # 列出 html 目录下的文件（看是否生成了内容）
            html_files = os.listdir(html_dir)
            print(f"html 目录下的文件：{html_files}")
        else:
            print(f"❌ html 目录不存在：{html_dir}（allure generate 执行失败）")

        # 5. 检查 summary.json 并终止程序
        if not os.path.exists(summary_json_path):
            print(f"\n❌ 最终错误：summary.json 不存在 → {summary_json_path}")
            raise RuntimeError("Allure 报告生成失败，summary.json 不存在")

        allure_data = AllureFileClean().get_case_count()
        notification_mapping = {
            NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
            NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
            NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
            NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
        }

        if config.notification_type != NotificationType.DEFAULT.value:
            notify_type = config.notification_type.split(",")
            for i in notify_type:
                notification_mapping.get(i.lstrip(""))()

        if config.excel_report:
            ErrorCaseExcel().write_case()

        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        # os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")

        #启动本地服务供内网查看报告
        server = ReportServer(report_path=ensure_path_sep("\\report\\html"), port=9999, host='0.0.0.0')
        server.start_server()

    except Exception:
        # 如有异常，相关异常发送邮件
        e = traceback.format_exc()
        print("==========自动化执行异常=========")
        print(e)
        send_email = SendEmail(AllureFileClean.get_case_count())
        send_email.error_mail(e)
        raise


if __name__ == '__main__':
    run()
