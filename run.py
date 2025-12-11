#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 15:01
# @Author : 闻武
import json
import os
import shutil
import subprocess
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

        #------------生成allure报告文件
        # 1. 定义核心路径（简洁易维护）
        tmp_dir = "./report/tmp"
        html_dir = "./report/html"
        summary_json = f"{html_dir}/widgets/summary.json"

        # 2. 清空旧报告（避免残留）
        if os.path.exists(html_dir):
            shutil.rmtree(html_dir)
        os.makedirs(html_dir, exist_ok=True)

        # 3. 静默执行 Allure 生成（核心命令，带超时+静默）
        print("开始生成 Allure 测试报告...")
        try:
            # 替代 os.system，静默执行+3分钟超时（避免卡顿）
            subprocess.run(
                ["allure", "generate", tmp_dir, "-o", html_dir, "--clean", "-q"],
                stdout=subprocess.DEVNULL,  # 屏蔽所有输出
                stderr=subprocess.DEVNULL,
                timeout=180,  # 超时控制：3分钟
                check=False
            )
        except Exception:
            # 执行失败不报错，直接走兜底逻辑
            pass

        # 4. 兜底：自动创建 summary.json（解决文件缺失问题）
        os.makedirs(f"{html_dir}/widgets", exist_ok=True)
        if not os.path.exists(summary_json):
            # 生成默认统计数据（保证程序不崩溃）
            default_data = {"total": 0, "passed": 0, "failed": 0, "broken": 0, "skipped": 0}
            # 尝试统计 tmp 目录用例数（更精准）
            if os.path.exists(tmp_dir):
                default_data["total"] = len([f for f in os.listdir(tmp_dir) if "result.json" in f])
            # 写入默认文件
            with open(summary_json, "w", encoding="utf-8") as f:
                json.dump(default_data, f)
            print(f"提示：Allure 报告未正常生成，已创建默认 {summary_json}")
        else:
            print(f"Allure 报告生成成功：{summary_json}")



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
