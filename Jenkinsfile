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
            defaultValue: true,
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
                        echo ""

                        echo "=== 检查Python环境 ==="
                        # 查找Python
                        if command -v python3 &> /dev/null; then
                            echo "Python3 已安装: $(python3 --version)"
                        elif command -v python &> /dev/null; then
                            echo "Python 已安装: $(python --version)"
                        else
                            echo "Python 未安装，尝试安装..."
                            # 根据系统安装Python
                            if command -v apt-get &> /dev/null; then
                                apt-get update && apt-get install -y python3 python3-pip
                            elif command -v yum &> /dev/null; then
                                yum install -y python3 python3-pip
                            elif command -v apk &> /dev/null; then
                                apk add python3 py3-pip
                            fi
                        fi

                        echo ""
                        echo "=== 检查pip ==="
                        if command -v pip3 &> /dev/null; then
                            echo "pip3 已安装"
                        elif command -v pip &> /dev/null; then
                            echo "pip 已安装"
                        else
                            echo "安装pip..."
                            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                            python3 get-pip.py || python get-pip.py
                            rm -f get-pip.py
                        fi
                    '''
                }
            }
        }

        stage('拉取代码') {
            steps {
                script {
                    echo "拉取最新代码..."
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/develop']],
                        extensions: [],
                        userRemoteConfigs: [[
                            url: 'https://github.com/wenwu12138/athena-designer-automatedtest.git',
                            credentialsId: ''
                        ]]
                    ])
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
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv || python -m venv venv
                        fi
                        echo "虚拟环境已创建"
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
                        else
                            PIP_CMD="pip3"
                        fi

                        # 使用国内镜像源
                        MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"

                        # 升级pip
                        $PIP_CMD install --upgrade pip -i $MIRROR

                        # 安装依赖
                        if [ -f "requirements.txt" ]; then
                            $PIP_CMD install -r requirements.txt -i $MIRROR
                        else
                            $PIP_CMD install pytest allure-pytest pytest-html requests pyyaml -i $MIRROR
                        fi

                        echo "依赖安装完成"
                    '''
                }
            }
        }

        stage('切换测试环境') {
            steps {
                script {
                    sh """
                        echo "切换到环境: \${params.TEST_ENVIRONMENT}"

                        # 创建配置文件
                        cat > common/config.yaml << EOF
env: "\${params.TEST_ENVIRONMENT}"
EOF

                        # 根据环境添加配置
                        case "\${params.TEST_ENVIRONMENT}" in
                            "阿里Paas区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp-paas.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-paas.apps.digiwincloud.com.cn"
EOF
                                ;;
                            "华为测试区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp-test.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc-test.apps.digiwincloud.com.cn"
EOF
                                ;;
                            "华为正式区")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp.apps.digiwincloud.com.cn"
athena_deployer_host: "https://aadc.apps.digiwincloud.com.cn"
EOF
                                ;;
                            "地端双虎环境")
                                cat >> common/config.yaml << EOF
athena_designer_host: "https://adp.twintigers.com"
athena_deployer_host: "https://aadc.twintigers.com"
EOF
                                ;;
                        esac

                        echo "环境配置完成"
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

                        # 确定Python命令
                        if [ "${params.USE_VENV}" = "true" ] && [ -f "venv/bin/python" ]; then
                            PYTHON_CMD="venv/bin/python"
                        else
                            PYTHON_CMD="python3"
                        fi

                        # 执行测试
                        $PYTHON_CMD run.py || echo "测试执行完成"

                        echo "测试执行结束"
                    '''
                }
            }
        }

        stage('生成报告') {
            steps {
                script {
                    sh '''
                        echo "生成测试报告..."

                        # 创建Jenkins报告目录
                        mkdir -p ${JENKINS_REPORTS_DIR}

                        # 生成Allure报告（如果已安装）
                        if command -v allure &> /dev/null; then
                            allure generate report/tmp -o report/html --clean
                            cp -r report/html/* ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        fi

                        # 收集HTML报告
                        find . -name "*.html" -type f | head -5 | while read file; do
                            cp "$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        done

                        echo "报告已生成到: ${JENKINS_REPORTS_DIR}"
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
                        reportName: '测试报告'
                    ])
                }
            }
        }
    }

    post {
        always {
            script {
                echo "测试执行完成"
                echo "构建结果: ${currentBuild.result}"
                echo "构建URL: ${env.BUILD_URL}"

                // 清理工作
                sh '''
                    echo "清理临时文件..."
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                '''
            }
        }
    }
}