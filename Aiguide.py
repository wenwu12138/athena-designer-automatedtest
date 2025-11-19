"""
学习自动化yaml用例格式，并且我会给你一些curl，帮我依照你学习的规范生成yaml用例

有一些生成规范请注意一下：
1.请求头中仅保留digi-middleware-auth-user， token，locale，并且igi-middleware-auth-user， token的value为$cache{token}
2.如果请求信息中存在application等应用code 替换成变量 ${{app2_code()}}
3.如果存在新增/更新数据接口中存在name，descrition 等名称描述字段 尽量贴合用例描述 言简意赅 并且 拼接后缀${{get_time()}}
4.在明确结构的前提上，学会使用 current_request_set_cache 添加缓存已经缓存使用方法 当多个curl之间存在关联关系能自动将存在关联的接口使用缓存串联起来
5. 根据域名生成不同的host
6.用例默认不存在依赖 dependence_case 为false
7.尽量保证结构一致



query_SwitchProcess_001:
  host: ${{athena_deployer_host()}}
  url: /athenadeployer/deploy/v3/queryProcess
  method: GET
  detail: 查询应用发版进度
  headers:
    digi-middleware-auth-user: $cache{token}    #cookie: $cache{login_cookie}
    token: $cache{token}
  requestType: PARAMS
  is_run: False
  data:
    deployNo: a1db6768be984179bf3852aba7d52e49
    application: A20240311173157-lcdp
  # 是否有依赖业务，为空或者false则表示没有
  dependence_case: False
  # 依赖的数据
  dependence_case_data:
  assert:
    code:
      jsonpath: $.code
      type: ==
      value: 0
      AssertType:

# 创建权限测试应用（权限管理功能前置数据准备）
basis_CreateAuthTestApp_001:
  host: ${{athena_designer_host()}}
  url: /athena-designer/application/addV3
  method: POST
  detail: 创建权限测试应用（权限管理功能前置数据准备）
  headers:
    authorization: $cache{token}
    digi-middleware-auth-user: $cache{token}
  requestType: json
  is_run: true
  data:
    application:
      code: "${{AuthTestApp_code()}}"
      name: "权限授权测试应用"
      description: "权限管理功能自动化测试专用应用"
      iconName: "1.png"
      iconBgcolor: "#0189FF"
      commonApp: false
      createType: 1
      serviceCode: ["DPBAS"]
      appType: 5
      lang:
        name:
          zh_CN: "权限授权测试应用"
          zh_TW: "權限授權測試應用"
          en_US: "Auth Test Application"
        description:
          zh_CN: "权限管理功能自动化测试专用应用"
          zh_TW: "權限管理功能自動化測試專用應用"
          en_US: "Auto test application for auth management"
    code: "${{AuthTestApp_code()}}"
    name: "权限授权测试应用"
    description: "权限管理功能自动化测试专用应用"
    iconName: "1.png"
    iconBgcolor: "#0189FF"
    commonApp: false
    createType: 1
    serviceCode: ["DPBAS"]
    serverResources: []
  dependence_case: False
  dependence_case_data:
  assert:
    code:
      jsonpath: $.code
      type: ==
      value: 0
      AssertType:
  current_request_set_cache:
    # request是从请求中提取内容，  response是从详情中提取需求
    - type: request
      jsonpath: $.code
      # 自定义缓存名称
      name: AuthTestApp_code


# 用户申请应用权限
auth_ApplyForAuth_001:
  host: ${{athena_designer_host()}}
  url: /athena-designer/auth/applyForAuth
  method: POST
  detail: 用户申请应用权限
  headers:
    digi-middleware-auth-user: $cache{token}
    token: $cache{token}
    content-type: application/json
  requestType: json
  is_run: true
  data:
    userId: yaosla@digiwin.com
    role: application:actor
    description: 我申请权限我申请权限我申请权限我申请权限我申请权限我申请权限
    application: $cache{AuthTestApp_code}
  dependence_case: False
  dependence_case_data:
  assert:
    code:
      jsonpath: $.code
      type: ==
      value: 0
      AssertType:
"""