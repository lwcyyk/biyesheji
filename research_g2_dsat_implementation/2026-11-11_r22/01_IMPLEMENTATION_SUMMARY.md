# G2-R22补充实现摘要

执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。

当前裁决：**D1B1_PARTIAL_IMPLEMENTATION**。当前选定122项执行结果：**121 PASS、1 ERROR（原始记录保留，修复后的54项尚未完整验收）**。


严格修改原五个Python文件：live、lifecycle、Windows provider、新test、新runner；在原fixture子树追加R22_SUPPLEMENTAL_CASES.json。services.py、storage.py、launcher及其他源码保持。六目标锁见R22_SCOPE_LOCK.json。

资源准备/初始化与运行所有权分开。独立进程从持久instance、seed descriptor、marker和单动作批准重新接纳；启动前在实际OS独占锁内校验并持久消费。消费、启动成功、资源停止和拥有进程退出分别表示。

真实独立进程见证覆盖旧marker/epoch、已消费重放、崩溃后CLAIMED、别名、截断/缺失/损坏记录。F24强化为两真实进程争用同一动作批准，T41验证跨进程有界Status/Stop，P2总额0。

首轮54项53 PASS、F24一项ERROR：败者已退出，stdin.close刷新时报OSError22。已有最小修复，只在精确拥有子进程已退出时接纳该关闭结果。完整失败及修复前快照保留。

D1-A24和A1/H1 44已实际重跑通过。额外重跑以ADDITIONAL_RUN_REQUEST和实际独立批准为准；未得到批准时三次上限保持。任何已完成追加运行均在R22_TEST_RUNS列出。

所有执行均为本轮新临时对象和测试子进程。真实Authority服务、正式部署根、网络监听/RPC、生产DB/key、P1/P2/S3-B2/S5均未开放。
