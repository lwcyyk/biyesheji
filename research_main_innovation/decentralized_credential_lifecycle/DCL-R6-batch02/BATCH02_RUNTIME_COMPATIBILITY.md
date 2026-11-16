# batch02运行时兼容性证据

2026-11-10。Material Passport：实际入口/资源程序运行，五业务兼容性UNRUN_RESOURCE_GATE。

实际Python3.12.3完成Launcher、Controller、Watchdog及guard_probe的C00/C01。固定路径、摘要、UID999/GID989、隔离参数及Root票据均匹配；这为Linux资源层入口/标准库使用提供真实证据。

冻结程序在13项资格完成前不导入业务模块。C02在持久预付阶段因校准软截止失败，五业务模块的动态加载、输入解析、canonical/JSON、整数费用、DP/参考比较等未执行。用户允许这些检查，但资源/冻结入口的前置条件未满足，失败后按停止规则关闭，未另行执行未冻结脚本。

|项目|实际结果|
|---|---|
|原生解释器/资源层启动|有C00/C01与进程身份/OS限制证据|
|五业务源码/缓存摘要|匹配L-C冻结锁|
|五业务动态导入|UNRUN_RESOURCE_GATE|
|状态/JSON确定性与费用兼容|UNRUN_RESOURCE_GATE|
|与3.14实测等价|未建立，旧3.14版本保留|
|RUNTIME_COMPATIBILITY_FAILED|未观察到；也没有RUNTIME_COMPATIBILITY_PASS|

Gate B02-1=PARTIAL。编译/摘要及资源程序运行不替代五业务语义验证。-I忽略PYTHONHASHSEED的原合同继续适用，当前没有新的确定性运行数据。
