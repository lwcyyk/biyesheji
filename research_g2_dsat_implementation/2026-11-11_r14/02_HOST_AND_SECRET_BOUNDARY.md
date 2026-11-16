# 宿主、RPC与秘密边界

## 实际数据流

`OfflineController` → `OfflineAuthorityRPC`验证预置合成Bearer及operation → 已注册`VerifiedLocalCaller` → `HostReadPolicy`核精确scope和独立读取权 → `AuthorityReadHost`核单次permit/reader/epoch/空闲连接 → 原R12适配器 → 合成reader/codec → Authority域内B1净化对象 → 最小摘要JSON → Controller。

RPC/Controller/codec位于新测试文件；工程宿主模块只依赖标准库、原R12及其纯规范函数。无storage/services/Provider/SQLite/NetworkX导入，无服务启动或新RPC部署。

身份绑定由受信合成RPC在验证Bearer后选取已登记对象。正文自报actor/admin/trusted/source_confirmed、选择器、reader/key/path和字段扩展均被拒绝。`bind_authenticated_caller`和`allow`是宿主内部API；它们接收已认证事实，实际部署中的认证发行链仍属H2责任。同进程受信Python代码可调用内部API，H1未提供对敌对Python代码的隔离。

## 权限与范围

管理主体actor=user，合成服务通道为rpc:controller；业务caller=agentA等属于获准任务tuple。两者分别核对。每项读取权绑定account/audience/task/caller/generation、预定grant、输出scope引用、有效期和策略版本。

只接受singleton tuple，避免将多个获准tuple展平成笛卡尔积。请求正文无单grant/rid筛选能力；宿主用可信策略中预定grant核验R12内部结果，出现额外同tuple grant时整体拒绝。历史管理读取权与业务grant.active分开；业务grant撤回后，在明确历史查看许可下仍可获取最小摘要。

permit绑定本宿主对象、reader、producer、locator、epoch、已认证caller及当前策略版本。合法尝试在读取前消耗一次permit；预算拒绝或后续失败仍保持该次使用，自动重试0。两线程争用同permit时只发生一次读。

## 公开结果

`dsat-host-read-summary/1`保持R13根及audit字段白名单，≤4096字节。包含局部a、内部净化快照摘要、获准scope引用、读时钟、绑定状态、固定缺口和有限审计。

Controller输出中没有grants/requests/原请求/handle/材料/原生标识和完整state。测试探针在模拟Authority域内核对rid、request_digest、origin、operation、source_rid、phase、结果引用、legacy O及来源关系；探针只将布尔检查和净化管理摘要写入公开结果。

原R12在源内核原完整请求digest、handle/grant/origin及attempt/release。跨origin或缺失父来源保留source_rid=null及SOURCE_REFERENCE_UNAVAILABLE。Native来源全集、容量、持续失活、原生frame和typed O/o均保持缺口。

HostSummary保存规范JSON字节，to_dict返回新对象。上下文、policy、permit、host禁止序列化，repr固定redacted。异常/日志采用固定码，host audit回调只接收固定投影；日志故障丢弃业务数据并保留已付费用。Python内存及时安全擦除和OS级跨进程隔离保持后继责任。

## 与R13规格的精化

- 原R13 Schema JSON中的大整数上界经JavaScript数值表达写为9223372036854776000。实现采用原B1的精确`(1<<63)-1`，属于边界收紧。原文和Schema副本保持原字节。
- missing_fields收紧为固定码枚举；H1 source_kind限定SYNTHETIC_ONLY，真实源注册仍需H2。
- source_sql_count=0表示实际SQLite调用0；真实key_read_count=null、key_count_basis=NOT_OBSERVED。模拟SELECT/key/解码的实测计数放在独立测试证据中，保持两种证据口径。
- 世界/event不变由测试对合成源的前后摘要独立验证；公开摘要相应观测值仍为null，避免伪装进行了H2读前/后SQL核验。

实际错误码复用R13与B1枚举；REJECT_UNAUTHORIZED、INSUFFICIENT_SCOPE、BUDGET_EXHAUSTED、SOURCE_BINDING_FAILED、SECRET_BOUNDARY_VIOLATION、UNKNOWN_PENDING是结果报告分类，未改旧协议。审计一旦发现越界尝试，标记HOST_ISOLATION_BLOCKED并令整轮验收失败。缺typed O/o及SOURCE_OR_REFINEMENT_GAP持续输出，Native/global/math资格固定关闭。

当前Controller与Authority的隔离证据属于合成传输的数据合同；真实进程认证、ACL、key权限、全状态解码域和部署日志策略尚未验证。
