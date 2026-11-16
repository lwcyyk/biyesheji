# 自动行政收尾执行与权限合同

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

可信执行者为冻结Windows入口及其finalizer、Ubuntu-24.04下Root行政Python进程。新Native命令精确绑定为：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pf01/src/admin_postexit.py --post-exit-export
```

|范围|允许行为|
|---|---|
|固定pf01源/输入|Root受信元数据/摘要/解释器核验后只读；module origin必须为该src|
|当前batch12|只读当前state/counter、Root私有记录、native ZIP/manifest和已存在日志|
|进入私有审计前|runtime回执必须与当前control回执同SHA；activation的boot/批次/源/执行锁/回执绑定一致；错配即拒绝导出|
|角色/组|读取/proc、当前父cgroup与已登记Owner/child/停止器PID/starttime/boot；空cmdline仍由已登记身份核验；错误保留UNKNOWN|
|可写位置|本批固定control下独立STARTUP_NATIVE_AUDIT、startup_snapshot、post计划/双流/错误/manifest/ZIP与host结果|
|历史批次/原账|不写入、不重置、不恢复；实例固定为batch12，错配记录原样保留|

主入口在源摘要读取和目标模块装载前设置AS硬界1GiB及唯一30秒alarm，记录原行政deadline；export继承剩余时间并核验timer/AS，避免重新开始30秒。独立角色收敛等待最多5秒/128次采样，且受原行政deadline、已有预窗120秒或运行deadline剩余值进一步限制。此过程不延长业务/校准/启动窗口。

host对post正常wait使用32秒，超时后仅终止并尝试在总35秒剩余内回收该WSL客户端，记录客户端是否reaped。Root行政进程的30秒alarm、主机调用/存储/调度延迟与客户端到Native退出的对应关系仍需Native证据；这些界不构成Windows/WSL实时调度保证。

实际T0/预算存在则读取，缺失继续null，部分对象保持UNRESOLVED。native ZIP流验证成功记COMPLETED，真实seal error记FAILED，其余保留UNRESOLVED或纯预窗NOT_APPLICABLE。该状态先落盘为单独行政audit；后续导出失败时host仍可保存这份有当前回执绑定的native事实。

native完成后仍生成独立行政快照和host行政ZIP，包含原始错误、双流、回执、退出、native包与manifest。复制上限256文件/32MiB；host再核数量/字节/相对路径与SHA。权限/模块/IO失败经独立FAILURE或FINALIZATION_ERROR保留；重复收尾只验证并返回已有manifest/ZIP事实，不创建新的运行资格或覆盖原生结果。

适用表：无T0、已有T0、native成功/失败/未知、内部UNKNOWN、Root正常/异常退出、业务服务结束、CLOSED均有只读分支。仍有角色/组或读取错误则DEFERRED/CLEANUP_UNKNOWN。当前默认ACL、真实回收延迟、原生AS及所有条件的实际IO行为均待下一动态验收。

[新入口](evidence/SOURCE_FINAL_R3/src/admin_postexit.py) · [Native导出](evidence/SOURCE_FINAL_R3/src/startup_lifecycle.py) · [host收尾](evidence/SOURCE_FINAL_R3/host/startup_finalize.py)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
