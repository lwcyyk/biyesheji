# 下一轮运行时适配与准入范围

Material Passport：DCL-R6-TR-A；batch13-r1；TerminalRead-static-1/r1；2026-11-13（Asia/Shanghai）；冻结入口1次、退出125、源码修改/测试重跑0。

本文件为具体后续请求，当前没有修改、安装、降级或新执行授权。

1. 以只读导出的3个现行文件、1241对象核对和包日志为依据，审查glibc2.39-0ubuntu8.12及其相关ABI/映射/资源计量/信号与Root TCB假设。验证当前包来源与完整闭包，必要时补齐/lib与/usr/lib合并路径的元数据归属。
2. 保持旧r1及历史所有hash冻结，在独立候选中更新受影响runtime_files/runtime_critical/runtime_tree_lock、相关输入与执行锁DAG；不能只改第一次命中的一个loader hash。
3. 证明原CPY312-UBU24/1、AS4-PAYLOAD/1、1GiB/父4tasks、1800/300/120与访问界的适用范围。若合同影响超出有限适配，明确提交补充授权。
4. 终态读取/活动态拒绝/native/admin原有源码及PT/PF/TR判据优先保持；如需更改代码另列最小diff与原因。
5. 重新静态核验、冻结新独立身份与准确argv，再申请正常WORK/C00/PT64/PF48/TR40/CLOSED/readonly/native/admin的有限动态验收。

当前batch13/control保留为已执行且封存的预检失败attempt。新运行时资格未审查前，不能继续现回执、重置预算或执行MR/C09/S34/门18/F1/F4。当前Source未进入运行窗口，这一事实不构成额外免费重跑许可。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2安全与原创性结论保持。
