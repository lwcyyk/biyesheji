# LR：五业务文件静态版本兼容性审查

2026-11-10。Material Passport：源码逐段阅读＋公开语言/库语义核对；编译、导入和语义测试0。审查对象是v3的五个冻结业务文件，摘要与v2相同。结论：**支持CPython3.12的条件兼容候选；未发现必须3.14的具体依赖**。

## 1. 文件与依赖

|文件/位置|使用特性|3.12静态判断及平台责任|
|---|---|---|
|f1_model.py:7/23/50|json.dumps排序/紧凑分隔，deepcopy，SHA-256，dict/list/set，生成器、闭包默认参数、普通f-string、整数位运算|均属3.12已有能力；无3.14专有语法、类型参数或注解求值依赖|
|f1_check.py:9/50/76|独立监视器、deque BFS、Counter、集合成员/包含判断、排序错误、Path及guard.LimitReached|语言/标准库有据；guard必须单独Linux接入；replay仍复用原转换关系|
|f4_dp.py:validate/decide|递归belief DP、dict memo、tuple/sorted/max(default=)、整数费用；lru_cache导入|3.12已支持；语义核心没有依赖新解释器API|
|f4_reference.py:17/61|itertools.product、具体轨迹deque、JSON历史键与SHA-256|3.12已支持；保持与DP分离的解释/终态路径|
|compare.py:34/74/87/118|固定夹具、G64、range、product、Path读写、比较与独立参考重放|3.12已支持；ROOT/write/digest来自资源guard，路径与证据写入要适配|

没有第三方依赖、typing注解、async/模式匹配或3.14特有功能。普通f-string和容器构造足以表达当前代码；本审查只推荐已发现的3.12，未据此扩展支持所有旧版本。主资源guard的msvcrt/_winapi/WinDLL、O_BINARY、Job/句柄/Windows路径仍需另行处理。

## 2. 状态编码、顺序与费用

**状态编码**：F1 canonical采用sort_keys=True及separators=(',',':')，随后默认UTF-8 encode；当前有限域由普通字符串键、整数、布尔、None和列表/字典组成。输入构造和SHA字节约定保持后，可静态支持相同canonical字节的预期。JSON输出参数与输入/状态域仍需真实测试。来源：[Python3.12 json](https://docs.python.org/3.12/library/json.html)。

**F1顺序**：cfg由configs列表构造，successors按dict插入顺序、固定children/证书/attempt列表和range生成。heads中的parents、double_child中的used只用于成员判断；monitor中的集合用于基数/包含关系，错误最后sorted(set)。所审路径没有将未排序字符串set遍历作为后继调度来源。BFS的deque/发现时seen登记决定最短首轨迹；重放使用同一转换关系，独立性限于monitor与业务守卫分离。

**F4顺序**：action/initial/segments来自冻结列表；normalized返回排序tuple；observation分支排序；参考product按actions列表顺序枚举策略、deque按具体后继顺序解释。相同合法输入和资源中止边界下，3.12具备保留这些顺序的语言依据。字典插入序自3.7有语言保证，整数有任意精度：[内置类型](https://docs.python.org/3.12/library/stdtypes.html)。

**费用**：固定夹具/G64使用小整数累加、比较、min/max，未使用浮点、Decimal或机器整数溢出截断。h=0,1,2、m=0..20保持；memo大小/速度/内存随版本可变化，资源截止可能让实际完成范围不同，结果需分别标INCONCLUSIVE。

## 3. 哈希随机化与跨平台输出

保留`-I -S -B`作为候选启动约定；`-I`忽略全部PYTHON*环境变量。因此`PYTHONHASHSEED=0`与`-I`并用无法认证固定种子。本方案依靠审过的有序构造/排序，未来用独立进程重复比较语义状态与轨迹；若需要固定hash种子，另审启动合同。[v3.12.3官方命令行源](https://raw.githubusercontent.com/python/cpython/v3.12.3/Doc/using/cmdline.rst)。

业务状态canonical预期可保持；报告中的Linux相对路径分隔符、绝对路径、时间/内存/平台字段会变化。比较应明确字段及输入字节，避免将全报告字节等同当作跨平台语义要求。业务五文件保持原字节，资源三文件负责输出平台字段及错误停止。

## 4. 待授权的独立验收

|ID|有限测试目标|判据/边界|
|---|---|---|
|V0|五文件解析/导入及guard兼容API|真实3.12固定映像、字节hash不变；语义导入先有正式准入；当前未执行|
|V1|canonical/JSON/哈希|手工确定键序/紧凑UTF-8字节的固定小输入，独立SHA基准；不只比较两份相同实现|
|V2|F1初态/有序后继/BFS/monitor|固定已有参数/正见证/变异，保存有序状态/轨迹；独立monitor与重放；soft cutoff保持INCONCLUSIVE|
|V3|F4独立数学夹具|COST1在h1最优15、h2最优10；CE5_FULL一步最坏10；REAL_QUERY_COST两步2；PREFIX_BAD须选安全替代15；再按原夹具/G64及DP/参考交叉验收|
|V4|跨进程确定性与输入锁|新进程重复比较同输入的canonical/后继/轨迹/策略及整数费用；不把环境种子登记当作观测|
|V5|完整部署/资源|解释器首入口/映射、AS/pids/计数/时钟与所有故障矩阵；语义兼容通过也无法授资源资格|

这些是未来测试规格，当前无测试代码/运行。所有真实业务访问、参考、重放、变异和重复均计入获准批次统一额度；先资源资格再正式模型。原3.14从未取得正式模型结果，当前没有可声称已实测相同的3.14基准；若要求两版本实测对比，还需原生3.14与对应授权。

官方3.12在线分支当前展示3.12.16；本文只引用长期语言/库合同。实际Ubuntu3.12.3补丁源码等价性、完整依赖及动态行为未据此认证。LR-2=CONDITIONAL_PASS。
