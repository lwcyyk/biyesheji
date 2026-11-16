# O原子转换、风险覆盖与条件证明

## 1. 两层责任

O中的每项至少有稳定ID、origin/attempt/material/scope、风险组件与covers引用、创建/更新revision、来源/前提、审计性质和费用ref。风险组件包括未见直接创建、已见材料使用、后代/未来入口、结果/handler审计、窗口与业务效果；合法B支持是被保护资源，不要求立即关闭。

要求对每个可靠当前相容真实s：Risk_declared(s)⊆⋃Coverage(o)，o∈O_after。真实source不完整时，不用空F或缺证缩成空风险，保留原更宽义务。

**S3-A保守门**：数学/条件证书不消除真实Native风险。默认O_after为旧O与新增O的并集；允许标签/分组重构仅在新covers结构包含旧全部未排除组件时。settle→close必须同时保留未证的unseen/origin/descendant/source-premise残余，可称pending_source或保留原settle。真正Native discharge仅留给S3-B。旧rid phase及legacy义务视图不因数学H=0消失。

covers不能只由提案自填true或ID列表。验证器采用固定语义规则：保留旧描述、或由pending_source持有不可变旧描述摘要，才能覆盖原未见风险；close:u仅覆盖该材料风险。旧描述/原scope/birth/origin引用必须可核对，不允许用标签重命名伪装覆盖。

## 2. 转换规则

| 条件 | S3-A提案与持久效果 |
|---|---|
| Unknown Issue/Refresh | 保留settle及匿名可能材料；无收件不减容量 |
| 正向绑定u | 增close:u及历史birth，保持原origin；直接总容量和其他残余分别记录 |
| R_T=0、H_T>0 | 存容量饱和条件记录，保留材料使用/源前提债务和审计 |
| H_T=0、Native前提未验 | 存CONDITIONAL_SCOPE_CLOSED；原真实风险不清，审计/window不清 |
| 来源歧义 | 分组覆盖全部Γ/保守E，不任选一个真实f；covers保持旧风险 |
| 新批准/新release/后代 | 由相应domain event原子增O与revision；旧proof仅原scope历史有效 |
| 迟到 | 五元/原origin核验后隔离，增历史与材料责任；不重绑B/V或恢复旧许可 |
| B局部进展 | 只改自身执行责任；甲/V责任不被抹除，当前B守卫独立 |
| F空/冲突 | 可存已证数学不可行档案，保留旧O、双方证据及investigate项；不作全称关闭 |
| 直接请求删O/改grant/phase | 拒绝不支持的写集；没有partial strong-close更新 |

本地纯审计/重复档案可按独立可信终态结清，必须有适用证据，不能由H=0顺便删除。所有旧历史、birth、spent和费用保留。

## 3. 十项安全性质

| 性质/形式命题 | 前提与位置 | 证明、反例、缺口/未来测试 |
|---|---|---|
| P1 原子性：成功则O/档案/费用/版本/回执同存 | SQLite原子持久、T5—T6同库事务 | 前COMMIT回滚、后COMMIT全存；外部proof文件先删会悬空，改同库；事务中kill待测 |
| P2 覆盖：旧未排除Risk仍有covers | 可靠初始化/源包含，T4覆盖校验 | union/包含替换逐组件归纳；只按H0删settle反例；真实G1前提仍缺 |
| P3 版本：接受基于当前a/o | 所有world/O写者遵循同一入口，T3锁内核对 | BEGIN IMMEDIATE串行，旧base拒绝；漏给legacy release增o失败；双提案/独立O变化待测 |
| P4 来源不变 | 固定五元/实例/origin与birth，T3—T5 | 转换继承不可变origin；迟到改到B为反例；Scope映射/可信导出仍需G1 |
| P5 幂等 | 持久ID/digest/owner/结果，同事务 | 先查簿再CAS，不重做effect；簿在事务外丢失或失败ID换body为反例；ACK丢失/冲突重放待测 |
| P6 scope保持 | 三层结果及允许写集，T4/T5 | 数学记录不授权/不改Native；把条件bool写旧CLOSED为反例；S3-B独立门 |
| P7 恢复安全 | SQLite/文件系统/无外部回滚、key/codec可用 | 恢复已提交状态或拒绝服务；恢复缓存覆盖DB反例；跨重启/坏codec/旧schema待测 |
| P8 B保留 | 不写B批准/支持，实际B最终守卫/共享frame | 提案变换不越权，B事件增加自身责任；根独立却共享配额为反例；真实影响域仍需原生证据 |
| P9 外部当前性 | 独立Native frame/epoch/前沿与路径证据 | a/o只代表本地，不能推出AS未变；旧handler在CAS后创建反例；S3-A只存条件，Native门blocked |
| P10 历史兼容 | 新namespace/版本协商/旧写者fence | 旧CLOSED/1原义不变，typed O不被legacy全局通道忽略；旧连接跨迁移写入反例；B迁移/客户端门待测 |

## 4. 条件归纳证明

H1可信当前单实例写边界/身份/持久化不回滚；H2初始O与来源/风险过近似可靠；H3全部domain事件同事务维护a/o/O；H4proof/checker/数据字节绑定及覆盖规则可靠；H5当前权限/本地依赖锁内检查、Native条件另守；H6费用/ID簿同库原子且保留期满足。

基态满足覆盖。读取/计算无权删除旧状态；拒绝/回放只写档案或读取回执，不改世界风险。成功commit在锁内重核当前快照，允许delta只增加或保守覆盖替换，故逐组件保持覆盖；证明/审计/费用与receipt一起持久。domain事件对新风险先建责任，撤回保旧已release风险，迟到继承原origin。SQLite恢复只显现完整提交或旧状态，缓存不成为权威；版本/幂等守卫在重试后重新作用。逐有限前缀得到P1—P8/P10的条件安全。

P9不从本地归纳推出AS事实，而由“无Native写入＋外部门”维持层级隔离。H失效时停止强声明，保存更保守O/冲突；没有最终消除UNKNOWN或固定墙钟保证。标准事务、幂等簿及持久工作流足以实现此合同，未主张新通用协议。
