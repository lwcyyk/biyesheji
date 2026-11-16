# R6-B-Repair最终裁决

2026-11-10。完成原证据逐项核对、API/ABI/时窗审查、v3资源代码静态修订、严格界的条件证明/缺口和新批次申请草案。本轮**新增校准0、正式模型0、Python导入/语法试跑0**。batch01已到期并保持关闭；F1/F4继续UNRUN_RESOURCE_GATE。

## 1. 四项Gate

|Gate|裁决|依据与边界|
|---|---|---|
|RG-1 根因审查|CONDITIONAL_PASS|源码/API/原日志链已重建，ABI静态相容、释放/退出时窗混合及准入缺口可定位；87和两个峰值异常的唯一内部原因仍未认证|
|RG-2 监督器修复|PARTIAL|v3只改资源三文件，五个业务文件hash一致；观测/账/关闭/准入防护已静态修补；平台包络适配器和完整运行接线未完成|
|RG-3 硬资源资格|UNRUN，保持RESOURCE_GATE_FAILED|原批到期，新批未授权，v3未执行；严格启动及峰值界尚有未决项，不能授PASS|
|RG-4 模型验证资格|UNRUN_RESOURCE_GATE|资源证明、完整校准和新批次许可均未齐；F1/F4恢复条件未满足|

## 2. 已确认的增量

1. 原ZIP60项、59条manifest及manifest本身、批次62个原文件和R6-B研究63项锁核对通过。原evidence目录缺失属实际布局，证据位于root/reports/raw/calibration。
2. class9、Windows AMD64/LLP64下64/144/80结构布局与SDK静态相容；v1失败早于进程Job关联。v2成功不证明错误87唯一原因。16页min与20页读回的差异明确，因果仍待单因素验证。
3. memory sub Job在首成员关联前已设限额，不能用“旧成员先占用”默认解释其峰值。失败分配入账/暂态计账仍为假说。
4. 子统计确实在chunks.clear之后，父统计又在进程退出后；两者不能描述五块仍保留时的内存。PeakWS没有设置前/后窗口，4KiB与页大小相等不足以证明根因。
5. 原控制器自启动窗、WD异常联动、单独调用run_batch、计数短写/中断和重复批次初始化均有可定位控制缺口。v3增强观测和拒绝，未用配置值或JSON开关制造资格。

## 3. v3的实际交付边界

静态候选保存在batch01/versions/v3，保留v1/v2、batch01/src及所有失败原件。只修改guard.py、guard_probe.py、run_batch.py资源接入；各静态发布稿均有hash/差异历史。业务转换、不变量、F4候选与参考、冻结输入全部未改。

v3提供分阶段当前/Peak/身份观测、分配前后仍持有快照、Native reserve/commit诊断候选、预留journal、关闭/到期拒绝、-S依赖隔离及模型前准入防护。**严格启动包络适配器未实现，main/calibrate的正式入口有意保持拒绝**。这是部分静态修复，尚无可运行的完整RESOURCE_GATE_PASS监督器，语法/动态正确性也未认证。

## 4. 原账与授权

batch01原deadline为05:32:39.337 UTC/13:32:39.337 Asia/Shanghai，本轮只读检查时已过期。27次访问、118.7340827秒历史实际消耗、原计数/deadline均不改。剩余999973不授予重启资格。本轮没有新会话免费窗口，没有创建batch02。

当前用户允许的是根因分析/静态资源修补/准入计划。新校准或正式模型需要独立新批次许可；这项要求来自本任务§5.3及§8，和旧F1/F4许可是否存在分开。申请草案见[NEXT_BATCH_AUTHORIZATION.md](NEXT_BATCH_AUTHORIZATION.md)，且授权本身仍不能替缺失资源证明。

## 5. 恢复路线

先解决从第一个controller开始的前置内核资源包络与全角色合成界，再锁定平台/版本并授权新诊断批次，完成全部必要校准。Windows现有自限路径的启动窗未证，当前停止把它视作可直接准入的路线。

全地址空间界＋不可提高的任务数界可提供更强条件引理；本机只发现Docker/WSL CLI，未认证后端。官方不支持Docker CLI as选项，不能给出该快捷运行方案。任何OCI/受控平台的指标映射、首入口限制及所有辅助角色都需实际证明/单独授权；当前未启环境、未下载。

只有RG-3全部通过且有有效新批次许可，才能按原F1→F4恢复。现阶段没有PASS_BOUNDED、没有新协议反例/缺陷证据，1.1保留；强G覆盖、I1/I2/I3归档、严格分离0和IMPLEMENTATION_GATE=CLOSED保持。F2/F3、Casdoor、原生T1–T4、真实凭据、外部发送均未执行。

## 6. 交付与复核

[根因审查](RESOURCE_FAILURE_ROOT_CAUSE.md)、[API计账审计](WINDOWS_MEMORY_ACCOUNTING_AUDIT.md)、[严格界/缺口](RESOURCE_BOUND_PROOF.md)、[v3变更](GUARD_V3_CHANGELOG.md)、[重试矩阵](CALIBRATION_RETRY_PLAN.md)、[旧账锁](BATCH01_ACCOUNTING_LOCK.md)及[来源索引](SOURCE_INDEX.json)组成当前交付。

证据/源码哈希和链接核对属于ADMIN_CHECK，不能填充校准actual字段或升级为机器证明。独立外部审查/一般机器证明继续为0，未把本轮同会话静态审查登记为外部认证。
