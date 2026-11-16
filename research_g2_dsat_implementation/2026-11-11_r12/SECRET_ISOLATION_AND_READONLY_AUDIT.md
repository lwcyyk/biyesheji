# 秘密隔离与只读行为

## 公开出口

适配器从白名单构造新对象，未使用“复制原请求再删字段”的方式。原handle只在受信源内参与原完整request_digest核验。password、access/refresh/ID token、client secret、API key、private key、原始敏感body、native材料及未知扩展均不进入输出。

B20等用例扫描返回JSON、对象表示、pickle后的Staging、stdout/stderr、日志、错误返回和异常文本。上下文调试表示固定为redacted，序列化上下文被拒绝；原始reader不进入结果。嵌套未知公开字段即使重算内容摘要也被Schema拒绝。合成reader抛含哨兵的异常时，只返回固定错误码。

所有输入哨兵仅保留在获准合成夹具中。运行/报告公开数据不记录哨兵原值；输入夹具SHA用于版本固定，不作能力或材料引用。验证限定已给哨兵、白名单和scope行为，生产秘密分类与宿主/OS边界另需实际证据。

## scope

账户、audience、task、caller、generation同时约束输出，覆盖grants、requests、disposals、windows及嵌套creator列表。foreign记录和聚合数量未复制到代理输出。无法证明Native来源全集时保留SCOPE_UNIVERSE_INCOMPLETE，窗口source_scope_complete保持false。

管理者已具有读取能力，与是否将全部管理数据交给Agent分别判断。当前工厂假定宿主已做真实认证/授权，本轮使用合成上下文验证子集和reader绑定逻辑，没有取得生产身份发行链证据。

## 世界只读

测试对每次常规接口调用比较源state规范字节和version，检查grants、requests、预算、phase、窗口、隔离、旧O和event不变；修改输出的嵌套列表/字典不能修改源对象。旧call/execute写入口设置断言陷阱，命中数为0。

B31以4个线程在同一起始barrier会合，每线程执行3次读取。12次都经同一source lock串行化，最大持锁深度1；version一致、世界/event不变。读取遥测counter属于允许的源副作用，单次读取预算也实际计数。

有限operation_limit下保留一次源读加6次旧writer预检的headroom；不足时在读取前拒绝，自动重试0。真实read_state的日志fsync/key访问仅在源码合同中说明，本轮未执行。

## 保守责任

legacy_obligations严格按获准phase/window视图保留。conservative_O_view另含source_hold、UNKNOWN settle、await_terminal、opaque材料close及window_review。reserved队列即使free budget=0也保留queued_creator前沿。旧CLOSED/1只呈现历史单attempt摘要，legacy空列表仍保留其他风险。

H=0、点失活、本地ACK、伪造source flags和本地a不变均未升级Native资格。typed O/o为未实现，接口没有O提交、regrant或凭据操作。

最终运行审计的SQLite、网络、进程、私密/越界文件访问尝试均为0。原有服务和真实运行目录未访问。
