# 原件保全与独立校验边界

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


旧ra01的64/64份实际文件与最终锁逐字节相同，D1/D2、五业务、预算核心、RootIPC权限、C09 ACK、C00Ready、Boot、PreT0/PT/PF、TerminalRead及既有MR分类均保持原字节。新代码限于4份独立维护/验收组件，MR hook只保存为审查patch。

TR-A2真实native233条与行政249条manifest均按现存原始文件重新计算SHA，FullChain-B证据ZIP122文件/123成员逐项验证。新增主机fixture写在本轮目录，源输入与历史运行账保持只读。历史基线9439份文件与四份导航原件已保存，交付时执行前后摘要核对。

证据清单区分ACTUAL_HISTORICAL_FILE与STATIC_PATH_WITNESS。相同历史摘要只建立内容等价候选组，当前删除/去重/跨批次替换0。计划文件的未知SHA/字节保持null，独立校验字段标记仅路径静态证明。

新增archive组件保持逐成员检查，额外拒绝多种非法表示；它未改变现有终态work_allowed、CLOSED吸收性或native_ready义务。原生环境与权限/退出/封存行为继续UNRUN，主机检查无法授予这些性质。

[64份保全核验](evidence/PROTECTED_SEMANTICS_CHECK.json) · [实际新增diff](evidence/ACTUAL_ADDITIONS.patch) · [未应用MR hook](evidence/PROPOSED_MR_HOOK.patch)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
