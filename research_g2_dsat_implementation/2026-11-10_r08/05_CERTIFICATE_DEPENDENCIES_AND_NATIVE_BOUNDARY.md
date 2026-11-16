# 证明层、依赖当前性与旧协议边界

## 1. 三层断言

数学包证明输入关系的MATH_OPTIMAL/MATH_INFEASIBLE_CERTIFIED及R/H；条件档案保存“若来源/c/birth/E/D/P/前沿成立则scope关闭”的历史命题；真实Native资格另需当前可信G1/部署证据。S3-A只保存前两层与保守O，native_admission固定SOURCE_OR_REFINEMENT_GAP，global_complete=false。

C_local来自已提交撤回及执行覆盖；C_native覆盖声明材料/后代/前沿/路径；C_effect需要业务sink/在途效果合同。A24的H=0不结清await_terminal/window/effect。B准入有自己的当前授权/支持/共享影响守卫，不由旧证书授予。

## 2. 绑定与当前验证

| 依赖 | 保存与重核 |
|---|---|
| 数学对象/packet | 按内容哈希固定，可信验证器读取完整字节并核独立证书；不信任body.math_accepted=true |
| checker代码/Schema | 验证记录绑定checker_source_digest与packet；变更后重验，历史结果保留 |
| base世界/O | a/o和base_O/source_snapshot/request_scope/current_grant摘要锁内对比 |
| 投影O/证明上下文O | 分开于base O，核projection_O_digest=proof_context_O_digest并校验原义务覆盖 |
| 请求/来源/birth | 原五元、原审批实例/代次、DB/issuer/birth与完整I/E对应，变更重准备 |
| grant/policy | 目标gA可已撤回；当前管理写权与目标状态分开；B撤回、gV新增、服务策略epoch变化重核 |
| 时间/证据scope | 按可信当前clock和有效范围检查，过期可留历史数学；不改原packet claims伪装当前 |
| AS版本/材料/前沿 | 独立外部frame/epoch/源收据；本地a/o无变化不代表AS无变化 |
| 已付费用/严格O | stable work ID与digest防重复，audit/新源风险不能由旧proof删掉 |

既有R07 packet的dependency只有authority_version/source_version/evidence_version/now/valid_until，未含真实O revision/管理授权。S3用外层提案绑定扩展，不改变旧dsat-proof/1或重命名其SYNTHETIC模式。

数学计算/检查可锁外缓存；可信缓存按packet/checker/输入摘要索引，原生当前资格从不由缓存自动继承。CAS通过后AS仍可变化，只有有保证的持续frame/前沿合同才能跨提交区间使用；一次即时读AS不补出原子Fence。

## 3. 时间退化策略

提案把require_current_dependency或允许历史归档的策略纳入digest。若要求当前且已过期，持久拒绝/重准备；若允许历史档案，可记录数学命题并标current_use=STALE/UNESTABLISHED，不静默升级/改变原proof。R07逻辑now/valid_until来自合成夹具，不对应现场墙钟资格。

锁内时刻检查也不等于有效期覆盖到COMMIT：fsync/调度可能延迟，AS仍独立变化。S3-A只记录checked_at和input-time条件，不返回CURRENT_NATIVE_ELIGIBLE。若将来要求贯穿提交/使用区间的真实有效性，需单独可靠frame/服务协议或相应时间保证；重复读一次时钟不能消除最后的间隙。

## 4. 旧消费者与迁移

旧native-attempt-closure/1按原单未知条件保存/读取。新的typed proof/commit不写旧CLOSED、不清legacy phase/窗口；W_h继续完整终态，不通过删旧O使其可行。

当前legacy status按phase重新生成rid义务；简单添加typed O字段会被忽略，严格字段客户端也可能拒绝。S3-B需要新版本读端点及权限，DSAT模式的全局完成只能读完整typed ledger；旧单未知接口仅在原scope且无重叠新风险时允许，否则LEGACY_SCOPE_UNSUPPORTED。保留旧格式不等于允许旧消费者作新全域判断。

最小生产迁移候选：逻辑dsat命名空间内加o/O/历史ref，同时提升DB user_version到3，使旧AuthorityStore启动拒绝。当前旧连接不会因header变化自动停止，因此还需停止/确认旧writer退出、单实例policy/schema fence并更新所有维护O的legacy事件。仅加schema号无法阻止已打开的旧连接继续写。

迁移要把初始化O、版本、历史/迁移receipt和schema fence放受控事务，失败保持旧状态或拒绝启动；现有自动migration没有这项完整保证。S3-A只做合成旧JSON加载/模式隔离测试，不执行生产迁移。

## 5. S3-B剩余门

真实读用权限、可信typed导出/原请求连接、源到运行实现、全部writer/holder/重试/后代、持续D/接受路径、当前frame与预算/清理均待实例化。当前S1也只接受合成冻结manifest；真实来源桥必须单独版本化审查，不能把mode换名当认证。数学包保持不可变，实际资格若将来成立也应由独立外层记录证明。
