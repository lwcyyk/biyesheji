# 运行时身份锁精化与最小代码依赖

Material Passport：DCL-R6-RuntimeAdapt-Fix；RuntimeAdapt-static-1/r1；2026-11-13（Asia/Shanghai）；READ_ONLY_PLATFORM_AND_HOST_STATIC；业务动态测试0。

**新资源profile仍为CPY312-UBU24/1；另加精确glibc身份GLIBC-UBU24-2.39-8.12/1。** AS1GiB、父TasksMax4、总1000000/1800、校准100000/300、预T0120及提前1740均不改变。

程序变更分两类：必要的namespace/版本字面值适配将tr01/batch13改为独立ra01/batch14；功能变更限于新的runtime_identity、RA32驱动/oracle及运行时匹配/授权调用点。固定SPEC和批次检查使全程序字节保持与独立新身份无法同时实现，完整diff明确标出机械重命名。

严格pin仅显式更新已确认变化的loader/libc/libm，在runtime_files与runtime_critical中同步。stdlib runtime_tree中没有这三项路径，旧1241合并闭包的其他pin未更新。新metadata记录包身份、Build-ID、别名、dpkg目录和六项加载配置；输入摘要DAG重新生成，原Root运行时字节检查继续抛错。

新匹配器：只读固定Root文件/合同；full模式校SHA/Build-ID/路径/元数据；包模式校dpkg中精确版本/架构/安装状态和已安装目录摘要；当前进程maps校3项路径、inode/device与deleted状态。hot Guard先由原runtime_files循环查字节，再轻量查路径和映射。包/配置full检查在预检、服务前/内、seal与行政入口执行。

没有改为版本范围、缺hash放行、warning-only或自动学习新hash。新增RuntimeAdapt及来源前提批准位，当前模板false。host entry/finalizer字节保持；admin bootstrap仅在原资源界后、目标模块加载前追加只读身份检查。

13关键文件逐字节、70成员AST、完整RootIPC/MR/Terminal模块与PT/PF/TR jobs归一保持。namespace/cfg变化和新增只读检查不构成新研究机制实施，严格分离0与实施门CLOSED保持。

[3项pin差异](evidence/RUNTIME_PIN_DIFF.json) · [全部源码/输入差异](evidence/FILE_DIFF_INDEX.json) · [完整diff](evidence/FULL_DIFF.patch) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。历史安全与原创性裁决保持。
