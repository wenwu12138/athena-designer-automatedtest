pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    # 创建虚拟环境
                    python3 -m venv venv
                    . venv/bin/activate

                    # 安装核心依赖
                    pip install PyYAML requests pytest openpyxl pymysql flask

                    # 安装其他依赖（跳过 Windows 包）
                    pip install -r requirements.txt || true
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python run.py
                '''
            }
        }
    }

    post {
        always {
            echo "构建完成: ${currentBuild.result ?: 'SUCCESS'}"
        }
    }
}