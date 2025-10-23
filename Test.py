"""重写正则替换方法"""
from symtable import Class

from faker import Faker
import random
import re
from utils.cache_process.cache_control import CacheHandler
from utils.logging_tool.log_control import ERROR

class Context:
    """进行正则替换"""
    def __init__(self):
        self.faker = Faker(locale='zh_CN')
        # Faker是一个生成mock数据的第三方库，初始化生成

    @classmethod
    def random_int(cls) -> int:
        """生成随机整数"""
        _data = random.randint(0, 5000)
        return _data

    def get_phone(self):
        """
        随机生成一个手机号码
        """
        phone = self.faker.phone_number()
        return  phone

    def get_id_number(self) -> str:
        """随机生成身份证"""
        id_number = self.faker.phone_number()
        return id_number




# 这个缓存替换方法其实里面说的缓存就是全局变量  目前一般用于替换请求token
def cache_regular(value):
    from utils.cache_process.cache_control import CacheHandler
    """
    根据缓存信息替换占位符
    传入待替换的值，返回已经替换的值 这里的缓存就是全局变量
    一般情况下缓存数据value为$chche{token}
    """
    regular_datas = re.findall(r"\$cache\{(.*?)}",value)  # 匹配目标中符合正则的内容以list返回

    for regular_data in regular_datas:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        """
        兼容各种缓存key写法的情况下 生成一个正则对象
        """
        if any(i in regular_data for i in value_types) is True:      #猜测可能是有这种写法$cache{int:age}
            value_types = regular_data.split(':')[0]
            regular_data = regular_data.split(':')[1]
            # 如果是 $cache{int:age} 类型的缓存那就重新更新缓存数据和类型 来组成正则
            pattern = re.compile(
                r"\$cache\{" + value_types.split(".")[0] + r"\}"# 创建一个正则对象
            )
        else:
            #普通情况，例如$cache{token} regular_data 为token，name等替换key ,里面兼容了有$cache{$[token}
            pattern = re.compile(
                r"\$cache\{" + regular_data.replace("$",r"\$").replace("[", r"\[") + r"\}"
            )

        try:
            cache_data = CacheHandler.get_cache(regular_data) # 根据缓存key获取缓存数据
            # 使用sub方法替换
            value = re.sub(pattern, str(cache_data), value)
        except Exception:
            pass
    return value


def regular(target):
    """
    正则替换，数据来源是通过上面的Context方法进行数据替换，有从config=里面取来源数据
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):    # re.findall 返回一个list，元素为匹配的内容，正则中有分组则返回分组无则整个对象
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(':')[1].split('(')[0]
                value_name = key.split(':')[1].split('(')[1][:-1]
                if value_name == '':
                    value_data = getattr(Context, func_name)
                else:
                    value_data = getattr(Context, func_name)(*value_name.split(','))
                regular_int_pattern = r'\'\${{(.*>)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]
                if value_name == '':
                    value_data = getattr(Context, func_name)()
                else:
                    value_data = getattr(Context, func_name)(*value_name.split(','))
                target = re.sub(regular_pattern, str(value_data), target, 1)
        return target
    except AttributeError:
        ERROR.logger.error("未找到对应的替换的数据, 请检查数据是否正确 %s", target)
        raise
    except IndexError:
        ERROR.logger.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：${{get_time()}}")
        raise



# 静态方法以及属性装饰器

class MathTils:
    def __init__(self,a, b):
        self.a = a
        self.b = b

    #普通方法
    def add(self, a, b):
        return  a + b

    @property
    def sub(self):
        return self.a - self.b

    @staticmethod
    def multiply(d, c):
        return d * c




proton = MathTils(a=1, b=3)
print(proton.sub)

print(MathTils.multiply(100,3))







if __name__ == '__main__':
    CacheHandler.update_cache(cache_name="test",value="闻武12313213312")

    # print(cache_regular("weweweweew:$cache{test}"))
    print()