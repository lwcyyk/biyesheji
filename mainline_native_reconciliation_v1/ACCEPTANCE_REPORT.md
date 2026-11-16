# 未知创建尝试的对账与关闭验收

2026-11-05，Asia/Shanghai。

本轮裁决为 **现有成熟组合在登记的受限模型中完成关闭**。适用范围是预先启用标识元数据日志、一个实际刷新发送、该源码模型每发送至多一个原生单位、唯一未知创建、可信入口与受控写入者、窗口内暂停 B 新创建并保留 B 资源使用。

两条原生轨迹各采样一次，均为 PASS_CLOSED。安全失败、ABORTED、INCONCLUSIVE、未运行和自动重采均为 0。M3-02 另包含一次预期的保守 UNKNOWN，随后取得新证据才关闭。密码学辅助线保持 FROZEN。

## 实际关闭路径及新增条件

普通 get-tokens 的 user 过滤采用 LIKE %value%，无法直接证明仅读取本批新账户。该路线未发送，返回后的筛选没有被用作权限补偿。已有 get-token 按主键精确读取，本批使用应用 Basic 凭据，两个点读均 HTTP 200，并核对对应新账户、组织、应用与原生材料。

为获得可合法点读的标识，本轮在原生请求之前启用普通 identifier-only journal。适配器核验响应后，将签名 jti、attempt、原始来源与响应序号持久保存，完整 operational inbox 保持关闭。R 的结果登记丢失后，恢复者通过自身标识日志和获准点读取回该单位。

这是新的实验前提和日志配置，覆盖启用后已经收到并核验响应的请求。历史 M2-03 没有该日志，其历史 UNKNOWN 和原义务继续保持。本轮没有用评分者的旧私有响应重建运行者信息。完整结果收件箱是同条件下更直接的成熟方案，本轮不主张新的密码原语或独立算法优势。

## 两条轨迹的完整结果

| 轨迹 | 初始未知状态与观察 | 后续处理 | 最终 |
|---|---|---|---|
| M3-01 | AS 已生成，标识日志已持久化，控制器在结果权威登记前终止 | 恢复、撤回 A、打开窗口，精确点读归属 A1，处置 A0/A1，核验 B | 条件性 CLOSED，剩余创建上界 0，运行态义务为空 |
| M3-02 | 屏障在适配器实际发送前。标识日志为空、实际发送计数 0 | 首次保持 UNKNOWN、剩余上界 1；释放发送后记录唯一单位，再点读、处置并核验 B | 条件性 CLOSED，剩余上界 0，运行态义务为空 |

M3-02 的首次空观察属于本地标识日志。没有发送不具备范围依据的原生列表，因此它不能作为“原生列表为空”的实测。实际屏障位于 NativeHTTP 预算登记和发送之前，未使用 AS 内部处理屏障。

该轨迹的原始调用在关闭后继续交付相同结果，返回 RESULT_DUPLICATE，单位保持 DISPOSED。证明依据是有界效果已饱和，未将外层 HTTP/RPC 的处理完成等同于未来创建效果穷尽。AS 内部线程终态未被直接观测。

## 七项关闭依据

1. 两次精确点读分别返回一个已验证的新单位。
2. 单发送上界 1 与已观察同源单位 1 饱和，只建立该 attempt 效果集合完整性。
3. 日志、请求、点读和材料绑定同一 rid/attempt/批准/代次/账户/client/摘要。
4. 自身发送账本计数为 1，客户端没有自动 HTTP 重发路径，登记未来重试受到现有单次放行语义约束。
5. 权威窗口拒绝新 issue/refresh 和新批准，唯一未知创建在打开窗口时保存。其他原生管理写入者排除属于显式受控夹具前提。
6. A0/A1 的单材料处置、UserInfo、内省与独立 RT 刷新拒绝分别保存。
7. B 在窗口内使用既有材料成功，A 处置后的 B 请求也成功，之后才提交 CLOSED 收据。

独立后验来源核对还确认，实际刷新发送使用了登记 A0 的 RT，点读返回的 AT 与该原生尝试响应一致，精确主键与日志标识相同，记录所属账户符合授权。该核对读取评分私有证据，发生在运行决定以后，不回流 R。

## 收据、检查器与代码

| 交付 | 路径 |
|---|---|
| 关闭条件与源码定位 | CAPABILITY_AND_CLOSURE_CONDITIONS.md |
| 成熟收据生成 | auth-lifecycle/src/auth_lifecycle/online_state/reconciliation.py |
| 权威窗口、来源与关闭提交 | storage.py，begin_reconciliation / reconciliation_context / save_reconciliation |
| 真实查询 | native_provider.py，reconcile_query；native_http.py，get_token 固定路径 |
| 正常 R 入口 | services.Controller.reconcile，用户角色的 begin_reconciliation/reconcile |
| 采样入口 | scripts/native_reconciliation.py |
| 普通收据独立检查 | scripts/check_reconciliation_receipt.py |
| 独立轨迹评分 | scripts/score_reconciliation.py |
| 原始收据 | raw/batch01/M3-01/runner/closure_receipt.json、M3-02 同路径 |
| 首次 UNKNOWN | raw/batch01/M3-02/runner/empty_receipt.json |
| 独立检查结果 | receipt_checks/M3-01.json、M3-02.json |

