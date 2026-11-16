# 执行授权、源码锁与独立身份

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

**已执行获批的最小正常A一次：C00 → PT64 → PF48 → 关闭 → 适用性审查 → 自动行政收尾。** 实际active和外层入口均返回0；完整验收另按封存与观测证据裁决。

|绑定|实际结果|
|---|---|
|最终版本|PTA-PhaseFinalizer-static-1/r3；55文件/38程序；Linux部署53项|
|manifest SHA|31be4cdcf2bebff97b8eca38fe1b4b606b7499921ff6babd1da23fd2c6f91c1d|
|execution_lock SHA|31c6fe1ba61cd9acbc4c4c1d62f5f641a0d0be8c0ac6ca816df88cbebec0b0a7|
|源/实例/slice|/var/lib/dcl-r6/pf01；/var/lib/dcl-r6/batch12；dclr6batch12.slice|
|控制目录|DCL-R6-PTA-PhaseFinalizer-Fix/authorization/batch12-r3，启动前新建授权文件，原模板保持|
|boot|6b12daf8-f8cc-4788-bcaa-382f2d3407fb；新预检、运行与自动post一致|
|平台|Ubuntu-24.04、CPython3.12.3、原内核/systemd摘要、UID999/GID989/cgroup v2核验通过|
|预检隔离|运行目录/新slice/service/cgroup尚无；Root/Payload残留为空，failed仅mnt-e.mount|
|Root身份|Owner445/start8616，scheduler838/start8801，停止器849；原始start_ticks/boot见实际结果|
|历史保护|执行前锁7236份既有文件；4份根导航另存原字节，后续只追加当前记录|

授权scope=PT_STARTUP_DIAGNOSTIC_ONLY、mode=NORMAL_START，RootIPC/单会话/PreT0/PF及Calibrate-only必要批准位true；Full、MR诊断、预窗77注入false。SameProcess_C09兼容位满足冻结schema，实际C09发放仍由最小scope排除。真实用户原文逐字节复制并绑定SHA，回执绑定两锁及PF合同。

资源重新核算：C00=1，PT64完成1089/硬1536，PF48完成817/硬1152；正常A完成1907/硬2689。17变异包含在112jobs内。原完整硬65618加PF硬1152＝66770，距软访问100000余33230。失败关闭、hash及只读审计沿用冻结有限TCB，未重放搜索状态或窗口外checker。

冻结程序缺少逐次成功锁时间、完整导入起始/Live RLIMIT回执等观测项，执行前已记录此边界；相应结论保持条件性。本批没有加入观测代码或改变判据。

[源码与范围](evidence/SOURCE_AND_SCOPE_ADMISSION.json) · [资源准入](evidence/RESOURCE_ADMISSION_PROOF.json) · [部署](evidence/DEPLOYMENT_RESULT.json) · [当前环境](evidence/ENVIRONMENT_AUDIT.json) · [执行后源码](evidence/SOURCE_AFTER_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
