# MR原生异常关闭覆盖审计

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


MR64原驱动origin=MR-SIMULATION/1，覆盖分类、STOP/CLOSED模型、幂等和UNKNOWN有限夹具。C06/C07/C09提供真实指定故障与期望退出审查；旧C10后diagnostic_marker只让Root scheduler返回78，尚不足以证明新受控systemd未审查失败的完整关闭链。

维护入口run(G,contract)为独立A准备一个当前前缀mr-native-fault.service，复用C10的User/Group/slice/AS/TasksMax/NoNewPrivileges等全部现有sandbox属性。专用worker在当前cgroup内输出boot/PID原始日志后实际exit79。Root先取得active PID/InvocationID，再核failed与相同InvocationID/exit时间，failed集合只允许多出该单位，调用既有historical拒绝规则取得MR_UNREVIEWED_MANAGER_FAILURE。

原生记录保存于既有Root私有BC.Store，RootIPC policy与权限规则保持原字节。测试预付512，随后验证预算保持，写真实来源记录和旧诊断marker，再沿原M.fail/abort→STOP→CLOSED→pidfd/waitpid→native/admin封存。分类函数没有新白名单或跳过分支。原生异常只能终止A。

此故障模型中的MANAGER沿用项目已查明的systemd failed-unit集合语义，实际故障对象为专用Payload服务。systemd/PID1本体失效、Root或独立停止器丢失属于另列故障边界，当前入口不据此授予通过。

入口的授权位、合同摘要、runtime_enabled、scope、版本、精确argv和C10结果均须匹配；当前合同runtime_enabled=false、unit_argv=null、批次/nonce/回执均未签发，hook尚未应用。worker主函数与原生模块导入0，只有AST/compile检查。

[专项入口审查稿](maintenance/mr_native_entry.py) · [合同提案](proposals/MR_NATIVE_CLOSURE_CONTRACT.json) · [未应用hook](evidence/PROPOSED_MR_HOOK.patch)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
