# DCL-R6-LR最终裁决

2026-11-10。Material Passport：有限环境/版本查询与静态兼容、权限、适配设计。本轮Linux查询35条，Python仅一次--version；资源配置、依赖安装、验证代码、业务导入、探针/校准/模型均0。

## 1. 明确下一决定

**选L2：推荐复用已安装的原生CPython3.12.3，并申请CPY312-UBU24/1＋L-C静态配置/接入。** 无必须3.14的代码依赖证据，本轮无需安装申请。版本变更保持候选，原3.14要求保留；静态兼容尚未成为实测等价或运行许可。

真实解释器为/usr/bin/python3.12，默认python3指向它；包python3.12-minimal=3.12.3-1ubuntu0.17，ELF64 x86-64，SHA256=`e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`。直接ELF库/标准库关键文件已有本地来源与摘要，完整依赖/映射闭包仍待补锁。有限目录与本地缓存未找到3.13/3.14，范围之外保持未知。

## 2. 部署事实与障碍

实际manager255.4-1ubuntu8.18可查询，状态degraded；失败清单仅列mnt-e.mount，候选部署避开/mnt/e且当前未修复。根与system.slice的AS/资源相关现值未建立所需批次上界；根memory/pids启用、system.slice为domain，但目标父slice/tasks4尚未配置。

root查询与私有socket/目录权限有据，专用dcl-r6用户/组缺失。/var/lib/dcl-r6及batch02路径缺失，/var/lib位于ext4；空间为查询时虚拟文件系统值，持久性/宿主容量/权限封闭继续待核。root cgroup.type不存在符合非根接口范围，原错误保存。

五业务文件保留字节，语法/标准库/状态编码/有序搜索/整数费用的3.12条件兼容已逐项审查。-I忽略PYTHONHASHSEED这一约束已列入合同；后续以实际canonical/轨迹验收确定性。资源三文件仅设计映射表，未修改/生成代码。

## 3. LR验收门

|Gate|状态|边界|
|---|---|---|
|LR-1 运行时定位|CONDITIONAL_PASS|路径/版本/本地包来源/原生ELF/摘要已核；完整来源真实性/扩展依赖闭包与运行映射待证|
|LR-2 兼容性|CONDITIONAL_PASS|五业务静态支持3.12候选；编译/导入/语义/跨版本实测均未执行|
|LR-3 权限部署|PARTIAL|所需单位/身份/目录/资源/代理与持久性条件已具体化；尚无配置及动态证明|
|LR-4 后续路线|PASS_STATIC|L2选择及可直接审阅L-C写入/命令/停止清单已给；batch02最终锁与执行另待|

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；batch02=UNAUTHORIZED；L-C=UNAUTHORIZED；CPY312-UBU24/1=PROPOSED_NOT_ADOPTED。AS4-PAYLOAD/1仍仅原则接受；原WS4 E2=UNRESOLVED；IMPLEMENTATION_GATE=CLOSED；STRICT_SEPARATION_INSTANCES=0。

## 4. 证据与历史

35条argv均在启动前登记、实际调用无shell组合。19/20的getent缺条目、23的根type缺失、25的目录缺失原exit保留；其余31条exit0。一次host等待返回后台session时，后续8个已登记计划在Linux启动前被顺序检查拒绝；等待确认后按原计划顺序各执行一次，无命令重跑，事件单独保存。

原始输出70流、metadata与静态ELF行政读取本地保存；公网仅访问公开官方文档URL，无项目上传。查询耗时合计60.8155828秒，窗口09:39:08.2570889–09:49:25.8153645 UTC，跨度617.5582756秒，均属LR平台准备；没有batch02窗口或费用重置。

batch01原27次/118.7340827秒/关闭deadline、v1/v2/v3、全部失败与ZIP及P/Envelope原件保持。D1-PBFT-SEAL/1.1、D2有限模型条件结论、强G覆盖和I1/I2/I3归档不变。没有新协议反例、PASS_BOUNDED或外部机器认证。

Ubuntu-24.04在授权操作期间运行；末次后的即时发行版状态未额外查，也未主动停止，未请求启动其他发行版或Docker。新boot_id仅在本地留证，未来启动锁不得复用P代次。

## 5. 下一阶段范围

请审[LR_NEXT_AUTHORIZATION](LR_NEXT_AUTHORIZATION.md)：明确接受CPY312候选、创建新专用身份/工作区、装入inactive单位、仅修改资源三文件并做静态语法/配置校验。当前LR任务§3.3、§7–9明确将版本测试、配置和代码适配留给下一专项许可；本次已授权只读工作已完成，无需重复批准。

[运行时清单](LR_RUNTIME_INVENTORY.md)、[兼容审查](LR_PYTHON_COMPATIBILITY_AUDIT.md)、[适配方案](LR_LINUX_ADAPTER_PLAN.md)、[证据索引](EVIDENCE_INDEX.md)、[来源索引](SOURCE_INDEX.json)、[行政核对](evidence/LR_DELIVERY_CHECK.json)。
