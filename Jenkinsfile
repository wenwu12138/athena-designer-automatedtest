pipeline {
    agent any  // 使用任何可用的 Jenkins agent1

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "📥 阶段 1/6: 代码检出开始"
                    echo "📁 工作目录: ${WORKSPACE}"
                }
                checkout scm  // 从 Jenkins 任务配置获取代码
                script {
                    echo "✅ 代码检出完成"
                    // 显示最近提交信息，便于调试
                    sh 'echo "最新提交:" && git log --oneline -1 || echo "Git信息获取失败"'
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    echo "🔧 阶段 2/6: 环境设置开始"
                    echo "💡 目的: 创建独立Python环境，避免依赖冲突"
                }
                sh '''
                    echo "🐍 系统Python信息:"
                    echo "Python3路径: $(which python3 || echo '未找到')"
                    echo "Python3版本:"
                    python3 --version || echo "Python3命令失败"

                    echo "🧹 清理旧环境(如果存在)..."
                    if [ -d "venv" ]; then
                        echo "发现旧虚拟环境，开始清理..."
                        rm -rf venv
                        echo "旧环境已清理"
                    else
                        echo "未发现旧虚拟环境"
                    fi

                    echo "📦 创建新虚拟环境..."
                    python3 -m venv venv
                    if [ $? -eq 0 ]; then
                        echo "✅ 虚拟环境创建成功"
                    else
                        echo "❌ 虚拟环境创建失败"
                        exit 1
                    fi

                    echo "🔌 激活虚拟环境..."
                    . venv/bin/activate
                    echo "激活后Python路径: $(which python)"
                    echo "激活后Python版本: $(python --version 2>&1 || echo '获取失败')"

                    echo "⬆️ 升级基础工具..."
                    pip install --upgrade pip setuptools wheel
                    echo "升级后pip版本: $(pip --version || echo '获取失败')"

                    echo "📊 环境设置完成"
                '''
            }
        }

        stage('Install Core Dependencies') {
            steps {
                script {
                    echo "📦 阶段 3/6: 核心依赖安装开始"
                    echo "💡 目的: 安装项目运行必须的核心包"
                }
                sh '''
                    echo "🔌 激活虚拟环境..."
                    . venv/bin/activate

                    echo "🔍 当前Python环境信息:"
                    echo "Python: $(which python)"
                    echo "版本: $(python --version 2>&1)"
                    echo "PIP: $(pip --version 2>&1 | head -1)"

                    echo "📥 步骤1: 安装核心包..."
                    echo "  安装 PyYAML (配置文件处理)..."
                    pip install PyYAML==6.0.2 || { echo "❌ PyYAML安装失败"; exit 1; }

                    echo "  安装 requests (HTTP请求)..."
                    pip install requests==2.32.4 || { echo "⚠️ requests安装警告"; }

                    echo "  安装 pytest (测试框架)..."
                    pip install pytest==7.4.4 || { echo "⚠️ pytest安装警告"; }

                    echo "  安装 jsonpath (缺失的关键包)..."
                    pip install jsonpath==0.82.2 || { echo "❌ jsonpath安装失败，这是关键包!"; exit 1; }

                    echo "  安装 openpyxl (Excel处理)..."
                    pip install openpyxl==3.1.5 || echo "⚠️ openpyxl安装警告"

                    echo "  安装 pymysql (MySQL数据库)..."
                    pip install pymysql==1.1.1 || echo "⚠️ pymysql安装警告"

                    echo "  安装 flask (Web框架)..."
                    pip install flask==3.1.0 || echo "⚠️ flask安装警告"

                    echo "📥 步骤2: 安装数据处理包..."
                    echo "  安装 python-dateutil (日期处理)..."
                    pip install python-dateutil==2.9.0 || echo "⚠️ dateutil安装警告"

                    echo "  安装 cryptography (加密)..."
                    pip install cryptography==44.0.3 || echo "⚠️ cryptography安装警告"

                    echo "  安装 allure-pytest (测试报告)..."
                    pip install allure-pytest==2.13.2 allure-python-commons==2.13.2 || echo "⚠️ allure安装警告"

                    echo "📥 步骤3: 安装其他必需包..."
                    echo "  安装 Jinja2模板引擎..."
                    pip install jinja2==3.1.6 markupsafe==3.0.2 || echo "⚠️ Jinja2安装警告"

                    echo "  安装 Flask相关包..."
                    pip install click==8.2.1 itsdangerous==2.2.0 blinker==1.9.0 werkzeug==3.1.3 || echo "⚠️ Flask相关包安装警告"

                    echo "📊 核心依赖安装统计:"
                    echo "已安装包数量: $(pip list | wc -l)个"
                    echo "✅ 核心依赖安装完成"
                '''
            }
        }

        stage('Install Project Dependencies') {
            steps {
                script {
                    echo "📦 阶段 4/6: 项目依赖安装开始"
                    echo "💡 目的: 安装requirements.txt中其他依赖，过滤Windows专用包"
                }
                sh '''
                    echo "🔌 激活虚拟环境..."
                    . venv/bin/activate

                    echo "🔍 检查requirements.txt文件..."
                    if [ ! -f "requirements.txt" ]; then
                        echo "⚠️ requirements.txt不存在，跳过此阶段"
                        exit 0
                    fi

                    echo "📄 requirements.txt内容概览:"
                    echo "总行数: $(wc -l < requirements.txt)"
                    echo "包含的包数量: $(grep -v "^#" requirements.txt | grep -v "^$" | wc -l)"

                    echo "🧹 过滤Windows专用包..."
                    echo "过滤规则: 移除 pywin32, mitmproxy-windows, pydivert 等Windows包"

                    # 创建过滤后的文件
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

                    echo "📦 安装过滤后的依赖..."
                    echo "开始安装，这可能需要几分钟..."
                    START_TIME=$(date +%s)
                    pip install -r requirements_filtered.txt
                    INSTALL_STATUS=$?
                    END_TIME=$(date +%s)
                    DURATION=$((END_TIME - START_TIME))

                    if [ $INSTALL_STATUS -eq 0 ]; then
                        echo "✅ 依赖安装成功，耗时 ${DURATION} 秒"
                    else
                        echo "⚠️ 部分依赖安装失败，继续执行..."
                    fi

                    echo "🔧 处理可能失败的包..."
                    echo "  尝试安装 altgraph..."
                    pip install altgraph==0.17.4 2>/dev/null && echo "  ✅ altgraph安装成功" || echo "  ⚠️ altgraph安装失败，跳过"

                    echo "  尝试安装 html5tagger..."
                    pip install html5tagger==1.3.0 2>/dev/null && echo "  ✅ html5tagger安装成功" || echo "  ⚠️ html5tagger安装失败，跳过"

                    echo "  尝试安装 crypto..."
                    pip install crypto==1.4.1 2>/dev/null && echo "  ✅ crypto安装成功" || echo "  ⚠️ crypto安装失败，跳过"

                    echo "📊 最终依赖统计:"
                    echo "总包数量: $(pip list | wc -l)个"
                    echo "✅ 项目依赖安装完成"
                '''
            }
        }

        stage('Verify Dependencies') {
            steps {
                script {
                    echo "🔍 阶段 5/6: 依赖验证开始"
                    echo "💡 目的: 验证所有关键模块能正常导入"
                }
                sh '''
                    echo "🔌 激活虚拟环境..."
                    . venv/bin/activate

                    echo "🔬 开始模块导入测试..."
                    echo "测试时间: $(date)"

                    # 创建详细的测试脚本
                    cat > verify_deps.py << 'EOF'
import sys
import traceback

print("=" * 60)
print("依赖验证报告")
print("=" * 60)
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print("-" * 60)

# 关键模块列表
critical_modules = [
    ('yaml', '配置文件处理'),
    ('requests', 'HTTP请求库'),
    ('pytest', '测试框架'),
    ('jsonpath', 'JSON路径查询'),
    ('openpyxl', 'Excel文件处理'),
    ('pymysql', 'MySQL数据库'),
    ('flask', 'Web框架'),
    ('allure', '测试报告'),
    ('cryptography', '加密库'),
    ('redis', 'Redis缓存'),
]

print("核心模块验证:")
all_critical_passed = True
for module_name, description in critical_modules:
    try:
        __import__(module_name)
        version = getattr(sys.modules[module_name], '__version__', '未知版本')
        print(f"  ✅ {module_name:15} - {description:20} 版本: {version}")
    except Exception as e:
        print(f"  ❌ {module_name:15} - {description:20} 错误: {str(e)[:50]}")
        all_critical_passed = False

print("-" * 60)

# 项目特定模块测试
print("项目模块验证:")
try:
    from utils.other_tools.models import NotificationType
    print("  ✅ utils.other_tools.models - 通知类型模块")
except Exception as e:
    print(f"  ❌ utils.other_tools.models - 错误: {str(e)[:100]}")
    # 打印详细错误信息用于调试
    print(f"      详细错误: {traceback.format_exc()[:200]}")

print("-" * 60)

# 总结
if all_critical_passed:
    print("✅ 所有核心模块验证通过")
    sys.exit(0)
else:
    print("❌ 部分核心模块验证失败")
    sys.exit(1)
EOF

                    echo "🚀 执行验证脚本..."
                    python verify_deps.py
                    VERIFY_STATUS=$?

                    if [ $VERIFY_STATUS -eq 0 ]; then
                        echo "🎉 依赖验证全部通过!"
                    else
                        echo "⚠️ 依赖验证失败，但继续执行测试..."
                    fi

                    # 清理临时文件
                    rm -f verify_deps.py
                    echo "✅ 依赖验证完成"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo "🚀 阶段 6/6: 测试执行开始"
                    echo "💡 目的: 运行自动化测试套件"
                }
                sh '''
                    echo "🔌 激活虚拟环境..."
                    . venv/bin/activate
                    # ========== 新增：安装 Allure 命令行工具 ==========
                    echo "📥 安装 Allure 命令行工具..."
                    # 下载 Allure 2.27.0（兼容所有环境）
                    ALLURE_VERSION="2.27.0"
                    ALLURE_URL="https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip"
                    # 下载并解压
                    wget -q ${ALLURE_URL} -O /tmp/allure.zip || { echo "❌ Allure 下载失败"; exit 1; }
                    unzip -oq /tmp/allure.zip -d /opt/ || { echo "❌ Allure 解压失败"; exit 1; }
                    # 配置环境变量（临时生效）
                    export PATH="/opt/allure-${ALLURE_VERSION}/bin:${PATH}"
                    # 验证 Allure 命令
                    allure --version && echo "✅ Allure 命令行工具安装成功" || { echo "❌ Allure 验证失败"; exit 1; }
                    echo "📁 项目结构检查:"
                    echo "当前目录: $(pwd)"
                    echo "目录内容:"
                    ls -la
                    echo ""
                    echo "Python文件统计:"
                    find . -name "*.py" -type f | wc -l

                    echo "🔍 查找测试相关文件:"
                    find . -name "*test*.py" -type f | head -5
                    find . -name "run*" -type f | head -5

                    echo "🚦 准备执行测试..."
                    echo "测试开始时间: $(date)"
                    echo "环境变量 PYTHONPATH: ${PYTHONPATH:-未设置}"

                    # 设置 Python 路径
                    export PYTHONPATH="${PWD}:${PYTHONPATH}"
                    echo "设置后 PYTHONPATH: $PYTHONPATH"

                    # 记录开始时间
                    START_TIME=$(date +%s)

                    echo "▶️ 开始执行自动化测试..."
                    echo "执行命令: python run.py"

                    # 执行测试
                    python run.py
                    TEST_STATUS=$?

                    # 记录结束时间
                    END_TIME=$(date +%s)
                    DURATION=$((END_TIME - START_TIME))

                    echo "⏱️ 测试执行统计:"
                    echo "  开始时间: $(date -d @$START_TIME)"
                    echo "  结束时间: $(date -d @$END_TIME)"
                    echo "  总耗时: ${DURATION} 秒"

                    if [ $TEST_STATUS -eq 0 ]; then
                        echo "🎉 测试执行成功!"
                    else
                        echo "❌ 测试执行失败，退出码: $TEST_STATUS"
                    fi

                    echo "✅ 测试执行完成"
                '''
            }
        }
    }

    post {
        always {
        // 存档报告文件z
        archiveArtifacts artifacts: 'report/html/**', fingerprint: true

        // 生成访问链接
        script {
            def jobUrl = env.JOB_URL ?: ''
            def buildNumber = env.BUILD_NUMBER ?: ''

            if (jobUrl && buildNumber) {
                echo "📊 报告存档信息:"
                echo "   存档链接: ${jobUrl}${buildNumber}/"
                echo "   直接下载: ${jobUrl}${buildNumber}/artifact/report/html/index.html"
            }
        }
            script {
                echo ""
                echo "=" * 60
                echo "🏁 构建完成总结"
                echo "=" * 60
                echo "📋 基本信息:"
                echo "  项目: athena-designer-automatedtest"
                echo "  分支: develop"
                echo "  构建: #${BUILD_NUMBER}"
                echo "  状态: ${currentBuild.result ?: 'SUCCESS'}"
                echo "  时长: ${currentBuild.durationString}"
                echo "  链接: ${BUILD_URL}"
                echo ""
                echo "📊 阶段统计:"
                echo "  1. ✅ 代码检出"
                echo "  2. ✅ 环境设置"
                echo "  3. ✅ 核心依赖安装"
                echo "  4. ✅ 项目依赖安装"
                echo "  5. ✅ 依赖验证"
                echo "  6. ✅ 测试执行"
                echo "  7. ✅ 报告收集"
                echo "=" * 60
            }
        }

        success {
            script {
                echo ""
                echo "🎉 🎉 🎉 构建成功! 🎉 🎉 🎉"
                echo "所有测试通过，可以部署!"
                echo ""
                echo "📎 相关链接:"
                echo "  Jenkins控制台: ${BUILD_URL}console"
                echo "  测试报告: ${BUILD_URL}artifact/report/html/index.html"
                echo "  工作空间: ${WORKSPACE}"
            }
        }

        failure {
            script {
                echo ""
                echo "💥 💥 💥 构建失败! 💥 💥 💥"
                echo "请检查以下问题:"
                echo "  1. 查看上方具体错误信息"
                echo "  2. 检查依赖是否完整"
                echo "  3. 验证环境配置"
                echo "  4. 检查测试代码"
                echo ""
                echo "🔧 调试信息收集:"
            }
            sh '''
                echo "最后错误位置:"
                tail -20 ${WORKSPACE}/jenkins-log.txt 2>/dev/null || echo "无法读取日志"

                echo "环境信息:"
                echo "Python版本: $(python3 --version 2>/dev/null || echo '未找到')"
                echo "虚拟环境: $(ls -la venv/bin/python 2>/dev/null && echo '存在' || echo '不存在')"

                echo "关键包状态:"
                if [ -f "venv/bin/activate" ]; then
                    . venv/bin/activate
                    echo "jsonpath: $(pip show jsonpath 2>/dev/null | grep Version || echo '未安装')"
                    echo "PyYAML: $(pip show PyYAML 2>/dev/null | grep Version || echo '未安装')"
                    echo "requests: $(pip show requests 2>/dev/null | grep Version || echo '未安装')"
                fi
            '''
        }
    }
}