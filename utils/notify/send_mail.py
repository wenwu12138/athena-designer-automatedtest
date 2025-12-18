#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/29 14:57
# @Author : 闻武
描述: 发送邮件
"""
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from utils.other_tools.allure_data.allure_report_data import TestMetrics, AllureFileClean
from utils import config


class SendEmail:
    """ 发送邮箱 """
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.allure_data = AllureFileClean()
        self.failed_detail = self.allure_data.get_failed_cases_detail() or "本次无失败用例"
        # 计算补充指标（保证简洁，只加核心）
        self.pass_rate = self.metrics.pass_rate
        self.failure_rate = round((self.metrics.failed / self.metrics.total * 100) if self.metrics.total > 0 else 0, 2)
        self.exec_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def send_mail(cls, user_list: list, sub, content: str) -> None:
        """

        @param user_list: 发件人邮箱
        @param sub:
        @param content: 发送内容
        @return:
        """
        send_user = config.email.send_user

        user = "闻武" + "<" + config.email.send_user + ">"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')
        message['Subject'] = sub
        message['From'] = send_user
        message['To'] = ";".join(user_list)
        server = smtplib.SMTP_SSL(config.email.email_host, 465, timeout=30)
        server.connect(config.email.email_host)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(send_user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        执行异常邮件通知
        @param error_message: 报错信息
        @return:
        """
        email = config.email.send_list
        user_list = email.split(',')  # 多个邮箱发送，config文件中直接添加  '806029174@qq.com'

        sub = config.project_name + "接口自动化执行异常通知"
        content = f"自动化测试执行完毕，程序中发现异常，请悉知。报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self, report_path: str = None) -> None:
        """
        发送邮件
        :return:
        """
        # 设置默认报告路径
        default_report_path = "http://192.168.201.161:9999"
        final_report_path = report_path if report_path else default_report_path

        # 打印提示信息
        if not report_path:
            print("未获取到云端jenkins报告路径，使用默认本地路径")

        email = config.email.send_list
        user_list = email.split(',')  # 多个邮箱发送，yaml文件中直接添加  '806029174@qq.com'

        sub = config.project_name + "接口自动化报告"
        content = f"""
                    各位同事：
                    
                    您好！{config.project_name}接口自动化用例执行完成，核心结果如下：
                    
                    ┌────────────────┬────────────────────┐
                    │  执行维度      │  执行结果          │
                    ├────────────────┼────────────────────┤
                    │  执行时间      │  {self.exec_time:<16} │
                    │  用例总数      │  {self.metrics.total:>4} 个        │
                    │  通过用例      │  {self.metrics.passed:>4} 个        │
                    │  失败用例      │  {self.metrics.failed:>4} 个        │
                    │  异常用例      │  {self.metrics.broken:>4} 个        │
                    │  跳过用例      │  {self.metrics.skipped:>4} 个        │
                    │  成功率        │  {self.pass_rate:>6.2f}%           │
                    │  失败率        │  {self.failure_rate:>6.2f}%           │
                    └────────────────┴────────────────────┘
                    
                    【失败用例详情】
                    {self.failed_detail}
                    
                    【报告链接】
                    Jenkins详情地址：{final_report_path}
                    
                    温馨提示：
                    1. 非相关负责人员可忽略此邮件
                    2. 失败用例请及时排查原因并修复
                    3. 本邮件为系统自动发送，无需回复
                    
                    感谢配合！
                    """.strip()
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_main()
