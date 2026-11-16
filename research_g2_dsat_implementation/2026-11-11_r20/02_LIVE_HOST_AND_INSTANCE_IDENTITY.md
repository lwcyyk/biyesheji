# live 宿主、实例身份与会话合同

本稿为待实施规格，所有运行身份字段当前为空。结构化合同见 `D1B_INSTANCE_IDENTITY_CONTRACT.json`。

## 可信边界与最小适用域

首个 D1-B2 实例限定为单机 Windows、本地 NTFS、研究者控制的单一可信账户。研究者 SID、SYSTEM/管理员、Python/原生库和受批准 bootstrap 属于可信计算基。Agent、Controller、Provider 与普通网络请求均处于接纳边界之外。恶意同 SID 代码、管理员篡改、内核攻击和存储回滚超出本合同。

实际部署前须针对指定主体核验 SID、进程 DACL、解释器路径与来源。R20 保持这些运行值为空，未来通过有界 self/owned-child 句柄读取；账户名称或本机用户名推断均无法替代该核验。文件系统或 API 前提无法满足时，部署安全拒绝。

运行主体候选为研究者控制的普通专用测试进程，本次范围不创建Windows账户。新根与private对象在创建时应用保护DACL，许可主体限指定研究者SID与SYSTEM，避免先写秘密再收紧ACL。进程核验申请 QUERY_LIMITED_INFORMATION/SYNCHRONIZE 与指定安全描述符读取，stop申请受控Event信号；PROCESS_TERMINATE、进程内存读取/写入和远程线程操作保持0。已有宿主/解释器/父目录ACL仅核验，新实例之外的ACL修改保持禁止。

## 身份元组

部署身份为以下实际量的联合绑定：

`environment_id, approved_root, root_volume/fileID, instance_uuid, initialization_id, DB_volume/fileID, source_manifest_digest, effective_config_digest, Python_image_identity, owner_SID`。

运行身份再加入：

`PID, creation_FILETIME, process_epoch, loaded_artifact_origin_set, owned_listener_reference`。

宿主绑定加入同一 `Store/connection/RLock` 的强引用与生命周期状态。Python 对象标识仅作当前进程内关联；PID、路径或 UUID 单独使用均不足以提供完整身份。

`application_version=0.16.0` 继承现有包版本，部署版本使用批准后源清单摘要补充。`loaded_code_digest` 的精确定义是获准 artifact 字节清单和已加载模块 origin 的核对结果，依赖可信 OS 与只读源区域；它尚无硬件证明或远程内存完整性证明能力。

## 源码与配置接纳

1. 固定完整内部源闭包、SQL、入口脚本及运行依赖来源清单；部署源码至多 64 文件、2 MiB，实际清单在 B1 后固定。
2. 在批准根的 `artifacts/src` 与 `artifacts/scripts` 写入独立快照，排除测试、venv、运行数据与秘密。固定入口使用已批准 base Python，禁写 pyc，live 模式屏蔽环境 PYTHONPATH/user-site 注入。
3. 导入生产模块前核对 source manifest、解释器和 config；导入后检查内部模块实际 origin 及当前文件摘要。源文件 ACL 收缩为运行时只读，配置文件按实际有效字段计算完整摘要。
4. R19 `SOURCE_BASIS` 继续仅作历史来源。其 digest 与本轮合成 process 元数据均无法替代未来部署源摘要。
5. 部署批准记录来自研究者指定的可信文件/执行过程，字段 `approved=true` 或一个 authorization_id 字符串单独出现时，权限保持关闭。

配置摘要覆盖完整有效的不可变 live 配置，排除摘要自身及尚未发生的 PID/epoch/结果字段。批准记录单向绑定 config/source 摘要，配置不反向 hash 该批准记录，从而避免摘要循环。R18 确认文件保持历史内容，live 扩展配置以新版本记录引用它。

源加载前后摘要核对仍有可信宿主前提。拥有修改源码或注入进程权限的主体处于当前可信计算基，相关对抗保证继续保留为外域问题。

## 持久实例标识与复制

独占创建新根之后，用 CSPRNG 生成 256 位实例标识和初始化 ID，写入 `config/instance.json`。该文件绑定实际根的 volume/file-ID、获准路径、owner SID 和部署作用域。键/库创建时记录各自文件 ID、用途与初始化来源。

