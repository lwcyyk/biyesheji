# 最小依赖修复与保留的安全逻辑

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

最终C00Ready-static-1/r2只位于host `D:\毕业设计\DCL-R6-isolated-verification\cr01`，当前Linux部署/查询/服务0。实际依赖：原八项位于boot_continuity.service_confirmed，由C00/C10共用；Guard负责票据发布，必须把有界native lease送入该调用。C10只调整相同启动资格，原业务探针字节保持。

新增service_readiness.py、readiness_regression.py、readiness_oracle.py；Guard接入C00/C10屏障、64回归、FORMAL附加门和明确的最小/完整模式。boot_continuity的service_confirmed委托native lease，保留原service_policy、Owner/boot、BOOT_START/RESUME发布逻辑；仅增加固定ready公共文件目标和新范围检查。

sealed cap的生成/封印/继承/exec代码段、read_capability、ticket_policy、guard_admission、child_admission等保护函数AST保持（命名归一后），同进程C09恢复仅额外阻断诊断模式。RootIPC、C09与BC40仅batch08/cr01命名适配。15份既有程序字节、24预算/资格函数AST保持；五业务、原probe、runner、range核心/夹具/oracle不动。

第一模式C00_DIAGNOSTIC_ONLY：真实C00 READY＋原probe＋64合成检查后close/seal，不授RESOURCE_GATE_PASS。第二模式原完整条件链要求Full_conditional_chain_explicitly_approved；原FORMAL scope与C/S/H/负向门均保留，新增ready证明无法绕过原门。最小模式不要求授权未使用的RootIPC探针或C09恢复。

新包23 Linux源码＋1 Windows入口＋12输入=36项，保持source-only。输入只必要批名/路径/版本/锁与新合同适配，原RootIPC56/C09H34/BC40/S34/门17语义归一相同。r1候选36项与检查保留；最终动态申请仅匹配r2。

[原32项](evidence/original)、[完整source diff](evidence/SOURCE_COMPLETE.diff)、[完整input diff](evidence/INPUT_COMPLETE.diff)、[静态结构检查](evidence/STATIC_CHECKS.json)。
