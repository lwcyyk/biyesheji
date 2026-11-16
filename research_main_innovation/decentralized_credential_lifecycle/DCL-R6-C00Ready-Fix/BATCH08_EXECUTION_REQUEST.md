# batch08最小动态诊断与独立完整条件链申请

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

当前文件为可审阅申请，尚无动态许可。绑定C00Ready-static-1/r2，batch07继续CLOSED/R0，不能恢复原窗或借用其许可。

|锁|SHA-256|
|---|---|
|static_manifest.json|23f93f4b436ae4f5285d631735ca497855d84b598a7f55ca1b42a0c436b9e629|
|execution_lock.json|051cc0d995f084504fc393f176321eec09d03c8f4113509d8e253ab4e29dd8e3|
|readiness_contract.json|456dc61fb2abe9a72f24c057be39e21e81808457a33c7cab15bea20dbf57b68a|
|boot_contract.json|3daee2f531297dea4683670bcc17650e7993f84ba13920a4c67cfa60dbdbf2e4|
|root_ipc_contract.json|ac67cf2627612d4c25c0bfa6acb7c877876763db78a17caea4aad77a0433d60b|
|c09_contract.json|b76bcc9a7a8e432100e1212d394d3ef8b6f1bf00f2f1cf2312e38a71eb038a92|
|safety_contract.json|caa1bc43bbb8e7c690ad79e025ba08e0088aa730d4ffd840a9d4998e307f8bb9|

**第一目标/推荐范围：C00_DIAGNOSTIC_ONLY。** 请求部署cr01源模式包（35个Linux文件）、原生3.12语法/当前平台只读核验、单会话bootstrap/sealed claim/same-PID exec、C00真实逐字段/双次采样/就绪lease、原C00 probe、64正反夹具/17mutant及独立raw重算、必要停止与封存。无新增常驻服务/探针进程；最小模式完成即关闭，不进入C01/C09或模型。

Windows入口：

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\cr01\host\windows_entry.py --activate
```

唯一内部WSL argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/cr01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch08
```

**第二目标独立范围：完整条件链。** 只有新的明确Full_conditional_chain_explicitly_approved及原RootIPC探针/同进程C09恢复接受后，使用scope CALIBRATE_S1S9_THEN_F1_F4；C00/64通过后继续原实际依赖：C01–C08→C09H34→RootIPC56→BC40→真实C09→原窗一次内部恢复→C10新启动屏障→C11–C12→S34→门17→RESOURCE_GATE_PASS→F1→F4。第一目标成功不自动授权第二目标。

两份[最小模板](evidence/BATCH08_DIAGNOSTIC_AUTHORIZATION_TEMPLATE.json)/[完整模板](evidence/BATCH08_FULL_AUTHORIZATION_TEMPLATE.json)仅供审阅，批准位/原文hash尚空。最小模板明确不授予未使用的RootIPC探针与C09恢复。未来实际回执/原文放在冻结的host batch08研究路径，入口内fresh安装和核验；本轮不建立该批运行目录。

原CPY312-UBU24/1、AS4-PAYLOAD/1保持；native环境期望Python3.12.3/e50d…150f、kernel6.18.33.2、systemd255.4、cgroup2/UID999:GID989必须真实重核。当前没有查询这些平台；接口/字段缺失、权限或摘要漂移时停止，不改锁续跑。

资源差异明确：原总1000000/T0后1800、提前1740、cal300/100000、payload AS1GiB/父4tasks保持；预检TCB120秒/AS1GiB、sealed初始10秒继承原流程。C00/C10 readiness复用原14秒启动获取窗口，从请求前计时，写证/等待纳入已建立窗口。样本最多300＋最终确认、每行131072B；新64完成449、硬限512，共用原C00 ticket计费。完整校准硬访问静态上界由62034增加512至62546，仍低于100000，不增加总cap或延长300秒。C09H/RootIPC/BC原共同5000保持，真实全套耗时待测。

首次失败即保存实际8字段、辅助门、原始errno、前后unit/proc/cgroup/身份/boot/锁与时钟。禁止自动重跑、放宽字段、等待稳定错误变好、重置窗口、改源码/权限续跑或自动batch09。源/诊断写失败也fail-closed。原APP_READY不能代替exec-ready，读取旧boot或CLOSED无法发放新资格。

F2/F3、Casdoor、T1–T4、真实账户/凭据、WSL全局配置、依赖安装、无关单位和误副本处置/外发均不在申请内。实际原生验证、合成测试和F1/F4当前均UNRUN；IMPLEMENTATION_GATE=CLOSED。
