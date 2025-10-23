var data = {
	"PC_776ff98210001b7c": {
		"purchascczzx": [{
			"purchascczzx_id": 6.0,
			"manage_status": "N",
			"complete_state": "0",
			"serial_number": "",
			"eoc_company_id": "",
			"eoc_site_id": "",
			"eoc_region_id": "",
			"owner_dept_id": "",
			"owner_dept_name": "",
			"owner_emp_id": "",
			"owner_emp_name": "",
			"supplier_id": 1112233.0,
			"tenantsid": 8.47600433497088E14,
			"tenant_id": "athenadeveloperTest",
			"create_by": "wenwu@digiwin.com",
			"create_date": "2025/09/12 11:22:00",
			"creator_name": "闻武"
		}]
	},
	"purchasezzc": {
		"purchascczzx": [{
			"purchascczzx_id": 6.0,
			"manage_status": "N",
			"complete_state": "0",
			"serial_number": "",
			"eoc_company_id": "",
			"eoc_site_id": "",
			"eoc_region_id": "",
			"owner_dept_id": "",
			"owner_dept_name": "",
			"owner_emp_id": "",
			"owner_emp_name": "",
			"supplier_id": 1112233.0,
			"tenantsid": 8.47600433497088E14,
			"tenant_id": "athenadeveloperTest",
			"create_by": "wenwu@digiwin.com",
			"create_date": "2025/09/12 11:22:00",
			"creator_name": "闻武"
		}]
	}
}['PC_776ff98210001b7c'];
var request = {
	"std_data": {
		"parameter": {
			"purchasezzc": [{
				"manage_status": "I",
				"purchasezzc_id": data.purchasezzc[0].purchasezzc_id,
				"serial_number": {
					"completeState": 0,
					"createTime": "2025-09-12T11:22:00",
					"dueDate": "2025-09-12T23:59:59",
					"emergency": 50,
					"id": 344542,
					"initiatorId": "wenwu@digiwin.com",
					"initiatorName": "闻武",
					"initiatorNo": "5.40572277027392E14",
					"limitTime": "2025-09-12T11:22:00",
					"name": "采购单创建触发z",
					"personInChargeId": "wenwu@digiwin.com",
					"personInChargeName": "闻武",
					"processId": "PC_776ff98210001b7c",
					"processLocale": "zh_CN",
					"projectCode": "PC_776ff98210001b7c",
					"serialNumber": "wf_api_534331346223370240",
					"singleSceneProject": true,
					"state": 1,
					"subject": "未命名标题",
					"tenantId": "athenadeveloperTest",
					"tenantName": "配置测试器",
					"updateTime": "2025-09-12T11:22:01",
					"version": 1
				}.serialNumber,
				"complete_state": {
					"completeState": 0,
					"createTime": "2025-09-12T11:22:00",
					"dueDate": "2025-09-12T23:59:59",
					"emergency": 50,
					"id": 344542,
					"initiatorId": "wenwu@digiwin.com",
					"initiatorName": "闻武",
					"initiatorNo": "5.40572277027392E14",
					"limitTime": "2025-09-12T11:22:00",
					"name": "采购单创建触发z",
					"personInChargeId": "wenwu@digiwin.com",
					"personInChargeName": "闻武",
					"processId": "PC_776ff98210001b7c",
					"processLocale": "zh_CN",
					"projectCode": "PC_776ff98210001b7c",
					"serialNumber": "wf_api_534331346223370240",
					"singleSceneProject": true,
					"state": 1,
					"subject": "未命名标题",
					"tenantId": "athenadeveloperTest",
					"tenantName": "配置测试器",
					"updateTime": "2025-09-12T11:22:01",
					"version": 1
				}.completeState
			}]
		}
	}
};
console.log(request);