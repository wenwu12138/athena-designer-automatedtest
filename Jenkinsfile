pipeline {
    agent any

    environment {
        PROJECT_NAME = 'athena-designer-automatedtest'
        PYTHON_VERSION = '3.9'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/develop']],
                    extensions: [[$class: 'CleanCheckout']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/wenwu12138/athena-designer-automatedtest.git'
                    ]]
                ])

                sh '''
                    echo "项目拉取完成"
                    echo "当前目录:"
                    pwd
                    ls -la
                '''
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "===== 设置 Python 环境 ====="
                    python3 --version

                    # 创建虚拟环境
                    python3 -m venv venv
                    . venv/bin/activate

                    echo "虚拟环境已创建并激活"
                    python --version
                    pip --version
                '''
            }
        }

        stage('Prepare Requirements') {
            steps {
                sh '''
                    echo "===== 准备依赖安装 ====="

                    # 创建适用于 Linux 的 requirements 文件
                    cat > requirements_jenkins.txt << 'EOF'
# 基础依赖
PyYAML==6.0.2
requests==2.32.4
requests-toolbelt==1.0.0
requests_to_curl==1.1.0
urllib3==2.5.0
certifi==2025.6.15
charset-normalizer==3.4.2
idna==3.10

# 测试框架
pytest==7.4.4
pytest-forked==1.6.0
pytest-xdist==3.5.0
allure-pytest==2.13.2
allure-python-commons==2.13.2
coverage==7.12.0
atomicwrites==1.4.1
iniconfig==2.3.0
pluggy==1.6.0
py==1.11.0
attrs==25.3.0
colorama==0.4.6

# 数据库
PyMySQL==1.1.1
redis==6.2.0

# 数据处理
openpyxl==3.1.5
et_xmlfile==2.0.0
xlrd==2.0.2
xlutils==2.0.0
xlwt==1.3.0
xlwings==0.33.15

# Web 框架
Flask==3.1.0
Werkzeug==3.1.3
Jinja2==3.1.6
MarkupSafe==3.0.2
click==8.2.1
itsdangerous==2.2.0
blinker==1.9.0

# 加密和安全
cryptography==44.0.3
cffi==1.17.1
pycparser==2.22
pyOpenSSL==25.0.0
passlib==1.7.4
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0

# 异步和网络
aiofiles==24.1.0
aioquic==1.2.0
sanic==25.3.0
sanic-routing==23.12.0
websockets==15.0.1
tornado==6.5
h11==0.16.0
h2==4.1.0
hpack==4.1.0
hyperframe==6.1.0
httptools==0.6.4
Brotli==1.1.0
pylsqpack==0.3.22
multidict==6.5.1
msgpack==1.1.0
wsproto==1.2.0

# 工具库
python-dateutil==2.9.0
six==1.17.0
tzdata==2025.2
chardet==5.2.0
colorlog==6.9.0
execnet==2.1.1
Faker==37.4.0
jsonpath==0.82.2
kaitaistruct==0.10
ldap3==2.9.1
mitmproxy==12.1.1
mitmproxy_rs==0.12.6
Naked==0.1.32
packaging==25.0
pefile==2023.2.7
protobuf==6.31.1
psutil==7.1.3
publicsuffix2==2.20191221
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.11.7
pydantic_core==2.33.2
pyDes==2.0.1
Pygments==2.19.2
pyparsing==3.2.3
pyperclip==1.9.0
pypng==0.20220715.0
PyQRCode==1.2.1
ruamel.yaml==0.18.10
ruamel.yaml.clib==0.2.12
service-identity==24.2.0
setuptools==80.9.0
shellescape==3.8.1
sortedcontainers==2.4.0
text-unidecode==1.3
toml==0.10.2
tracerite==1.1.3
typing-inspection==0.4.1
typing_extensions==4.14.0
urwid==2.6.16
wcwidth==0.2.13
zstandard==0.23.0
DingtalkChatbot==1.5.7
itchat==1.3.10

# 移除 Windows 专用包:
# pywin32==310
# pywin32-ctypes==0.2.3
# mitmproxy-windows==0.12.6
# pydivert==2.1.0 - Windows 网络驱动
# altgraph==0.17.4 - pyinstaller 相关
# crypto==1.4.1 - 可能有问题
# html5tagger==1.3.0 - 可能不需要
EOF

                    echo "已创建 Jenkins 专用 requirements 文件"
                    echo "文件大小:"
                    wc -l requirements_jenkins.txt
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "===== 安装依赖 ====="
                    . venv/bin/activate

                    # 升级 pip
                    pip install --upgrade pip setuptools wheel

                    # 先安装核心依赖
                    echo "安装核心依赖..."
                    pip install PyYAML requests pytest openpyxl PyMySQL Flask

                    # 安装 Jenkins 专用 requirements
                    echo "安装 Jenkins requirements..."
                    pip install -r requirements_jenkins.txt

                    # 处理可能失败的特殊包
                    echo "处理特殊包..."

                    # 尝试安装 pywin32-ctypes（Linux 替代）
                    pip install pywin32-ctypes==0.2.3 || echo "pywin32-ctypes 安装失败，跳过"

                    # 安装其他可能需要的包
                    pip install python-dateutil==2.9.0 || pip install python-dateutil

                    echo "安装完成，已安装包数量:"
                    pip list | wc -l
                '''
            }
        }

        stage('Verify Installation') {
            steps {
                sh '''
                    echo "===== 验证安装 ====="
                    . venv/bin/activate

                    echo "测试关键模块导入..."
                    python -c "
import sys
print('Python 版本:', sys.version)

modules_to_test = [
    'yaml', 'requests', 'pytest', 'pymysql', 'openpyxl',
    'flask', 'allure', 'cryptography', 'redis'
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f'✅ {module}')
    except Exception as e:
        print(f'❌ {module}: {e}')
"

                    echo "检查 yaml 模块..."
                    python -c "import yaml; print(f'PyYAML 版本: {yaml.__version__}')" || echo "yaml 导入失败"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "===== 运行测试 ====="
                    . venv/bin/activate

                    echo "当前工作目录:"
                    pwd

                    echo "查找入口文件..."
                    find . -maxdepth 1 -type f \( -name "run.py" -o -name "run" -o -name "main.py" \) | head -5

                    if [ -f "run.py" ]; then
                        echo "执行 run.py..."
                        python run.py
                    elif [ -f "run" ]; then
                        echo "执行 run 脚本..."
                        chmod +x run
                        ./run
                    else
                        echo "未找到入口文件，尝试运行 pytest..."
                        python -m pytest test_cases/ -v --html=reports/report.html
                    fi
                '''
            }
        }

        stage('Generate Reports') {
            steps {
                sh '''
                    echo "===== 生成报告 ====="

                    # 创建报告目录
                    mkdir -p reports

                    echo "报告文件:"
                    find reports -type f 2>/dev/null || echo "无报告文件"
                '''

                // 归档测试报告
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

                // 发布 HTML 报告
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: '*.html',
                    reportName: 'API 测试报告'
                ])
            }
        }
    }

    post {
        always {
            echo "===== 构建完成 ====="
            echo "项目: ${PROJECT_NAME}"
            echo "分支: develop"
            echo "状态: ${currentBuild.result ?: 'SUCCESS'}"
            echo "构建编号: ${BUILD_NUMBER}"

            // 清理（可选）
            // sh 'rm -rf venv'
        }
        success {
            echo "✅ 自动化测试执行成功！"
            // 可以添加成功通知
        }
        failure {
            echo "❌ 自动化测试执行失败！"
            // 可以添加失败通知
        }
    }
}