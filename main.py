# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
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