# LC：CPY312-UBU24/1运行时合同

2026-11-10。Material Passport：APPROVED_FOR_STATIC_DEPLOYMENT。用户本轮§1明确批准此候选用于L-C；原Python3.14合同保留。当前标签：STATIC_SYNTAX_PASS，RUNTIME_COMPATIBILITY_UNVERIFIED（任务§5亦称COMPATIBILITY_RUNTIME_UNVERIFIED）。

|字段|冻结值/依据|
|---|---|
|解释器|/usr/bin/python3.12；Python3.12.3；LC命令02/03重新核对|
|SHA-256|e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f|
|来源|LR已核python3.12-minimal=3.12.3-1ubuntu0.17，Ubuntu Noble本地包/缓存来源；未新增安装|
|映像/架构|ELF64LE/x86-64，kernel6.18.33.2-microsoft-standard-WSL2；沿用同摘要ELF审查|
|manager|实际255.4-1ubuntu8.18，现有失败范围mnt-e.mount保持|
|启动|-I -S -B，绝对解释器/源码路径；清除LD_PRELOAD/LD_LIBRARY_PATH/LD_AUDIT及PYTHONPATH/HOME的单位环境入口|
|源码|八文件，五业务字节不变；源/缓存/静态manifest/执行锁分别冻结|
|标准库|/usr/lib/python3.12中1224个.py/.pyc/.so代码文件快照；三个UNC符号链接通过Linux原生hash补齐|
|关键运行文件|31项解释器/关键stdlib/直接库/压缩库/工具摘要；ELF直接依赖及来源沿用LR|

完整代码树快照是静态文件清单，实际loader缓存/扩展依赖解析、映射和业务导入仍待动态验收。平台TCB假设包括无并发特权更新/篡改；文件hash也需在未来启动时复核。数据见[LC_STATIC_MANIFEST](evidence/LC_STATIC_MANIFEST.json)、[代码树](evidence/LC_RUNTIME_TREE_LOCK.json)、[LR运行时清单](../DCL-R6-LR/LR_RUNTIME_INVENTORY.md)。

## 语义与I/O合同

业务状态编码仍由未改动的f1_model.canonical执行sort_keys与紧凑分隔、UTF-8编码及SHA-256。dict插入顺序、显式sorted、固定列表/range/product保证的顺序维持原审查范围；费用仍为普通Python整数。-I忽略PYTHONHASHSEED等变量，确定性依靠冻结构造/排序及后续真实状态/轨迹比较。新guard的行政JSON按UTF-8、排序键写入，Linux路径/平台字段区别于Windows报告；原业务输入域与canonical函数保持。

业务输入原计划逐字节复制为inputs/business_plan_original.json，SHA256=2245be87d589e6f5b055b7f19b67f7f757914fae6064d4c1f8a21956c5a36801。其Windows运行时字段是历史记录，当前候选由本合同及静态manifest明确给出。动态生成的业务夹具仍由原五文件/固定调度生成，输出位于本批out/generated_inputs。

## 异常与准入

0为该入口完成；23为明确计划的故障注入；65为校准/结果不完整；124为额度/墙钟中止；125为准入/监督失败；126为监督线程I/O等异常。run_batch原模型错误分类4/5/6保留，整体覆盖不足以FINISHED_WITH_GAPS登记。所有非预期错误停止当前批次；既有失败文件和不确定额度保留。

Root-owned许可、启动票据和资格收据均须与源码/输入/boot_id/实际OS状态结合。AS/pids/UID/capability/NoNewPrivileges/组写权来自原生读取，单个JSON布尔字段无法开放模型门。校准13项的完整原件与摘要链必须齐备，正式准入位于业务import之前。

本轮仅编译，无新模块正文、业务导入或语义测试；AS4首入口/特殊映射/调度与停止假设继续待真实证据。RESOURCE_ENFORCEMENT_UNVERIFIED、MODEL_CHECK_UNRUN。
