# 证据语义、字段修订与兼容读取

2026-11-06。本轮原生AS/RP请求0，历史报告、原始轨迹、源码快照和判定保持只读。当前读取接口为auth_lifecycle.online_state.evidence_semantics：normalize_material、normalize_query及显式RT证据判据。数据版本为native-material-observation/2和native-enumeration-observation/2。

## 1 旧字段到明确证据

| 旧字段/上下文 | 原真实含义 | 当前明确字段/视图 | 转换与限制 |
|---|---|---|---|
| refresh_rejected=true，refresh_check_kind=READ_ONLY_INTROSPECTION | RT内省返回active=false | refresh_token_introspection.performed/active/http/native_sequence | refresh_attempt.performed=false；不补造刷新请求 |
| refresh_rejected=true，存在refresh_http，原生产者为主动探测分支 | 实际刷新请求返回指定4xx，响应未含access_token | refresh_attempt.http、response_rejects_request、new_material_in_response及legacy_only_no_access_token | 是否有其它材料与是否有AS创建效果继续分别登记；密文响应可离线补证 |
| 无模式、无HTTP，仅refresh_rejected=true | 未定类型的旧断言 | legacy_ambiguous_boolean=true | 不作为明确RT状态或刷新拒绝依据 |
| refresh_introspection_active | RT查询的active值 | rt_introspection_active及规范视图 | 新生产者记录rt_introspection_http和原生序号；HTTP错误、非布尔值保留未知 |
| 测量row.introspection_active/introspection_http | AT内省，而非RT | at_introspection_active/http | 网关处置返回中的同名字段按该固定access_token请求解释，运行态schema本轮保留 |
| query.reported_pages | Casdoor GetTokens的data2计数 | native_reported_count | 不映射成页数，不作集合完整性或截止证据 |
| 返回数组长度 | 该Find响应的实际行数 | returned_record_count | 与count查询的值、时点分开 |
| page_capacity/page_number | 请求容量及页码 | 保留并在规范视图加requested前缀 | native_reported_page_count=None；如需派生页数须标注计数快照 |

原生产者定位为M6/source_frozen/scripts/measure_native_casdoor.py的两个final分支，以及source_frozen的native_provider.reconcile_enumeration。当前生产者移除歧义refresh_rejected输出，分别记录实际刷新及内省字段。四项当前评分脚本改为读取明确证据；旧类型缺失不自动提升。所有历史原件仍保留旧键。

Casdoor controllers/token.go:GetTokens先执行GetTokenCount，再调用GetPaginationTokens，返回paginator.Nums()。go.mod固定Beego v2.3.8。本轮定向取得对应公开paginator.go，L50–51的Nums返回p.nums；PageNums另在L37–41计算页数。因此data2的计数含义有原生控制器、依赖原文和实际响应支撑。该公开源码请求单独记入sources/SOURCE_RETRIEVAL.json，未访问原生AS/RP。

## 2 不能合并的状态与单位

| 观察/单位 | 可以支持 | 独立证据责任 |
|---|---|---|
| LOCAL_REVOKE_COMMITTED | 可信事务中旧批准的新放行停止 | 原生单位是否接受、全部后代及E效果截止 |
| 撤销HTTP200 | 对应接口返回 | 原生实际失效；Casdoor未找到记录也可能成功返回 |
| RT/AT内省inactive | 授权方在该查询下的声明 | 指定资源接受、离线JWT/ID token和其它RP |
| UserInfo401/accepted=false | 指定cookie-free端点本次拒绝 | 任意RP与不可逆业务效果终结 |
| 当前Find集合完整 | 登记范围的读快照覆盖 | 查询后迟到创建、来源完整及每尝试效果上界 |
| 条件性CLOSED、义务列表空 | 在收据前提下结清该尝试的登记义务 | 无界后代、未登记写入者及原模型之外能力 |
| 本地阶段DISPOSED | 代码所登记的已知单位处置条件 | 原生全局关闭；其本身不认证事实真实性 |
| W_h的h | 有限模型决策步 | 墙钟、网络阻塞和产品SLA |
| M_r的r | 单任务原子重绑次数 | 认证HTTP数、配置动作数及模型决策步 |
| 算法Q、批准budget、原生HTTP账本 | 各自资源合同内的消耗 | 它们没有默认一一对应；一次处置可能产生多个HTTP |
| G、token字符串、批准代次、OS域 | 已审定原生效果域、材料、批准来源、部署对象 | 它们没有默认相等关系；M_r根需额外原生映射 |
| 逻辑状态序列化字节、WAL文件大小 | 实现级代理量及留存尺寸 | 设备物理写入、fsync次数；缺测保留NOT_MEASURED |
| 43检查、2条M6原生轨迹、148项历史回归 | 检查项目、采样与开发正确性各自分母 | 不汇总成独立样本数或统计显著性 |

UNKNOWN也有三种上下文：模型中已声明的观察标签、求解器模型边界状态、运行层结果/恢复不确定状态。前者按完整Post继续，后两者按各自失败规则保持未决，不互相充任成功。模型终态依赖非空K及全部严格义务；运行层义务空不能替代完整模型终态精化。

## 3 转换证据与读取方式

verify_evidence.py读取原测量、各冻结生产者和预算序号；审计密文仅在评分权限下解封。最终输出到audit_final_v3/NORMALIZED_EVIDENCE.json，原路径、SHA-256、JSON pointer、冻结生产者及可取得的native_http_ref逐项保留。实际RT主动请求与内省按actor、token引用、类型和序号比对，公开输出不含原文材料。

登记语料共有79个规范化视图，其中8个RT内省视图、9个实际刷新请求视图和3个枚举视图。这些是历史工件的读取视图，新增原生采样为0。旧RT内省缺少直接HTTP字段时保持缺项标识，再以封存响应补证；解密失败会输出UNAVAILABLE，避免补造数据。

源码归档、原判定、M2评分修订、M4清理修复和M6公钥计划内ACL追加均保留。M1初始文件中20个NOT_RUN是槽位占位符，续行只替换这些占位符，原ABORTED仍在21分母内。首轮校验程序曾把占位符与续行重复相加，并误读52调查的rows外层；audit01原结果保留，修订程序在后续目录复核。

## 4 消费者与共享边界

当前measure_native_casdoor与native_provider仅调整证据字段。score_native_casdoor、score_reconciliation、score_unidentified、score_native_isolation使用新的纯读取函数，不改原生处置或关闭条件。测试用例把无类型合成断言改为明确主动刷新响应。历史评分不被重写。

新读取器属于生产者/消费者共享的数据解释基础，独立评分的全部代码不能因此称为完全独立实现。判定、来源、事务顺序和收据证明责任仍在各自检查器。9项新增语义回归专门检验状态提升、HTTP错误、歧义布尔及count/page混用；全仓结果单独绑定本轮源码。
