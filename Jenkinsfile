pipeline {
    agent any

    // 参数化构建 - 支持所有环境
    parameters {
        choice(
            name: 'TEST_ENVIRONMENT',
            choices: ['阿里Paas区', '华为测试区', '华为正式区', '地端双虎环境'],
            description: '选择测试环境'
        )

        choice(
            name: 'TEST_TYPE',
            choices: ['全部测试', '冒烟测试', '回归测试', '指定模块'],
            description: '测试类型'
        )

        choice(
            name: 'TEST_MODULE',
            choices: ['全部模块', 'Login', 'Application2.0_Businessconstruction', 'Basis', 'DataDriven', 'Tenant_designer', 'Home_page', 'Data_Analysis', 'Maintenance_centre'],
            description: '选择测试模块（当测试类型为"指定模块"时生效）'
        )

        string(
            name: 'SPECIFIC_TEST_FILE',
            defaultValue: '',
            description: '指定具体测试文件（可选，如：test_Login.py）'
        )

        choice(
            name: 'NOTIFICATION_TYPE',
            choices: ['无通知', '邮件通知', '钉钉通知', '企业微信通知', '全部通知'],
            description: '测试结果通知方式'
        )

        booleanParam(
            name: 'GENERATE_EXCEL_REPORT',
            defaultValue: false,
            description: '是否生成Excel错误报告'
        )

        booleanParam(
            name: 'START_LOCAL_REPORT',
            defaultValue: false,
            description: '是否启动本地报告服务'
        )

        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: false,
            description: '是否并行执行测试'
        )

        booleanParam(
            name: 'CLEAN_ALLURE_HISTORY',
            defaultValue: true,
            description: '是否清理Allure历史数据'
        )

        // 新增参数：是否自动安装系统依赖
        booleanParam(
            name: 'INSTALL_SYSTEM_DEPS',
            defaultValue: true,
            description: '是否自动安装系统依赖（Python、pip等）'
        )
    }

    environment {
        // 基本配置
        PROJECT_NAME = 'Athena开发平台'
        TESTER_NAME = '闻武'

        // 报告路径
        ALLURE_RESULTS_DIR = 'report/tmp'
        ALLURE_REPORT_DIR = 'report/html'
        JENKINS_REPORTS_DIR = "jenkins-reports/${env.BUILD_NUMBER}_${params.TEST_ENVIRONMENT}"

        // 根据环境设置标签
        ENV_LABEL = "${params.TEST_ENVIRONMENT}"

        // 邮件通知配置
        EMAIL_RECIPIENTS = '742611390@qq.com, your-team@example.com'
        EMAIL_SUBJECT_PREFIX = '[Athena自动化测试]'

        // 系统依赖配置
        PYTHON_VERSION = '3'
        PIP_MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple'
        ALTERNATIVE_MIRRORS = [
            'https://mirrors.aliyun.com/pypi/simple/',
            'https://pypi.douban.com/simple/',
            'https://pypi.org/simple'
        ]
    }

    stages {
        // 阶段1：环境信息展示
        stage('环境信息') {
            steps {
                echo """
                ╔═══════════════════════════════════════════════════╗
                ║          Athena开发平台 - 接口自动化测试           ║
                ╠═══════════════════════════════════════════════════╣
                ║ 项目名称: ${PROJECT_NAME}                         ║
                ║ 测试人员: ${TESTER_NAME}                          ║
                ║ 测试环境: ${params.TEST_ENVIRONMENT}              ║
                ║ 测试类型: ${params.TEST_TYPE}                     ║
                ║ 构建编号: #${env.BUILD_NUMBER}                    ║
                ║ 执行时间: ${new Date().format('yyyy-MM-dd HH:mm:ss')} ║
                ╚═══════════════════════════════════════════════════╝
                """

                script {
                    // 显示当前目录结构
                    sh '''
                        echo "📁 项目目录结构:"
                        echo "================================="
                        ls -la
                        echo ""
                        echo "🧪 测试用例目录:"
                        echo "================================="
                        ls -la test_case/
                        echo ""
                        echo "📊 数据驱动目录:"
                        echo "================================="
                        ls -la data/
                    '''
                }
            }
        }

        // 阶段2：检查并安装系统依赖
        stage('检查系统依赖') {
            when {
                expression { params.INSTALL_SYSTEM_DEPS.toBoolean() }
            }
            steps {
                echo "🔧 检查系统依赖环境..."

                script {
                    sh '''
                        echo "=== 系统信息 ==="
                        uname -a
                        echo ""

                        echo "=== 检查包管理器 ==="
                        if command -v apt-get &> /dev/null; then
                            echo "✅ 检测到 apt (Debian/Ubuntu)"
                            OS_TYPE="debian"
                        elif command -v yum &> /dev/null; then
                            echo "✅ 检测到 yum (CentOS/RHEL)"
                            OS_TYPE="centos"
                        elif command -v apk &> /dev/null; then
                            echo "✅ 检测到 apk (Alpine)"
                            OS_TYPE="alpine"
                        else
                            echo "⚠️  未知包管理器，尝试继续执行"
                            OS_TYPE="unknown"
                        fi

                        echo ""
                        echo "=== 检查Python环境 ==="
                        # 检查Python
                        if command -v python3 &> /dev/null; then
                            echo "✅ Python3 已安装: $(python3 --version)"
                        elif command -v python &> /dev/null; then
                            echo "✅ Python 已安装: $(python --version)"
                            # 创建python3软链接
                            if ! command -v python3 &> /dev/null; then
                                echo "📌 创建 python3 软链接"
                                ln -s $(which python) /usr/local/bin/python3 2>/dev/null || true
                            fi
                        else
                            echo "❌ Python 未安装，开始安装..."
                            case "$OS_TYPE" in
                                "debian")
                                    apt-get update
                                    apt-get install -y python3 python3-dev python3-pip
                                    ;;
                                "centos")
                                    yum install -y python3 python3-devel python3-pip
                                    ;;
                                "alpine")
                                    apk add python3 py3-pip python3-dev
                                    ;;
                                *)
                                    echo "⚠️  未知系统，尝试下载Python..."
                                    curl -O https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tar.xz
                                    tar -xf Python-3.9.18.tar.xz
                                    cd Python-3.9.18
                                    ./configure --enable-optimizations
                                    make -j$(nproc)
                                    make altinstall
                                    cd ..
                                    ;;
                            esac
                            echo "✅ Python 安装完成: $(python3 --version)"
                        fi

                        echo ""
                        echo "=== 检查pip ==="
                        # 检查pip
                        if command -v pip3 &> /dev/null; then
                            echo "✅ pip3 已安装: $(pip3 --version)"
                        elif command -v pip &> /dev/null; then
                            echo "✅ pip 已安装: $(pip --version)"
                            # 创建pip3软链接
                            if ! command -v pip3 &> /dev/null; then
                                echo "📌 创建 pip3 软链接"
                                ln -s $(which pip) /usr/local/bin/pip3 2>/dev/null || true
                            fi
                        else
                            echo "❌ pip 未安装，开始安装..."
                            # 使用get-pip.py安装
                            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                            python3 get-pip.py --no-warn-script-location
                            rm -f get-pip.py

                            # 验证安装
                            if command -v pip3 &> /dev/null; then
                                echo "✅ pip3 安装成功: $(pip3 --version)"
                            else
                                # 添加到PATH
                                export PATH="$PATH:/usr/local/bin"
                                echo "✅ pip 安装完成"
                            fi
                        fi

                        echo ""
                        echo "=== 检查其他系统依赖 ==="
                        # 安装编译依赖（某些Python包需要）
                        case "$OS_TYPE" in
                            "debian")
                                echo "安装Debian编译依赖..."
                                apt-get install -y \
                                    build-essential \
                                    libssl-dev \
                                    libffi-dev \
                                    python3-dev \
                                    gcc \
                                    g++ \
                                    make \
                                    curl \
                                    wget \
                                    git
                                ;;
                            "centos")
                                echo "安装CentOS编译依赖..."
                                yum install -y \
                                    gcc \
                                    gcc-c++ \
                                    make \
                                    openssl-devel \
                                    libffi-devel \
                                    python3-devel \
                                    curl \
                                    wget \
                                    git
                                ;;
                            "alpine")
                                echo "安装Alpine编译依赖..."
                                apk add \
                                    build-base \
                                    libffi-dev \
                                    openssl-dev \
                                    python3-dev \
                                    curl \
                                    wget \
                                    git
                                ;;
                        esac

                        echo ""
                        echo "=== 环境验证 ==="
                        echo "Python: $(python3 --version 2>/dev/null || echo '未找到')"
                        echo "pip: $(pip3 --version 2>/dev/null || pip --version 2>/dev/null || echo '未找到')"
                        echo "Python路径: $(which python3 2>/dev/null || which python 2>/dev/null || echo '未找到')"
                        echo "pip路径: $(which pip3 2>/dev/null || which pip 2>/dev/null || echo '未找到')"
                    '''
                }
            }
        }

        // 阶段3：拉取代码
        stage('拉取代码') {
            steps {
                echo "📥 拉取最新代码..."

                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/develop']],
                    extensions: [],
                    userRemoteConfigs: [[
                        url: 'https://github.com/wenwu12138/athena-designer-automatedtest.git',
                        credentialsId: ''  // 如果是私有仓库需要配置
                    ]]
                ])

                sh '''
                    echo "✅ 代码拉取完成"
                    echo "当前分支: $(git branch --show-current)"
                    echo "最新提交: $(git log -1 --oneline --pretty=format:"%h - %s [%an]")"
                    echo "提交时间: $(git log -1 --pretty=format:"%cd" --date=format:"%Y-%m-%d %H:%M:%S")"
                '''
            }
        }

        // 阶段4：安装Python依赖
        stage('安装Python依赖') {
            steps {
                echo "📦 安装Python依赖包..."

                script {
                    // 首先尝试使用国内镜像源
                    def mirrors = [
                        'https://pypi.tuna.tsinghua.edu.cn/simple',
                        'https://mirrors.aliyun.com/pypi/simple/',
                        'https://pypi.douban.com/simple/',
                        'https://mirrors.cloud.tencent.com/pypi/simple'
                    ]

                    def installed = false

                    for (mirror in mirrors) {
                        try {
                            echo "尝试使用镜像源: ${mirror}"
                            sh """
                                # 升级pip
                                python3 -m pip install --upgrade pip -i ${mirror} --trusted-host \$(echo ${mirror} | sed 's|https://||' | cut -d'/' -f1)

                                # 安装依赖
                                if [ -f "requirements.txt" ]; then
                                    echo "使用requirements.txt安装依赖"
                                    python3 -m pip install -r requirements.txt -i ${mirror} --trusted-host \$(echo ${mirror} | sed 's|https://||' | cut -d'/' -f1)
                                else
                                    echo "⚠️ requirements.txt不存在，安装基础包"
                                    python3 -m pip install pytest allure-pytest pytest-html requests pyyaml openpyxl pymysql redis -i ${mirror} --trusted-host \$(echo ${mirror} | sed 's|https://||' | cut -d'/' -f1)
                                fi
                            """
                            installed = true
                            echo "✅ 使用镜像源 ${mirror} 安装成功"
                            break
                        } catch (Exception e) {
                            echo "⚠️ 镜像源 ${mirror} 失败: ${e.getMessage()}"
                            continue
                        }
                    }

                    // 如果所有镜像都失败，尝试使用官方源
                    if (!installed) {
                        echo "⚠️ 所有镜像源失败，尝试使用官方源（可能较慢）"
                        sh '''
                            # 降级pip以兼容旧版本
                            python3 -m pip install --upgrade pip

                            if [ -f "requirements.txt" ]; then
                                echo "使用官方源安装依赖..."
                                python3 -m pip install -r requirements.txt --retries 3 --timeout 60
                            else
                                echo "安装基础包..."
                                python3 -m pip install pytest allure-pytest pytest-html requests pyyaml openpyxl pymysql redis
                            fi
                        '''
                    }

                    // 验证安装的关键包
                    sh '''
                        echo ""
                        echo "✅ 依赖安装完成，验证关键包:"
                        python3 -c "
import sys
packages = ['pytest', 'requests', 'yaml', 'allure', 'openpyxl', 'pymysql', 'redis']
for pkg in packages:
    try:
        if pkg == 'yaml':
            import yaml
            print(f'✅ PyYAML: 已安装')
        elif pkg == 'allure':
            import allure
            print(f'✅ allure-pytest: {allure.__version__}')
        else:
            module = __import__(pkg)
            version = getattr(module, '__version__', '已安装')
            print(f'✅ {pkg}: {version}')
    except ImportError as e:
        print(f'❌ {pkg}: 未安装 - {e}')
        "

                        echo ""
                        echo "已安装的Python包:"
                        python3 -m pip list --format=columns | head -20
                    '''
                }
            }
        }

        // 阶段5：安装Allure命令行工具
        stage('安装Allure工具') {
            steps {
                echo "📊 安装Allure报告工具..."

                script {
                    sh '''
                        # 检查是否已安装Allure
                        if command -v allure &> /dev/null; then
                            echo "✅ Allure已安装: $(allure --version)"
                        else
                            echo "📥 下载并安装Allure..."

                            # 根据系统架构选择
                            ARCH=$(uname -m)
                            OS=$(uname -s)

                            if [ "$ARCH" = "x86_64" ]; then
                                ALLURE_VERSION="2.24.0"
                                if [ "$OS" = "Linux" ]; then
                                    echo "下载Linux版本..."
                                    wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz
                                    tar -xzf allure-${ALLURE_VERSION}.tgz
                                    sudo mv allure-${ALLURE_VERSION} /opt/allure
                                    sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
                                    rm -f allure-${ALLURE_VERSION}.tgz
                                elif [ "$OS" = "Darwin" ]; then
                                    echo "下载macOS版本..."
                                    wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
                                    unzip -q allure-${ALLURE_VERSION}.zip
                                    sudo mv allure-${ALLURE_VERSION} /opt/allure
                                    sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
                                    rm -f allure-${ALLURE_VERSION}.zip
                                fi
                            else
                                echo "⚠️ 不支持的架构: $ARCH，跳过Allure安装"
                                echo "提示: 手动安装Allure或使用其他报告格式"
                            fi

                            # 验证安装
                            if command -v allure &> /dev/null; then
                                echo "✅ Allure安装成功: $(allure --version)"
                            else
                                echo "⚠️ Allure安装失败，HTML报告可能无法生成"
                            fi
                        fi
                    '''
                }
            }
        }

        // 阶段6：切换测试环境
        stage('切换测试环境') {
            steps {
                echo "🔄 切换到测试环境: ${params.TEST_ENVIRONMENT}"

                script {
                    // 使用环境管理器切换环境
                    sh """
                        echo "使用环境管理器切换环境..."
                        if [ -f "env_config_manager.py" ]; then
                            python3 env_config_manager.py switch "${params.TEST_ENVIRONMENT}"
                        else
                            echo "⚠️  env_config_manager.py不存在，手动更新配置"
                            echo "创建临时脚本切换环境..."

                            # 创建临时切换脚本
                            cat > switch_env_temp.py << 'EOF'
import yaml
import sys

env_name = sys.argv[1]
env_configs = {
    "阿里Paas区": {
        "athena_designer_host": "https://adp-paas.apps.digiwincloud.com.cn",
        "athena_deployer_host": "https://aadc-paas.apps.digiwincloud.com.cn",
        "athena_tenant_deployer_host": "https://atdp-paas.apps.digiwincloud.com.cn",
        "iam_host": "https://iam-test.digiwincloud.com.cn"
    },
    "华为测试区": {
        "athena_designer_host": "https://adp-test.apps.digiwincloud.com.cn",
        "athena_deployer_host": "https://aadc-test.apps.digiwincloud.com.cn",
        "athena_tenant_deployer_host": "https://atdp-test.apps.digiwincloud.com.cn",
        "iam_host": "https://iam-test.digiwincloud.com.cn"
    },
    "华为正式区": {
        "athena_designer_host": "https://adp.apps.digiwincloud.com.cn",
        "athena_deployer_host": "https://aadc.apps.digiwincloud.com.cn",
        "athena_tenant_deployer_host": "https://atdp.apps.digiwincloud.com.cn",
        "iam_host": "https://iam.digiwincloud.com.cn"
    },
    "地端双虎环境": {
        "athena_designer_host": "https://adp.twintigers.com",
        "athena_deployer_host": "https://aadc.twintigers.com",
        "athena_tenant_deployer_host": "https://atdp.twintigers.com",
        "iam_host": "http://iam.twintigers.com"
    }
}

if env_name not in env_configs:
    print(f"❌ 环境 '{env_name}' 不存在")
    sys.exit(1)

with open("common/config.yaml", "r") as f:
    config = yaml.safe_load(f)

config.update(env_configs[env_name])
config["env"] = env_name

with open("common/config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

print(f"✅ 已切换到环境: {env_name}")
print(f"   设计器: {env_configs[env_name]['athena_designer_host']}")
EOF

                            python3 switch_env_temp.py "${params.TEST_ENVIRONMENT}"
                            rm -f switch_env_temp.py
                        fi
                    """

                    // 显示当前配置
                    sh '''
                        echo "当前环境配置:"
                        echo "================================="
                        if [ -f "common/config.yaml" ]; then
                            grep -E "env:|athena_.*_host:|iam_host:" common/config.yaml || echo "无法读取配置"
                        else
                            echo "❌ common/config.yaml不存在"
                        fi
                    '''
                }
            }
        }

        // 阶段7：更新测试配置
        stage('更新测试配置') {
            steps {
                echo "⚙️ 更新测试配置..."

                script {
                    // 更新config.py中的通知配置
                    sh """
                        echo "更新通知配置..."
                        if [ -f "config.py" ]; then
                            # 备份原配置
                            cp -f config.py config.py.backup

                            # 处理通知类型映射
                            NOTIFICATION_VALUE="0"
                            case "${params.NOTIFICATION_TYPE}" in
                                "无通知")
                                    NOTIFICATION_VALUE="0"
                                    ;;
                                "邮件通知")
                                    NOTIFICATION_VALUE="3"
                                    ;;
                                "钉钉通知")
                                    NOTIFICATION_VALUE="1"
                                    ;;
                                "企业微信通知")
                                    NOTIFICATION_VALUE="2"
                                    ;;
                                "全部通知")
                                    NOTIFICATION_VALUE="1,2,3"
                                    ;;
                            esac

                            # 使用sed更新配置
                            sed -i "s/notification_type =.*/notification_type = \\"${NOTIFICATION_VALUE}\\"/g" config.py
                            sed -i "s/excel_report =.*/excel_report = ${params.GENERATE_EXCEL_REPORT}/g" config.py

                            echo "✅ 通知配置已更新"
                            echo "   通知类型: ${params.NOTIFICATION_TYPE} -> ${NOTIFICATION_VALUE}"
                            echo "   Excel报告: ${params.GENERATE_EXCEL_REPORT}"
                        else
                            echo "⚠️  config.py不存在，跳过配置更新"
                        fi
                    """
                }
            }
        }

        // 阶段8：执行测试
        stage('执行接口测试') {
            steps {
                echo "🚀 开始执行接口测试..."

                script {
                    // 创建报告目录
                    sh """
                        echo "创建报告目录..."
                        mkdir -p ${ALLURE_RESULTS_DIR}
                        mkdir -p ${ALLURE_REPORT_DIR}
                        mkdir -p ${JENKINS_REPORTS_DIR}

                        if ${params.CLEAN_ALLURE_HISTORY}; then
                            echo "清理Allure历史数据..."
                            rm -rf ${ALLURE_RESULTS_DIR}/* 2>/dev/null || true
                        fi
                    """

                    // 设置测试执行超时（30分钟）
                    timeout(time: 30, unit: 'MINUTES') {
                        sh """
                            echo "开始执行测试..."
                            echo "环境: ${params.TEST_ENVIRONMENT}"
                            echo "测试类型: ${params.TEST_TYPE}"
                            echo "测试模块: ${params.TEST_MODULE}"
                            echo "并行执行: ${params.PARALLEL_EXECUTION}"

                            # 设置环境变量
                            export JENKINS_BUILD="true"
                            export BUILD_NUMBER="${env.BUILD_NUMBER}"
                            export JOB_NAME="${env.JOB_NAME}"
                            export BUILD_URL="${env.BUILD_URL}"
                            export TEST_ENVIRONMENT="${params.TEST_ENVIRONMENT}"

                            # 执行run.py（你的主测试脚本）
                            echo "执行命令: python3 run.py"
                            python3 run.py

                            # 记录退出码
                            EXIT_CODE=\$?
                            echo \$EXIT_CODE > test_exit_code.txt
                            echo "测试退出码: \$EXIT_CODE"
                        """
                    }

                    // 检查测试结果
                    def exitCode = sh(script: 'cat test_exit_code.txt 2>/dev/null || echo "0"', returnStdout: true).trim().toInteger()

                    if (exitCode != 0) {
                        echo "⚠️ 测试执行异常，退出码: ${exitCode}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        // 阶段9：处理测试报告
        stage('处理测试报告') {
            steps {
                echo "📊 处理测试报告..."

                script {
                    // 生成Allure报告
                    sh """
                        echo "生成Allure报告..."
                        if command -v allure &> /dev/null && [ -d "${ALLURE_RESULTS_DIR}" ]; then
                            allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_REPORT_DIR} --clean
                            echo "✅ Allure报告生成完成"

                            # 复制Allure报告到Jenkins目录
                            cp -r ${ALLURE_REPORT_DIR}/* ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        else
                            echo "⚠️  跳过Allure报告生成"
                            echo "生成简易HTML报告..."
                            # 如果没有Allure，生成简单的pytest-html报告
                            if command -v pytest &> /dev/null; then
                                pytest --html=${JENKINS_REPORTS_DIR}/pytest_report.html --self-contained-html || true
                            fi
                        fi
                    """

                    // 复制其他报告文件
                    sh """
                        echo "收集报告文件..."
                        # 复制pytest-html报告
                        find . -name "*.html" -type f -not -path "./venv/*" -not -path "./.venv/*" | head -5 | while read file; do
                            cp "\$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        done

                        # 复制日志文件
                        find . -name "*.log" -type f | head -3 | while read file; do
                            cp "\$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        done

                        # 生成测试摘要
                        cat > ${JENKINS_REPORTS_DIR}/test_summary.md << EOF
# Athena开发平台 - 接口自动化测试报告

## 测试信息
- **项目名称**: ${PROJECT_NAME}
- **测试人员**: ${TESTER_NAME}
- **测试环境**: ${params.TEST_ENVIRONMENT}
- **测试类型**: ${params.TEST_TYPE}
- **测试模块**: ${params.TEST_MODULE}
- **构建编号**: #${env.BUILD_NUMBER}
- **执行时间**: \$(date '+%Y-%m-%d %H:%M:%S')
- **测试时长**: ${currentBuild.durationString}
- **Python版本**: \$(python3 --version 2>/dev/null || echo 'N/A')
- **pip版本**: \$(pip3 --version 2>/dev/null || echo 'N/A')

## 环境配置
- **设计器地址**: \$(grep "athena_designer_host:" common/config.yaml | cut -d' ' -f2)
- **部署器地址**: \$(grep "athena_deployer_host:" common/config.yaml | cut -d' ' -f2)
- **租户部署器**: \$(grep "athena_tenant_deployer_host:" common/config.yaml | cut -d' ' -f2)
- **IAM地址**: \$(grep "iam_host:" common/config.yaml | cut -d' ' -f2)

## 测试结果
- **退出码**: \$(cat test_exit_code.txt 2>/dev/null || echo "N/A")
- **报告目录**: ${JENKINS_REPORTS_DIR}
- **详细日志**: 查看Jenkins控制台输出

## 系统信息
\$(uname -a)

## 已安装的Python包
\$(python3 -m pip list --format=freeze 2>/dev/null | head -20 | sed 's/^/- /')

EOF

                        echo "✅ 报告处理完成"
                        echo "报告目录: ${JENKINS_REPORTS_DIR}"
                        ls -la ${JENKINS_REPORTS_DIR}/
                    """

                    // 发布HTML报告到Jenkins
                    script {
                        def htmlFiles = findFiles(glob: "${JENKINS_REPORTS_DIR}/*.html")
                        if (!htmlFiles.isEmpty()) {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: JENKINS_REPORTS_DIR,
                                reportFiles: htmlFiles[0].name,
                                reportName: "Athena测试报告-${params.TEST_ENVIRONMENT}"
                            ])
                        } else if (fileExists("${ALLURE_REPORT_DIR}/index.html")) {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: ALLURE_REPORT_DIR,
                                reportFiles: 'index.html',
                                reportName: "Athena测试报告-${params.TEST_ENVIRONMENT}"
                            ])
                        }
                    }

                    // 归档报告文件
                    archiveArtifacts artifacts: "${JENKINS_REPORTS_DIR}/**/*", fingerprint: true
                    archiveArtifacts artifacts: "${ALLURE_REPORT_DIR}/**/*", fingerprint: true
                }
            }
        }
    }

    post {
        always {
            echo "🧹 清理工作..."

            script {
                sh """
                    # 恢复配置文件
                    if [ -f "common/config.yaml.backup" ]; then
                        mv -f common/config.yaml.backup common/config.yaml
                        echo "✅ 恢复common/config.yaml"
                    fi
                    if [ -f "config.py.backup" ]; then
                        mv -f config.py.backup config.py
                        echo "✅ 恢复config.py"
                    fi

                    # 清理Python缓存
                    echo "清理Python缓存..."
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

                    echo ""
                    echo "📋 测试执行完成"
                    echo "================================="
                """
            }
        }
    }
}