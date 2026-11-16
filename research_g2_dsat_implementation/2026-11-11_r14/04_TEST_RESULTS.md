# H1冻结24项实际验收

最终来源：`2026-11-11_r13_h1_offline/run_004/RESULTS.json`及stdout.log；本目录H1_ACTUAL_RESULTS为原字节副本。

| 口径 | 最终结果 |
|---|---|
| 冻结ID/实际执行 | H01–H24，24/24 |
| PASS / FAIL / ERROR / SKIP / NOT_RUN | 24 / 0 / 0 / 0 / 0 |
| 内部检查 | 1361条，全部满足 |
| 新增独立测试 | 0；所有子场景归属原冻结用例 |
| 实际隔离审计 | SQLite/network/process/private-file/越界write尝试均0 |
| 旧测试/真实调用 | 0 |

## 四轮记录与修复

| run | 结果 | 实际变化 |
|---|---|---|
| 001 | 24 PASS | 首次实现；既有H13覆盖日志/key/decode/host-audit失败 |
| 002 | 23 PASS、1 FAIL | H13补核适配器返回边界故障，发现已发生读的额度增量被报告为0 |
| 003 | 24 PASS | 新宿主read_summary用finally保留已消耗额度，故障结果丢弃业务数据 |
| 004 | 24 PASS | 跨任务创建者phase/预算改为与窗口unknown记录一致；并发证据保存实际线程标识；最终冻结 |

run_002失败断言是OPERATION_DELTA_EXACT_SEPARATE_FROM_WORLD，原始错误栈、输入hash、源码快照和JSON保持。其该次调用在检查失败时中止，calls列表尚未追加完整逐调用条目；这一记录局限保留，未补造原始观测。run_003/004同一故障场景的完整费用、摘要与状态已实际记录。

原R13用例ID、name、expected、关联B1用例和范围作为R13_original_case逐项保留；嵌套原execution_status=NOT_RUN表示历史计划。外层status/executed表示本轮实际结果，避免改写冻结计划。

## 24项与不变量

| 用例 | 实际验证重点 |
|---|---|
| H01–H04 | 注册来源、已认证身份对象、正文伪造拒绝、有效期/撤回 |
| H05–H09 | 精确tuple、跨账户/任务/caller/generation、笛卡尔积、选择器及同tuple额外grant拒绝 |
| H10–H15 | 4线程受锁读、危险入口0、1+6配额、全部故障计费、事务拒绝、未知Schema/真实source注册拒绝 |
| H16–H18 | 私有codec边界、所有公开sink、上下文序列化拒绝、严格白名单、世界与遥测/额度分离、深拷贝 |
| H19–H21 | 撤回排序、同permit并发重放、reader/epoch/producer/locator替换拒绝 |
| H22–H24 | 输出/记录资源界、历史读取权独立、版本/来源/旧CLOSED、未知保持、业务写操作拒绝、软期限 |

H1-P1对应H01–H09/H23；P2对应全部常规世界hash及H10/H19/H20批次；P3对应H12/H13/H18；P4对应所有公开sink和H16/H17；P5/P6对应H05/H09/H21/H24；P7对应H10/H19/H20；P8对应H05/H24及旧文件保护；P9对应所有摘要固定缺口与H24；P10对应runner审计和H11/H15。

## 状态与测试结果分开

73份常规响应中14份STAGING_READY_WITH_GAPS，59份为按预期的拒绝、资源或UNKNOWN类结果。3组并发/排序场景另产生7份响应（6份ready、1份replay），合计80份输出。业务拒绝不计作测试FAIL。

常规业务分类：REJECT_UNAUTHORIZED 7、INSUFFICIENT_SCOPE 7、BUDGET_EXHAUSTED 2、SOURCE_BINDING_FAILED 9、UNKNOWN_PENDING 34、ready 14。分类在outcome_category定义；精确wire状态和逐调用费用见JSON，不按分类推断原生效果。

最终所有结果的秘密/外scope标识扫描CLEAN。该结论限已登记合成canary及输入族；真实状态字段、秘密域和OS隔离仍待H2。追加的窗口阶段一致性只校正手写夹具，完整Authority历史与原生材料验证继续超出H1。
