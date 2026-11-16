# 28项身份、原预期与量词审定

TOTAL_TESTS=28，UNIQUE_TEST_IDS=28。原ID仍为R40-PC-T01…T28，原顺序、输入、状态/费用/前缀预期逐项原样保留在R42_28_TEST_MANIFEST的frozen_original_row，并附规范化摘要。每项status=NOT_RUN。新增装配字段只描述未来调用、观察及边界。

## 每组装配责任

| ID | 实际受测入口与独立观察 |
|---|---|
| T01—T03 | 实际checkpoint/safe_checkpoint；精确容量拒绝、后续独立terminal包、完整前缀字节及链 |
| T04 | 实际observe_result/commit_case_record；合成A01形状回调，原状态保留与缺失ACK |
| T05—T09 | 实际io_write；观察write进入/接受/返回及flush、fsync故障，分别统计 |
| T10—T11 | 实际checkpoint；属性存储探针在fsync后抛错，覆盖头更新与确认引用返回之前 |
| T12 | 两个独立terminal容量拒绝；同failed record早退，费用和次数不重置 |
| T13—T15 | 回调后reserve截止、扣费后write前截止、terminal准入及write后截止 |
| T16—T18 | receipt上限与一次性路径、收尾再失败、旧Poison保持 |
| T19 | 实际两次小包checkpoint确认；独立解析seq/previous/hash及收到的引用 |
| T20 | 原结果确认缺失时整体验收false；主拒绝与后续证据的I/O计数量词待明确 |
| T21—T24 | 原cap整数、身份冲突、token/边界未知、真实账本赋值中断 |
| T25—T28 | 已确认结果后的日志故障、一次性门、预检/来源拒绝、读取/清理截止 |

54个内部装配变体只细化这些28项既有责任；它们没有获得新的顶层测试身份，也与历史R25等54项suite分别管理。故障arm总次数需要包含准备与收尾，目前没有据此推定已批准上限。

## T20的精确缺口

原行保留 `expected_io_attempts.new_payload_write_calls=0`，同时输入包含“one original result FAILED/UNKNOWN checkpoint plus eventual terminal evidence”。原行没有明确该0适用于主拒绝操作，还是包含后续证据的整个用例。

全程调用数应为 `setup+action+recovery+cleanup`，各项非负。若后续Journal证据实际成功追加，recovery>=1，因而全程>=1。该分支可以同时满足“主拒绝write=0”，但无法同时满足“全程write=0”。如果后续仅观察或被拒，整个动作可以保持0。

本轮裁定为计数范围缺失，未宣称T20必然不可实现，也未发现实际Runner动态失败。原0和原状态全部保留。建议在最小实施批准中明确：0约束主被拒绝结果；准备、收尾、清理及全程数另外如实报告。若研究者要求全程0，应明确选用允许的无成功追加实例。确认前，ORACLE_SCOPE_UNRESOLVED_T20保持，任何动态PASS均不可登记。

## 原输入域与能力边界

T01使用R40的1062字节静态种子及998461字节大列表请求，属于Journal接口数据域。它保持其历史source绑定范围，未被改成真实A01结果或冻结68可达运行。

T04/T13应使用当前源中的真实回调处理方法接收合成A01形状输入。它们不导入或运行原A01测试体，不能据此报告原A01测试PASS。真实已到达结果/前缀的纸面前提仍由R40/R41分别管理。

T12明确采用terminal容量已不足的初始状态，两独立请求均能实际到达容量guard。工作阶段首拒绝后的stop仍保持，后一请求可先被WORK_DEADLINE_OR_STOP拒绝；通过重置stop来伪造重复guard覆盖不在规格内。

T16的实际路径可能先触发行/codec长度guard，再触发reserve；断言保留到达的真实拒绝，不为取得指定错误而替换serializer。T26仅验证纯操作没有触及合成业务能力哨兵并结合源码边界，真实H2许可或持久授权业务操作保持关闭。

原计划没有被删除、合并或改预期。待审定内容是原计数量词和未来执行装配，全部状态仍NOT_RUN。
