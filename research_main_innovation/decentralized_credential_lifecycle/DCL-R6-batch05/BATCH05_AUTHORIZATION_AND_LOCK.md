# batch05 授权、冻结锁与启动前核验

Material Passport：DCL-R6-batch05；C09Fix-static-1/r1；真实执行后证据分析；2026-11-11；复跑 0。

本批获准执行独立 batch05，Root 协调器、C09H 34 项及完整资源门均在授权范围内；F1/F4 依赖同批 RESOURCE_GATE_PASS。授权原文与安装回执分别见 [TASK_REQUEST](evidence/TASK_REQUEST.txt)、[execution_authorization](evidence/execution_authorization.json)。冻结执行锁原有 `DYNAMIC_UNAUTHORIZED` 字段保留其静态历史语义，当前专项授权由新回执绑定，锁字节保持。

|对象|SHA-256|
|---|---|
|static_manifest.json|81af510478f40c454e152a37b884b3965ba5e4990693529dc1de80601c42d0b9|
|execution_lock.json|031045992c5564348b3958dd324d2d1a26d9a30c17a5d990f213e8d69087b622|
|c09_contract.json|b41e509d8746dfe0bb81c74979a33e029109b7f0652668a427db838cbc903b78|
|safety_contract.json|8030e5e47806ecc6f53544e98c02e50ab657c6d229ab5264ad1d0f5c46a01e5c|
|TASK_REQUEST.txt|cbb37ee1061baa59b1126d3192a7efcf3a422669edd0bdf8a1b389e84a7ed3a2|

唯一源为 `/var/lib/dcl-r6/c09f01`，host 为 `D:\毕业设计\DCL-R6-isolated-verification\c09f01`；14 源码、14 缓存、9 输入共 37 项与冻结锁一致。原 10 份程序字节保持。14 份源码语法检查属于 C09Fix 静态阶段记录，本批通过最终文件摘要绑定该记录；本批新增语法执行 0。

启动前 native sha256sum 对 1,282 个唯一 Linux 文件核验通过，范围见 [HASH_SCOPE](evidence/HASH_SCOPE.json)。Ubuntu 24.04.5、kernel `6.18.33.2-microsoft-standard-WSL2/x86_64`、systemd `255.4-1ubuntu8.18`、cgroup2fs、页大小 4096；Python `/usr/bin/python3.12` 3.12.3，SHA-256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`。payload UID/GID=999/989，补充组仅 989。唯一已知历史 manager 失败为 mnt-e.mount。启动前专用 UID、batch05 单位、旧账及窗口均为空。

5 条冻结准备命令安装本批目录/slice、verify、daemon-reload；verify exit 0。授权文件 root:989/0640，out 999:989/0700；父 slice inactive，TasksMax=4、MemoryMax=4 GiB。最终启动前核验 [PREFLIGHT_FINAL](evidence/PREFLIGHT_FINAL.json) 全部成立，随后仅初始化一次窗口与预算。

唯一启动为命令 24：

```text
/usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/c09f01/src/guard.py --role launcher --batch-root /var/lib/dcl-r6/batch05
```

boot `8f92c77b-39bb-4526-a85c-174189b689ce`；T0=3877.668033944，deadline=5677.668033944，stop_at=5617.668033944。资源合同 CPY312-UBU24/1、AS4-PAYLOAD/1；总访问 1,000,000、总窗 1,800 秒、提前停止 T0+1,740、校准软窗 300 秒/100,000、每 payload 进程 AS 1 GiB、payload 父 slice 4 tasks、C09H 硬限 5,000。

执行锁含 16 组 payload argv、34 个原 S worker 模板及 17-unit journal 导出。实际命令完整记录见 [COMMAND_SUMMARY](COMMAND_SUMMARY.md)。31 条 native 调用仅命令 24 启动测试链；resume 调用 0。首次失败后仅查询和封存。PowerShell 辅助函数别名冲突在准备前修正，未导致 native/payload 调用，见 [ADMIN_EVENT](evidence/ADMIN_EVENT.json)。

[源码/输入索引](SOURCE_INDEX.json)、[历史保护](evidence/HISTORY_PROTECTION_CHECK.json)、[实际结果](evidence/ACTUAL_RESULTS.json)。
