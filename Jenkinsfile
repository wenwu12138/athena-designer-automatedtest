pipeline {
    agent any

    environment {
        PROJECT_NAME = 'athena-designer-automatedtest'
        VENV_PATH = 'venv'
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
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    echo "检查系统环境..."
                    echo "Python3版本:"
                    python3 --version || echo "python3 未找到"

                    echo "创建虚拟环境..."
                    python3 -m venv ${VENV_PATH} || python3 -m venv venv

                    echo "激活虚拟环境..."
                    source ${VENV_PATH}/bin/activate
                    python --version
                    pip --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "激活虚拟环境..."
                    source ${VENV_PATH}/bin/activate

                    echo "升级pip..."
                    python -m pip install --upgrade pip

                    echo "检查 requirements.txt..."
                    if [ -f "requirements.txt" ]; then
                        echo "发现 requirements.txt，安装依赖..."
                        pip install -r requirements.txt
                    else
                        echo "requirements.txt 不存在，安装基础依赖..."
                        pip install requests pytest
                    fi
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    echo "激活虚拟环境..."
                    source ${VENV_PATH}/bin/activate

                    echo "查看项目结构..."
                    pwd
                    ls -la

                    echo "查找并执行测试入口文件..."
                    # 查找可能的入口文件
                    if [ -f "run.py" ]; then
                        echo "执行 run.py..."
                        python run.py
                    elif [ -f "main.py" ]; then
                        echo "执行 main.py..."
                        python main.py
                    elif [ -f "run" ]; then
                        echo "执行 run 脚本..."
                        chmod +x run
                        ./run
                    else
                        echo "查找测试文件..."
                        find . -name "test_*.py" -o -name "*test.py" | head -10
                        echo "请指定具体的测试入口文件"
                    fi
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    echo "清理工作..."
                    # 可以在这里添加清理步骤
                '''
            }
        }
    }

    post {
        always {
            echo "构建状态: ${currentBuild.result ?: 'SUCCESS'}"
            echo "项目: ${PROJECT_NAME}"
            echo "分支: develop"
        }
    }
}