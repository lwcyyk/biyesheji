# 原结果先登记与持久化确认

三项修复中的结果登记已实现。Results.addSuccess:1706、addFailure:1709、addError:1712、addSkip:1715均先record，再调用原super日志/格式化。startTest:1684在普通进度日志前建立开始标记和检查点。

## 提交顺序

原回调状态先进入预分配的68项状态槽；随后生成原ID、组、源hash、Runner版本、原预期、可信组阶段和已知错误L0头，尝试TEST_ASSERTION检查点。checkpoint:829沿用原journal身份/前缀检查与fsync逻辑，成功后才返回seq/hash/path引用。最后才进入标准库普通日志或原诊断渲染。

commit_case_record:653区分：

| 状态 | 依据 |
|---|---|
| RESULT_OBSERVED_IN_MEMORY | 已有真实原回调事实，尚未取得提交确认。 |
| RESULT_CHECKPOINT_COMMITTED | checkpoint返回真实确认，RESULT_DURABLE=true。 |
| RESULT_PERSISTENCE_FAILED | 本条没有进入追踪的write阶段；未提交。 |
| RESULT_PERSISTENCE_UNKNOWN | 已进入write阶段或确认不完整，RESULT_DURABLE=UNKNOWN。 |

同一记录最多一次尝试：已提交返回原引用，失败/未知维持原状态。不同真实回调用id:ordinal分别保存，原FAIL/ERROR不被覆盖。原冻结用例没有subTest或addCleanup注册；标准Case的setup失败跳过body/tearDown，否则body/tearDown最多两个结果回调。源码证据见FROZEN_CALLBACK_BOUND。超过该冻结图的额外回调触发overflow/UNKNOWN和完整失败。

多回调没有被任意排出优先级：原状态事件全部保留，case聚合为UNKNOWN；新增observed_original_callback_counts与68项case分类计数分别呈现，避免混为同一个分母。PASS必须来自真实原success回调，日志内容不产生结果。

## 原W01回查

若A01真实success回调已取得、TEST_ASSERTION已fsync确认，而后“ok”日志write失败，原事件/引用保持；finally继续尝试原缓存DETAILS。日志文件失败不删除journal，也不改写既有PASS。全局原日志/错误取证义务仍可使最终任务失败，与原测试结果事实分别管理。

若结果提交本身失败，回调停止后续普通日志，已观察状态留在内存槽，结果持久化为FAILED或UNKNOWN，完整接受false。header未知/超限标明不完整；已知errno/code先独立于待批诊断提取。任意磁盘或RAM故障下的完整耐久性并无无条件保证。

最终RESULTS仍是候选材料，TEST_RUNS还需全部绑定和外部native exit0。native_exit_observed保持UNKNOWN，native_exit_required作为要求单列。最终关闭/读取失败即使发生在候选写出后，完整协议仍需要真实退出确认。
