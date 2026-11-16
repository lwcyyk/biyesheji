# R40最终静态裁决

**R40_PATCH_SPEC_READY。已确认局部Write前拒绝的Poison分类缺陷，冻结五函数最小修复合同和28项未来验证责任。本轮源码修改0、动态测试0、EXECUTION_AUTHORIZED=false。**

最关键证据为Runner668、899的无条件Poison，以及1008前置截止仍进入1023的内层Poison。975和992的指定同步拒绝在payload-write和字节扣费前；1008处则保留此前已扣费用。健康已确认前缀能够保持，当前处理器却关闭了合格的既有收尾提交资格。

## 分层裁决

| 项 | 本轮结论 |
|---|---|
| R40_PATCH_SPEC_READY | true；可独立申请维护补丁及静态复核 |
| R40_PREFIX_COUNTEREXAMPLE_CONFIRMED | true；限已确认前缀局部模型；完整冻结输入可达性继续未证 |
| R40_PREWRITE_CLASSIFICATION_PROVED | true；是带可信前提的充分分类规格，源代码尚待实现 |
| R40_UNCERTAIN_IO_FAIL_CLOSED_PRESERVED | true；指修复规格和证明责任，动态回归尚待执行 |
| R40_TEST_PLAN_FROZEN | true；28项输入/oracle冻结，均NOT_RUN |
| R40_IMPLEMENTATION_AUTHORIZATION_PENDING | true；本轮授权仅静态审定 |
| PREWRITE_POISON_CLASSIFICATION | 工程缺陷成立，实际修复未实施 |
| COMPLETE_L0_CAPACITY | UNPROVEN；正常和最坏异常必需总字节均UNKNOWN |
| BOUNDED_EVIDENCE_CONTRACT | R37部分批准，九项原完整内容义务保持 |
| RUNTIME_ORIGIN_ADMISSION | PENDING；7内容变化/5旧路径缺失本轮重核一致 |
| D1-B1 | PARTIAL_IMPLEMENTATION |

## 十二项退出回答

| 问题 | 回答与证据 |
|---|---|
| 1. Write前拒绝能可靠识别吗？ | 在975、992、1008这些明确同步位置可以证明。通用处理需本次调用匹配令牌、可信前缀、扣费与write边界共同证据；现有代码尚缺这种分类。 |
| 2. 存在零write却Poison的路径吗？ | 有。975/992→668或899；1008→1023。metadata读取可能已发生，“零I/O”在此专指零受保护payload-write。 |
| 3. 取得完整状态轨迹了吗？ | 局部协议层取得。A为真实A01路径加R39可达/可适配前提；B为1062字节前缀与998461字节合成请求的精确原语实例。二者都保留范围限定。 |
| 4. 已提交前缀的保持条件可核验吗？ | 可以：可信旧ACK、独占句柄、身份/extent/tell一致、受保护write尚未开始、没有外部变更。P1—P6给出证明；旧609条历史链另做完整校验，其历史fsync未被重新观测。 |
| 5. 收尾预留有独立预算身份吗？ | 有：原工作cap983040与总cap1048576之差65536；其他最终JSON/receipt份额仍属于原13caps。剩余时间、次数和实际包长度继续单独约束。 |
| 6. 哪些拒绝可保持健康？ | 具备上述全部前提的明确同步容量、截止或字段预检拒绝。已经扣费的1008路径保留全费。 |
| 7. 哪些失败继续Poison？ | 身份/extent/tell冲突、部分/未知write、flush/fsync错误、头部发布/ACK未知、旧Poison，以及缺少可靠边界证据的情况。 |
| 8. 持久化未知仍保守吗？ | 规格要求默认保守、禁止清除旧Poison、禁止未知写重试。真实实施和动态验证继续待取得。 |
| 9. 有重复写入或预算重置风险吗？ | 盲目去掉Poison会引入风险。冻结合同保持失败记录的一次尝试、全部charge/次数/授权单调，仅允许既有独立terminal动作。T11/T12/T18/T23/T24/T26专门验收。 |
| 10. 能局限在已批准Runner吗？ | 可以形成单文件方案；需新授权明确列出commit_case_record、safe_checkpoint、checkpoint、reserve_bytes、io_write五函数，及至多一个有界helper。本轮文件保持原字节。 |
| 11. 需要什么测试？ | T01—T28，共28项，全部NOT_RUN。原68项断言、ID、fixture和54项历史证据保留。最终补丁/测试源与执行资源锁形成后再单独申请动态验证。 |
| 12. 还有来源/容量/合同缺口吗？ | 有：完整L0联合适配、九组证据条款、运行时来源、新可执行命令/源码锁以及完整回归准入继续独立。 |

## 反例与创新责任

A的同payload终止计量沿用R39的13字节增量界，不能替代实际不同CASE_EVIDENCE包的完整适配证明。B请求在通用checkpoint的JSON域内合法，但大列表未满足A01结果schema；它只承担原语级字节拒绝反例。当前字面命令禁用，完整68可达轨迹及全局字节超额反例均未取得。

同等可信前缀、资源、接口及期限下，成熟事务式事前拒绝分类可以保留已有收尾提交资格。当前行为差异支持工程维护。通用方法必要代价更高的实例未建立，本轮不登记算法创新或原创候选机制；严格分离实现门继续沿用。

## 保全与执行边界

继承2405条保全基线和5个预先缺失路径，并新增保护R39全部28文件。入口/结尾核对见sources/HISTORY_BEFORE与HISTORY_AFTER。Runner仍为SHA `33276c053116537db4c8921410f860968dc966fbc99cc42b798fdf836c9c601e`。历史R25 PASS、R28/R30/R32失败、R33—R39证据与旧SOURCE_LOCK保持各自原字节。

本轮原工程/测试/fixture/依赖修改0，项目函数求值和动态测试0，真实服务、数据库、密钥、RPC、监听及部署操作0。D1-B2、P1a、P1b、P2、S3-B2、S5继续NOT_AUTHORIZED。完整L0容量未证，D1-B1继续部分实现。

## 唯一下一动作

独立批准 `R40_NEXT_AUTHORIZATION_REQUEST.json`：在上述单Runner五函数/至多一helper范围实施Write前分类维护，并完成静态源码、常量、边界和费用增量复核；测试运行请求为0。

这次需要新的实施授权，因为用户R40第一节明确规定“本轮禁止：修改 Runner”和“执行 Runner 或测试 suite”。本轮已完成可审阅的修复合同及后续测试oracle，申请没有提前实施。

成功意味着已证事前拒绝保持健康前缀及合格独立收尾资格，不确定I/O继续阻断；随后可以基于实际补丁单独冻结离线测试执行包。失败意味着保留具体边界、费用或范围缺口并继续阻断。完整L0容量、G3/G4和真实部署资格各按其独立合同判断。

本轮为当前对话内知情模型辅助静态审查，外部独立核验待取得。
