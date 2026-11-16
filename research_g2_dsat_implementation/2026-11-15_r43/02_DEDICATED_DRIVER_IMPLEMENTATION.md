# 单文件驱动实现

已新增 `test_dsat_runner_poison_classification.py`，源码SHA `28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd`。原28个ID各有明确test_T入口，按原顺序运行54个已冻结内部变体；当前全部NOT_RUN。内部变体与历史54项suite分别管理。

## 四个角色

| 角色 | 实现 |
|---|---|
| SYSTEM_UNDER_TEST | R41原Runner及真实六函数/helper，实际字节锁不变 |
| TEST_DRIVER | 单个新文件的PoisonClassification28、工厂、独立断言和main |
| FAULT_INJECTION_BOUNDARY | 每目标模块独享的时钟/path/FileIO/fsync facade，以及真实字段/字典赋值探针 |
| OBSERVATION_INTERFACE | 独立进入/返回/接受/确认事件、原字节与链、费用和所有权快照 |

未来入口先核验研究者执行packet、Driver/Runner/输入哈希及资源条件，再将已验证的原Runner字节compile到非main模块。没有用项目缓存字节码，也没有改写目标逻辑。导入原68/54模块、Runner main/controls/State.__init__、真实授权生命周期均不在调用图中。

目标State通过object.__new__及合成属性初始化。夹具工厂只定义输入状态；Poison和费用转移由实际受测方法执行。字节包参考仅编码已发表的本地协议格式，状态oracle未复制目标分类条件。

## 故障和断言

ObservedFileIO记录方法进入，再接受k字节、返回或抛错。返回0、可靠返回k和接受后抛错分别观察。flush/fsync各有单次故障。PublicationProbeState在真实seq/head/bytes赋值前后中断；ObservedLedger在真实账本赋值后中断，均不替代checkpoint。

异常匹配结合实际计划已触发证据；OSError的errno本身不足以通过。明确Refusal代码保留，其他异常成为ERROR。故障未触发、边界错位或独立断言失败均停止余下测试，自动重跑0。

前缀比较包含旧完整字节、记录顺序/内容、seq/previous/hash、压缩载荷摘要和实际收到的引用。费用检查使用c、B、k等式及独立write进入事件；目标prewrite_safe只作为待核输出。旧确认前缀为合成工厂的可信输入前提，未声称执行了原A01或完整68。

## 导入与恢复

模块顶层只含字面常量、定义和main保护，顶层import/I/O均0。目标源码加载只在main执行门之后。facade只替换目标模块属性，宿主os/time/Path继续供取证使用。离开用例时在finally恢复，释放自有模型缓冲；它没有退回SUT费用或把失败close改成原确认。

取证文件用新独占根、xb和一次性claims；旧目录没有fallback。驱动保留完整异常格式；超过单文件cap会真实拒绝并保持不完整，完整容量没有据此视为已证。

## 物理边界

当前实现的SUT流均为模型接口，可选native成功Journal模式未实现；这处选择在R41的“至多一个”范围内，实际物理目标Journal数量0。宿主输入及未来取证文件是native FileIO，均需后续独立授权。

模型fsync表示边界回调正常返回。真实断电稳定性、任意Windows故障及系统调用数需要独立证据。当前静态语法与源绑定通过，动态行为尚未验证。
