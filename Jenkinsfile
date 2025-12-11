pipeline {
    agent any

    environment {
        PROJECT_NAME = 'athena-designer-automatedtest'
        PYTHON_VERSION = '3.9'  // 根据你的项目调整
        VENV_PATH = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/develop']],  // 使用 develop 分支
                    extensions: [[$class: 'CleanCheckout']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/wenwu12138/athena-designer-automatedtest.git',
                        credentialsId: ''  // 如果有私有仓库，填写凭据ID
                    ]]
                ])

                script {
                    echo "已拉取代码仓库: ${PROJECT_NAME}"
                    echo "分支: develop"
                    echo "仓库地址: https://github.com/wenwu12138/athena-designer-automatedtest.git"
                }
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    echo "设置Python环境..."
                    python --version || echo "Python未安装"
                    pip --version || echo "pip未安装"

                    echo "创建虚拟环境..."
                    python -m venv ${VENV_PATH} || echo "使用系统Python"
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "激活虚拟环境并安装依赖..."

                    # 激活虚拟环境（Linux/Mac）
                    if [ -f "${VENV_PATH}/bin/activate" ]; then
                        source ${VENV_PATH}/bin/activate
                    # Windows（如果Jenkins在Windows上运行）
                    elif [ -f "${VENV_PATH}\\Scripts\\activate" ]; then
                        ${VENV_PATH}\\Scripts\\activate
                    fi

                    echo "升级pip..."
                    pip install --upgrade pip

                    echo "安装项目依赖..."
                    if [ -f "requirements.txt" ]; then
                        pip install -r requirements.txt
                    else
                        echo "requirements.txt 不存在，安装常用依赖..."
                        pip install requests pytest pytest-html pytest-xdist allure-pytest
                    fi

                    echo "安装额外工具..."
                    pip install pyyaml openpyxl  # 常见的数据处理库
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "开始执行自动化测试..."
                    echo "当前目录:"
                    pwd
                    ls -la

                    echo "查找 run 文件..."
                    if [ -f "run.py" ]; then
                        echo "找到 run.py，执行..."
                        python run.py
                    elif [ -f "run" ]; then
                        echo "找到 run 脚本，执行..."
                        chmod +x run  # 添加执行权限
                        ./run
                    else
                        echo "未找到启动文件，尝试查找测试文件..."
                        # 查找并执行测试
                        find . -name "test_*.py" -type f | head -5
                    fi
                '''
            }
        }

        stage('Generate Report') {
            steps {
                sh '''
                    echo "生成测试报告..."
                    mkdir -p reports

                    # 如果使用 pytest-html 生成报告
                    if [ -d "reports" ]; then
                        echo "检查报告目录..."
                        ls -la reports/
                    fi
                '''

                // 归档测试报告
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true

                // 如果生成 HTML 报告，发布到 Jenkins
                publishHTML([
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: '*.html',
                    reportName: '自动化测试报告'
                ])
            }
        }
    }

    post {
        always {
            echo "========== 构建完成 =========="
            echo "项目: ${PROJECT_NAME}"
            echo "分支: develop"
            echo "状态: ${currentBuild.result ?: 'SUCCESS'}"

            // 清理工作空间（可选）
            // cleanWs()
        }
        success {
            echo "✅ 自动化测试执行成功！"

            // 可以添加成功通知
            // emailext body: '测试通过，所有接口正常', subject: '测试成功通知', to: 'team@example.com'
        }
        failure {
            echo "❌ 自动化测试执行失败！"

            // 可以添加失败通知
            // emailext body: '测试失败，请检查日志', subject: '测试失败通知', to: 'team@example.com'
        }
        unstable {
            echo "⚠️ 测试结果不稳定"
        }
    }
}