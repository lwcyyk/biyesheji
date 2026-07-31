# VDNS-PM 运行与恢复手册

| 属性 | 内容 |
|---|---|
| 适用对象 | 研究环境维护者、测试人员、答辩演示人员 |
| 环境 | Linux、Go 1.25.12、Node.js 18+、SQLite 3 |
| 数据分类 | `TEST_ONLY` 固定数据；禁止导入真实用户密码库 |
| 最后验证 | 2026-07-23 |
| 自动演练 | `./scripts/drill-g7-recovery.sh` |

> 本手册面向研究原型，不是生产值班承诺。当前实现没有远程托管服务、生产密钥托管或真实区块链部署；链锚定和外部站点使用研究适配器。

## 1. 启动前检查

在仓库根目录执行：

```bash
env -u GOPATH go version
node --version
sqlite3 --version
env -u GOPATH go mod verify
./scripts/check-spec-trace.sh
```

预期结果：

- Go 解析到 `go.mod` 固定的工具链；
- 模块校验输出 `all modules verified`；
- 规范检查输出 `spec-trace-ok`；
- 工作目录只包含研究数据，不包含真实密码、TOTP、恢复码或浏览器配置。

任一检查失败时停止演示，不应通过删除校验文件或降低密码学策略继续。

## 2. 一键演示

必须使用空目录或脚本自行创建的临时目录：

```bash
demo_dir="$(mktemp -d)"
./scripts/demo-vdns-pm.sh --data-dir "${demo_dir}"
```

完成标志为 `demo-vdns-pm-ok`。演示覆盖初始化、凭据创建、自动填充、多设备同步、网站确认更新、撤销、离线、VDNS、审计和可选响应边界。

失败判定：

- 脚本非零退出；
- 任一 JSON 结果出现 `failed > 0`；
- 可选 SCOPE-ZK 未配置却出现 proof time/size；
- 非空目标目录被脚本接受。

失败后保留目标目录用于取证，不在原目录重跑；另建空目录执行。

## 3. 健康检查

```bash
env -u GOPATH go test ./...
./scripts/check-g7-api.sh
./scripts/check-g7-security.sh
./scripts/drill-g7-recovery.sh
```

必须分别出现：

```text
g7-api-review-ok
g7-security-gate-ok
g7-recovery-drill-ok
```

机器证据位于 `test-results/g7/`，不得手工修改测试结果来获得通过状态。

## 4. 标准停止与秘密处理

1. 关闭浏览器扩展演示页面和本地 Agent；
2. 触发密码库锁定，确认活动 session 与 secret handle 失效；
3. 删除仅用于演示的临时目录；若需要论文取证，只保留无秘密 JSON/CSV 和测试日志；
4. 不复制 SQLite 演示库、RootCapsule、恢复秘密或浏览器本地存储到公开材料。

锁定后仍能消费旧句柄、重新读取根秘密或继续自动填充，均按 P0 安全故障处理。

## 5. 故障响应

### 5.1 前五分钟

1. 停止新的生命周期写入和设备加入；
2. 记录故障发生时间、当前检查点、设备和凭据伪名；
3. 区分内容故障与控制面故障：
   - 云对象缺失、损坏或回滚；
   - VDNS/log/checkpoint 不一致；
   - 本地数据库或进程故障；
   - 设备丢失或能力凭证泄露；
   - 网站改密状态不明；
4. 不把“自动填充完成”或“表单已提交”当成网站确认。

### 5.2 云、日志和检查点异常

```bash
env -u GOPATH go test ./tests/integration \
  -run 'Test.*(Rollback|Transparency|Checkpoint|Monitor)' -count=1
```

期望设备输出 `REJECT`、`REVIEW_REQUIRED` 或安全降级，不能接受低于 VDNS 当前版本的对象。保留对象 digest、ProofBundle、检查点和 monitor 证据，不记录明文字段。

恢复条件：

- 对象哈希与 VDNS 描述一致；
- 包含证明和一致性证明通过；
- 当前检查点不低于本地已见检查点；
- 本地策略重新输出可接受 verdict。

### 5.3 网站改密结果不明

状态必须保持：

```text
ACTIVE(v) + durable candidate(v+1) + UNKNOWN/REVIEW_REQUIRED
```

操作员应通过独立登录或网站恢复渠道确认实际密码，再提交强确认回执。禁止直接覆盖旧密码或把页面跳转推断成 `SITE_CONFIRMED`。

### 5.4 设备丢失

1. 从仍受信设备发起设备撤销；
2. 固定撤销最终序号；
3. 轮换名称空间秘密代际；
4. 仅向剩余活动设备封装新根；
5. 验证丢失设备无法获得新代际对象；
6. 对高风险站点另行撤销会话、API token 或重置 MFA。

边界：撤销不能擦除丢失设备在撤销前已经取得的历史明文或密钥。

### 5.5 本地数据库损坏

先复制损坏文件用于诊断，不在原文件上执行破坏性修复。恢复必须同时验证：

- RootCapsule 和高熵恢复秘密；
- 内容寻址对象完整；
- VDNS 当前状态与版本；
- 根身份一致；
- RouteMap 和凭据对象引用可达。

缺少任何一项时失败关闭，不得只凭主密码和云端对象重建根秘密。

## 6. 冲突人工处理

并发更新产生两个合法分支时：

1. 两个候选均保留并标记 `CONFLICTED`；
2. 展示设备主体、最终序号、网站确认等级和对象摘要；
3. 用户独立验证网站当前有效密码；
4. 显式选择保留分支；
5. 生成新的已签解析事件，而不是删除另一分支掩盖历史。

没有人工选择时不得使用“最后写入获胜”。

## 7. 备份与恢复演练

执行：

```bash
./scripts/drill-g7-recovery.sh
jq '.summary, .drills[] | {id, status, expectedOutcome}' \
  test-results/g7/recovery/recovery-drill.json
```

演练包含锁定、断网、重启、高熵恢复、设备丢失、冲突和网站结果不明。每项必须有独立日志，`summary.failed` 必须为 0。

每季度或以下文件变化后重跑：

- `go.mod`、密码策略或协议注册表；
- `migrations/*.sql`；
- `.github/workflows/*`；
- VDNS、日志、恢复或设备代际代码；
- 浏览器扩展 CSP 和 Native Messaging 边界。

## 8. 升级与回滚

升级前：

1. 保存无秘密的规范 baseline、依赖清单、SBOM 和测试证据；
2. 执行全量测试和恢复演练；
3. 确认数据库迁移仅追加、checksum 固定；
4. 记录可恢复的上一个构建版本。

回滚触发条件：

- 出现可达高危漏洞；
- 规范 baseline 漂移；
- 旧版本回滚或撤销绕过测试失败；
- 数据库迁移无法在备份副本恢复；
- 任何秘密进入日志、OpenAPI JSON 或公开叶。

协议或数据库已产生新版本对象后，不得只回滚二进制而忽略数据版本。应暂停写入、恢复兼容构建，并通过迁移 checksum、对象版本和 VDNS 当前状态共同确认。

## 9. 证据与事后复盘

每次故障保留：

- 无秘密的时间线；
- 输入数据集版本和 seed；
- 命令、退出码和原始日志；
- 受影响 AC/FR/NFR；
- 修复前后测试；
- 残余风险和是否需要更新威胁模型。

不保留主密码、恢复秘密、字段明文、DEK、完整 RootCapsule 或稳定账户关系。事件关闭后更新本手册的“最后验证”日期。
