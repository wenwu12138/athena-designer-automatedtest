#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 14:12
# @Author : 闻武
import pytest
import time
import allure
import requests
import ast
from common.setting import ensure_path_sep
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.cache_process.cache_control import CacheHandler
from datetime import datetime
import json
from utils.read_files_tools.regular_control import regular
from utils import config


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    del_file(ensure_path_sep("\\report"))


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    获取登录的cookie
    :return:
    """

    url = "https://www.wanandroid.com/user/login"
    data = {
        "username": "wenwu",
        "password": 123456
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # 请求登录接口

    res = requests.post(url=url, data=data, verify=True, headers=headers)
    response_cookie = res.cookies

    cookies = ''
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)

@pytest.fixture(scope="session", autouse=True)
def get_iam_token():
    """"
    调用iam接口获取token
    """
    url = "${{iam_host()}}/api/iam/v2/identity/login"

    data = {
    "userId": "wenwu@digiwin.com",
    "passwordHash": "lOqy40uSwNkSrh2WxxkQdQ==",
    "clientEncryptPublicKey": "eKUub4lLDSwDkyc5kyLzkTyqtWEtOYTDLW4pd95sbMkO94OJIE9ClHzKgKw0HxeCnJuG1KdbMKaR6I58bESQWNbifxMsO1zcroBffXU6ZUewq1kKfz2S8O83384BS7Aw+UPawwUQlKzZwUGUPqreZU5LSD4+1iir/NIdp2658CcY0oFZdXdXiCLc+dDNng8hC2t13u8q//bgIhTNwKF2W/z3JCeziZzL42jx1/hsrrNlhnXeN/4w+Kfbklr7XSvJSLz6zgu4YqYcu4DWUfxdRWn+Khj6NYNr2RrouZQlGjUDZjqgAn+TxGu4j4RF6Mf14xVeaB+6toENoq7gQqL7yw==",
    "excludeNonVisible": True,
    "tenantId":"athenadeveloperTest"
}
    headers = {
        "Content-Type": "application/json",
        "digi-middleware-auth-app":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzczMjY2ODk0NjEsInNpZCI6NDA3MTI4ODI1NTM0NDY0MSwiaWQiOiJEaWdpd2luQ2xvdWQifQ.XGPl3brNeNTCivWN_bIYj8TfcxqlkQ0sFV2woPOr0TY"

    }

    """
    #  双虎地端环境
    data = {
    "userId": "default",
    "passwordHash": "skv1PcefW8T6aX43rdbkhg==",
    "clientEncryptPublicKey": "a/j/W/AIcXb7nWL0pDAZ27h28IiZHa8A5R2cP+WbYNE9bFZwv330c5VX/cFj23Lg1xk0bECInHxQk0gSD8NWdIFRz9SVZUWjGfhDOkmK83yhThuzYTK4wtJlcX36RemJGXldAhtE2b2tgPGoBbT+DXFMJVUjbPmqo16Lgzwi82zi1jLTkkGt+m39M+bU3sFf/deUWwNZiYyMt1oxXvH4MRgdGCJGEqnjdz3xiiWJvAQTLDHW3ox9opbJ2hUQZMZ7SH2M6XAFOWXDCFmwWRA34jAr8d4oSGN2onfJHe7smquTl5yaHQ4Niwquo5kRMruJ3wu2NSZNSD41Ney1BC/hXw==",
    "excludeNonVisible": True
}
    headers = {
   'digi-middleware-auth-app': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MzczMjY2ODk0NjEsInNpZCI6NDA3MTI4ODI1NTM0NDY0MSwiaWQiOiJEaWdpd2luQ2xvdWQifQ.XGPl3brNeNTCivWN_bIYj8TfcxqlkQ0sFV2woPOr0TY',
   'digi-middleware-device-id': 'bYdVWJHMnxMl/wj0DPeFlkpHNWO12g/RNg9oc+CtSxRkdmQUJVyFvAp5lBcJB8ytn5SeAhsp+YDfZk50ohrJU/Rw/AcHjlIoqE2wRByylk8=',
   'Content-Type': 'application/json'
}
    """

    # 正式区就要用lcdp这个租户验证  只有这个租户能发微软正式
    # if '正式' in config.env:
    #     data['tenantId'] = 'lcdp'
    url = regular(str(url))
    res = requests.post(url=url, json=data, headers=headers, verify=False)
    response_data = res.json()
    token = response_data["token"]
    CacheHandler.update_cache(cache_name='token', value=token)



## 需要前置生成的测试数据
@pytest.fixture(scope="session", autouse=True)
def pretest_data():
    testdata = {
        "TestApp_code": "${{random_id()}}AT",
        "Data_Code": "${{random_hexcode()}}",
        "Project_Data_Code": "${{random_hexcode()}}"
    }
    for k, v in testdata.items():
        k = regular(str(k))
        v = regular(str(v))
        testdata[k] = v
        # print(testdata)
        CacheHandler.update_cache(cache_name=k, value=v)
        # print(CacheHandler.get_cache(k))




def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

    # 期望用例顺序
    # print("收集到的测试用例:%s" % items)
    appoint_items = ["test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
                     "test_Clear_Cart_Item"]

    # 指定运行顺序
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)

        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    config.addinivalue_line("markers", 'smoke')
    config.addinivalue_line("markers", '回归测试')


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if isinstance(in_data.is_run, str):
        in_data.is_run = eval(in_data.is_run)
    #目前is_run有两种形式,如果是string 就当表达式执行一下
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()

def pytest_sessionstart(session):
    """测试会话开始时记录时间"""
    global _session_start_time
    _session_start_time = time.time()
    print(f"测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时记录时间"""
    global _session_start_time
    if _session_start_time:
        duration = time.time() - _session_start_time
        print(f"测试结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")


def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    session_start = terminalreporter._session_start
    session_start_timestamp = time.mktime(session_start.timetuple()) if isinstance(session_start, datetime) else 0
    #计算使用时间
    global _session_start_time

    if _session_start_time:
        duration = time.time() - _session_start_time
    else:
        duration = 0


    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - session_start_timestamp     # 不太对啊 先放着 不报错~
    INFO.logger.error(f"用例总数: {_TOTAL}")
    INFO.logger.error(f"异常用例数: {_ERROR}")
    ERROR.logger.error(f"失败用例数: {_FAILED}")
    WARNING.logger.warning(f"跳过用例数: {_SKIPPED}")
    INFO.logger.info(f"测试总时长: {duration:.2f}秒")

    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        INFO.logger.info("用例成功率: 0.00 %")


