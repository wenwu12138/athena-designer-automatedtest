#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025-10-24 10:42:20


import allure
import pytest
from utils.read_files_tools.get_yaml_data_analysis import GetTestCase
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.teardown_control import TearDownHandler
from utils.assertion.asynchronous_assert import AsynchronousAssert
from utils.cache_process.cache_control import CacheHandler
import datetime
import json


case_id = ['basis_AddBranch_001', 'basis_Compile_001', 'basis_PublishTest_001', 'basis_SwitchPlanTest_001', 'basis_PublishHuaweiProd_001', 'basis_SwitchPlanHuaweiProd_001', 'basis_PublishAzureProd_001', 'basis_SwitchPlanAzureProd_001']
TestData = GetTestCase.case_data(case_id)
re_data = regular(str(TestData))


@allure.epic("开发平台接口")
@allure.feature("基础功能验证")
class TestBasisFunction001:

    @allure.story("基于已有数据验证基础功能z")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_Basis_function001(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl(in_data).http_request()
        """
                        处理异步接口断言
                        判断用例是否为发版切板用例
                        如果是的话循环调用查询接口，设定超时次数为100次 100次以内没满足条件抛异常
        """
        # 如果是编译接口那么就存储存储编译包信息给后面用
        if any(i in in_data for i in ["compile"] ):
            CacheHandler.update_cache(cache_name='compileDataCode', value=json.loads(res.response_data)["data"])
        TearDownHandler(res).teardown_handle()
        Assert(assert_data=in_data['assert_data'],
               sql_data=res.sql_data,
               request_data=res.body,
               response_data=res.response_data,
               status_code=res.status_code).assert_type_handle()
        AsynchronousAssert(in_data=in_data, in_data_res=res).deployer_assert()


if __name__ == '__main__':
    pytest.main(['test_test_Basis_function001.py', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
