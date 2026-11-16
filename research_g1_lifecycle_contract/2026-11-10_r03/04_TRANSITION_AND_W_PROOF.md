# 转换、P1—P8与W屏障

## 1. 纸面关系与量词

固定00的源/身份/读取/创建/独立/有效窗口条件及03的一次有限过程。关系R(s,n)由已观察过程阶段、固定绑定、保守余额、责任及安全谓词决定；n的具体化包含所有相容未观察AS进度。读到可信c后还需真实原ID到c槽的映射。对任意相关真实s和本例允许动作，每个同观察真实后继均与列出的某后继节点相关；安全与终态在下面条件下反映真实scope。

额外原生动作、重试、派生、到期/另行批准变化等需扩关系或退出当前scope。隐蔽前提违约没有自动检测证明，本包含定理只覆盖满足条件的执行。给出全部保守分支并不自动使每条表路径都可由真实服务实现，所以一般只主张安全充分性。

## 2. P1 初始覆盖

命题：E0的已知账本可映到展示节点s0；研究模型实际从既成LOST接管，每个W0/W1/W2映入K_U，K非空。s0的条件化LOST边不承担前瞻原生Refresh全部结果的覆盖证明。

证明：三个u锚保留未发、未完成、已创建的全部类别，父状态差异并入最坏责任，所有类别均spent1/无返还。真实W1f无创建也可保守映为未结类。状态CONSERVATIVELY_EMBEDDABLE；真实快照/完整请求投影仍SOURCE_OR_REFINEMENT_GAP。

## 3. P2 观察保持

命题：LOST不排除潜在/已创建c。源码branches/expand对同一观察取目标并集，因此K_U包含三个u；没有按隐藏发生点选一个u的接口。

用户撤回只使全部u转v并撤回ap_a，未结责任保持。NO_BOUND_RECORD/NO_DELIVERY只记没有取得绑定证据；它们不产生C_native终态。可靠迟到变k须验证原i/来源/代次和直接容量，不按返回时间迁移到乙。源外观察使boundary，停止使用当前证书。状态EXACTLY_EMBEDDABLE（并集规则），场景整体为保守表示。

## 4. P3 预算保持

命题：release后a_slots由1变0，native_calls由9变8，LOST与以后撤回不退回；B槽独立保存。后续native余额按3/1/0/3/1的最坏宏收费。

证明逐边预算delta：u/v余额(0,1,8)，d(0,1,5)，n/x/k(0,1,4)，cd/fc(0,1,1)，t/fb(0,0,0)，observe_late不变。成本相同而实际分支请求更少时，模型以已预付最坏预算作保守下界，不冒充真实精确剩余。c_i=1作为另一个有限事实/外部定理，不等于native剩余或放行槽。状态CONSERVATIVELY_EMBEDDABLE；RPC/计算与当前A多资源入口另有缺口。

## 5. P4 来源保持

命题：所有节点保持bind_i_rA_gA_v0_p；k中的c仍归原i/甲旧批准。证明逐边固定事实不删除、不添加新批准；迟到只加入c绑定/容量饱和和待处置引用，ap_a仍缺失，不能使甲重新使用c。

原生真实性来自受权映射和R02 record/验证，标签本身不验证签名/完整origin。固定有限来源在L0可EXACTLY_EMBEDDABLE，真实字段到标签的当前接口仍SOURCE_OR_REFINEMENT_GAP。

## 6. P5 本地撤销安全

命题：撤回观察可靠时v及后续不含ap_a，release_refresh需要ap_a且refresh_ready已消失/槽已用完，故该模型中没有甲的新refresh。老i的AS推进仍被保留。C_local由真实权威撤回提交和新放行截止反映。

语法表示可EXACTLY_EMBEDDABLE；“把撤回当作必须经过当前W门的可选动作”存在下面反例。真实持久Controller目前独立处理撤回，本轮不把该接线障碍写成现有产品撤回失败。

## 7. P6 独立乙保留

命题：B-independent与B-window成立时，本例全部节点support:b及ap_b保持，p/c处置不破坏乙支持；t还记录一次真实UserInfo接受。

