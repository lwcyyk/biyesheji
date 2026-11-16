# G2-R47：显式I/O与来源读取计费

新增ExplicitIO按Python调用层计数，数据分为PRE_QPC_COST和QPC_SCOPED_COST。23个site ID覆盖15个前置phase/site和11个QPCphase/site，其中3个路径site跨阶段出现。每项都有attempt、success、failure、refusal及字节单位；详细字段见R47_EXPLICIT_IO_CALLSITE_MATRIX.json和R47_SOURCE_READ_ACCOUNTING.json。

## 实际调用点

下表定位于最终Supervisor版本。所有本轮实际资源指标为NOT_MEASURED，调用图纸面核读未运行其中的动作。

| site | 函数及行 | 操作 | 对象/范围 |
|---|---|---|---|
| path.exists | checked_path:243 | metadata | every checked ancestor |
| path.lstat | checked_path:244 | metadata | existing checked ancestors |
| path.is_symlink | checked_path:245 | metadata | existing checked ancestors |
| path.is_file | checked_path:248 | metadata | existing input file |
| path.stat_identity | checked_path:249 | metadata | nlink check |
| source.stat_before | PolicyValidator.read_hashed:287 | metadata | control/runtime source |
| source.stat_after | PolicyValidator.read_hashed:315 | metadata | control/runtime source |
| source.open | PolicyValidator.read_hashed:294 | open | 20 control +K runtime source objects |
| source.read | PolicyValidator.read_hashed:304 | read | bounded blocks; EOF also counted |
| source.close | PolicyValidator.read_hashed:332 | close | one close per opened source; close slot reserved |
| pe.open | PolicyValidator.read_pe_header:362 | open | Python PE fragment |
| pe.read | PolicyValidator.read_pe_header:372 | read | 64 and6 requested bytes; actual returned separately |
| pe.seek | PolicyValidator.read_pe_header:371 | seek | validated DOS offset |
| pe.close | PolicyValidator.read_pe_header:387 | close | Python PE fragment |
| output.preflight_exists | PolicyValidator.validate:555 | metadata | two output roots |
| witness.mkdir | OutputController.open:783 | mkdir | owned observer root1 |
| witness.open | OutputController.open:784 | open | SUPERVISOR_WITNESS.jsonl xb1 |
| pipe.read | OutputController.drain:919 | read | two owned pipe streams; request<=65536 |
| witness.write | OutputController.append:854 | write | one serialized whole record request; no retry |
| witness.flush | OutputController.append:866 | flush | per issued record |
| witness.fileno | OutputController.append:869 | fileno | descriptor lookup; distinct from physical I/O |
| witness.fsync | OutputController.append:871 | fsync | per issued record |
| witness.close | OutputController.close_file:958 | close | one owned FileIO close |

Runtime SOURCE_LOCK由runtime_origin_lock读取；Runner、Driver、Supervisor、Python、manifest及原input pins通过相同受控读取入口。相同文件重复读取分别计账。受测Runner自己的MODEL Journal和Child文件I/O继续属于原owner，父没有第二次物理写入Raw。

Path父链由词法构造；exists/lstat/is_symlink/is_file/stat分别计量。源码没有目录枚举。Path.open/ReadFile等底层隐式元数据与内核调用数继续未知。WindowsApi的28个声明和原逐API计数保留，不能与这些Python调用直接合并成系统调用总数。

## 单位与失败

- API_CALL_ATTEMPTS：通过额度守卫后进入action wrapper的次数；成功返回与抛出分别记录。它包含Python适配层边界，无法证明每次都已经进入内核。
- READ_REQUESTED_BYTES与READ_RETURNED_BYTES：前者在动作前计费，后者依据实际bytes长度/ReadFile返回量登记。文件st_size单列，无法代替返回字节。
- WRITE_REQUESTED_BYTES与WRITE_ACCEPTED_BYTES：以完整序列化请求及FileIO实际返回数分别登记。短写保留原返回数，异常保留unknown_write_returns。
- PERSISTED_CONFIRMED_BYTES：仅在当前完整记录flush/fsync返回后增加。PERSISTENCE_UNCERTAIN_BYTES保留可能已开始写入但尚未确认的整条请求包络，属于保守不确定量。
- FILES_OPENED与METADATA_OPERATIONS：open成功数、元数据尝试数分别登记。返回False的exists属于成功取得“不存在”观察。

action已返回而结果校验失败时，success计数保持，另增result_unconfirmed和未知返回标志，随后抛出。观察器失败无法被算作“底层没有发生I/O”。代码没有catch-and-ignore；所有新增捕获均标记后重新抛出。

## 来源逐对象记录

20个控制读取、K个运行时完整哈希和1个PE片段形成最多21+K≤32789条source_reads。每条有read_id、kind、path_sha256、file_size_before、read_calls、read_requested、read_returned、hashed_bytes、EOF、完整哈希/元数据状态、实际摘要与close状态。PE记录只读64+6B，file_size_before=null、hash_complete=false，避免把70B称为整个EXE长度。

path_sha256是新增对象引用标识，配合原锁定输入和runtime catalog定位精确路径；原self.pins完整路径记录保持。它没有替换任何原L0字段。native FileId保持UNKNOWN，路径前后元数据一致也无法证明恶意文件系统竞态安全。

read_hashed每次请求min(65536,st_size+1−已返回)，观察EOF、校验返回总量=st_size、哈希完整以及前后dev/ino/size/mtime一致。增长最多取得额外探测字节后拒绝，截短/摘要错配拒绝；已取得字节与已哈希字节分别保留。close在finally进行，close异常继续暴露，Python异常链保留原错误上下文。

read_calls/read_requested在受控action中递增；额度在此之前拒绝时只增加refusals，实际读取调用数保持。ReadFile抛出或返回不可核验时，未知返回标志保留原可靠前缀，并标注传输尾部未知。

## 前置额度与未闭合范围

独立审批policy新增pre_qpc_accounting_limits的五项：io_attempts、read_requested_bytes、read_returned_bytes、runtime_files、runtime_source_bytes；分别受R2 approved_maximum中的pre_qpc_*同名额度约束。当前这些值缺失，八类批准均为null。资源空值原门先拒绝，后续缺少读取额度也会拒绝。

policy与approval两个bootstrap对象先受每文件2MiB和有界读取约束；配置额度后核对已发生的实际前置成本。普通PRE_QPC操作预留一个close调用槽，因为此阶段最多同时持有一个来源/PE FileIO。读取额度拒绝后仍有显式close名额，拒绝与资源回收分开计账。

runtime文件目录要求每项bytes、K≤min(32768,批准值)、Σbytes≤批准来源字节额度，遍历哈希前核验；实际stat必须与所列bytes相等。读请求总量还包含EOF探测及短读影响，必须另有批准界，不能直接用Σ文件长度替换。

PRE_QPC_COST在原ADMITTED中一次性输出，包括显式调用快照、来源记录、run_id及锚点之前/之上的QPF/QPC封装快照。Python初始化、模块导入、DLL加载、隐式loader I/O和锚点前耗时明确排除；最终receipt仅引用已提交ADMITTED。

`SOURCE_READ_BYTES_UNPROVEN`在本轮继续：实际拟用目录、独立批准数值、全加载器/原生/物理I/O和前置耗时均未取得。前置校验失败可能发生于输出创建之前，内存中的失败计费无法保证被持久化；外部失败取证仍需单独合同。
