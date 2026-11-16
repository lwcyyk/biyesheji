# RuntimeAdapt最终静态裁决

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**已形成带明确来源条件的新基线RuntimeAdapt-static-1/r1，业务动态验证0。GNU libc仍2.39，Ubuntu包修订8.9→8.12，三项新文件身份/归属和静态必要兼容条件可复核。**

|验收门|结果|范围与未决边界|
|---|---|---|
|RA-1 版本与来源|CONDITIONAL_PASS|正确包归属/MD5/版本/日志、两签名与完整索引匹配；依赖Root/DB/keyring，缺新.deb独立payload再现|
|RA-2 兼容性|CONDITIONAL_PASS|66 ELF入口/114对象、必要版本需求无缺项，Python和当前map符合；全部行为/资源/服务仍待原生验证|
|RA-3 安全重冻结|CONDITIONAL_PASS|旧hash拒绝保留、3项显式新pin、包/路径/mappings等重查；path→exec原子性及后续特权替换边界保留|
|RA-4 执行准备|PASS_STATIC|64文件/44程序、RA32/8变异、资源68498及独立A2模板齐备，未批准|

本轮7次原生只读查询、3项纯ELF-note主机探针和20静态控制流断言完成；13保护文件字节/70成员AST、RootIPC/MR/Terminal模块和PT/PF/TR jobs保持。原host finalizer/entry字节保持；功能变更仅运行时检查及其授权/调用点/新增回归。

本轮安装/下载/系统库写入/WSL配置修改或重启均0；Launcher/服务/资源校准/PT/PF/TR/RA套件/生产oracle/F1/F4均0，T0/R=null。源与配置仅在新ra01和本轮交付目录适配，未来Linux源、实例和实际回执未创建。

旧TR-A的exit125/PREFLIGHT_FAILED、3项失配、T0/R未初始化、全部未运行及自动14/15行政成功保留。旧PFA112/17、R1907、native UNRESOLVED/internal UNKNOWN与行政成功保持。

新静态身份仍须独立执行批准；后续若不接受显式来源信任前提，保持RUNTIME_PROVENANCE_UNRESOLVED。下一步仅审阅[独立TR-A2申请](NEXT_DYNAMIC_AUTHORIZATION.md)，不恢复旧attempt，不直接进入MR或模型。

[来源裁决](RUNTIME_PROVENANCE_ASSESSMENT.md) · [安全矩阵](RUNTIME_SECURITY_IMPACT_MATRIX.md) · [最终源码锁](SOURCE_AND_INPUT_LOCK.md) · [证据索引](EVIDENCE_INDEX.md) · [交付核验](evidence/DELIVERY_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
