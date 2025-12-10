#!/usr/bin/env python3
"""
环境配置管理器
用于管理和切换不同测试环境
"""
import shutil

import yaml
import sys
import os


class EnvironmentManager:
    """环境配置管理器"""

    # 定义所有环境的配置模板
    ENVIRONMENTS = {
        "阿里Paas区": {
            "env": "阿里Paas区(代地端)",
            "athena_designer_host": "https://adp-paas.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc-paas.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp-paas.apps.digiwincloud.com.cn",
            "iam_host": "https://iam-test.digiwincloud.com.cn",
            "app1_code": "A5f1a0f58aAT",
            "app1_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkE1ZjFhMGY1OGFBVCIsInNpZCI6MH0.mesrYxqbgyvShHD0FBqilTXNDzyvPEoOnpuEaPAJmpI",
            "app2_code": "Aded5e0256AT",
            "app2_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkFkZWQ1ZTAyNTZBVCIsInNpZCI6MH0.1VL2mxXiVR1tKSxn-Wjr_JfcnCiJ-mj9pEob6waLkSs",
            "tenantId": "athenadeveloperTest",
            "tenantSid": 847600433497088,
            "tenantName": "配置测试器",
            "serviceCode": "DPBAS",
            "api_serviceCode": "dpbas"
        },
        "华为正式区": {
            "env": "华为正式区",
            "athena_designer_host": "https://adp.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp.apps.digiwincloud.com.cn",
            "iam_host": "https://iam.digiwincloud.com.cn",
            "app1_code": "A1dbf6e345AT",
            "app1_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkExZGJmNmUzNDVBVCIsInNpZCI6MH0.lOzR2mZxVVlwU9YyYzRgZhVouLHx_NNyvLqLOI5r32E",
            "app2_code": "A2ba74bfe3AT",
            "app2_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkEyYmE3NGJmZTNBVCIsInNpZCI6MH0.mJoe-Lzd7ruaF_L_hwgn45hK0_Qn4YkuXwq1QSrl9Wg",
            "tenantId": "athenadeveloperTest",
            "tenantSid": 847600433497088,
            "tenantName": "配置测试器",
            "serviceCode": "DPBAS",
            "api_serviceCode": "dpbas"
        },
        "华为测试区": {
            "env": "华为测试区",
            "athena_designer_host": "https://adp-test.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc-test.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp-test.apps.digiwincloud.com.cn",
            "iam_host": "https://iam-test.digiwincloud.com.cn",
            "app1_code": "Aautotest1AT",
            "app1_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkFhdXRvdGVzdDFBVCIsInNpZCI6MH0.x51q6SkRChvBOr1ca-iqzHU6SS_Mu2DqnrrJfFKO-7o",
            "app2_code": "A2a1989618AT",
            "app2_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkEyYTE5ODk2MThBVCIsInNpZCI6MH0.hS1fWh2DVpE0TKSEI5hrJcpr3I6SvwRcnpJB2qqO8sc",
            "tenantId": "athenadeveloperTest",
            "tenantSid": 847600433497088,
            "tenantName": "配置测试器",
            "serviceCode": "DPBAS",
            "api_serviceCode": "dpbas"
        },
        "地端双虎环境": {
            "env": "地端双虎环境",
            "athena_designer_host": "https://adp.twintigers.com",
            "athena_deployer_host": "https://aadc.twintigers.com",
            "athena_tenant_deployer_host": "https://atdp.twintigers.com",
            "iam_host": "http://iam.twintigers.com",
            "app1_code": "A17cf8730dAT",
            "app1_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkExN2NmODczMGRBVCIsInNpZCI6MH0.S-9XQqvDmQZEZLuelfS_ek_1LQPTNTmjNKtWBG5apjc",
            "app2_code": "Ac83bda9c1AT",
            "app2_Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IkFjODNiZGE5YzFBVCIsInNpZCI6MH0.2LMn7mwB0vNiJBfkD3KFJItI6qRaXCpb_Ah6w4bk6Hw",
            "tenantId": "72011633_test",
            "tenantSid": 21129805496897,
            "tenantName": "武汉双虎涂料股份有限公司测试",
            "serviceCode": "dtdapp",
            "api_serviceCode": "dtdapp"
        }
    }

    @classmethod
    def get_available_environments(cls):
        """获取所有可用的环境"""
        return list(cls.ENVIRONMENTS.keys())

    @classmethod
    def switch_environment(cls, env_name, config_file="common/config.yaml"):
        """切换到指定环境"""
        if env_name not in cls.ENVIRONMENTS:
            raise ValueError(f"环境 '{env_name}' 不存在。可用环境: {', '.join(cls.get_available_environments())}")

        # 读取原配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 备份原配置
        backup_file = f"{config_file}.backup"
        import shutil
        if os.path.exists(config_file):
            shutil.copy2(config_file, backup_file)
            print(f"✅ 已备份原配置到: {backup_file}")

        # 获取环境配置
        env_config = cls.ENVIRONMENTS[env_name]

        # 更新配置
        for key, value in env_config.items():
            config[key] = value

        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 已切换到环境: {env_name}")
        print(f"   设计器: {env_config['athena_designer_host']}")
        print(f"   部署器: {env_config['athena_deployer_host']}")
        print(f"   租户部署器: {env_config['athena_tenant_deployer_host']}")
        print(f"   IAM: {env_config['iam_host']}")
        print(f"   租户: {env_config['tenantId']}")

        return True

    @classmethod
    def restore_config(cls, config_file="common/config.yaml"):
        """恢复原配置"""
        backup_file = f"{config_file}.backup"
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, config_file)
            os.remove(backup_file)
            print(f"✅ 已恢复原配置")
            return True
        else:
            print(f"⚠️  没有找到备份文件: {backup_file}")
            return False

    @classmethod
    def get_env_info(cls, env_name):
        """获取环境信息"""
        if env_name in cls.ENVIRONMENTS:
            return cls.ENVIRONMENTS[env_name]
        return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            print("可用的测试环境:")
            for env in EnvironmentManager.get_available_environments():
                info = EnvironmentManager.get_env_info(env)
                print(f"  - {env}: {info['athena_designer_host']}")

        elif command == "switch":
            if len(sys.argv) > 2:
                env_name = sys.argv[2]
                EnvironmentManager.switch_environment(env_name)
            else:
                print("请指定环境名称")
                print("可用环境:", ", ".join(EnvironmentManager.get_available_environments()))

        elif command == "restore":
            EnvironmentManager.restore_config()

        elif command == "info":
            if len(sys.argv) > 2:
                env_name = sys.argv[2]
                info = EnvironmentManager.get_env_info(env_name)
                if info:
                    print(f"环境: {env_name}")
                    for key, value in info.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"环境 '{env_name}' 不存在")
            else:
                print("请指定环境名称")

        else:
            print("可用命令:")
            print("  python env_config_manager.py list           # 列出所有环境")
            print("  python env_config_manager.py switch <env>   # 切换到指定环境")
            print("  python env_config_manager.py restore        # 恢复原配置")
            print("  python env_config_manager.py info <env>     # 查看环境详情")
    else:
        print("请提供命令参数")
        print("例如: python env_config_manager.py list")