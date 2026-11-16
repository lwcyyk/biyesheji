# 四类只读证据：真实能力与证明责任

## 1. 读取、推断和本地登记分别计费

读取原生证据不新增Token；UserInfo仍是一次外部访问，可能有日志/配额影响。Inbox lookup读取已持久结果，Controller.deliver随后会写权威记录。本轮ProjectEvidence被定义为无I/O的纸面函数；获取证据和提交对账是前后两个独立阶段。

原生响应、可信适配器内部和代理公开投影分别管理。Token原值、密码、client secret留在可信域；AI仅接收自身获准任务所需的最小无秘密结论。组织全读的秘密/隐私批准不能由事后账户筛选替代。

## 2. Inbox

接口：C03:44—52 lookup；C02:118—130 deliver。所需批准：管理者有deliver，Controller/Provider身份合法，查询严格绑定rid/digest/origin/attempt_id/release_version。

可见事实：Provider在收到成功响应并完成token_bundle校验后，按上述五元保存outcome/material。C03:132—140逐项AES-GCM、append/flush/fsync，重启加载19—39。它直接证明“可信适配器保存了这个返回”；与当前权威release连接后才支持来源与创建推导。source_rid不在inbox五元中，必须回到原请求。UNKNOWN Issue和Refresh均可能有可回放的成功结果。

限制：没有Inbox项，只说明当前没有可取得的持久返回。AS可能已创建而响应丢失、验签失败、保存前崩溃或禁用inbox。Inbox自身不证明请求曾被合法接纳/放行，需权威版本。迟到/隔离由C01:264—304决定，不能仅凭保存时间判断。

新增发现：C03重启用`results[attempt_id]=result`逐行装载，存在最后项覆盖早项的代码形状；它没有输出同attempt冲突全集。AEAD每项认证不证明日志无删行、无重排或无合法密钥持有者篡改。新规格要求可信内部导出全部相关条目/尾部状态、重复和冲突，不能把当前单lookup当作完备日志证明。

费用：新增AS机会0；本地密文读取/解密、索引、RPC、权威登记和历史获取成本照计。当前过期Token结果回放与命名材料验证有不同路径，不能因此自动标失活。

## 3. Identifier Journal

C03:116—121对Issue和Refresh采用相同event名，保存五元、native_unit_id、verified_account/client、native_sequence。顺序为原生响应→token_bundle验证→journal→可选inbox；它位于AS创建之后，并非AS事务内写前日志。

日志行不含operation/source_rid，必须与权威原请求或摘要核验的请求正文连接。AT的JWT jti到持久Token单位需要G1源映射；ID Token自己的jti不另计一次创建。

C11:86—98 EventLog使用进程内锁、append/flush/fsync。普通日志没有独立AS签名、不可删链、全写入者序号或完备性证明。启动消息只声明本进程启动后收到响应的范围。缺项可能对应响应未到、关闭journal、崩溃/部分尾行等；不能据缺项消除容量。

可信正向日志可以辅助绑定一个实际创建单位，完整性/唯一性/代次由源合同另外保证。日志中的同一创建在inbox、点读和快照出现多次，U只计一次。当前没有通用journal只读导出RPC，属于最小接线缺口。

费用：本地读取、解析、完整性/权限检查、索引和历史原生获取成本；按ID继续点读时增加各次AS机会。

## 4. 命名查询

| 接口→批准 | 可见字段/覆盖对象 | 可信前提 | 无法单独推出 | 费用 |
|---|---|---|---|---|
| get-token→命名记录/组织读取权 | owner/name、账户/app、时间、Token字段；当前行 | 精确ID、AS授权、账户/app校验、真实存在性语义 | 本地父子/attempt来源；未来无迟到 | 每次1 AS机会＋本地验证/秘密披露 |
| RT introspect→client及指定RT使用权 | 对应时点active及元数据 | 真实调用、状态/HTTP可解释、身份绑定 | Refresh已发送/失败、旧handler已停止 | 每次1；当前独立Controller入口缺 |
| AT UserInfo→当前任务/同源材料 | 固定cookie-free路径、HTTP/sub | C01最终准入、C03/C10、G11/G12 | 任意RP/cookie拒绝、未来可用性 | 每次1＋RPC；不新建U |
| AT introspect→指定材料 | 该路径的当前active | 与RT内省分型 | 所有路径及后代已关闭 | 每次1 |
| 已有disposal结果读取→管理范围 | 已发生revoke和命名AT检查记录 | 权威记录、源/路径范围 | 再次原生验证、全部RT/前沿终态 | 本地读取；历史三次成本保留 |

本轮只读路线不调用dispose本身，因为该操作包含原生Revoke。已有disposal记录可作证据输入；缺持续失效证据则保留close义务。未来处置属于另行批准的生命周期流程。

C03点读helper的refresh-only机会SQL及写死组织/app、C04的verified_unit_id守卫、C12单未知收据都保留。不能把Issue字段换个名字塞入旧helper。

C13为旧记录保留字段别名，有些HTTP缺失的历史观测仍可被归一展示。R04须保留其缺项标记；新的当前状态/失活证书要求明确performed、HTTP/错误、对象与路径范围，不能将兼容归一值自动提升为完整证据。实际刷新拒绝字段的creation_effect_excluded在该模块中仍为未证。

## 5. 获准范围快照

G01:37—70的count和Find分开；C04:161—167固定组织等值、p=1、pageSize和name排序。C05单Find完整性还要求注册宇宙、行数界、唯一ID及manifest。scope包括整个返回组织，user/app在可信内部再精确筛选。

完整性分解：读取批准/全字段边界；实际查询参数；未截断响应；足够单页上界或可靠一致分页；单Find数据库读合同；账户/app筛选；已知初始历史与全部允许写入者。跨多页无共享快照/稳定窗口时，不能合并成一个时点的完整集合。HTTP读取上限和解析错误均须保留，不能截断后当完整。

第三grant使旧2批准/预算20不适用。新完整性依据应覆盖整组织所有账户/应用的初始记录及全部允许创建，保守界可用`R_initial+Σ全域批准可产生的单位上界`；不能只取本账户三项尝试或当前记录数。此为标准计数推论，真实manifest/排他写入仍需证据。

快照没有task/rid/attempt/parent字段；出现行只提供存在及有限候选来源。记录删除不删除历史创建见证。没有新行不封旧V位置handler；H01/H02历史条件实例不能直接扩大到本轮。

## 6. 权限和覆盖结论

Inbox正向回放、可信journal正向绑定、获准命名查询、满足合同的范围快照均可成为可靠输入。无合法权限的读取返回REJECT_UNAUTHORIZED；未暴露接口记SOURCE_OR_REFINEMENT_GAP；合法但证据不足记UNKNOWN/INSUFFICIENT_COVERAGE。各来源之间不存在能免除其余责任的单一“最高级”字段。
