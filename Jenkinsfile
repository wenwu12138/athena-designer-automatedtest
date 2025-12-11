pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    echo "===== 设置 Python 环境 ====="
                    python3 --version

                    # 创建虚拟环境
                    python3 -m venv venv
                    . venv/bin/activate

                    echo "升级 pip 和 setuptools"
                    pip install --upgrade pip setuptools wheel
                '''
            }
        }

        stage('Install Core Dependencies') {
            steps {
                sh '''
                    echo "===== 安装核心依赖 ====="
                    . venv/bin/activate

                    # 先安装绝对必要的核心包
                    echo "1. 安装核心包..."
                    pip install PyYAML==6.0.2 requests==2.32.4 pytest==7.4.4
                    pip install openpyxl==3.1.5 pymysql==1.1.1 flask==3.1.0
                    pip install jsonpath==0.82.2  # 这是缺失的包

                    echo "2. 安装数据处理包..."
                    pip install python-dateutil==2.9.0
                    pip install cryptography==44.0.3
                    pip install allure-pytest==2.13.2 allure-python-commons==2.13.2

                    echo "3. 安装其他必需包..."
                    pip install jinja2==3.1.6 markupsafe==3.0.2
                    pip install click==8.2.1 itsdangerous==2.2.0 blinker==1.9.0
                    pip install werkzeug==3.1.3
                '''
            }
        }

        stage('Install Project Dependencies') {
            steps {
                sh '''
                    echo "===== 安装项目依赖 ====="
                    . venv/bin/activate

                    # 过滤掉 Windows 专用包和不兼容的包
                    echo "创建清理后的 requirements 文件..."
                    cat > requirements_filtered.txt << 'EOF'
aiofiles==24.1.0
aioquic==1.2.0
allure-pytest==2.13.2
allure-python-commons==2.13.2
annotated-types==0.7.0
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0
asgiref==3.8.1
atomicwrites==1.4.1
attrs==25.3.0
blinker==1.9.0
Brotli==1.1.0
certifi==2025.6.15
cffi==1.17.1
chardet==5.2.0
charset-normalizer==3.4.2
click==8.2.1
colorama==0.4.6
colorlog==6.9.0
coverage==7.12.0
cryptography==44.0.3
DingtalkChatbot==1.5.7
et_xmlfile==2.0.0
execnet==2.1.1
Faker==37.4.0
Flask==3.1.0
h11==0.16.0
h2==4.1.0
hpack==4.1.0
httptools==0.6.4
hyperframe==6.1.0
idna==3.10
iniconfig==2.3.0
itchat==1.3.10
itsdangerous==2.2.0
Jinja2==3.1.6
jsonpath==0.82.2
kaitaistruct==0.10
ldap3==2.9.1
MarkupSafe==3.0.2
mitmproxy==12.1.1
mitmproxy_rs==0.12.6
msgpack==1.1.0
multidict==6.5.1
Naked==0.1.32
openpyxl==3.1.5
packaging==25.0
passlib==1.7.4
pefile==2023.2.7
pluggy==1.6.0
protobuf==6.31.1
psutil==7.1.3
publicsuffix2==2.20191221
py==1.11.0
pyasn1==0.6.1
pyasn1_modules==0.4.2
pycparser==2.22
pydantic==2.11.7
pydantic_core==2.33.2
pyDes==2.0.1
Pygments==2.19.2
pyinstaller==6.15.0
pyinstaller-hooks-contrib==2025.8
pylsqpack==0.3.22
PyMySQL==1.1.1
pyOpenSSL==25.0.0
pyparsing==3.2.3
pyperclip==1.9.0
pypng==0.20220715.0
PyQRCode==1.2.1
pytest==7.4.4
pytest-forked==1.6.0
pytest-xdist==3.5.0
python-dateutil==2.9.0
PyYAML==6.0.2
redis==6.2.0
requests==2.32.4
requests-toolbelt==1.0.0
requests_to_curl==1.1.0
ruamel.yaml==0.18.10
ruamel.yaml.clib==0.2.12
sanic==25.3.0
sanic-routing==23.12.0
service-identity==24.2.0
setuptools==80.9.0
shellescape==3.8.1
six==1.17.0
sortedcontainers==2.4.0
text-unidecode==1.3
toml==0.10.2
tornado==6.5
tracerite==1.1.3
typing-inspection==0.4.1
typing_extensions==4.14.0
tzdata==2025.2
urllib3==2.5.0
urwid==2.6.16
wcwidth==0.2.13
websockets==15.0.1
Werkzeug==3.1.3
wsproto==1.2.0
xlrd==2.0.2
xlutils==2.0.0
xlwings==0.33.15
xlwt==1.3.0
zstandard==0.23.0
EOF

                    echo "安装过滤后的依赖..."
                    pip install -r requirements_filtered.txt

                    # 处理可能的失败
                    echo "处理可能失败的包..."
                    pip install altgraph==0.17.4 || echo "altgraph 安装失败，跳过"
                    pip install html5tagger==1.3.0 || echo "html5tagger 安装失败，跳过"
                    pip install crypto==1.4.1 || echo "crypto 安装失败，跳过"
                '''
            }
        }

        stage('Verify Dependencies') {
            steps {
                sh '''
                    echo "===== 验证依赖 ====="
                    . venv/bin/activate

                    echo "测试关键模块导入..."
                    python -c "
modules = [
    'yaml', 'requests', 'pytest', 'jsonpath', 'openpyxl',
    'pymysql', 'flask', 'allure', 'cryptography', 'redis'
]

print('测试模块导入:')
for module in modules:
    try:
        __import__(module)
        print(f'  ✅ {module}')
    except Exception as e:
        print(f'  ❌ {module}: {str(e)[:50]}...')

print('\\n测试 run.py 所需模块:')
try:
    from utils.other_tools.models import NotificationType
    print('  ✅ utils.other_tools.models 导入成功')
except Exception as e:
    print(f'  ❌ utils.other_tools.models: {e}')
"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "===== 运行测试 ====="
                    . venv/bin/activate

                    echo "当前目录内容:"
                    ls -la

                    echo "运行自动化测试..."
                    python run.py
                '''
            }
        }

        stage('Collect Reports') {
            steps {
                sh '''
                    echo "===== 收集报告 ====="

                    # 创建报告目录
                    mkdir -p reports

                    echo "查找报告文件..."
                    find . -name "*.html" -o -name "*.xml" -o -name "*.json" | grep -E "(report|allure|test)" | head -10
                '''

                // 归档测试报告
                archiveArtifacts artifacts: 'reports/**/*,allure-results/**,test-results/**', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo "===== 构建完成 ====="
            echo "状态: ${currentBuild.result ?: 'SUCCESS'}"
            echo "构建 URL: ${BUILD_URL}"
        }
        success {
            echo "✅ 测试执行成功！"
        }
        failure {
            echo "❌ 测试执行失败！"
            sh '''
                echo "失败信息:"
                . venv/bin/activate 2>/dev/null || true
                echo "已安装的包:"
                pip list | grep -E "(jsonpath|yaml|request|pytest)" || echo "无法获取包列表"
            '''
        }
    }
}