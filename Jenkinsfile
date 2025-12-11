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

        // 新增参数：Python版本选择
        choice(
            name: 'PYTHON_VERSION',
            choices: ['python3', 'python3.9', 'python3.8', 'python3.7', 'python'],
            defaultValue: 'python3',
            description: '选择Python版本'
        )

        // 新增参数：是否使用虚拟环境
        booleanParam(
            name: 'USE_VENV',
            defaultValue: true,
            description: '是否使用Python虚拟环境'
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
        PYTHON_CMD = "${params.PYTHON_VERSION}"
        VENV_DIR = 'venv'
        PIP_MIRROR = 'https://pypi.tuna.tsinghua.edu.cn/simple'
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
                ║ Python版本: ${params.PYTHON_VERSION}              ║
                ║ 使用虚拟环境: ${params.USE_VENV}                  ║
                ╚═══════════════════════════════════════════════════╝
                """

                script {
                    // 显示系统信息
                    sh '''
                        echo "🖥️ 系统信息:"
                        echo "================================="
                        uname -a
                        echo ""
                        echo "💾 磁盘空间:"
                        df -h .
                        echo ""
                        echo "🧠 内存信息:"
                        free -h || true
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
                echo "🔧 检查并安装系统依赖..."

                script {
                    sh '''
                        set +e  # 允许命令失败，继续执行

                        echo "=== 检测操作系统和包管理器 ==="
                        # 更可靠的OS检测
                        if [ -f /etc/os-release ]; then
                            . /etc/os-release
                            OS_NAME="$ID"
                            OS_VERSION="$VERSION_ID"
                            echo "✅ 检测到系统: $OS_NAME $OS_VERSION"
                        elif [ -f /etc/redhat-release ]; then
                            OS_NAME="centos"
                            OS_VERSION=$(cat /etc/redhat-release | sed 's/.*release //' | sed 's/ .*//')
                            echo "✅ 检测到系统: CentOS $OS_VERSION"
                        elif [ -f /etc/alpine-release ]; then
                            OS_NAME="alpine"
                            OS_VERSION=$(cat /etc/alpine-release)
                            echo "✅ 检测到系统: Alpine Linux $OS_VERSION"
                        else
                            OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')
                            OS_VERSION=$(uname -r)
                            echo "⚠️  无法识别的系统: $OS_NAME $OS_VERSION"
                        fi

                        # 检测包管理器
                        if command -v apt-get > /dev/null 2>&1; then
                            PKG_MANAGER="apt"
                            UPDATE_CMD="apt-get update -y"
                            INSTALL_CMD="apt-get install -y"
                            echo "✅ 使用apt包管理器"
                        elif command -v yum > /dev/null 2>&1; then
                            PKG_MANAGER="yum"
                            UPDATE_CMD="yum makecache fast"
                            INSTALL_CMD="yum install -y"
                            echo "✅ 使用yum包管理器"
                        elif command -v apk > /dev/null 2>&1; then
                            PKG_MANAGER="apk"
                            UPDATE_CMD="apk update"
                            INSTALL_CMD="apk add"
                            echo "✅ 使用apk包管理器"
                        elif command -v dnf > /dev/null 2>&1; then
                            PKG_MANAGER="dnf"
                            UPDATE_CMD="dnf makecache"
                            INSTALL_CMD="dnf install -y"
                            echo "✅ 使用dnf包管理器"
                        else
                            echo "⚠️  未检测到标准包管理器，尝试继续"
                            PKG_MANAGER="unknown"
                        fi

                        echo ""
                        echo "=== 检查Python环境 ==="

                        # 查找Python命令
                        PYTHON_CMD=""
                        for cmd in "${params.PYTHON_VERSION}" python3 python3.9 python3.8 python3.7 python; do
                            if command -v "$cmd" > /dev/null 2>&1; then
                                PYTHON_CMD="$cmd"
                                echo "✅ 找到Python: $($cmd --version 2>&1)"
                                break
                            fi
                        done

                        if [ -z "$PYTHON_CMD" ]; then
                            echo "❌ Python未安装，开始安装..."

                            case "$PKG_MANAGER" in
                                "apt")
                                    $UPDATE_CMD
                                    $INSTALL_CMD python3 python3-pip python3-dev python3-venv
                                    ;;
                                "yum"|"dnf")
                                    $UPDATE_CMD
                                    $INSTALL_CMD python3 python3-pip python3-devel
                                    ;;
                                "apk")
                                    $UPDATE_CMD
                                    $INSTALL_CMD python3 py3-pip python3-dev
                                    ;;
                                *)
                                    echo "⚠️  无法自动安装Python，请手动安装"
                                    exit 1
                                    ;;
                            esac

                            # 重新查找Python
                            for cmd in python3 python; do
                                if command -v "$cmd" > /dev/null 2>&1; then
                                    PYTHON_CMD="$cmd"
                                    break
                                fi
                            done

                            if [ -z "$PYTHON_CMD" ]; then
                                echo "❌ Python安装失败"
                                exit 1
                            fi
                        fi

                        echo ""
                        echo "=== 检查pip ==="

                        # 尝试不同的pip命令
                        PIP_CMD=""
                        for cmd in pip3 pip; do
                            if command -v "$cmd" > /dev/null 2>&1; then
                                PIP_CMD="$cmd"
                                echo "✅ 找到pip: $($cmd --version 2>&1)"
                                break
                            fi
                        done

                        if [ -z "$PIP_CMD" ]; then
                            echo "❌ pip未安装，尝试安装..."

                            # 使用ensurepip
                            if $PYTHON_CMD -m ensurepip --help > /dev/null 2>&1; then
                                $PYTHON_CMD -m ensurepip --upgrade
                            else
                                # 下载get-pip.py
                                curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                                $PYTHON_CMD get-pip.py --no-warn-script-location
                                rm -f get-pip.py
                            fi

                            # 重新查找pip
                            for cmd in pip3 pip; do
                                if command -v "$cmd" > /dev/null 2>&1; then
                                    PIP_CMD="$cmd"
                                    break
                                fi
                            done
                        fi

                        if [ -z "$PIP_CMD" ]; then
                            echo "⚠️  pip安装失败，尝试直接使用python -m pip"
                            PIP_CMD="$PYTHON_CMD -m pip"
                        fi

                        echo ""
                        echo "=== 安装编译依赖 ==="

                        case "$PKG_MANAGER" in
                            "apt")
                                $INSTALL_CMD build-essential libssl-dev libffi-dev \
                                    python3-dev gcc g++ make curl wget git
                                ;;
                            "yum"|"dnf")
                                $INSTALL_CMD gcc gcc-c++ make openssl-devel \
                                    libffi-devel python3-devel curl wget git
                                ;;
                            "apk")
                                $INSTALL_CMD build-base libffi-dev openssl-dev \
                                    python3-dev curl wget git
                                ;;
                        esac

                        echo ""
                        echo "=== 环境验证 ==="
                        echo "Python命令: $PYTHON_CMD"
                        echo "Python版本: $($PYTHON_CMD --version 2>&1)"
                        echo "Python路径: $(which $PYTHON_CMD 2>/dev/null || echo '未找到')"

                        if [ "$PIP_CMD" != "$PYTHON_CMD -m pip" ]; then
                            echo "pip命令: $PIP_CMD"
                            echo "pip版本: $($PIP_CMD --version 2>&1)"
                            echo "pip路径: $(which $(echo $PIP_CMD | cut -d' ' -f1) 2>/dev/null || echo '未找到')"
                        else
                            echo "使用: $PYTHON_CMD -m pip"
                        fi

                        set -e  # 恢复错误检查
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
                    echo "当前分支: $(git branch --show-current 2>/dev/null || echo '无法获取')"
                    echo "最新提交: $(git log -1 --oneline --pretty=format:"%h - %s [%an]" 2>/dev/null || echo '无法获取')"
                '''
            }
        }

        // 阶段4：创建Python虚拟环境
        stage('设置Python环境') {
            when {
                expression { params.USE_VENV.toBoolean() }
            }
            steps {
                echo "🐍 创建Python虚拟环境..."

                script {
                    sh '''
                        echo "检查Python虚拟环境..."

                        # 查找Python命令
                        PYTHON_CMD=""
                        for cmd in "${params.PYTHON_VERSION}" python3 python; do
                            if command -v "$cmd" > /dev/null 2>&1; then
                                PYTHON_CMD="$cmd"
                                break
                            fi
                        done

                        if [ -z "$PYTHON_CMD" ]; then
                            echo "❌ 未找到Python命令"
                            exit 1
                        fi

                        echo "使用Python: $($PYTHON_CMD --version 2>&1)"

                        # 检查是否支持venv
                        if $PYTHON_CMD -c "import venv" 2>/dev/null; then
                            echo "✅ Python支持venv模块"
                        else
                            echo "⚠️  Python不支持venv，尝试安装python3-venv"

                            # 尝试安装venv
                            if command -v apt-get > /dev/null 2>&1; then
                                apt-get update && apt-get install -y python3-venv || true
                            elif command -v yum > /dev/null 2>&1; then
                                yum install -y python3-virtualenv || true
                            fi
                        fi

                        # 创建虚拟环境
                        if [ ! -d "${VENV_DIR}" ]; then
                            echo "创建虚拟环境..."
                            $PYTHON_CMD -m venv "${VENV_DIR}" || {
                                echo "⚠️  venv创建失败，尝试virtualenv"
                                if command -v virtualenv > /dev/null 2>&1; then
                                    virtualenv "${VENV_DIR}" -p $PYTHON_CMD
                                else
                                    echo "❌ 无法创建虚拟环境"
                                    exit 1
                                fi
                            }
                        fi

                        # 激活虚拟环境
                        if [ -f "${VENV_DIR}/bin/activate" ]; then
                            echo "✅ 虚拟环境创建成功"
                            echo "虚拟环境路径: $(pwd)/${VENV_DIR}"

                            # 检查虚拟环境中的Python
                            if [ -f "${VENV_DIR}/bin/python" ]; then
                                echo "虚拟环境Python: $(${VENV_DIR}/bin/python --version 2>&1)"
                            fi
                        else
                            echo "⚠️  虚拟环境文件不存在，跳过虚拟环境使用"
                        fi
                    '''
                }
            }
        }

        // 阶段5：安装Python依赖
        stage('安装Python依赖') {
            steps {
                echo "📦 安装Python依赖包..."

                script {
                    sh '''
                        set +e  # 允许命令失败

                        # 确定使用的pip命令
                        if [ "${params.USE_VENV}" = "true" ] && [ -f "${VENV_DIR}/bin/pip" ]; then
                            PIP_CMD="${VENV_DIR}/bin/pip"
                            PYTHON_CMD="${VENV_DIR}/bin/python"
                            echo "✅ 使用虚拟环境中的pip"
                        else
                            # 查找系统pip
                            PIP_CMD=""
                            for cmd in pip3 pip; do
                                if command -v "$cmd" > /dev/null 2>&1; then
                                    PIP_CMD="$cmd"
                                    break
                                fi
                            done

                            if [ -z "$PIP_CMD" ]; then
                                PIP_CMD="python -m pip"
                            fi
                        fi

                        echo "使用的pip命令: $PIP_CMD"
                        echo "pip版本: $($PIP_CMD --version 2>&1 || echo '无法获取版本')"

                        echo ""
                        echo "=== 配置pip镜像源 ==="

                        # 国内镜像源列表（按优先级排序）
                        MIRRORS=(
                            "https://pypi.tuna.tsinghua.edu.cn/simple"
                            "https://mirrors.aliyun.com/pypi/simple/"
                            "https://pypi.douban.com/simple/"
                            "https://mirrors.cloud.tencent.com/pypi/simple"
                        )

                        # 尝试升级pip（使用默认源）
                        echo "升级pip..."
                        $PIP_CMD install --upgrade pip --retries 3 --timeout 30 || \
                            echo "⚠️  pip升级失败，继续执行"

                        # 尝试不同的镜像源安装依赖
                        INSTALLED=false
                        for MIRROR in "${MIRRORS[@]}"; do
                            echo ""
                            echo "尝试使用镜像源: $MIRROR"

                            # 提取域名用于--trusted-host
                            DOMAIN=$(echo $MIRROR | sed 's|https://||' | cut -d'/' -f1)

                            if [ -f "requirements.txt" ]; then
                                echo "从requirements.txt安装依赖..."
                                if $PIP_CMD install -r requirements.txt \
                                    -i "$MIRROR" \
                                    --trusted-host "$DOMAIN" \
                                    --retries 3 \
                                    --timeout 60; then
                                    INSTALLED=true
                                    echo "✅ 依赖安装成功"
                                    break
                                else
                                    echo "⚠️  镜像源 $MIRROR 安装失败"
                                fi
                            else
                                echo "requirements.txt不存在，安装基础包..."
                                if $PIP_CMD install pytest allure-pytest pytest-html requests pyyaml openpyxl pymysql redis \
                                    -i "$MIRROR" \
                                    --trusted-host "$DOMAIN" \
                                    --retries 3 \
                                    --timeout 60; then
                                    INSTALLED=true
                                    echo "✅ 基础包安装成功"
                                    break
                                else
                                    echo "⚠️  镜像源 $MIRROR 安装失败"
                                fi
                            fi
                        done

                        # 如果所有镜像源都失败，尝试官方源
                        if [ "$INSTALLED" = "false" ]; then
                            echo ""
                            echo "⚠️ 所有镜像源失败，尝试官方源..."

                            if [ -f "requirements.txt" ]; then
                                $PIP_CMD install -r requirements.txt --retries 3 --timeout 120 || {
                                    echo "❌ 官方源安装失败"
                                    echo "尝试离线安装或检查网络连接"
                                }
                            else
                                $PIP_CMD install pytest allure-pytest pytest-html requests pyyaml openpyxl pymysql redis --retries 3 --timeout 120 || {
                                    echo "❌ 基础包安装失败"
                                }
                            fi
                        fi

                        echo ""
                        echo "=== 验证安装 ==="

                        # 检查关键包
                        $PYTHON_CMD -c "
import sys
print('Python版本:', sys.version)
print('')
packages = [
    ('pytest', 'pytest'),
    ('requests', 'requests'),
    ('yaml', 'yaml'),
    ('allure', 'allure'),
    ('openpyxl', 'openpyxl'),
    ('pymysql', 'pymysql'),
    ('redis', 'redis')
]

for import_name, display_name in packages:
    try:
        if import_name == 'yaml':
            import yaml
            version = getattr(yaml, '__version__', '已安装')
        else:
            module = __import__(import_name)
            version = getattr(module, '__version__', '已安装')
        print(f'✅ {display_name}: {version}')
    except ImportError as e:
        print(f'❌ {display_name}: 未安装')
                        " || echo "Python包检查失败"

                        echo ""
                        echo "已安装的包:"
                        $PIP_CMD list --format=columns 2>/dev/null | head -15 || true

                        set -e  # 恢复错误检查
                    '''
                }
            }
        }

        // 阶段6：安装Allure命令行工具
        stage('安装Allure工具') {
            steps {
                echo "📊 安装Allure报告工具..."

                script {
                    sh '''
                        set +e

                        # 检查是否已安装Allure
                        if command -v allure > /dev/null 2>&1; then
                            echo "✅ Allure已安装: $(allure --version 2>&1 | head -1)"
                            exit 0
                        fi

                        echo "📥 下载并安装Allure..."

                        # 检测系统架构
                        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
                        ARCH=$(uname -m)

                        echo "系统: $OS, 架构: $ARCH"

                        # 选择适合的版本
                        ALLURE_VERSION="2.24.0"

                        # 检查是否已经下载
                        if [ -d "/opt/allure" ] && [ -f "/opt/allure/bin/allure" ]; then
                            echo "✅ Allure已存在于/opt/allure"
                            sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure 2>/dev/null || true
                            exit 0
                        fi

                        # 根据系统下载
                        if [ "$OS" = "linux" ]; then
                            if [ "$ARCH" = "x86_64" ]; then
                                echo "下载Linux x86_64版本..."
                                wget -q --show-progress https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz

                                if [ -f "allure-${ALLURE_VERSION}.tgz" ]; then
                                    tar -xzf allure-${ALLURE_VERSION}.tgz
                                    sudo mkdir -p /opt
                                    sudo mv allure-${ALLURE_VERSION} /opt/allure
                                    sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure
                                    rm -f allure-${ALLURE_VERSION}.tgz
                                    echo "✅ Allure安装完成"
                                else
                                    echo "⚠️  Allure下载失败"
                                fi
                            elif [ "$ARCH" = "aarch64" ]; then
                                echo "⚠️  ARM架构，尝试其他安装方式..."
                                # 对于ARM，可能需要其他方式安装
                                sudo apt-get install -y default-jre 2>/dev/null || true
                                echo "提示: ARM架构可能需要手动安装Allure"
                            fi
                        elif [ "$OS" = "darwin" ]; then
                            echo "下载macOS版本..."
                            wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
                            unzip -q allure-${ALLURE_VERSION}.zip
                            sudo mv allure-${ALLURE_VERSION} /opt/allure
                            sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure
                            rm -f allure-${ALLURE_VERSION}.zip
                            echo "✅ Allure安装完成"
                        else
                            echo "⚠️  不支持的系统: $OS"
                        fi

                        # 验证安装
                        if command -v allure > /dev/null 2>&1; then
                            echo "✅ Allure安装成功: $(allure --version 2>&1)"
                        else
                            echo "⚠️  Allure安装失败或路径未配置"
                            echo "可以手动执行: export PATH=/opt/allure/bin:\$PATH"
                        fi

                        set -e
                    '''
                }
            }
        }

        // 阶段7：切换测试环境
        stage('切换测试环境') {
            steps {
                echo "🔄 切换到测试环境: ${params.TEST_ENVIRONMENT}"

                script {
                    sh '''
                        # 检查配置文件目录
                        if [ ! -d "common" ]; then
                            mkdir -p common
                            echo "创建common目录"
                        fi

                        echo "切换到环境: ${params.TEST_ENVIRONMENT}"

                        # 定义环境配置
                        cat > common/config.yaml << EOF
# Athena自动化测试环境配置
# 自动生成 - 构建号: ${BUILD_NUMBER}
env: "${params.TEST_ENVIRONMENT}"
EOF

                        # 根据环境添加配置
                        case "${params.TEST_ENVIRONMENT}" in
                            "阿里Paas区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp-paas.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-paas.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp-paas.apps.digiwincloud.com.cn"
iam_host: "https://iam-test.digiwincloud.com.cn"
EOF
                                ;;
                            "华为测试区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp-test.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-test.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp-test.apps.digiwincloud.com.cn"
iam_host: "https://iam-test.digiwincloud.com.cn"
EOF
                                ;;
                            "华为正式区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp.apps.digiwincloud.com.cn"
iam_host: "https://iam.digiwincloud.com.cn"
EOF
                                ;;
                            "地端双虎环境")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp.twintigers.com"
athena_deployer_host: "https://aadc.twintigers.com"
athena_tenant_deployer_host: "https://atdp.twintigers.com"
iam_host: "http://iam.twintigers.com"
EOF
                                ;;
                        esac

                        echo "✅ 环境配置已生成"
                        echo ""
                        echo "当前环境配置:"
                        echo "================================="
                        cat common/config.yaml
                    '''
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
                        mkdir -p "${ALLURE_RESULTS_DIR}"
                        mkdir -p "${ALLURE_REPORT_DIR}"
                        mkdir -p "${JENKINS_REPORTS_DIR}"

                        if ${params.CLEAN_ALLURE_HISTORY}; then
                            echo "清理Allure历史数据..."
                            rm -rf "${ALLURE_RESULTS_DIR}"/* 2>/dev/null || true
                        fi
                    """

                    // 设置测试执行超时（30分钟）
                    timeout(time: 30, unit: 'MINUTES') {
                        script {
                            // 确定Python命令
                            def pythonCmd = "python3"
                            if (params.USE_VENV.toBoolean()) {
                                pythonCmd = "${VENV_DIR}/bin/python"
                            }

                            sh """
                                echo "开始执行测试..."
                                echo "环境: ${params.TEST_ENVIRONMENT}"
                                echo "测试类型: ${params.TEST_TYPE}"
                                echo "测试模块: ${params.TEST_MODULE}"
                                echo "并行执行: ${params.PARALLEL_EXECUTION}"
                                echo "Python命令: ${pythonCmd}"

                                # 设置环境变量
                                export JENKINS_BUILD="true"
                                export BUILD_NUMBER="${env.BUILD_NUMBER}"
                                export JOB_NAME="${env.JOB_NAME}"
                                export BUILD_URL="${env.BUILD_URL}"
                                export TEST_ENVIRONMENT="${params.TEST_ENVIRONMENT}"

                                # 检查run.py是否存在
                                if [ ! -f "run.py" ]; then
                                    echo "❌ run.py不存在"
                                    echo "尝试查找其他测试入口..."

                                    # 查找可能的测试入口
                                    TEST_FILES=\$(find . -name "test_*.py" -o -name "*test.py" | head -5)
                                    if [ -n "\$TEST_FILES" ]; then
                                        echo "找到测试文件:"
                                        echo "\$TEST_FILES"
                                        echo "请更新配置使用正确的测试入口"
                                    fi
                                    exit 1
                                fi

                                # 执行run.py
                                echo "执行命令: ${pythonCmd} run.py"
                                ${pythonCmd} run.py

                                # 记录退出码
                                EXIT_CODE=\$?
                                echo \$EXIT_CODE > test_exit_code.txt
                                echo "测试退出码: \$EXIT_CODE"
                            """
                        }
                    }

                    // 检查测试结果
                    def exitCode = sh(script: 'cat test_exit_code.txt 2>/dev/null || echo "0"', returnStdout: true).trim().toInteger()

                    if (exitCode != 0) {
                        echo "⚠️ 测试执行异常，退出码: ${exitCode}"
                        currentBuild.result = 'UNSTABLE'
                    } else {
                        echo "✅ 测试执行完成"
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
                        set +e

                        echo "生成Allure报告..."
                        if command -v allure > /dev/null 2>&1 && [ -d "${ALLURE_RESULTS_DIR}" ]; then
                            echo "使用Allure生成报告..."
                            allure generate "${ALLURE_RESULTS_DIR}" -o "${ALLURE_REPORT_DIR}" --clean

                            if [ -f "${ALLURE_REPORT_DIR}/index.html" ]; then
                                echo "✅ Allure报告生成完成"
                            else
                                echo "⚠️  Allure报告生成可能失败"
                            fi
                        else
                            echo "⚠️  Allure未安装或结果目录不存在"
                        fi

                        # 复制报告文件
                        echo "收集报告文件..."
                        mkdir -p "${JENKINS_REPORTS_DIR}"

                        # 复制Allure报告
                        if [ -d "${ALLURE_REPORT_DIR}" ]; then
                            cp -r "${ALLURE_REPORT_DIR}"/* "${JENKINS_REPORTS_DIR}"/ 2>/dev/null || true
                        fi

                        # 查找并复制HTML报告
                        find . -name "*.html" -type f -not -path "./venv/*" -not -path "./.venv/*" -not -path "./report/*" | head -10 | while read file; do
                            cp "\$file" "${JENKINS_REPORTS_DIR}"/ 2>/dev/null || true
                        done

                        # 复制日志文件
                        find . -name "*.log" -type f | head -5 | while read file; do
                            cp "\$file" "${JENKINS_REPORTS_DIR}"/ 2>/dev/null || true
                        done

                        # 生成测试摘要
                        EXIT_CODE=\$(cat test_exit_code.txt 2>/dev/null || echo "0")

                        cat > "${JENKINS_REPORTS_DIR}/test_summary.md" << EOF
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
- **退出码**: \$EXIT_CODE

## 环境配置
\`\`\`yaml
\$(cat common/config.yaml 2>/dev/null || echo '配置文件不存在')
\`\`\`

## 系统信息
\$(uname -a)

## 报告文件
- Allure报告: \${ALLURE_REPORT_DIR}/index.html
- Jenkins报告目录: \${JENKINS_REPORTS_DIR}

\$(ls -la "\${JENKINS_REPORTS_DIR}" 2>/dev/null | tail -n +2)
EOF

                        echo "✅ 报告处理完成"
                        echo "报告目录: ${JENKINS_REPORTS_DIR}"
                        ls -la "${JENKINS_REPORTS_DIR}"/ 2>/dev/null || echo "报告目录为空"

                        set -e
                    """

                    // 发布HTML报告到Jenkins
                    script {
                        def reportDir = new File("${JENKINS_REPORTS_DIR}")
                        if (reportDir.exists()) {
                            def htmlFiles = findFiles(glob: "${JENKINS_REPORTS_DIR}/*.html")
                            if (!htmlFiles.isEmpty()) {
                                // 找到第一个HTML文件
                                def reportFile = htmlFiles[0].name
                                publishHTML([
                                    allowMissing: false,
                                    alwaysLinkToLastBuild: true,
                                    keepAll: true,
                                    reportDir: JENKINS_REPORTS_DIR,
                                    reportFiles: reportFile,
                                    reportName: "Athena测试报告-${params.TEST_ENVIRONMENT}"
                                ])
                                echo "✅ HTML报告已发布: ${reportFile}"
                            } else if (fileExists("${ALLURE_REPORT_DIR}/index.html")) {
                                publishHTML([
                                    allowMissing: false,
                                    alwaysLinkToLastBuild: true,
                                    keepAll: true,
                                    reportDir: ALLURE_REPORT_DIR,
                                    reportFiles: 'index.html',
                                    reportName: "Athena Allure报告-${params.TEST_ENVIRONMENT}"
                                ])
                                echo "✅ Allure报告已发布"
                            } else {
                                echo "⚠️  未找到可发布的HTML报告"
                            }
                        } else {
                            echo "⚠️  报告目录不存在"
                        }
                    }

                    // 归档报告文件
                    archiveArtifacts artifacts: "${JENKINS_REPORTS_DIR}/**/*", fingerprint: true, allowEmptyArchive: true
                    if (fileExists("${ALLURE_REPORT_DIR}")) {
                        archiveArtifacts artifacts: "${ALLURE_REPORT_DIR}/**/*", fingerprint: true, allowEmptyArchive: true
                    }
                }
            }
        }
    }

    post {
        always {
            echo "🧹 清理工作..."

            script {
                sh '''
                    set +e

                    echo "清理临时文件..."

                    # 清理Python缓存
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

                    # 清理临时文件
                    rm -f test_exit_code.txt 2>/dev/null || true
                    rm -f get-pip.py 2>/dev/null || true
                    rm -f switch_env_temp.py 2>/dev/null || true

                    echo ""
                    echo "📋 测试执行完成"
                    echo "================================="
                    echo "构建结果: ${currentBuild.result}"
                    echo "构建时长: ${currentBuild.durationString}"
                    echo "构建URL: ${env.BUILD_URL}"

                    set -e
                '''
            }
        }

        success {
            echo "✅ 测试执行成功！"
            script {
                // 可以根据需要添加成功通知
            }
        }

        failure {
            echo "❌ 测试执行失败！"
            script {
                // 可以根据需要添加失败通知
            }
        }

        unstable {
            echo "⚠️  测试执行不稳定！"
            script {
                // 可以根据需要添加不稳定通知
            }
        }
    }
}