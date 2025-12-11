pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'develop',
                     url: 'https://github.com/wenwu12138/athena-designer-automatedtest.git'
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    # 创建并激活虚拟环境
                    python3 -m venv venv
                    . venv/bin/activate

                    # 安装依赖
                    pip install --upgrade pip
                    pip install -r requirements.txt || pip install requests pytest
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate

                    # 尝试运行测试
                    if [ -f "run.py" ]; then
                        python run.py
                    elif [ -f "run" ]; then
                        chmod +x run
                        ./run
                    else
                        echo "未找到 run.py 或 run 文件"
                        echo "当前目录内容:"
                        ls -la
                        exit 1
                    fi
                '''
            }
        }
    }
}