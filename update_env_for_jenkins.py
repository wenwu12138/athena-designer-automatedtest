#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/10 13:35  
# @Author  : wenwu        
# @Desc    :      
# @File    : update_env_for_jenkins.py       
# @Software: PyCharm


# !/usr/bin/env python3
"""
简化版环境切换脚本
用于Jenkins中快速切换环境
"""
import yaml
import sys
import os


def switch_environment(env_name):
    """切换到指定环境"""

    # 环境配置映射
    ENV_CONFIGS = {
        "阿里Paas区": {
            "env": "阿里Paas区(代地端)",
            "athena_designer_host": "https://adp-paas.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc-paas.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp-paas.apps.digiwincloud.com.cn",
            "iam_host": "https://iam-test.digiwincloud.com.cn"
        },
        "华为测试区": {
            "env": "华为测试区",
            "athena_designer_host": "https://adp-test.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc-test.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp-test.apps.digiwincloud.com.cn",
            "iam_host": "https://iam-test.digiwincloud.com.cn"
        },
        "华为正式区": {
            "env": "华为正式区",
            "athena_designer_host": "https://adp.apps.digiwincloud.com.cn",
            "athena_deployer_host": "https://aadc.apps.digiwincloud.com.cn",
            "athena_tenant_deployer_host": "https://atdp.apps.digiwincloud.com.cn",
            "iam_host": "https://iam.digiwincloud.com.cn"
        },
        "地端双虎环境": {
            "env": "地端双虎环境",
            "athena_designer_host": "https://adp.twintigers.com",
            "athena_deployer_host": "https://aadc.twintigers.com",
            "athena_tenant_deployer_host": "https://atdp.twintigers.com",
            "iam_host": "http://iam.twintigers.com"
        }
    }

    if env_name not in ENV_CONFIGS:
        print(f"❌ 错误：环境 '{env_name}' 不存在")
        print(f"可用环境: {', '.join(ENV_CONFIGS.keys())}")
        return False

    config_file = "common/config.yaml"

    # 读取原配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 备份原配置
    backup_file = f"{config_file}.backup"
    if os.path.exists(config_file):
        import shutil
        shutil.copy2(config_file, backup_file)
        print(f"✅ 已备份原配置到: {backup_file}")

    # 更新配置
    env_config = ENV_CONFIGS[env_name]
    for key, value in env_config.items():
        config[key] = value

    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ 已切换到环境: {env_name}")
    print(f"   设计器地址: {env_config['athena_designer_host']}")
    print(f"   部署器地址: {env_config['athena_deployer_host']}")
    print(f"   租户部署器: {env_config['athena_tenant_deployer_host']}")
    print(f"   IAM地址: {env_config['iam_host']}")

    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python update_env_for_jenkins.py <环境名称>")
        print("可用环境: 阿里Paas区, 华为测试区, 华为正式区, 地端双虎环境")
        sys.exit(1)

    try:
        success = switch_environment(sys.argv[1])
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 切换环境时出错: {e}")
        sys.exit(1)