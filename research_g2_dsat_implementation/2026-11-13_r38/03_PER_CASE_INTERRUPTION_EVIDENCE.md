# 逐用例中断证据

原清单固定A1=20、H1=24、D1A=24，顺序A1→H1→D1A，总ID68。状态初始化按原manifest预分配；原ID、原预期/源码和测试断言均保持。

start观察点为result.startTest的受控开始标记，位于普通进度日志前；它只证明Case执行协议已经开始，测试body是否开始不由此推断。

| 情形 | case状态 | 其他独立事实 |
|---|---|---|
| 尚无开始标记 | NOT_RUN | 原清单中仍占一个ID。 |
| 已开始、尚无终态且仍开放 | RUNNING | 开始检查点可能已确认。 |
| 已开始、未取得终态而中断 | RUNNING_INTERRUPTED | 可保存已有checks，完整DETAILS标为缺失/中断。 |
| 一个原终态回调 | PASS/FAIL/ERROR/SKIP | case-call返回及结果持久化另列。 |
| 多个原回调或无明确终态而返回 | UNKNOWN | 原回调事实不消失，完整接受false。 |

assertion_rows:903以生命周期与原状态槽重建每个ID的已知分类。case_partition:801给出confirmed_result_set、begun_result_unconfirmed_set、not_started三集合，互斥并覆盖68；它还单列case-call完成/中断、durable、memory-only/uncertain。这里“confirmed result”指真实原回调已观察，独立于fsync和全部审计完成。

## 每个用例的finally

OrderedSuite.run:1725始终在finally执行end_case。发生原异常时先进入允许的terminal阶段，保留原异常；详情采集再次失败则独立记录，既有primary继续传播。D24上下文先按原逻辑退出，不调用新的业务流程。

capture_case_details:727只读已加载模块的DETAILS和已有checks，不调用tearDown/safe_session、不导入测试模块、不执行SQL。原详情用已批准canonical JSON无损复制，按组cursor保存一次，绑定原case ID与索引。内存捕获后cursor前移，避免提交失败导致重复转移；提交前后状态分开。

正常原DETAILS保留在self.details及TEST_CASE_EVIDENCE完整payload中；每个case的end_record为提交回执。缺失当前完整DETAILS时标MISSING_OR_INTERRUPTED，有限原checks只作为部分事实，完整接受false。

原组末capture_details调用已撤除，组汇总继续保留已有原数据；它不替代逐项记录。逐项结果的seq/hash引用、详情索引及提交引用可与原journal前缀核对，未经确认的尾部不计为持久化成功。

14个纸面中断场景在R38_PER_CASE_INTERRUPTION_MATRIX：首项之前、A1/H1/D1A组中、各边界、第68项后、来源/账本/检查点/日志/最终JSON失败等。例中的PASS为明示纸面假设，实际新测试数0；没有使用历史609条替代未来证明。
