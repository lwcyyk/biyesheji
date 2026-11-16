# batch06 专项授权、冻结锁及预检裁决

Material Passport：DCL-R6-batch06；RootIPC-static-1/r4；真实预检/准备记录；动态测试0；2026-11-11。

本次用户明确批准独立batch06、RootIPC-static-1/r4、56项专项回归、原C/S/门链、额外1个顺序可信Root探针，以及资源资格后同批自动F1→F4。授权原文见[TASK_REQUEST](evidence/TASK_REQUEST.txt)，已安装真实回执见[execution_authorization](evidence/execution_authorization.json)。静态执行锁的DYNAMIC_UNAUTHORIZED历史标签保持原字节，本轮授权由新的用户原文hash与有效回执绑定。

|对象|SHA-256|
|---|---|
|static_manifest.json|f47f15c1bd41c037200203864199c062027ebf2f708ae9e46fd601c382400e95|
|execution_lock.json|6da1da1cc5d89ccfb9b9f5cf615dc47398784114b5f3cc6189b4714646e8a2e8|
|root_ipc_contract.json|0a26a1a3c7d6491bc85a781145ab53672946ec46174a17c445cfeacb6850fe77|
|c09_contract.json|3e51bdb78d6047f22873eb7594001d77b2b21298c53e363d9c9e3e3c2e2495a3|
|safety_contract.json|28bd92be7541e959f8048de5719cb4473196459c90f47a2f6deb421a3b340203|
|TASK_REQUEST.txt|53c13992d889695a089c08df26fb5941b0dfaef21d51bf30d896b8cd06d14eeb|

基础预检通过：44项host源/缓存/输入与冻结r4一致；native sha256sum核验1326个唯一Linux文件（原1282加新44）通过；17份最终源码语法记录通过hash绑定继承，本轮重新编译0。五业务、runner、预算核心、探针、C09H34、RootIPC56、S34及门17均按最终输入锁核验。

Python3.12.3 `/usr/bin/python3.12`，摘要e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f；Ubuntu24.04.5、kernel6.18.33.2-microsoft-standard-WSL2/x86_64、systemd255.4-1ubuntu8.18、cgroup2fs、page4096。UID999/GID989且补充组仅989；既有nobody65534/GID65534供获准探针使用；实际探针启动0。Root行政AS为原外部TCB范围，payload AS4条件保持。

6条冻结准备命令实际exit0：建立batch06目录、out、root_private，安装原slice，systemd-analyze verify、daemon-reload；随后安装授权原文及回执。父slice属性TasksMax4、MemoryMax4294967296、inactive/dead；Root:989/0750批根/inputs，999:989/0700 out，Root:Root/0700 private，授权文件Root:989/0640，ACL均空、同设备；out/窗口/账/关闭文件均为空。

最终预检命令15的boot_id=c92b8cbc-fada-48bd-8b61-eaaf134a06ee，与基础命令2的3f63d905-84a9-47c0-b212-fdda02584774不同。`same_boot=false`，其他最终谓词全部true，因此**PREFLIGHT_FAILED**。窗口建立前的证据链已跨boot；Launcher调用0、预算初始化0、动态case0。本轮保留失败记录后仅核查/导出；Source/lock/权限现场修复0。

精确argv及原始双流见[命令索引](COMMAND_SUMMARY.md)。拟使用的冻结顺序为C00–C08→C09H34/Root审查→RootIPC56/Root审查→真实C09→同窗一次恢复→C10–C12→S34→门17→资格→F1→F4；本轮在前置预检处停止。

[基础预检](evidence/PREFLIGHT_RESULT.json)、[最终预检](evidence/PREFLIGHT_FINAL.json)、[首次失败](evidence/FIRST_FAILURE.json)、[源文件索引](SOURCE_INDEX.json)。
