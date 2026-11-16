# DCL-R6-P 最终裁决

2026-11-10。Material Passport：获准的有限WSL2平台资格检查，已完成12条固定命令；11条exit0，Python路径查询exit2。新增资源探针/动态校准/模型/验证代码/资源配置/安装均0。

## 1. 实际结论

Ubuntu-24.04已在授权查询期间运行，实际kernel为**6.18.33.2-microsoft-standard-WSL2**、架构**x86_64**。PID1实际路径为**/usr/lib/systemd/systemd**，工具版本为**systemd255 (255.4-1ubuntu8.18)**。cgroup挂载为**cgroup2**；根controllers含memory/pids，subtree_control含cpu memory pids。

当前查询身份为**root**。root提供管理入口候选，专用非特权payload身份、manager实际控制权限、capabilities和代理封闭尚未认证。拟议活账路径的已观察挂载祖先为ext4，目录/属主/空间/持久性仍待核对。

`/usr/bin/python3.14`和`/usr/local/bin/python3.14`均缺失，登记**NATIVE_PYTHON314_UNAVAILABLE（限定两个获准路径）**。没有追加搜索、版本执行、回退、Windows Python、虚拟环境或安装。因此Linux验证runtime目前无法进入最终锁。

全部命令有WSL localhost代理/NAT警告，原始stdout/stderr按字节保留；混合编码已离线校正，无命令重跑。12次命令顺序/argv与授权相符，无额外Linux命令。末次命令后的即时发行版状态未另查；没有主动停止、shutdown/terminate，也未请求启动其他发行版或Docker。

## 2. Gate P1–P5

|Gate|裁决|证据与边界|
|---|---|---|
|P1 运行平台|PASS_STATIC|kernel/架构/PID1/工具版本的只读审查证据齐备；manager版本属性/稳定启动代次仍待最终锁|
|P2 cgroup|CONDITIONAL_PASS|实际cgroup v2、memory/pids根能力及启用已观察；目标父slice/限制/权限未建立|
|P3 身份及运行时|FAIL|root已观察但部署权限/隔离只部分有据；两个指定native Python3.14路径缺失|
|P4 替代合同|PARTIAL|接口承载平台获得真实证据；A1–A5的有效执行条件仍需配置、映像/权限审计和校准|
|P5 batch02准备|PARTIAL|准确L补缺/申请清单已形成；最终runtime/UID/适配器/全命令锁尚缺|

P1中的PASS_STATIC指平台查询证据审查通过。当前没有RESOURCE_GATE_PASS，也没有AS1GiB与父pids4已共同生效的实例。原Windows WS4的E2=UNRESOLVED继续保留。

## 3. 授权与研究状态

AS4-PAYLOAD/1=**PRINCIPLE_ACCEPTED_FOR_REVIEW**；P=**AUTHORIZED_AND_COMPLETED**；L资源适配/配置=**UNAUTHORIZED**；batch02=**UNAUTHORIZED**。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED为空；IMPLEMENTATION_GATE=CLOSED；STRICT_SEPARATION_INSTANCES=0。D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖与I1/I2/I3归档继续保持。

原batch01的27次、118.7340827秒、关闭/到期状态、v1/v2/v3及所有失败记录均保持。Envelope全目录与四根导航旧版在本轮基线锁和快照中留证；旧manifest原文未改。命令耗时合计21.1719751秒，查询窗口跨度163.1891115秒，只记P平台准备，未建立batch02窗口。

## 4. 下一步

优先审阅[P_NEXT_STAGE_REQUIREMENTS](P_NEXT_STAGE_REQUIREMENTS.md)，先申请L-R的有限只读runtime/身份/manager/目录补缺。若仍缺3.14，形成确切版本/来源/摘要/路径的最小安装申请；已有systemd无需当前追加启用配置。之后才能冻结资源单位、Linux接入、全部输入/命令与正式合同，申请batch02实际配置/校准及条件F1→F4。

保留下一阶段许可的依据直接来自本次授权§1、§4、§5、§8、§11：P只覆盖12条平台查询，额外命令、安装、配置、代码适配和模型执行各需匹配授权。本次P范围已完整执行，无须重复申请。

交付：[README](README.md)、[命令总记录](evidence/P_COMMAND_RESULTS.json)、[前提矩阵](P_AS4_ASSUMPTION_MATRIX.md)、[来源/证据索引](SOURCE_INDEX.json)、[行政核对](evidence/P_DELIVERY_CHECK.json)。
