# 状态转换与前缀静态证明

R41_STATE_TRANSITION_AUDIT提供23条具体控制流审查，逐条含pre_state、触发阶段、实际/可能I/O、缓冲、预留、确认/未知字节、post_state、原错误、费用和前缀变化。R41_EXCEPTION_COVERAGE_MATRIX保留R39全部57原ID与R40全部32类，新增本轮token和诊断失败分支另行登记。

## 核心路径

| 触发 | I/O边界与状态 | 费用/前缀 |
|---|---|---|
| 健康已有Journal的容量、reserve截止或停止拒绝 | 精确同步异常绑定，write_possible=false，中心复核通过→PREWRITE_REJECTED/健康 | 字节新charge0；原尝试保持；旧seq/head/bytes及确认保持 |
| reserve成功后io_write前截止 | 同一active token、完整扣费、write尚未可能开始→健康 | 全额charge保留，实际新write0，confirmed保持 |
| 明确序列化guard拒绝 | 仅在纯预检位置且完整健康前提下保持健康 | 构造成本保留，无新字节确认 |
| 路径/权限检查无法确认前缀身份 | 缺少可信拒绝证明→Poison/信任未知 | 原费用保留；新payload可为0 |
| inode/extent/tell或不可解释可见字节冲突 | 即使新write为0也继续Poison | 已扣全长保留 |
| 扣费更新或全局guard间隙 | DEBIT_MUTATING或无认证拒绝→保守阻断 | 部分账本效果保留，退款0 |
| 短写/部分write/原生异常 | may-write标记已跨越→Poison | 全额计费；actual未知及已返回字节分别登记 |
| flush/fsync、write后截止、逻辑发布/ACK中断 | 同样保持Poison | 已知fsync事实和旧确认前缀各保留，未知尾部不重写 |
| 旧Poison、复用/失配token | 健康白名单不成立→Poison | 授权及尝试不重置 |
| 正常确认后日志失败 | 原ACK保留，另一路失败导致整体拒绝 | 原已确认字节保持 |

权限拒绝按实际位置判断。对于缺乏完整所有权证据的路径检查，修复继续保守；普通错误类名本身没有健康特权。任意可修改私有State或伪造可信代码的Python对手超出本次不可变harness合同。

## P1—P6

1. **旧前缀保持。** 认证拒绝要求write尚未可能开始，且流/row/seq/head/bytes/身份及计数与入口一致。新增覆盖、截断、seek、删除或rename原语为0。在独占和旧ACK可信前提下，原字节、顺序、Hash链及确认保持。
2. **虚假提交保持为零。** 认证无write结果为FAILED/false，未绑定或可能write结果为UNKNOWN；成功字段仍只在checkpoint返回原可靠引用后设置。
3. **费用保持。** 原cap与predebit逻辑不变，1008对应新位置的截止拒绝保留全费。账本中charge-minus-confirmed是保守分配上界，与已证实际新write0分别记录。
4. **收尾独立。** 原工作983040、总1048576和保护差65536保持；错误的新Poison被避免。收尾还需原115秒、32次、8320次、原scope/身份及实际包适配。
5. **未知保守。** 可能write之后全部错误及未获认证的身份/计费/token故障保持Poison，旧Poison没有清除路径。
6. **授权单调。** failed record的重入早退不变；原H2、epoch、持久启动消费、invocation及一次性输出源码与全部原55 pin独立保全。

## R40见证复核范围

A01真实路径的已到达健康/适配前缀及调度前提沿用R40。现有reserve同步拒绝能生成本次凭据，包装器保留失败并避免新增Poison；实际不同CASE_EVIDENCE仍需独立适配。完整68输入能否达到该前缀继续未证。

1062字节合成前缀与998461字节请求继续只作Journal接口层见证；大列表没有被提升为真实A01结果。其余量计算沿用原版本范围，未来测试的当前构建源哈希另锁。

同一failed record继续只有一次尝试。多个独立请求若处于已停止工作阶段，会先被WORK_DEADLINE_OR_STOP拒绝；连续terminal容量拒绝照常消耗terminal尝试。未来T12原输入不等式、拒绝与成本义务保持，测试通过重置stop取得结果的做法不在申请范围内。

这些是静态源码与纸面证明。原子native I/O、真实调度和故障注入结果均未在本轮观测，28项继续NOT_RUN。
