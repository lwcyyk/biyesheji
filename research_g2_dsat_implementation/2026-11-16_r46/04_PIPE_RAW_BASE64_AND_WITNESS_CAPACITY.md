# G2-R46：Pipe、Raw、Base64与witness完整容量

计算合同见 [R46_PIPE_RAW_BASE64_CAPACITY.json](R46_PIPE_RAW_BASE64_CAPACITY.json)。以下为符号算式和数据格式算术，没有执行Supervisor序列化函数或任何管道API。整体仍为 `ARTIFACT_BUDGET_UNPROVEN`。

## 管道与字节身份

父创建stdout/stderr两个匿名Pipe；stdin为NUL。策略由文件读取，退出信息通过进程句柄取得，当前没有Child控制Pipe。`CreatePipe(nSize=p)` 提供容量提示，实际内核缓冲各为未知Kout、Kerr；2p仅表示两个请求提示的总值。

每次drain在两流间交替，最多D轮，单次ReadFile请求s≤q≤65536。Child已退出后，继续drain到双EOF；循环没有固定轮数常量，但每次API仍消耗A名额和QPC准入。Peek返回ERROR_BROKEN_PIPE109才置相应EOF，成功收尾要求两个EOF均确认。

Raw计数在 `ReadFile` 返回之后、cap检查和append之前递增。若最后一次读取越cap，该次Raw已转移到父内存，且尚未写入witness；每流累计已读可用宽松上界Rstream+q，已确认完整帧的Raw≤Rstream。当前没有独立的Raw持久化前缀计数。读取成功、序列化完成、write返回及fsync确认具有不同语义。

Child `stdout.log/stderr.log` 是Driver主动创建的JSON文件；它们与进程stdout/stderr的Pipe流分开。父没有另建Raw或Base64临时文件，二者以Base64字段写入单个witness。

## Base64与精确帧长

设某帧返回n字节，b(n)=4⌈n/3⌉。n≤65536，故b(n)≤87384。Base64字母表在ensure_ascii JSON中无需额外转义。一次复制仍须计入编码bytes、ASCII str、JSON str/bytes和最终LF拼接。

源592–617、639–646定义了如下键集合：previous_sha256、schema、seq、sha256、stage、value(base64,raw_bytes)。在紧凑排序JSON、两个64字符摘要、CHILD_STDOUT/CHILD_STDERR同长stage和一个LF下，精确行长为

`P(seq,n) = 264 + d(seq) + d(n) + 4⌈n/3⌉`，其中d(0)=1。

264为固定JSON结构和文字长度，另外两项为序号与Raw长度十进制位数。空数据/单数字序号行长266。A≤2^63−1且每个确认帧至少消耗API名额，故seq至多19位，n至多5位，单Pipe行通用上界为264+19+5+87384=87672B。完整控制/错误/receipt记录仍需各自证明，不能使用这个Pipe专用界替代。

分成k个块时，`Σb(n_i) ≤ 4⌈Σn_i/3⌉ +4(k−1)`（k≥1），且每块单独支付固定头和数字宽度。推导令每块填充差额为0/1/2字节，合计差额≤2k，再按总长度模3取整即可。3个Raw字节一次编码为4字符，三个1字节块分别编码共12字符，并增加两个记录头。这是手工长度挑战，未声称某次Windows运行必然返回该分片。

即使ReadFile返回0，源码也会尝试append；容量证明须允许这类无Raw进展帧。每个完整帧至少消耗7个普通封装调用、266个输出字节，故确认帧数粗界为 `min(⌊(A−32)/7⌋,⌊(W−F)/266⌋)`。它是接纳界，producer输出能否全部被读取与保存另证。

## 完整witness与失败后缀

W为总witness cap，F为失败预留，L为最大单记录。源码要求L≤F≤W、普通帧累计≤W−F、最终帧累计≤W。完整需求必须同时满足：

1. 三个初始控制记录、最多S个资源记录和全部Pipe帧之和≤W−F。
2. 完整最终receipt行≤F，每行≤L。
3. Child933888+W≤2097152，即W≤1163264。

第3项描述可用空间。前两项需要完整生产者证明；当前错误文字、路径、原始L0和失败分支尚缺足够宽度约束。源码的len拒绝门只能阻止更多文件写入。

最终receipt有36个顶层字段，逐字段宽度和重复位置见 [sources/WITNESS_FIELD_WIDTHS.json](sources/WITNESS_FIELD_WIDTHS.json)。DWORD最多10位，uint64/SIZE_T最多20位，signed QPC含符号最多20位，策略计数最多19位，bool最多5字节，摘要字符串含引号66字节。未知错误及实际argv路径使用具名长度变量。

统一递推为：非空对象长=2+Σ[J(key)+1+J(value)]+(字段数−1)；数组同样计括号、元素及逗号；ensure_ascii字符串可用12×Unicode码点数+2作为保守界；最终外层行等于无sha事件长+77。完整取值长度未固定的字段保持null，所有36项均保留原字段义务。

`process_io_before/after`中的Job对象又在`job_io_before`等字段输出，`job_io_after`还在`job_memory_peak`重复。对象在内存中的别名会在JSON中重复展开。`error_record`只保存operation/type/message/errno/winerror，其与完整args/异常链/traceback等L0义务的等价性未建立。R37九组有损表示继续待批准，无新增截断、摘要替代或信息删减授权。

正常、测试失败、来源失败、超时、Job终止、Child未退出、清理失败、receipt写入失败及父自身异常均保留单独容量责任。策略拒绝可能发生在输出创建之前；此时父继承stderr的外部捕获角色与预算也尚待确定。witness短写/未知持久化会poison且保留全额charge，后续追加被拒绝，最终完整receipt无法保证。

## 峰值共存

令s为本次native buffer长度，n≤s为切片，J0为无sha事件JSON长度，J1=J0+76为有sha对象长度。一个安全的可见负载加总式为

`2s+n+2b(n)+2J0+3J1+65+q_previous`。

它分别保守计入native buffer、buffer.raw、slice、编码bytes/str、两层JSON编码与LF拼接、digest，以及下一次buffer分配时尚在的旧buffer（q_previous≤q）。尽管若干临时对象可在常规路径释放，本轮没有用未证明的互斥关系缩小此界。

在单个最大Pipe帧取s=n=q_previous=65536、b=87384、J0=87595、J1=87671，得可见负载分量包络875180B。完整峰值还必须增加Kout+Kerr、容器与对象头、JSON/Base64 native工作区、policy/catalog/sample/error/receipt、分配器保留内存和并发Child写入缓冲。其总值继续null；875180B无法用作完整Working Set或RSS额度。

Pipe缓冲有限，父停止drain、witness cap拒绝或同步写/fsync延迟均可能使Child输出阻塞。失败终止和退出确认继续按90/115/120合同处理，传输队列内容不得当成已持久证据。
