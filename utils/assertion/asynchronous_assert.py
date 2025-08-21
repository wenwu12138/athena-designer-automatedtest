import json
import requests
from utils.logging_tool.log_control import INFO, ERROR
import time
from utils.read_files_tools.regular_control import regular


class AsynchronousAssert:
    def __init__(self, in_data, in_data_res):
        self.in_data = in_data
        self.in_data_res = in_data_res



    def deployer_assert(self):
        # 轮询查询发版进度
        if "addDeployPlan" in self.in_data["url"]:
            url = '${{athena_deployer_host()}}/athenadeployer/deploy/v3/queryDeployProcess'
            params = {"deployNo": json.loads(self.in_data_res.response_data)["data"],
                      "application": self.in_data_res.body["applicationDataList"][0]["application"]}
            headers = {"Content-Type": "application/json",
                       "digi-middleware-auth-user": self.in_data_res.headers["digi-middleware-auth-user"],
                       "token": self.in_data_res.headers["digi-middleware-auth-user"]}
            result = False
            i = 0
            url = regular(str(url))
            while i < 100:
                query_res = requests.get(url=url, headers=headers, params=params)
                if json.loads(query_res.text)["data"] == 1:
                    result = True
                    INFO.logger.info("\n"
                                     "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                     "发版成功\n"
                                     "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                    break
                else:
                    i += 1
                    # INFO.logger.info(f"进行第{i}次查询操作，目前的进度为{json.loads(query_res.text)["data"]}")

                # 等待三秒后执行下一次查询
                time.sleep(3)
        elif "addSwitchPlan" in self.in_data["url"]:
            #切板查询处理
            url = '${{athena_deployer_host()}}/athenadeployer/deploy/v3/queryProcess'
            params = {"deployNo": json.loads(self.in_data_res.response_data)["data"]["id"],
                      "application": self.in_data_res.body["applicationDataList"][0]["application"]}
            headers = {"Content-Type": "application/json",
                       "digi-middleware-auth-user": self.in_data_res.headers["digi-middleware-auth-user"],
                       "token": self.in_data_res.headers["digi-middleware-auth-user"]}
            result = False
            i = 0
            url = regular(str(url))
            while i < 100:
                query_res = requests.get(url=url, headers=headers, params=params)
                if json.loads(query_res.text)["data"] == 1:
                    result = True
                    INFO.logger.info("\n"
                                     "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n"
                                     "切板成功\n"
                                     "⁽ଘ( ˊᵕˋ )ଓ⁾⁾\n")
                    break
                else:
                    i += 1
                    # INFO.logger.info(f"进行第{i}次查询操作，目前的进度为{json.loads(query_res.text)["data"]}")

                # 等待三秒后执行下一次查询
                time.sleep(3)

"""
        处理异步接口断言
        判断用例是否为发版切板用例
        如果是的话循环调用查询接口，设定超时次数为100次 100次以内没满足条件抛异常
"""
# 发版异步断言


