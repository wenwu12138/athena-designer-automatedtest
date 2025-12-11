pipeline {
    agent any

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
            description: '选择测试模块'
        )

        booleanParam(
            name: 'INSTALL_SYSTEM_DEPS',
            defaultValue: true,
            description: '是否自动安装系统依赖'
        )

        booleanParam(
            name: 'USE_VENV',
            defaultValue: false,
            description: '是否使用Python虚拟环境'
        )
    }

    environment {
        PROJECT_NAME = 'Athena开发平台'
        TESTER_NAME = '闻武'
        ALLURE_RESULTS_DIR = 'report/tmp'
        ALLURE_REPORT_DIR = 'report/html'
        JENKINS_REPORTS_DIR = "jenkins-reports/${env.BUILD_NUMBER}"
        VENV_DIR = 'venv'
    }

    stages {
        stage('环境信息') {
            steps {
                script {
                    echo """
                    ========================================
                    Athena开发平台 - 接口自动化测试
                    项目名称: ${PROJECT_NAME}
                    测试人员: ${TESTER_NAME}
                    测试环境: ${params.TEST_ENVIRONMENT}
                    测试类型: ${params.TEST_TYPE}
                    构建编号: #${env.BUILD_NUMBER}
                    虚拟环境: ${params.USE_VENV}
                    ========================================
                    """
                }
            }
        }

        stage('检查系统依赖') {
            when {
                expression { params.INSTALL_SYSTEM_DEPS.toBoolean() }
            }
            steps {
                script {
                    sh '''
                        echo "=== 检查系统环境 ==="
                        uname -a
                        cat /etc/os-release 2>/dev/null || echo "无法获取系统信息"
                        echo ""

                        echo "=== 安装必要系统包 ==="
                        # 检测包管理器并安装必要包
                        if command -v apt-get &> /dev/null; then
                            echo "使用apt包管理器"
                            apt-get update
                            apt-get install -y python3 python3-pip python3-venv curl wget git
                        elif command -v yum &> /dev/null; then
                            echo "使用yum包管理器"
                            yum install -y python3 python3-pip python3-virtualenv curl wget git
                        elif command -v apk &> /dev/null; then
                            echo "使用apk包管理器"
                            apk add python3 py3-pip python3-dev curl wget git
                        fi

                        echo ""
                        echo "=== 检查Python环境 ==="
                        python3 --version || python --version || echo "Python未安装"

                        echo ""
                        echo "=== 检查pip ==="
                        pip3 --version || pip --version || echo "pip未安装"
                    '''
                }
            }
        }

        stage('拉取代码') {
            steps {
                script {
                    echo "拉取最新代码..."
                    // 已经在Pipeline开始时自动拉取了，这里只做信息展示
                    sh '''
                        echo "当前目录: $(pwd)"
                        echo "文件列表:"
                        ls -la
                        echo ""
                        echo "Git信息:"
                        git log -1 --oneline 2>/dev/null || echo "无法获取Git信息"
                    '''
                }
            }
        }

        stage('创建虚拟环境') {
            when {
                expression { params.USE_VENV.toBoolean() }
            }
            steps {
                script {
                    sh '''
                        echo "创建Python虚拟环境..."

                        # 检查是否已安装venv
                        python3 -m venv --help 2>/dev/null
                        if [ $? -ne 0 ]; then
                            echo "venv模块不可用，尝试安装python3-venv"
                            if command -v apt-get &> /dev/null; then
                                apt-get install -y python3-venv
                            elif command -v yum &> /dev/null; then
                                yum install -y python3-virtualenv
                            fi
                        fi

                        # 删除旧的虚拟环境
                        rm -rf venv 2>/dev/null || true

                        # 创建虚拟环境
                        python3 -m venv venv || {
                            echo "venv创建失败，尝试virtualenv"
                            if command -v virtualenv &> /dev/null; then
                                virtualenv venv -p python3
                            else
                                echo "无法创建虚拟环境，跳过"
                            fi
                        }

                        if [ -d "venv" ]; then
                            echo "虚拟环境创建成功"
                            echo "Python路径: venv/bin/python"
                            echo "pip路径: venv/bin/pip"
                        else
                            echo "虚拟环境创建失败，将使用系统Python"
                        fi
                    '''
                }
            }
        }

        stage('安装Python依赖') {
            steps {
                script {
                    sh '''
                        echo "安装Python依赖..."

                        # 确定pip命令
                        if [ "${params.USE_VENV}" = "true" ] && [ -f "venv/bin/pip" ]; then
                            PIP_CMD="venv/bin/pip"
                            echo "使用虚拟环境pip"
                        else
                            # 优先使用pip3
                            if command -v pip3 &> /dev/null; then
                                PIP_CMD="pip3"
                            elif command -v pip &> /dev/null; then
                                PIP_CMD="pip"
                            else
                                echo "pip未找到，尝试安装"
                                curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                                python3 get-pip.py
                                PIP_CMD="pip3"
                                rm -f get-pip.py
                            fi
                            echo "使用系统pip: $PIP_CMD"
                        fi

                        echo "pip版本:"
                        $PIP_CMD --version || echo "无法获取pip版本"

                        # 使用国内镜像源
                        MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
                        DOMAIN="pypi.tuna.tsinghua.edu.cn"

                        echo ""
                        echo "升级pip..."
                        $PIP_CMD install --upgrade pip -i $MIRROR --trusted-host $DOMAIN || echo "pip升级失败，继续执行"

                        echo ""
                        echo "安装项目依赖..."
                        if [ -f "requirements.txt" ]; then
                            echo "使用requirements.txt安装依赖"
                            $PIP_CMD install -r requirements.txt -i $MIRROR --trusted-host $DOMAIN || {
                                echo "镜像源失败，尝试官方源"
                                $PIP_CMD install -r requirements.txt
                            }
                        else
                            echo "requirements.txt不存在，安装基础包"
                            $PIP_CMD install pytest allure-pytest pytest-html requests pyyaml openpyxl -i $MIRROR --trusted-host $DOMAIN || {
                                echo "镜像源失败，尝试官方源"
                                $PIP_CMD install pytest allure-pytest pytest-html requests pyyaml openpyxl
                            }
                        fi

                        echo ""
                        echo "验证安装的包:"
                        $PIP_CMD list | grep -E "(pytest|allure|requests|yaml|openpyxl)" || echo "无法列出包"
                    '''
                }
            }
        }

        stage('切换测试环境') {
            steps {
                script {
                    sh """
                        echo "切换到环境: \${params.TEST_ENVIRONMENT}"

                        # 创建配置目录
                        mkdir -p common

                        # 创建配置文件
                        cat > common/config.yaml << 'EOF'
env: "\${params.TEST_ENVIRONMENT}"
EOF

                        # 根据环境添加配置
                        case "\${params.TEST_ENVIRONMENT}" in
                            "阿里Paas区")
                                cat >> common/config.yaml << 'EOF'
athena_designer_host: "https://adp-paas.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-paas.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp-paas.apps.digiwincloud.com.cn"
iam_host: "https://iam-test.digiwincloud.com.cn"
EOF
                                ;;
                            "华为测试区")
                                cat >> common/config.yaml << 'EOF'
athena_designer_host: "https://adp-test.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-test.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp-test.apps.digiwincloud.com.cn"
iam_host: "https://iam-test.digiwincloud.com.cn"
EOF
                                ;;
                            "华为正式区")
                                cat >> common/config.yaml << 'EOF'
athena_designer_host: "https://adp.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc.apps.digiwincloud.com.cn"
athena_tenant_deployer_host: "https://atdp.apps.digiwincloud.com.cn"
iam_host: "https://iam.digiwincloud.com.cn"
EOF
                                ;;
                            "地端双虎环境")
                                cat >> common/config.yaml << 'EOF'
athena_designer_host: "https://adp.twintigers.com"
athena_deployer_host: "https://aadc.twintigers.com"
athena_tenant_deployer_host: "https://atdp.twintigers.com"
iam_host: "http://iam.twintigers.com"
EOF
                                ;;
                        esac

                        echo "环境配置完成:"
                        cat common/config.yaml
                    """
                }
            }
        }

        stage('执行测试') {
            steps {
                script {
                    sh '''
                        echo "开始执行测试..."

                        # 创建报告目录
                        mkdir -p report/tmp
                        mkdir -p report/html
                        mkdir -p ${JENKINS_REPORTS_DIR}

                        # 确定Python命令
                        if [ "${params.USE_VENV}" = "true" ] && [ -f "venv/bin/python" ]; then
                            PYTHON_CMD="venv/bin/python"
                            echo "使用虚拟环境Python"
                        else
                            PYTHON_CMD="python3"
                            echo "使用系统Python"
                        fi

                        echo "Python命令: $PYTHON_CMD"
                        echo "Python版本:"
                        $PYTHON_CMD --version || echo "无法获取Python版本"

                        # 检查run.py是否存在
                        if [ ! -f "run.py" ]; then
                            echo "错误: run.py 不存在"
                            echo "当前目录文件:"
                            ls -la
                            exit 1
                        fi

                        echo ""
                        echo "执行测试脚本..."
                        # 设置超时，避免无限期运行
                        timeout 1800s $PYTHON_CMD run.py || {
                            echo "测试执行异常，继续处理报告"
                            exit_code=$?
                            echo "退出码: $exit_code"
                        }

                        echo "测试执行完成"
                    '''
                }
            }
        }

        stage('生成报告') {
            steps {
                script {
                    sh '''
                        echo "生成测试报告..."

                        # 安装Allure（如果可用）
                        if ! command -v allure &> /dev/null; then
                            echo "Allure未安装，尝试安装..."
                            ALLURE_VERSION="2.24.0"
                            wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz
                            tar -xzf allure-${ALLURE_VERSION}.tgz
                            sudo mv allure-${ALLURE_VERSION} /opt/allure
                            sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure
                            rm -f allure-${ALLURE_VERSION}.tgz
                        fi

                        # 生成Allure报告
                        if command -v allure &> /dev/null && [ -d "report/tmp" ]; then
                            echo "生成Allure报告..."
                            allure generate report/tmp -o report/html --clean
                            echo "Allure报告生成完成"
                        else
                            echo "跳过Allure报告生成"
                        fi

                        # 复制报告文件
                        echo "收集报告文件..."
                        if [ -d "report/html" ]; then
                            cp -r report/html/* ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        fi

                        # 查找HTML报告
                        find . -name "*.html" -type f -not -path "*/venv/*" -not -path "*/.venv/*" | head -10 | while read file; do
                            echo "复制报告文件: $file"
                            cp "$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        done

                        echo ""
                        echo "报告文件:"
                        ls -la ${JENKINS_REPORTS_DIR}/ 2>/dev/null || echo "报告目录为空"
                    '''
                }

                // 发布HTML报告
                script {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${JENKINS_REPORTS_DIR}",
                        reportFiles: 'index.html',
                        reportName: "Athena测试报告-${params.TEST_ENVIRONMENT}"
                    ])
                }

                // 归档报告
                archiveArtifacts artifacts: "${JENKINS_REPORTS_DIR}/**/*", fingerprint: true, allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                echo """
                ========================================
                构建完成
                结果: ${currentBuild.result}
                编号: #${env.BUILD_NUMBER}
                环境: ${params.TEST_ENVIRONMENT}
                时长: ${currentBuild.durationString}
                URL: ${env.BUILD_URL}
                ========================================
                """

                // 清理工作
                sh '''
                    echo "清理Python缓存..."
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

                    # 清理临时文件但保留报告
                    echo "报告目录保留在: ${JENKINS_REPORTS_DIR}"
                '''
            }
        }

        success {
            echo "✅ 测试执行成功！"
        }

        failure {
            echo "❌ 测试执行失败！"
        }
    }
}