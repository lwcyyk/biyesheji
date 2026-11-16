# LR：三资源文件的最小Linux接入设计

2026-11-10。Material Passport：STATIC_DESIGN_ONLY；新增程序代码0，历史v1/v2/v3不改。当前v3 guard仍主动拒绝，没有可直接运行的完整Linux监督器。

## 1. 模块映射

|现有模块/责任|Linux对应机制|前置条件|未来修改点|验证方法（当前未执行）|
|---|---|---|---|---|
|guard.py顶层WinDLL/msvcrt/_winapi|Linux分支采用标准库fcntl/resource/os/signal等；外部systemd强制包络|明确平台、native runtime和源锁|平台判断先于Windows导入；保留ROOT/LimitReached/write/digest等业务API|源码/依赖审查、获准语法检查，随后受限导入|
|Job/HardWS/CreateProcess|manager设置LimitAS、父slice TasksMax，组继承与unit启动|初始映像/全部映射/权限/角色已审|删除Linux路径对Job对象的依赖；Windows原版归档不动|exec前属性、继承/第五task、迁移/逃逸校准|
|proc_memory/identity|/proc limits/stat/status/smaps、boot_id、pidfd；cgroup membership|权限可读、身份稳定|保留查询窗口、活时/退出后字段；RSS、AS、charge分别命名|固定PID复用/退出/峰值场景；pidfd不可用则拒绝静默降级|
|Job信息|父/子cgroup current/peak/events/pids/procs/events|真实路径和祖先锁定|读取实际文件/单位属性，禁止配置值充任actual|完整/截断/权限失败均记录；采样只作观测|
|Budget/locking|fcntl锁＋原二进制计数格式＋持久预留journal|ext4目录/唯一批次身份/单账deadline|O_BINARY等Windows标志隔离；短写/文件与目录fsync/模糊意图即停|并发/第18次/事务故障、真实总账不可回滚|
|watchdog/handles|同组W、pidfd/pipe租约、manager外部停止事件|C/W全部受AS/pids约束|双向异常检测，W死或C失联停grant/整组终止|C/W/Launcher崩溃、阻塞、子孙/绝对时限矩阵|
|guard_probe.py|保留mode目的，改为Linux映射/AS/组/权限/IO故障探针|有独立新批次授权及启动前包络|移除WinAPI引用；局部低AS测试先受全局包络|完整C00–C12，失败/INCONCLUSIVE不授门|
|run_batch.py|原顺序/预算包装与Linux观测接入|formal admission先于业务import|仅资源接线、来源/字段/关闭与全局结果传播|调用/收费点diff，输入/顺序/五业务hash及中断校准|

## 2. 独立启动与解释器变化

run_batch现有require_formal_admission的位置保留在业务import之前。Linux接入须同时核对：root-owned授权/源/runtime清单、boot_id/批次身份/绝对deadline、实际父slice与子unit归属、AS软硬值、祖先pids限额、有效W/租约，以及与相同源码/输入/配置摘要绑定的真实资格收据。

单独启动run_batch、编辑JSON状态或复制旧目录均无法替代实际内核事实。新目录的时间/计数由获准外部TCB初始化，普通模块不自动建窗；缺任何证据即拒绝，且不得在拒绝前处理模型状态。管理员被列入TCB，当前模型针对固定审过的验证程序/故障，未给恶意管理员或任意代码沙箱的一般安全证明。

外部Launcher在exec前复核runtime文件/标准库闭包摘要；payload再核对sys.executable/版本、源锁与当前组。无解释器/loader/权限或exec失败时由manager状态取证，C/W握手缺失便关闭，禁止自动换版本、自动重启或补窗。TOCTOU需依赖只读/受控更新策略，单次sha读取无法独立消除它。

## 3. 时间、停止与持久性

原Windows perf_counter/QPC字段不跨平台复用。新时间锁采用同一boot_id下的指定时钟，T0先于首次批次激活；1740秒提前停止，1800秒统一窗口。RuntimeMaxSec按active期计时，只作次级停止；外部manager停止事件独立于C/W/Launcher客户端。其目标单位、clock/挂起行为和整棵slice停止语义在L-C锁定、未来动态校准验证。

每个case完成/预期故障后必须确认空组再进入下一case。异常未知/退出未确认/真实账模糊即整批关闭；不得由普通watchdog无限公平性假设推出固定停止延迟。LimitCORE=0与core_pattern管道helper、特殊映射和系统辅助进程仍需审查，避免漏记外部角色。

文件写入分别处理完整写/flush/fsync/rename及父目录fsync，日志失败与计数失败统一关闭。崩溃后的模糊grant保持占用，重启boot_id变化拒绝恢复。实际WSL/ext4持久性与故障校准尚未发生。

## 4. 保留业务与当前边界

不改变任何F1转换/INV、ghost来源、F4 Post/终态/压缩/代价/独立解释器、输入域或参数。资源接入不得以“移植”名义共享DP与参考的语义函数，或把soft cutoff/缺变异检测登记为完成。新CPY312合同只改变运行时前提，原3.14/WS4/失败记录保持。

未来写入仅新L-C工作区的guard.py、guard_probe.py、run_batch.py；五业务文件只复制并核对原字节。其他新helper代码/第三方包/loader改动均超出该最小范围。当前仅本文和证据文档，不生成可执行代码、service文件或新的监督器版本。
