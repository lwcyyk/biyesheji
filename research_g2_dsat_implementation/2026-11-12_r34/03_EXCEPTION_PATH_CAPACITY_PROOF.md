# 异常路径、写入生命周期与峰值

用户列出的28类场景全部静态定位，另外加入调用槽/目录/Sink构造失败，以及诊断/编码器自身再失败两类，共30行。此覆盖指代码映射；每条的完整容量成功并未取得。当前禁用门保持，全部可达性讨论注明预期准入条件。

| 路径 | 可达性 | 容量状态 |
|---|---|---|
| X01 静态准入失败 | reachable;current disabled command takes this class | PROVED |
| X02 测试模块导入失败 | conditional intended admission | UNBOUNDED |
| X03 .pyc回退失败 | conditional;expected EACCES fallback separately allowed | UNBOUNDED |
| X04 非授权读取 | conditional audited read | UNBOUNDED |
| X05 来源SHA不匹配 | conditional source mismatch | UNBOUNDED |
| X06 A17导入屏障失败 | conditional early import or preload | UNBOUNDED |
| X07 D24路径投影失败 | conditional D24 context | UNBOUNDED |
| X08 单项断言失败 | conditional unittest failure | UNBOUNDED |
| X09 测试执行异常 | conditional setUp/body/tearDown failure | UNBOUNDED |
| X10 测试超时 | conditional intended prefix plus delayed allowed operation | UNKNOWN |
| X11 子进程退出异常 | unreachable in approved Runner-owned child graph | PROVED |
| X12 stdout/stderr写入异常 | conditional Sink I/O fault | UNKNOWN |
| X13 检查点保存失败 | conditional cap/I/O/fsync/identity failure | UNBOUNDED |
| X14 真实来源冲突 | conditional observed mismatch | UNBOUNDED |
| X15 未知来源对象 | conditional unsupported metadata/type | UNBOUNDED |
| X16 来源审计内部异常 | conditional collector/classifier error | UNBOUNDED |
| X17 资源账本构造或检查点写入失败 | conditional resource/encoding failure | UNBOUNDED |
| X18 最终RESULTS写入失败 | conditional encode/budget/storage failure | UNBOUNDED |
| X19 最终来源JSON写入失败 | conditional encode/budget/storage failure | UNBOUNDED |
| X20 最终资源JSON写入失败 | conditional encode/budget/storage failure | UNBOUNDED |
| X21 临时文件写入失败 | unreachable in harness evidence publication | PROVED |
| X22 原子发布失败 | no rename-based atomic publication;logical commit may fail | CONDITIONAL |
| X23 flush/fsync失败 | conditional any managed writer | UNKNOWN |
| X24 失败receipt写入失败 | conditional final publish fault | CONDITIONAL |
| X25 清理期间再次异常 | conditional watchdog/connection/journal/Sink cleanup failure | UNBOUNDED |
| X26 主异常与清理异常同时存在 | conditional combined branch | UNBOUNDED |
| X27 全部68项后框架错误 | conditional later provenance/resource/publication error | UNBOUNDED |
| X28 已提交结果最终ACK丢失 | outside Runner network protocol;external observer can lose exit notification | CONDITIONAL |
| X29 调用槽/目录/Sink构造异常 | conditional outer setup failure | UNBOUNDED |
| X30 异常记录器或编码自身再次失败 | conditional str/repr/traceback/canonical/codec/MemoryError | UNBOUNDED |

子进程退出异常在获准子进程图中无对象，launch在audit处拒绝。证据临时文件路径也不存在。最终ACK属于外部退出观测，Runner本身没有网络ACK协议；已存commit与未知native退出观测保持分层，唯一调用槽继续有效。

普通写入路径为内存构造→目标xb独占创建→write→flush/fsync→hash→最后TEST_RUNS逻辑提交。journal持有同一xb流，按字节追加并核对identity/size/tell；日志持有x流。磁盘临时副本峰值为0，正式文件部分前缀始终计入S(t)。codec内存副本的RAM和物理磁盘元数据开销没有被登记成0。

存在三个具体边界。

1. 超时收尾：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:360` 第361行先检查time≤deadline。对任一已进入load_group的合法准入前缀，若一次获准源读取延迟到t=121（deadline120），其后新checkpoint、最终三JSON和receipt均无法通过时间门。最终summary的Sink写入也可能把控制流送到entry，绕过TEST_RUNS。该纸面故障无需长消息，说明超时终态可用性须使用原条件边界或明确收尾时间预留，字节空间充足本身无法保证它。

2. 失败缓冲：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py:828` 第834行flush完成后，第835行才增加used。接口模型从已见文件60000、used60000开始，第一次4000字节被缓冲且flush失败；调用者捕获后再次写4000，两个前置检查都看到64000，随后flush可使文件达到68000、used却为64000。该例假设缓冲保留及调用者重入，未证明该序列由冻结68实际产生，也未证明全局2MiB超额。它暴露了全故障分区证明所缺的pending字节记账条件。已锁warnings.py确有捕获OSError的调用模式，具体冻结运行中的重入可达性仍待闭合。

3. receipt自身不可写：main在journal与日志关闭后发布TEST_RUNS。若该写入失败，publish会尝试向已关闭journal保存失败，后者继续拒绝，错误可只留内存并native退出1。完整耐久receipt在该条件下无法保证。此为存储可用性边界，独立于压缩尺寸。

已记录的单字段字节模型：262144字节构造trace生成200165字节receipt包，超过65536份额。它是表示/序列化接口反例，冻结68整段执行见证尚未建立。压缩是无损注入；缺少输入域长度界时，有限输出集合无法承载任意长字符串族的完整内容。该论证限定于接口域，未推导原冻结程序必然溢出。

所有上述模型均为纸面或已有数据的字节变换，故障注入、测试及真实I/O实验均为0。详表记录每条发生次数、已存文件、追加记录、错误文本、重复收尾、receipt与三JSON行为、临时副本和证明状态。
