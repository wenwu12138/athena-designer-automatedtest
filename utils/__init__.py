
from utils.read_files_tools.yaml_control import GetYamlData
from common.setting import ensure_path_sep
from utils.other_tools.models import Config
from utils.read_files_tools.regular_control import regular
import json


_data = GetYamlData(ensure_path_sep("\\common\\config.yaml")).get_yaml_data()
_data = eval(regular(str(_data)))
config = Config(**_data)
# 解决用例中存在 随机生成参数  并且参数在入参中存在多个路径用法
# 1.首先用例用配置的静态文件就用了  因为这个静态文件是通用替换的
# 2.然后在config里面加入配置文件  只不过这个配置文件的value 是一个变量（静态文件类型 ，可以只用方法替换）
# 3. 在取配置文件的时候 检索一下 有变量替换一下就ok了  那么配置文件就替换生成了