同一场景的PAPER_PROGRESS_SLICE进一步显式给出pending_revoked上的use_b_while_pending：它即时满足ap_b、预算和独立性守卫，后继保留settle:i和父处置义务。因而“乙动作可表示”和“甲未结责任持续”可以在同一raw表共存；能否经当前W门派发另判。

证明模型delta没有移除support:b/ap_b，原生反映依独立影响域和有效窗口。B_UNCERTAIN不证明业务完成，fb不terminal；持续刷新或超窗口可用性另证。没有B-window时，需加入到期/环境失效后的unsafe分支，不能继续保留当前全状态安全结论。状态为有限条件CONSERVATIVELY_EMBEDDABLE。

## 8. P7 严格责任保持

命题：v/d/n/x/ne仍有settle:i；父处置不消除此义务。只有绑定真实不同c并饱和直接容量后将settle:i换成close:material:c；c处置未知保留它，处置已证后才移除。

证据是完整JSON delta和R02容量饱和定理。未登记后代/新尝试不属于c_i=1，必须另入I/义务；否则A_native_closed不能可靠反映。L0普通义务和配对close义务已足够；A opaque源样例则始终保留，产生额外无法完成。状态CONSERVATIVELY_EMBEDDABLE。

## 9. P8 终态

本例Terminal仅t：全K安全、A_native_closed/B_operation_observed齐全、义务为空。cd虽原生范围关闭但乙观察未完成；fb无乙成功；未结节点均非终态。

若R关系和R02失效/封口条件成立，terminal反映C_local、限定p/c接受路径的C_native及一次乙成功；它不反映C_effect、全部RP或无限后代关闭。全称K＋严格义务防止从某个有利世界提前成功。状态CONSERVATIVELY_EMBEDDABLE；没有原生假设时标SOURCE_OR_REFINEMENT_GAP。

## 10. W_h手工推导：表示成功仍可能无胜策

按照现有语义，W_0=Terminal；W_(h+1)包含Terminal及存在合法动作、其所有观察后继都在W_h的知识状态。boundary/空K不能成功。

在本例纸面表，fp/x/ne/fc/fb均非终态且没有后续动作，因此任意h都不属于W_h。cd唯一动作use_b有B_UNCERTAIN→fb，故cd无有界全观察胜策；k有C_DISPOSAL_UNKNOWN→fc；n有NO_DELIVERY→ne；d有QUERY_UNKNOWN→x；v有P_DISPOSAL_UNKNOWN→fp；逐级得到u类及s0均无有界全观察胜策。证明只展开这些显式反例分支，不运行搜索，也不声称真实任务普遍不可完成。

即使把执行看作已经达到K_U，withdraw_a即时合法且保持B/义务，但其唯一后继v不在W_(h−1)。因此在合同摘要/adapter绑定正确且参考完全求解的条件下，BoundedController.step会按源码返回REJECTED/successor_not_bounded_winning；A.Shield.menu也不收录该动作。限额耗尽还可能先得到INCONCLUSIVE，这同样不授权派发。

这符合当前“保证有界完整成功”的设计，并揭示本次接线路线的目标差异：用户强制撤回、独立合法服务与未决责任托管，要求允许安全部分进展，当前全局关闭W门未提供这类保证。调整目标为仅C_local也不能直接把settle:i留着宣告全局terminal，因为现有terminal要求所有义务为空；需要分scope审计或运行层独立事件接口。

本轮完整表路径是纸面观察轨迹，不能称为已由W门实际派发的策略。FEASIBLE成功路径与“对全部允许观察保证成功”分别管理。该路由为UNSUPPORTED_BY_CURRENT_SEMANTICS，图的保守表达仍成立。

## 11. 局部进展切片的更小证明

在PAPER_PROGRESS_SLICE，成功节点revoked_b_observed已具备全部局部goal事实，却仍有settle:i和close:handle:p，因此现有terminal将它排除在W_0外。四个节点没有任何能结清这些义务的动作，任意h的W_h均为空。即便乙成功被保证，这个“局部完成＋全局未结”的单表严格终态仍不成立。

这只排除“同一模型中保留全部严格义务，同时把局部完成作为全局terminal”的路线。可以另行设计分scope视图/证书，并由可信全局台账持续托管原义务；须证明视图分离没有遗漏责任、当前批准与动作守卫保持。现有schema外的审计状态或多个模型组合未被本例排除。
