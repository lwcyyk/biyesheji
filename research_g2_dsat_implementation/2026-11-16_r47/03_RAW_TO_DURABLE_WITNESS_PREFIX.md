# G2-R47：Raw到已确认Witness前缀的对应证明

本稿是最终源码的静态归纳证明，未执行帧生成、故障注入、穷尽程序或测试。完整协议字段见R47_RAW_PREFIX_CONTRACT.json及R47_WITNESS_COMMIT_CONTRACT.json。

## 精确定义

每流分别记录R=可靠已读并被SHA覆盖的Raw前缀、A=完整序列化帧write已全额接受的Raw前缀、P=该完整帧flush/fsync返回确认的Raw前缀、C=已进入权威Witness提交游标的Raw前缀。每个前缀同时具有字节长度、流内帧数、SHA-256。出错调用的实际传输尾部可保持UNKNOWN。

Raw实际存放在同一JSONL帧的Base64字段中。A采用完整帧确认口径；短写即使已经写入部分Base64，也只在serialized accepted字节中记录，Raw A保留此前完整帧。此定义使完整解码及帧头/LF可核验性随确认保留。

一个witness_prefix字典包含全局sequence、bytes、sha256以及两个流的C。confirmed/sequence/head属性全部从该字典读取。旧版分散赋值被单个权威引用发布替代，处理fsync之后、确认元数据更新之前的失败窗口。

## 归纳不变量

初始四个前缀均为0、空SHA，流内帧数为0，全局链头为原64个零。对每条流始终保持 `0≤C≤P≤A≤R`，帧数也保持相同次序。各个已知SHA对应其实际Raw前缀；正在读取/计算时可明确为UNKNOWN。

1. drain的同一个Raw slice输入流SHA和Base64。成功读取使R增加n，尚无A/P/C变化。ReadFile失败或观察不完整时保持原可靠前缀并登记未知返回。
2. append要求global_seq=旧全局序号+1、stream_seq=旧C帧数+1、start=旧C=P=A、end=当前R、SHA=当前已读SHA，且Raw长度/Base64与drain传入的内部token一致。缺帧、重复或跳过前缀将触发拒绝。
3. 先完整序列化并验证cap，再保留整条charge。只有write实际返回完整行长，才以一次字典引用替换推进A的字节/帧/SHA三元组。
4. flush及fsync均返回之后，才以同样方式推进P。此时允许P领先C，准确表示已确认持久化而逻辑提交ACK尚未发布。
5. 在P之后准备全局新游标与两个流的新C，一次 `self.witness_prefix=committed` 发布。新C=P≤A≤R，其他流保持。全局字节增加实际整行长，sequence连续且链头绑定该行。
6. 该发布之后的会计失败保留已发布游标，若pending仍存在则标记POST_COMMIT_ACCOUNTING_UNCONFIRMED。发布之前的失败保留旧C并标记WITNESS_COMMIT_UNCONFIRMED。poison阻止后续追加与序号重用。

这是每次转换的归纳，覆盖所有主图可达帧。内部token只由drain建立；没有公开接收外部任意token的执行入口。摘要安全沿用SHA-256绑定假设，无法宣称数学无碰撞。

## 零长度、短写和失败

零字节帧仍增加流内帧数和全局序号，所以仅字节长度相等无法形成重复确认。短写/零写保留serialized返回量，A/P/C均保持之前完整帧。write异常保留整条费用和未知接受状态；flush/fsync异常允许A领先P/C，pending标为RAW_PERSISTENCE_UNCERTAIN。

Raw超cap、115门拒绝或序列化失败可使R领先已确认前缀；没有后续Raw跨越该空洞。全局主循环异常即停止该路径；即使再次调用，帧数/start守卫也会拒绝空洞。EOF、清理和退出都没有推进前缀的赋值。

若fsync已经返回而后续Python计量分配失败，可靠确认可保守停在旧P/C，pending指出WITNESS_COMMIT_UNCONFIRMED。瞬间内存分配/异步异常可能阻碍诊断持久化，无法由纸面逻辑保证错误后缀存在；已发布的权威游标不会凭空越过真实fsync边界。

## 外部核验与持久化边界

run_id复用policy摘要，结合本次fresh输出目录的独占xb、原PID/creation time识别本次执行。stream_id为stdout/stderr，对应stage；frame_seq由全局seq及每流计数关联。文件标识为本次根下的SUPERVISOR_WITNESS.jsonl，native FileId未知。

外部核验需检查每行canonical摘要、前链、连续全局序号、Base64解码长度、按stage聚合的Raw顺序/总长度/SHA，并与最终receipt之前的确认游标比对。缺行、重复、破损或未知尾部继续阻止完整接纳。

文件从xb创建起可见；没有临时文件、原子rename或新增发布API。磁盘fsync确认、内存逻辑ACK、后续包含ACK的receipt持久化分别管理。receipt自身在序列化时尚未执行write/fsync，完整外部ACK仍需后续观察。

fsync的保证依赖Windows/FileIO、文件系统、存储栈对成功返回的约定；任意硬件断电绝对持久性没有取得证明。上述STATIC_VERIFIED仅证明程序状态转换与可靠确认边界。

## Pipe原帧格式

未向CHILD_STDOUT/STDERR value添加字段。原event键、两个64字符摘要、Base64与Raw长度、LF均保持，故行长继续为 `264+d(seq)+d(n)+4⌈n/3⌉`，上界87672B。逐帧新增序列化字节为0。分片分别支付填充与头，整体容量仍待完整生产者证明。
