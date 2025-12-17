#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/12/17 16:58  
# @Author  : wenwu        
# @Desc    :      
# @File    : config_handler.py       
# @Software: PyCharm


"""
环境配置处理方法
"""
from typing import Dict, Any


def handle_env_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理环境配置

    规则：
    1. 如果配置中有environments，就处理环境配置
    2. 必须有current_environment字段
    3. current_environment必须在environments中存在
    4. 合并环境配置到顶层

    返回处理后的配置数据
    """
    # 如果没有environments配置，直接返回
    if 'environments' not in config_data:
        return config_data

    # 获取当前环境
    env_key = config_data.get('current_environment')
    if not env_key:
        raise ValueError("配置文件中必须设置 current_environment 字段")

    # 检查环境是否存在
    if env_key not in config_data['environments']:
        available = list(config_data['environments'].keys())
        raise ValueError(f"环境 '{env_key}' 不存在。可用环境: {available}")

    # 创建新配置
    new_config = {}

    # 复制非environments配置
    for key, value in config_data.items():
        if key != 'environments':
            new_config[key] = value

    # 合并环境配置
    env_config = config_data['environments'][env_key]
    new_config.update(env_config)

    return new_config