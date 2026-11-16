# 复现与证据入口

初始合同于2026-11-04冻结，C02权限补充及文档收口于2026-11-05完成。所有时间顺序的原始日志使用UTC和单调时钟，报告按Asia/Shanghai解释日期。

## 已执行批次

|批次|内容|本机HTTP|新建/删除账户|定位|
|---|---|---:|---:|---|
|run01|N01正常控制、W01迟到刷新结果及B重新授权|117|2 / 2|[结果](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run01/result.json)|
|run02_secretless|C01两步无client_secret刷新与父撤销|50|1 / 1|[结果](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run02_secretless/result.json)|
|run03_listing|C02普通Bearer与应用凭据的同用户过滤查询|32|1 / 1|[结果](D:/毕业设计/research_main_innovation/ci01_contract_audit/raw/run03_listing/result.json)|

总计24次方法请求、140次测量、20次配置/建户、15次清理，共199次。另有22次采样数据库查询、4次清理后只读核对和44次本地签名验证。全部结果、失败返回和额外能力补充进入计数。源码获取的公网请求单列于来源记录。[费用表](D:/毕业设计/research_main_innovation/ci01_contract_audit/COST_ACCOUNTING.json)

`http_and_events.jsonl`为脱敏API原始观察，包含请求路径/字段名、响应安全投影、时间和哈希链。材料只保存摘要，完整秘密值保留于采样进程内存。`runner_visible.jsonl`是运行者投影，`observations.json`或各条件的`*_observations.json`保存独立接受检查。每批都有环境锁、来源摘要和当时源代码快照。

## 只读核验命令

以下命令重新检查已有采样，不产生原生HTTP请求。检查范围包括哈希链、运行者投影、预期观测、C01请求中secret缺省、C02返回句柄对应关系、预算与清理结果。

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\毕业设计\research_main_innovation\ci01_contract_audit\audit_evidence.py'
```

本轮核验得到511条原始事件、44条接受检查、四个测试用户清理成功。该命令会重建本目录的派生事件索引、费用表和核验摘要，原始raw日志保持其采集版本。[核验结果](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVIDENCE_AUDIT.json)

## 原生重采的条件

重采使用已存在的本机Casdoor 4.25.0、l1-study组织及app-l1-0。服务应运行于127.0.0.1:18081，需既有测试管理员和应用凭据。新脚本只创建l1-ci01-*账户。发行包和可执行文件、应用配置、token类型、刷新轮换及userinfo端点会在每批开始核对。

初始两个条件的命令为`collect_evidence.py --run-id run01`，源码补充依次为`collect_secretless_probe.py --run-id run02_secretless`及`collect_listing_probe.py --run-id run03_listing`。两个补充读取前序批次的费用，扣除原预算后再采样。因此重采全套时应在新目录保持这三个批次名，保留原始批次。

```powershell
$auditRoot = 'D:\毕业设计\research_main_innovation\ci01_contract_audit'
$replayRoot = Join-Path $auditRoot 'replay_01'
if (Test-Path -LiteralPath $replayRoot) { throw 'Choose a new replay directory' }
New-Item -ItemType Directory -Path $replayRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $auditRoot 'raw\run01\source_snapshot\collect_evidence.py') -Destination $replayRoot
Copy-Item -LiteralPath (Join-Path $auditRoot 'raw\run01\source_snapshot\MODEL_AND_CONTRACT.md') -Destination $replayRoot
Copy-Item -LiteralPath (Join-Path $auditRoot 'collect_secretless_probe.py'),(Join-Path $auditRoot 'FROZEN_ADDENDUM.json'),(Join-Path $auditRoot 'collect_listing_probe.py'),(Join-Path $auditRoot 'FROZEN_LISTING_ADDENDUM.json'),(Join-Path $auditRoot 'audit_evidence.py') -Destination $replayRoot
$pythonPath = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
& $pythonPath -B (Join-Path $replayRoot 'collect_evidence.py') --run-id run01
& $pythonPath -B (Join-Path $replayRoot 'collect_secretless_probe.py') --run-id run02_secretless
& $pythonPath -B (Join-Path $replayRoot 'collect_listing_probe.py') --run-id run03_listing
& $pythonPath -B (Join-Path $replayRoot 'audit_evidence.py')
```

依赖当前工作区的`auth_lifecycle.experiment.providers/witness/journal`及Python cryptography 50.0.2。运行前应核对这些文件与run01/source_hashes.json所列摘要，源码变化时另建版本登记。每批记录自己的完整依赖快照。工具输出的OBSERVED/UNKNOWN和清理字段是运行事实，命令返回码不能单独替代核验摘要。

在其他主机上重建服务需要既有L1部署流程及新的凭据配置，当前目录提供的是本工作区的可复现取证入口。原生随机token/用户ID与时延可变化，当前保证可核对的对象为声明调度、接口与预期语义。

## 源码取得与版本

公开源码使用只读稀疏克隆，固定提交528a0213f01caf70b9f41009cbf7b2f67bdd67ec。GitHub API曾返回速率限制，连接器也发生传输失败，随后采用公开Git传输取得所需目录。authz/authz.go以同标签的raw入口补取，其Git blob身份与标签对象核对。实际可执行文件与发行ZIP中字节摘要相同，源码到二进制的可复现构建未执行。

原生研究配置和主合同冻结副本在raw/run01/source_snapshot。MODEL_AND_CONTRACT.md后来追加C01/C02能力说明，原冻结副本继续承担采样前规格证据。各批取证源码与快照相符，编辑说明和原始字节身份分别列于交付检查。

## 结果索引

- [MODEL_AND_CONTRACT.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/MODEL_AND_CONTRACT.md)给出选定操作、攻击能力和停止/保留合同。
- [NATIVE_CAPABILITY_MATRIX.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/NATIVE_CAPABILITY_MATRIX.md)给出原生能力、权限与替代成本。
- [EVENT_WITNESS.jsonl](D:/毕业设计/research_main_innovation/ci01_contract_audit/EVENT_WITNESS.jsonl)索引新采样，历史和纸面文件分别保存。
- [OBSERVATION_BOUNDARY.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/OBSERVATION_BOUNDARY.md)限定顺序、角色和材料来源证据。
- [COMPOSITION_OBLIGATIONS.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/COMPOSITION_OBLIGATIONS.md)列出强组合的兼容性前提。
- [STRONG_BASELINE_TRACE.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/STRONG_BASELINE_TRACE.md)将真实动作与纸面判定逐步对应。
- [RESIDUAL_GAP.md](D:/毕业设计/research_main_innovation/ci01_contract_audit/RESIDUAL_GAP.md)与[DECISION.json](D:/毕业设计/research_main_innovation/ci01_contract_audit/DECISION.json)记录研究裁决和改变裁决所需证据。