唯一性依赖随机碰撞概率与独占新路径；记录出现重复、根/库 file-ID 变化或复制到另一目录时，拒绝自动接管。数据库复制及目录复制会改变相应物理身份，旧批准元组无法直接复用。原地内容替换、恶意同 SID 复制、管理员操纵和快照回滚超出该检测保证。全局防克隆和防回滚状态均为未实现。

## Authority 单活与句柄传递

拟采用稳定 `runtime/instance.lock` 的 Win32 独占打开句柄：`CreateFileW`、shareMode=0，整个实例操作期保持打开，限制重解析/替换并核对最终路径和物理 file-ID。首次创建与后续打开分开，后续保持文件内容和身份。

准备/初始化各自持有锁。启动 supervisor 在消费一次启动授权前持锁，以显式 handle allowlist 向唯一子进程传递同一内核文件对象的句柄；至少一个拥有者在交接期间持续持有。子进程核验句柄对象后 ACK，双方按各自拥有权关闭副本。进程异常退出由 OS 关闭其句柄；父进程仍存活时，需要等待拥有子进程的退出证据并关闭父副本。

这保证遵守该入口的同一物理实例单活。SQLite WAL 写锁只串行化相应事务；RPC 端口占用也只保护地址。二者无法独立承担整个 Store 生命周期的单活保证。旧 writer 全面隔离继续属于 S3-B2；本测试域依赖可信主体只经受控入口访问此新库。

所有 Win32 操作均需 B1 在临时合成对象上验证：原型/64 位句柄类型、错误码、ACL、文件 ID、独占分享、句柄继承和崩溃释放。当前接口规格尚未执行平台验证。

## live issuer 的精确权限

`LiveDeploymentIssuer` 只接纳部署权限，创建进程内 opaque `LiveAuthorityContext`，并绑定核验后的 source/OS/root/epoch。它接收有效的继承资源和批准来源，外部 JSON 无法直接构造该能力。

子进程只有一个 context 和一个 Store；连接在取得时立即进入拥有资源栈，Store 完成后才能绑定 Dormant descriptor。部署阶段所有 `issue_permit`、`read_state` 和 P2 接纳保持固定拒绝。该 descriptor 尚未创建 R16 的已激活 MountTicket，也没有创建可使用的管理调用凭证。

真实 Host provider 分为两部分：Windows provider 证明当前受控进程/文件事实，LiveContext 绑定实际 Store 引用与状态。P1a 外部运行检查器仍延期；部署自身的有界 Ready/退出凭据限于 B2 成功判断，完整独立运行复核继续需要 P1a。

## 会话级一次读取的保持条件

R16 `_SESSION_NAMESPACES` 当前键为 connection 对象、authorization_id、epoch、规范 scope；claim 在读源前消耗槽，失败后保持已消耗。B1/B2 的真实受保护读取额为 0。

未来单独批准 P2 时，还须提供同时绑定上述部署/运行元组、singleton scope、caller/issuer、过期时间的研究者批准 envelope，并通过 R16 核心的同一 Store/连接执行。下表是未来接纳必须满足的条件，当前阶段仅实现固定拒绝及相应离线检查。

| 事件 | 所需处理 |
|---|---|
| 多 permit、并发、别名、重连 | 同一 process lifecycle registry 与原 R16 namespace 共用已消耗槽 |
| issuer 重建 | 维持同一 registry/Store/连接；重复注册拒绝 |
| 关闭后换连接或创建第二 Store | 同一生命周期内拒绝，整个 context 退役 |
| Authority 重启或启动失败后再启 | 原 epoch 失效；新的执行批准、新 epoch，P2 需重新批准 |
| 不同进程使用相同授权 ID | 核对完整 epoch/实例元组；字符串相同无法复用旧 envelope |
| 复制数据库/目录 | 物理实例绑定不符时拒绝；禁止自动继承读取批准 |
| 恢复旧会话对象 | opaque 对象不可持久反序列化；只恢复无权限记录 |
| 已 claim 后超时或日志错误 | 保留消耗状态，关闭 context，返回 UNKNOWN/拒绝 |

因此可声明的上界为：在可信同机、独占实例、单 Store 和 epoch 固定的合同下，每份未来获准的 P2 会话最多一次受保护源读。跨重启通过旧批准失效实现安全收缩。持久全局防重放、存储回滚和敌对历史 writer 保证仍需额外前提，当前文稿保留对应缺口。
