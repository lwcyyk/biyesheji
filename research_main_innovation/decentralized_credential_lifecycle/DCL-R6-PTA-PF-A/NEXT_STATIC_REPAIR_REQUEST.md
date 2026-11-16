# 下一最小静态审查范围

Material Passport：DCL-R6-PTA-PF-A；batch12-r3；PTA-PhaseFinalizer-static-1/r3；NORMAL_START；2026-11-12（Asia/Shanghai）；冻结入口1次，源码修改/测试重跑0。

当前为具体补缺请求，未执行代码修复或新动态批次。

1. 修复terminal_inspection到期限读取的接线：只有已认证当前批次的终态只读审查可读取已有state/window；保留boot/身份/源/授权/检查点和期限核验。正常work继续使用严格G.state/stopped守卫。
2. 对CLOSED、STOP_REQUEST、部分初始化、缺checkpoint/错误boot/预算身份及正常active建立相应最小静态回归与独立oracle；禁止靠删除终态守卫或补假T0取得seal。
3. 在源级定义有限的逐次锁版本/取得释放及Root决策日志、行政装载前实际RLIMIT/身份/cgroup/cwd/源和导入时点回执；限制记录数量/字节与原时间合同，重新核算观测成本。
4. 明确正常关闭内部UNKNOWN的含义；如需新增终态状态收敛，必须由原waitpid/角色/预算/原件证据证明，保持旧UNKNOWN记录及native/admin分项规则。
5. 保持预算核心、RootIPC权限、sealed/一次认领、MR管理审查、C09持久ACK、业务源与原资源上限；完整diff/hash/保护语义及新身份模板先静态冻结。

batch12保持关闭，原PT/PF动态通过仅归本次模型/输入范围。后续真实正常关闭/native seal与观测验收需要新独立身份、锁和明确授权。当前不自动恢复C09、MR64、S34、门18或F1/F4。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全与原创性裁决保持。
