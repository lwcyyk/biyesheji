# 八类资源口径与候选

八个原名称与R43的unit字段逐字保留，新增的分项单位用于避免混加。所有existing_approved_maximum仍为null，approval_status=PENDING。候选和静态界均未写入approved值。

| ID | 原始名称 | 分项单位 |
|---|---|---|
| R1 | fault injection/clock-transition arms total | count of callback registrations; count of virtual-clock writes; count of other fault configuration events |
| R2 | metadata/read/write/flush/fsync/open/close call ceilings | Python API count per op; OS read/write/other operation counts; OS read/write/other transfer bytes |
| R3 | lock objects and in-memory fixture/stream counts | objects by type, total/live separately; model file-content bytes, separately |
| R4 | maximum newly created directories | directory count by owner |
| R5 | whole interpreter RSS/working-set budget and enforcement | bytes of OS peak working set; bytes of private/job commit, separately |
| R6 | actual total cumulative payload write-byte ceiling | cumulative explicit payload bytes; process-accounted transfer bytes, separately |
| R7 | complete normal/failure evidence demand within each artifact cap | serialized required bytes by artifact; partial-file/temporary coexistence bytes |
| R8 | 120s external supervision/abort/cleanup contract | monotonic elapsed seconds; termination-request/exit lag seconds, separately |

## 可复用的局部界

R1回调arm上界23；ctx.clock写次数55次初始化+7次直接场景赋值+6次hook交付=68。其他mode、输入和账本配置采用独立口径，不能把23称为全部故障控制数。

R3夹具和自有RLock总构造界55，活动fixture域最多2。计入异常引用/延迟回收时，保守的自有RLock存活对象界可取总构造55，不能直接用活动域2替代。模型流总界71、单夹具文件4及内容cap包络1703936B继续限原条件。隐式runtime对象仍null。

R4当前driver只创建2目录。若未来观察器使用独立一层parent目录，组合计数为2+1=3；这是显式新设计候选，待单独确认，当前目录权限没有扩大。

R6显式8产物payload界为933888B，取U本身，不加无依据裕量。它不包括隐式stdio/native活动或新观察器。当前2MiB总约束原值保持；若父子证据共用它，算术剩余1163264B只代表可分配空间，不能证明观察器负载适配。

R8重复既有120秒，不新增宽限。终止完成迟滞上界为null；CPU-time限制和wall deadline不能互换。

## 必须保持null的字段

全故障统一总量、全进程操作/传输向量上限、隐式锁/句柄、整进程工作集/提交数值、全部进程payload、完整正常/失败文件需求及严格退出迟滞缺少依据。当前不建议512MiB等默认数，也不由933888B推断RSS。

每行JSON含源码位置、成立条件、测量/外部监督、超额与清理策略。候选工作集要另行选定并验证初始/持续策略；原32MiB请求仍只覆盖测试自有数据。

## 批准范围

R44_RESOURCE_LIMIT_APPROVAL_REQUEST的JSON和Markdown是局部候选审阅材料，完整8类数值包尚未就绪。120秒和2MiB原值不重新增加；新监督器文件/目录/句柄/开销也不会自动得到旧额度。

超额或观察失败后停止新动作，保留已花费用与可信前缀；只处理本次拥有对象，未知尾部保持UNKNOWN。自动重跑和不确定写重试0，任何额外资源需要独立明确批准。
