# batch08最小诊断授权与版本锁

Material Passport：DCL-R6-batch08-Diag；C00Ready-static-1/r2；真实最小诊断；2026-11-12（Asia/Shanghai）；重跑0。

实际scope为 **C00_DIAGNOSTIC_ONLY**，Full_conditional_chain=false、RootIPC_helpers=false、SameProcess_C09_resume=false；C00_diagnostic=true和单会话exec明确批准。原文/回执见[TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。

|对象|SHA-256|
|---|---|
|static_manifest.json|23f93f4b436ae4f5285d631735ca497855d84b598a7f55ca1b42a0c436b9e629|
|execution_lock.json|051cc0d995f084504fc393f176321eec09d03c8f4113509d8e253ab4e29dd8e3|
|readiness_contract.json|456dc61fb2abe9a72f24c057be39e21e81808457a33c7cab15bea20dbf57b68a|
|boot_contract.json|3daee2f531297dea4683670bcc17650e7993f84ba13920a4c67cfa60dbdbf2e4|
|root_ipc_contract.json|ac67cf2627612d4c25c0bfa6acb7c877876763db78a17caea4aad77a0433d60b|
|c09_contract.json|b76bcc9a7a8e432100e1212d394d3ef8b6f1bf00f2f1cf2312e38a71eb038a92|
|safety_contract.json|caa1bc43bbb8e7c690ad79e025ba08e0088aa730d4ffd840a9d4998e307f8bb9|
|TASK_REQUEST.txt|f6251c6c1b205c9eff834d7340e7676f5f8d7a964268855b34c2ae246aee9cd8|

本轮第7节要求按最小申请具体清单执行。冻结申请第一目标明确列出“原C00 probe、64正反夹具/17mutant及独立raw重算”；据此64项属于已批准最小范围。其余BC40、RootIPC56、C09H34、C01–C12、真实C09、S34、17完整门和F1/F4均未授权/未执行。范围与449/512、静态最小R上界513的核对见[SCOPE_AND_RESOURCE_ADMISSION](evidence/SCOPE_AND_RESOURCE_ADMISSION.json)。

36项host文件和24份程序身份匹配，35项Linux源码/输入部署为Root0:0/0644、目录0755、ACL空且无pyc。该部署观察不构成运行boot期望常量；冻结Windows入口的一次WSL调用重新取得当前动态身份。

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch08
```

实际冻结控制目录为`DCL-R6-batch08/evidence`，目标入口从该路径读取授权并写活动双流；报告位于`DCL-R6-batch08-Diag`。两处对应原文、回执及入口日志字节相同，source与argv未改。仅调用1次入口，无重试/补窗/代码或阈值现场修复。

[主机入口调用](evidence/FROZEN_ENTRY_INVOCATION.json)、[实际Windows plan](evidence/WINDOWS_ENTRY_PLAN.json)、[退出记录](evidence/WINDOWS_ENTRY_EXIT.json)、[部署结果](evidence/DEPLOYMENT_RESULT.json)、[命令索引](COMMAND_SUMMARY.md)。
