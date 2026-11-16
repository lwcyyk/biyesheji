# 预算、收尾与L0容量影响

本轮证明的仍是受控存储前缀安全及局部分类成本，完整必需L0适配继续UNPROVEN。

| 原合同项 | 本轮值 |
|---|---:|
| 总逻辑证据预算 | 2097152B |
| 原13cap之和 | 2000167B |
| 条件存储包络差额 | 96985B |
| Journal总/工作/保护收尾 | 1048576 / 983040 / 65536B |
| 工作/terminal I/O/关闭准入 | 90 / 115 / 120秒 |
| terminal/checkpoint准入上限 | 32 / 8320 |
| 新运行对象、磁盘临时副本、退款路径 | 0 |

常量和作用域外函数的原字节/AST一致；受控write、flush、fsync调用点各保持原数量。原生阻塞及调度晚返的时间前提继续有效，120秒没有被提升为硬实时保证。

## 按分支计费

reserve的容量或截止拒绝发生在字节扣费前，新字节charge为0；已经消费的构造尝试、terminal尝试、CPU及metadata费用保持。io_write之前已扣费的截止拒绝保留全部charge，confirmed保持，真实新增未知payload为0；unconfirmed allocation上界仍保守保留。

短写、部分write、flush/fsync错误与ACK未知保留全长charge；unknown与可见/确认字节属于同一已扣分配的不同观察。没有再次叠加到物理配额，也没有自动退回。

## 正常路径

检查点数量式继续为 `232+O+C+W`。O为不同ORIGIN_OBSERVED条数，C为不同ORIGIN_CLASSIFIED条数，W为WRAPPED_ORIGIN_OBSERVED条数。没有将它们替换为固定实测数。

正常成功路径新增payload字段0、新Journal调用点0、receipt发布数量增量0。新鲜token为内存状态。Runner哈希变化会改变来源值和实际压缩结果，因此旧wire长度和比例未被声明保持。

## 失败路径

新增21字段audit。按原受控整数、3字符test ID、64hex旧head、已验证stage JSON<=256及源码枚举阶段/拒绝点，单audit原始规范JSON条件上界为910B。加入非空父对象的保守原始增量：checkpoint_attempt至多932B，last_checkpoint_failure至多937B。逐项证书见sources/LOCAL_CAPACITY_IMPACT。

失败case、failure数组与Journal账本可分别带该对象。同一个内存引用在CASE_EVIDENCE、TESTS_FINISHED、RESULTS、RESOURCE_LEDGER、receipt及资源嵌套中会重复序列化；未假定免费去重。新增嵌套深度、raw/codec/行guard、最终文件共存及新增错误描述符均需进入完整联合证明。

直接调用checkpoint失败新增一条分类failure行，原上层错误保留；包装器仍用原有failure行。原192错误行cap保持，饱和可能提前，完整性拒绝责任继续存在。新增incomplete码为CHECKPOINT_UNCONFIRMED、CHECKPOINT_CLASSIFICATION_AUDIT_FAILED，新增输入拒绝码为CHECKPOINT_ATTEMPT_STATE。

失败后只有原调用图中的收尾提交恢复资格，新增恢复循环0。普通停止后的写入被事前拒绝。构造调用点保持13处checkpoint/10处safe_checkpoint；State.failure源码调用点从15增为16。已有失败调用图松包络仍只承担其有限上包络范围，实际可达完整L0需求仍需重算。

## 保持分层

PREWRITE_POISON_DEFECT_STATICALLY_REPAIRED成立。NORMAL_L0_REQUIRED_BYTES和WORST_FAILURE_L0_REQUIRED_BYTES均为UNKNOWN；COMPLETE_L0_CAPACITY保持UNPROVEN。910B部件界无法代替完整适配证明。

G3九组原完整内容责任保持。G4仍有7内容变化及5旧路径缺失；本轮没有重新接纳来源。R35旧命令与预算准入保持禁用，旧Runner pin未更新。D1-B1保持部分实现。