普通检查器不导入收据生成器，核对条件、目标、元数据绑定、证据包摘要及源码引用。独立评分器另读取权威、实际发送计数、原生观察和日志，核对收据已经提交及事实对应。检查结论为 VALID_CONDITIONAL_CLOSED，继续携带源码模型忠实、受信任日志和写入者范围等前提。

## 开发验证与模型边界

最终全仓 125/125 通过，耗时 86.439 秒，执行前源码锁为 SOURCE_LOCK.json。此前开发轮有 124/124 与对账模块 5/5 记录，原始日志均保存。

13 组负例覆盖空观察迟到创建、相同列表后新增、分页插入/删除遗漏、A/B 未知来源混淆、其他批准材料、多效果、实际重试、前沿开放、查询/处置超时、A 未知而 B 合法工作、未来重试未排除和缺少写入者清单。每组先得到 UNKNOWN，再强制改为 CLOSED 验证独立检查器拒绝。另有元数据篡改、缺少证据包和真实控制器方法的合成原生端到端回归。

原生结果绑定 raw/batch01/SOURCE_LOCK.json、MODEL.json、model_sources/ 及运行环境锁。源码到发行二进制的可复现构建尚未证明。单发送/单效果的论证来自核读源码和固定传输条件，有限采样只提供实现核对。

本批没有新增旧 A 资格的重放试探，相关入口回归复用 M2 和开发测试。本批直接核对撤回状态及已登记放行的事务顺序。分页遗漏和重复空列表为合成负例，真实 M3 没有发送多页列表或取得空原生列表。外部原生管理写入者的排除属于受控夹具模型前提，尚无敌对管理员或恶意 OS 用户条件下的截止证明。

## 成本和清理

| 分类 | 已用 HTTP | 上限 |
|---|---:|---:|
| 环境及建户 | 11 | 30 |
| 方法 | 24 | 45 |
| 独立测量 | 20 | 35 |
| 清理 | 18 | 50 |
| 总计 | 73 | 160 |

批次包含清理的执行时间为 27.329 秒，低于 40 分钟。方法请求包含两次精确点读，宽范围 get-tokens 为 0。各失败/负向刷新、内省和查询都进入相应分母。运行者自身发送计数查询为三次本地账本读取，独立 AS 数据库查询为六次，分别登记。

权威 SQL 调用为 167/180 次，提交 30/33 个事务，逻辑整状态写入累计为 1,185,165/1,385,454 字节。HTTP 请求/响应正文长度及操作分项见 COST_AND_RESULTS.json。物理累计 WAL 写入和 fsync 次数保持未测，逻辑字节不充任物理 I/O。

两个新账户均删除，清理后已观察 AT 的 UserInfo 接受均拒绝。每个账户观测到 3 个原生记录单位，刷新后父记录被替换，收尾各保留两条映射记录，其 expiry 均非正。B 保留评分发生于账户级收尾之前。证据密文与受保护测试密钥保留供复核。

## 复现与最终裁决

在新目录中设置 PYTHONPATH=auth-lifecycle/src，ONLINE_STATE_TEST_ROOT、NATIVE_TEST_ROOT、RECONCILIATION_TEST_ROOT 和 TEMP/TMP 指向新开发目录，运行 `python -B -m unittest discover -s tests -v`。原生重采需要新的授权编号、两个新账户和新的预算目录。

```powershell
Set-Location -LiteralPath 'D:\毕业设计\auth-lifecycle'
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B scripts/native_reconciliation.py `
  --out 'D:\毕业设计\mainline_native_reconciliation_v1\raw\另行授权的新批次' `
  --authorization-id '填写新的原生执行授权编号' --allow-native-casdoor
```

本轮确认了一条可检查的受限关闭路径。没有标识日志的旧丢失结果仍面临精确授权查询和来源证据缺口。最能改变该结论的新证据，是已有接口能够提供获准的精确账户枚举或等价的范围保证，并与唯一未知尝试和发送效果上界连接。

多个未知创建、自动重试、多效果、未排除写入者或已导出原生凭据会改变剩余能力与来源条件，须重新判定并保留 UNKNOWN。关闭仅针对登记 attempt 及该受限模型中的 A 单元，其他账户材料、无限后代和业务 RP 外部效果继续受各自合同约束。该结果按成熟方法覆盖、有限原生符合性和工程支撑登记。
