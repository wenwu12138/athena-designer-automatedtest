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
    }

    environment {
        // 基本配置
        PROJECT_NAME = 'Athena开发平台'
        TESTER_NAME = '闻武'

        // 报告路径
        ALLURE_RESULTS_DIR = 'report/tmp'
        ALLURE_REPORT_DIR = 'report/html'
        JENKINS_REPORTS_DIR = "jenkins-reports/${BUILD_NUMBER}_${params.TEST_ENVIRONMENT}"

        // 根据环境设置标签
        ENV_LABEL = "${params.TEST_ENVIRONMENT}"

        // 邮件通知配置（需要在Jenkins系统设置中配置）
        EMAIL_RECIPIENTS = '742611390@qq.com, your-team@example.com'
        EMAIL_SUBJECT_PREFIX = '[Athena自动化测试]'
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
                ║ 构建编号: #${BUILD_NUMBER}                        ║
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

        // 阶段2：拉取代码
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

        // 阶段3：Python环境准备
        stage('准备Python环境') {
            steps {
                echo "🐍 准备Python测试环境..."

                sh '''
                    echo "检查Python环境..."
                    python3 --version || python --version
                    pip3 --version || pip --version

                    echo "安装依赖包..."
                    if [ -f "requirements.txt" ]; then
                        echo "使用requirements.txt安装依赖"
                        pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/
                    else
                        echo "⚠️  requirements.txt不存在，安装基础包"
                        pip3 install pytest allure-pytest pytest-html requests pyyaml -i http://mirrors.aliyun.com/pypi/simple/
                    fi

                    echo "验证关键包:"
                    python3 -c "
try:
    import pytest
    import requests
    import yaml
    import allure
    print('✅ pytest:', pytest.__version__)
    print('✅ requests:', requests.__version__)
    print('✅ PyYAML: 已安装')
    print('✅ allure-pytest: 已安装')
except ImportError as e:
    print('❌ 导入错误:', e)
                    "

                    # 检查Allure命令行工具
                    if command -v allure &> /dev/null; then
                        echo "✅ Allure命令行: $(allure --version)"
                    else
                        echo "⚠️  Allure命令行工具未安装，HTML报告可能无法生成"
                        echo "   安装命令:"
                        echo "   wget https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz"
                        echo "   tar -zxvf allure-2.24.0.tgz"
                        echo "   sudo mv allure-2.24.0 /opt/allure"
                        echo "   sudo ln -s /opt/allure/bin/allure /usr/bin/allure"
                    fi
                '''
            }
        }

        // 阶段4：切换测试环境
        stage('切换测试环境') {
            steps {
                echo "🔄 切换到测试环境: ${params.TEST_ENVIRONMENT}"

                script {
                    // 使用环境管理器切换环境
                    sh '''
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
                    '''

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

        // 阶段5：更新测试配置
        stage('更新测试配置') {
            steps {
                echo "⚙️ 更新测试配置..."

                script {
                    // 更新config.py中的通知配置
                    sh '''
                        echo "更新通知配置..."
                        if [ -f "config.py" ]; then
                            # 备份原配置
                            cp -f config.py config.py.backup

                            # 更新通知类型
                            NOTIFICATION_MAP = {
                                "无通知": "0",
                                "邮件通知": "3",
                                "钉钉通知": "1",
                                "企业微信通知": "2",
                                "全部通知": "1,2,3"
                            }

                            NOTIFICATION_VALUE = "${NOTIFICATION_MAP[params.NOTIFICATION_TYPE] ?: '0'}"

                            # 使用sed更新配置
                            sed -i "s/notification_type =.*/notification_type = \"${NOTIFICATION_VALUE}\"/g" config.py
                            sed -i "s/excel_report =.*/excel_report = ${params.GENERATE_EXCEL_REPORT}/g" config.py

                            echo "✅ 通知配置已更新"
                            echo "   通知类型: ${params.NOTIFICATION_TYPE} -> ${NOTIFICATION_VALUE}"
                            echo "   Excel报告: ${params.GENERATE_EXCEL_REPORT}"
                        else
                            echo "⚠️  config.py不存在，跳过配置更新"
                        fi
                    '''
                }
            }
        }

        // 阶段6：执行测试
        stage('执行接口测试') {
            steps {
                echo "🚀 开始执行接口测试..."

                script {
                    // 创建报告目录
                    sh '''
                        echo "创建报告目录..."
                        mkdir -p ${ALLURE_RESULTS_DIR}
                        mkdir -p ${ALLURE_REPORT_DIR}
                        mkdir -p ${JENKINS_REPORTS_DIR}

                        if ${params.CLEAN_ALLURE_HISTORY}; then
                            echo "清理Allure历史数据..."
                            rm -rf ${ALLURE_RESULTS_DIR}/* 2>/dev/null || true
                        fi
                    '''

                    // 设置测试执行超时（30分钟）
                    timeout(time: 30, unit: 'MINUTES') {
                        sh '''
                            echo "开始执行测试..."
                            echo "环境: ${params.TEST_ENVIRONMENT}"
                            echo "测试类型: ${params.TEST_TYPE}"
                            echo "测试模块: ${params.TEST_MODULE}"
                            echo "并行执行: ${params.PARALLEL_EXECUTION}"

                            # 设置环境变量
                            export JENKINS_BUILD="true"
                            export BUILD_NUMBER="${BUILD_NUMBER}"
                            export JOB_NAME="${JOB_NAME}"
                            export BUILD_URL="${BUILD_URL}"
                            export TEST_ENVIRONMENT="${params.TEST_ENVIRONMENT}"

                            # 执行run.py（你的主测试脚本）
                            echo "执行命令: python3 run.py"
                            python3 run.py

                            # 记录退出码
                            EXIT_CODE=$?
                            echo $EXIT_CODE > test_exit_code.txt
                            echo "测试退出码: $EXIT_CODE"

                            # 如果run.py启动了自己的报告服务，这里可能需要处理
                        '''
                    }

                    // 检查测试结果
                    def exitCode = sh(script: 'cat test_exit_code.txt 2>/dev/null || echo "0"', returnStdout: true).trim().toInteger()

                    if (exitCode != 0) {
                        echo "⚠️ 测试执行异常，退出码: ${exitCode}"
                        // 不立即失败，继续生成报告
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        // 阶段7：处理测试报告
        stage('处理测试报告') {
            steps {
                echo "📊 处理测试报告..."

                script {
                    // 生成Allure报告
                    sh '''
                        echo "生成Allure报告..."
                        if command -v allure &> /dev/null && [ -d "${ALLURE_RESULTS_DIR}" ]; then
                            allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_REPORT_DIR} --clean
                            echo "✅ Allure报告生成完成"

                            # 复制Allure报告到Jenkins目录
                            cp -r ${ALLURE_REPORT_DIR}/* ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        else
                            echo "⚠️  跳过Allure报告生成"
                        fi
                    '''

                    // 复制其他报告文件
                    sh '''
                        echo "收集报告文件..."
                        # 复制pytest-html报告（如果有）
                        find . -name "*.html" -type f -not -path "./venv/*" -not -path "./.venv/*" | head -5 | while read file; do
                            cp "$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
                        done

                        # 复制日志文件
                        find . -name "*.log" -type f | head -3 | while read file; do
                            cp "$file" ${JENKINS_REPORTS_DIR}/ 2>/dev/null || true
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
- **构建编号**: #${BUILD_NUMBER}
- **执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **测试时长**: ${currentBuild.durationString}

## 环境配置
- **设计器地址**: $(grep "athena_designer_host:" common/config.yaml | cut -d' ' -f2)
- **部署器地址**: $(grep "athena_deployer_host:" common/config.yaml | cut -d' ' -f2)
- **租户部署器**: $(grep "athena_tenant_deployer_host:" common/config.yaml | cut -d' ' -f2)
- **IAM地址**: $(grep "iam_host:" common/config.yaml | cut -d' ' -f2)

## 测试结果
- **退出码**: $(cat test_exit_code.txt 2>/dev/null || echo "N/A")
- **Allure报告**: ${ALLURE_REPORT_DIR}/
- **详细日志**: 查看Jenkins控制台输出

## 生成的报告文件
$(find ${JENKINS_REPORTS_DIR} -type f -name "*.html" -o -name "*.xml" -o -name "*.json" | xargs -I {} basename {} | sort | uniq | while read file; do echo "- $file"; done)

EOF

                        echo "✅ 报告处理完成"
                        echo "报告目录: ${JENKINS_REPORTS_DIR}"
                        ls -la ${JENKINS_REPORTS_DIR}/
                    '''

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

        // 阶段8：启动本地报告服务（可选）
        stage('启动报告服务') {
            when {
                expression { params.START_LOCAL_REPORT.toBoolean() }
            }
            steps {
                echo "🌐 启动本地报告服务..."

                script {
                    sh '''
                        echo "启动Allure报告Web服务..."
                        if command -v allure &> /dev/null && [ -d "${ALLURE_RESULTS_DIR}" ]; then
                            # 在后台启动服务
                            nohup allure serve ${ALLURE_RESULTS_DIR} -h 0.0.0.0 -p 9999 > allure_service.log 2>&1 &
                            echo $! > allure_service.pid
                            sleep 3

                            # 获取服务器IP
                            SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
                            echo "✅ 报告服务已启动"
                            echo "   访问地址: http://${SERVER_IP}:9999"
                            echo "   PID: $(cat allure_service.pid)"
                            echo "   日志文件: allure_service.log"
                        else
                            echo "⚠️  无法启动报告服务"
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "🧹 清理工作..."

            script {
                // 恢复配置文件
                sh '''
                    echo "恢复配置文件..."
                    if [ -f "common/config.yaml.backup" ]; then
                        mv -f common/config.yaml.backup common/config.yaml
                        echo "✅ 恢复common/config.yaml"
                    fi
                    if [ -f "config.py.backup" ]; then
                        mv -f config.py.backup config.py
                        echo "✅ 恢复config.py"
                    fi

                    # 停止报告服务
                    if [ -f "allure_service.pid" ]; then
                        echo "停止报告服务..."
                        kill $(cat allure_service.pid) 2>/dev/null || true
                        rm -f allure_service.pid allure_service.log
                    fi

                    # 清理Python缓存
                    echo "清理Python缓存..."
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name ".coverage" -delete 2>/dev/null || true

                    # 显示报告信息
                    echo ""
                    echo "📋 测试执行完成"
                    echo "================================="
                    echo "构建状态: ${currentBuild.result}"
                    echo "构建编号: #${BUILD_NUMBER}"
                    echo "测试环境: ${params.TEST_ENVIRONMENT}"
                    echo "测试时长: ${currentBuild.durationString}"
                    echo ""
                    echo "📁 报告文件位置:"
                    echo "   Jenkins HTML报告: ${BUILD_URL}HTML_Report/"
                    echo "   归档文件: ${BUILD_URL}artifact/"
                    echo "   本地目录: ${JENKINS_REPORTS_DIR}"
                    echo ""
                    if [ -f "${JENKINS_REPORTS_DIR}/test_summary.md" ]; then
                        echo "测试摘要:"
                        cat ${JENKINS_REPORTS_DIR}/test_summary.md | grep -E "测试环境:|测试类型:|退出码:" | head -5
                    fi
                '''
            }
        }

        success {
            echo "🎉 Athena接口自动化测试成功！"

            script {
                // 成功通知
                if (params.NOTIFICATION_TYPE != '无通知') {
                    echo "发送成功通知..."

                    // 邮件通知
                    if (params.NOTIFICATION_TYPE.contains('邮件') || params.NOTIFICATION_TYPE == '全部通知') {
                        emailext(
                            to: "${EMAIL_RECIPIENTS}",
                            subject: "${EMAIL_SUBJECT_PREFIX} ✅ 测试成功 - ${params.TEST_ENVIRONMENT} - 构建 #${BUILD_NUMBER}",
                            body: """
                            <h2>✅ Athena开发平台接口测试成功</h2>
                            <hr>
                            <h3>测试信息</h3>
                            <p><strong>项目名称：</strong>${PROJECT_NAME}</p>
                            <p><strong>测试环境：</strong>${params.TEST_ENVIRONMENT}</p>
                            <p><strong>测试类型：</strong>${params.TEST_TYPE}</p>
                            <p><strong>构建编号：</strong>#${BUILD_NUMBER}</p>
                            <p><strong>执行时间：</strong>${new Date().format('yyyy-MM-dd HH:mm:ss')}</p>
                            <p><strong>测试时长：</strong>${currentBuild.durationString}</p>
                            <p><strong>测试人员：</strong>${TESTER_NAME}</p>
                            <hr>
                            <h3>测试结果</h3>
                            <p style="color: green; font-weight: bold;">✅ 所有接口测试通过，系统运行正常！</p>
                            <hr>
                            <h3>相关链接</h3>
                            <ul>
                                <li><a href="${BUILD_URL}">构建详情</a></li>
                                <li><a href="${BUILD_URL}HTML_Report/">查看测试报告</a></li>
                                <li><a href="${BUILD_URL}artifact/${JENKINS_REPORTS_DIR}/">下载报告文件</a></li>
                            </ul>
                            <hr>
                            <p><small>此邮件由Jenkins自动发送，请勿回复。</small></p>
                            """,
                            mimeType: 'text/html'
                        )
                    }
                }
            }
        }

        failure {
            echo "❌ Athena接口自动化测试失败！"

            script {
                // 失败通知
                if (params.NOTIFICATION_TYPE != '无通知') {
                    echo "发送失败通知..."

                    // 邮件通知
                    if (params.NOTIFICATION_TYPE.contains('邮件') || params.NOTIFICATION_TYPE == '全部通知') {
                        emailext(
                            to: "${EMAIL_RECIPIENTS}",
                            subject: "${EMAIL_SUBJECT_PREFIX} ❌ 测试失败 - ${params.TEST_ENVIRONMENT} - 构建 #${BUILD_NUMBER}",
                            body: """
                            <h2>❌ Athena开发平台接口测试失败</h2>
                            <hr>
                            <h3>测试信息</h3>
                            <p><strong>项目名称：</strong>${PROJECT_NAME}</p>
                            <p><strong>测试环境：</strong>${params.TEST_ENVIRONMENT}</p>
                            <p><strong>测试类型：</strong>${params.TEST_TYPE}</p>
                            <p><strong>构建编号：</strong>#${BUILD_NUMBER}</p>
                            <p><strong>执行时间：</strong>${new Date().format('yyyy-MM-dd HH:mm:ss')}</p>
                            <p><strong>测试时长：</strong>${currentBuild.durationString}</p>
                            <hr>
                            <h3>错误信息</h3>
                            <p style="color: red; font-weight: bold;">⚠️ 测试执行失败，请立即检查！</p>
                            <p>可能的原因：</p>
                            <ul>
                                <li>测试环境服务不可用</li>
                                <li>配置文件错误或权限问题</li>
                                <li>依赖包安装失败</li>
                                <li>测试用例执行异常</li>
                            </ul>
                            <hr>
                            <h3>立即处理</h3>
                            <ul>
                                <li><a href="${BUILD_URL}console">查看控制台错误日志</a></li>
                                <li><a href="${BUILD_URL}">进入构建详情页</a></li>
                                <li>检查测试环境: ${params.TEST_ENVIRONMENT}</li>
                            </ul>
                            <hr>
                            <p><small>此邮件由Jenkins自动发送，请勿回复。</small></p>
                            """,
                            mimeType: 'text/html'
                        )
                    }
                }
            }
        }

        unstable {
            echo "⚠️ 测试结果不稳定（有失败的用例）"

            script {
                // 不稳定通知
                if (params.NOTIFICATION_TYPE != '无通知') {
                    emailext(
                        to: "${EMAIL_RECIPIENTS}",
                        subject: "${EMAIL_SUBJECT_PREFIX} ⚠️ 测试不稳定 - ${params.TEST_ENVIRONMENT} - 构建 #${BUILD_NUMBER}",
                        body: """
                        <h2>⚠️ Athena开发平台接口测试有失败用例</h2>
                        <hr>
                        <p><strong>项目名称：</strong>${PROJECT_NAME}</p>
                        <p><strong>测试环境：</strong>${params.TEST_ENVIRONMENT}</p>
                        <p><strong>测试类型：</strong>${params.TEST_TYPE}</p>
                        <p><strong>构建编号：</strong>#${BUILD_NUMBER}</p>
                        <p><strong>执行时间：</strong>${new Date().format('yyyy-MM-dd HH:mm:ss')}</p>
                        <hr>
                        <p style="color: orange; font-weight: bold;">📋 有部分测试用例失败，请检查错误报告</p>
                        <p>建议操作：</p>
                        <ol>
                            <li>查看测试报告中的失败用例</li>
                            <li>检查测试环境是否正常</li>
                            <li>验证测试数据是否正确</li>
                            <li>如有Excel报告，查看详细错误信息</li>
                        </ol>
                        <hr>
                        <h3>相关链接</h3>
                        <ul>
                            <li><a href="${BUILD_URL}HTML_Report/">查看详细测试报告</a></li>
                            <li><a href="${BUILD_URL}artifact/${JENKINS_REPORTS_DIR}/">下载报告文件</a></li>
                            <li><a href="${BUILD_URL}console">查看控制台输出</a></li>
                        </ul>
                        <hr>
                        <p><small>此邮件由Jenkins自动发送，请勿回复。</small></p>
                        """,
                        mimeType: 'text/html'
                    )
                }
            }
        }
    }
}