#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/17 15:00  
# @Author  : wenwu        
# @Desc    :      
# @File    : test.py       
# @Software: PyCharm

"""
配置管理模块 - 支持环境隔离的动态配置平铺
"""
import os
import yaml
from typing import Dict, Any
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ensure_path_sep
from utils.other_tools.models import Config


class ConfigManager:
    """配置管理器 - 负责加载和合并配置"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or ensure_path_sep("\\common\\config.yaml")
        self._raw_config = None
        self._flat_config = None
        self.current_env = None

    def load_config(self) -> Dict[str, Any]:
        """加载原始配置文件"""
        self._raw_config = GetYamlData(self.config_path).get_yaml_data()
        return self._raw_config

    def get_environment(self) -> str:
        """获取当前环境"""
        # 1. 环境变量优先级最高
        env_from_env = os.getenv('TEST_ENVIRONMENT')
        if env_from_env:
            self.current_env = env_from_env
            return env_from_env

        # 2. 系统环境变量
        env_from_os = os.getenv('ENVIRONMENT', 'huawei-prod')
        self.current_env = env_from_os
        return env_from_os

    def flatten_config(self, raw_config: Dict[str, Any]) -> Dict[str, Any]:
        """将层级配置平铺为一维字典"""
        env_name = self.get_environment()

        # 获取基础配置（排除environments部分）
        base_config = {}
        for key, value in raw_config.items():
            if key != 'environments':
                base_config[key] = value

        # 获取环境特定配置
        env_config = {}
        if 'environments' in raw_config and env_name in raw_config['environments']:
            env_config = raw_config['environments'][env_name]
        else:
            # 如果找不到指定的环境，使用第一个环境
            available_envs = list(raw_config.get('environments', {}).keys())
            if available_envs:
                default_env = available_envs[0]
                print(f"⚠️ 警告: 环境 '{env_name}' 不存在，使用默认环境: {default_env}")
                env_config = raw_config['environments'][default_env]
                self.current_env = default_env
            else:
                print("⚠️ 警告: 没有找到任何环境配置")

        # 合并配置（环境配置覆盖基础配置）
        flat_config = {**base_config, **env_config}

        # 添加环境信息到配置中
        flat_config['_env_name'] = self.current_env

        return flat_config

    def get_config(self) -> Config:
        """获取最终的配置对象（兼容现有代码）"""
        if self._raw_config is None:
            self.load_config()

        if self._flat_config is None:
            self._flat_config = self.flatten_config(self._raw_config)

        # 打印调试信息
        if os.getenv('DEBUG_CONFIG', 'false').lower() == 'true':
            print("=" * 60)
            print(f"🔧 配置加载信息")
            print("=" * 60)
            print(f"当前环境: {self.current_env}")
            print(f"配置文件: {self.config_path}")
            print(f"基础配置项: {len([k for k in self._raw_config.keys() if k != 'environments'])}")
            print(f"可用环境: {list(self._raw_config.get('environments', {}).keys())}")
            print(f"最终配置项: {len(self._flat_config)}")
            print("关键配置验证:")
            for key in ['env', 'athena_designer_host', 'iam_host', 'app1_code', 'tenantId']:
                value = self._flat_config.get(key, '未找到')
                print(f"  {key}: {value}")
            print("=" * 60)

        # 返回Config对象（兼容现有代码）
        return Config(**self._flat_config)


# 全局配置实例（保持原有接口）
_config_manager = ConfigManager()
config = _config_manager.get_config()