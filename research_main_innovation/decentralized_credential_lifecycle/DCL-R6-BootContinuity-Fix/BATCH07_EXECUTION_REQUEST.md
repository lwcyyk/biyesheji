# batch07独立部署、平台核验与动态执行申请

Material Passport：BootContinuity-static-1/r4；host离线静态修复；2026-11-11；WSL查询/目标执行0。

本文件为可审阅申请，当前许可范围仍是静态工作。绑定BootContinuity-static-1/r4及下列实际hash；batch06保持原预检失败，无原窗口可恢复。

|锁|SHA-256|
|---|---|
|static_manifest.json|4cfebfbcd17fd39addbbab6a826ffec24d4cf8f586dfdd230c4cf397519e5863|
|execution_lock.json|4a71cd1135a82f46ae07fdb3abf49376732b6894b1fc00dc6d6accb9dda961fe|
|boot_contract.json|bc500b4512e3fb8bb2ddb966433ab20ebbe066caade04a944c23eba202065b40|
|root_ipc_contract.json|c402def08f2b7f9e81b077ab15dc50ce0dd73464cf53b4d5459a0336c914e3b3|
|c09_contract.json|649c71b6a56f2f61a4929e013b26a83833b0ebd5f5d410c600a61d20ec0aebe3|
|safety_contract.json|21366eb093350abea8ec808a009b4854b8d4334085693b7e497fafc1b903793b|

请求范围：部署bc01源模式包（31个Linux文件，Root0拥有、目录0755/文件0644，禁止残留pyc）、当前平台只读接口/权限核验、单会话受信Root入口及memfd/exec继承验证、同进程C09一次恢复、新40项模拟回归、全部原C/C09H/RootIPC/S/17门链和资源资格后自动F1→F4。原RootIPC顺序探针最多1个、UID999/GID989及现有65534身份保持原授权模型。

本轮未检查当前WSL环境。未来预检fresh核Python3.12.3/e50d…150f、原32关键文件与1224树、kernel6.18.33.2、systemd255.4、cgroup2/page4096、当前UID/GID/ACL/临时对象/残留、boot与Owner。原生3.12语法编译在入口内只生成内存代码对象，不运行模型，不修改冻结源或产生pyc。任何漂移、缺失接口、封印/继承错误或不确定状态即停止。

Windows唯一入口：

```text
python -X utf8 D:\毕业设计\DCL-R6-isolated-verification\bc01\host\windows_entry.py --activate
```

其内部唯一WSL argv：

```text
C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/bc01/src/boot_continuity.py --activate --batch-root /var/lib/dcl-r6/batch07
```

授权原文/回执在未来host batch07研究目录准备，原始路径由execution_lock固定；[模板](evidence/BATCH07_AUTHORIZATION_TEMPLATE.json)批准位及原文hash当前为空，无法作为执行许可。Linux入口完成实际六条冻结准备和授权安装；本轮不会提前创建batch07或安装其单位。新boot私有子目录由入口按Root:Root/0700受控创建。

TCB/资源差异：无新增常驻进程或服务，Linux预检入口exec后就是原Root父协调器；预检在T0之前单列最长120秒、入口设置AS1GiB，初始激活ticket最长10秒。C09验证后在同一个Root进程内调用一次原resume路径，不再调用第二次WSL。原预检/当前实例首映像、可信部署/loader、存储、调度条件保留；当前尚无硬实时认证。

运行合同保持总访问1000000、T0后1800秒、T0+1740停止、校准300秒/100000、payload AS1GiB/父slice4tasks、AS4-PAYLOAD/1条件。Boot40预付/Root重算完成481、硬限512；C09H2245＋RootIPC505＋BC481=3231，三阶段共同硬限5000，校准硬界62034保持。预检TCB不构成运行窗扩展，绝不重置已存在T0或预算。

执行关系：部署资格→单次WSL当前boot预检/准备/exec→Root接入→C00–C08→C09H34/Root审查→RootIPC56→BC40/独立审查→真实C09持久ACK/waitpid/fresh-read/一次分类→同进程同窗一次恢复→C10–C12→S34→17门→RESOURCE_GATE_PASS→F1→F4→停止与父最终seal。所有前置缺证/FAIL/UNRUN/变异未检出阻断正式业务导入。

首次关键失败保存当前boot/PID/fd/认领/单位/预算/时钟及完整双流，按原停止/回收合同关闭已开始的窗口；未开始则保留准备与失败记录。禁止自动重试、新窗口、改锁/权限/阈值续跑、复用CLOSED或自动创建下一批。模拟重启测试不发出真实shutdown/terminate；如要定位宿主触发者，需另列只读诊断或实际生命周期测试授权。

F2/F3、Casdoor、T1–T4、真实账户/凭据、依赖安装、WSL全局配置、无关单位、误副本处置和外发不在申请内。D1/强G原条件、严格分离0、IMPLEMENTATION_GATE=CLOSED保持。
