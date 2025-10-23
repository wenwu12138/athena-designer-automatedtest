# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import os
import subprocess


def package_python_app(script_path, output_dir="dist", onefile=True):
    """
    使用PyInstaller打包Python应用

    :param script_path: Python主脚本路径
    :param output_dir: 输出目录
    :param onefile: 是否打包为单个文件
    """
    # 检查脚本文件是否存在
    if not os.path.exists(script_path):
        print(f"错误: 脚本文件 {script_path} 不存在")
        return

    # 构建PyInstaller命令
    cmd = ["pyinstaller", "--distpath", output_dir]
    if onefile:
        cmd.append("--onefile")
    cmd.append(script_path)

    # 执行打包命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功!")
        print(f"可执行文件已生成在: {output_dir}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e.stderr}")
        return False


if __name__ == "__main__":
    # 替换为你的主脚本路径
    main_script = "run.py"
    package_python_app(main_script)

"""
对于缓存的使用有两种场景

第一种场景是静态缓存数据 就是固定写在配置文件种config种的缓存
使用静态缓存的第一步，在config文件中配置缓存数据
第二步 在模型值中配置配置缓存值 这里有缓存校验   from utils.other_tools.models import Config  这里
第三部 缓存方法种Context 类中添加对应的获取缓存方案
占位符例子未${{host}}
执行缓存替换时使用regular 方法去替换  这里的本质是regular方法里面有类 类方法里面有导入config值返回
==================================================
第二种是
动态的发版数据，例如每次的token
使用 CacheHandler.update_cache 存入缓存数据
使用 CacheHandler.get_cache获取缓存数据
本质是全局变量
"""