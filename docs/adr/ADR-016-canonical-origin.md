# ADR-016：CanonicalOrigin 规则

- 状态：Accepted
- 日期：2026-07-31
- 追踪：FR-010、FR-012、FR-016；AC-002、AC-015

## 背景

Origin规范化直接决定密码是否可被某页面请求。既有实现覆盖scheme、IDN、端口和iframe基本检查，规范没有完整冻结子域、顶层页面和重定向语义。

## 决策

`CanonicalOrigin`只包含：

```text
lowercase(scheme) + "://" + canonical-host + optional-non-default-port
```

规则如下：

1. `scheme`只接受`https`；开发模式可显式允许loopback `http`，远程HTTP拒绝。
2. hostname先去除DNS大小写差异，再按IDNA转换为小写ASCII Punycode；无效IDN、尾随混淆、空主机和用户信息拒绝。
3. IPv4按标准十进制形式，IPv6按规范压缩并使用方括号。
4. `https:443`和`http:80`省略；其他端口保留并参与绑定。
5. path、query、fragment不属于Origin；输入若作为Origin参数携带这些部分则拒绝，不能静默截断。
6. 子域名精确隔离。`login.example.com`与`example.com`是不同Origin；首版不启用eTLD+1自动共享。
7. iframe默认禁止。只有策略显式允许、目标frame与top-frame均可信且二者CanonicalOrigin完全相同时才可填充。
8. 路由和授权绑定top-level Origin。页面脚本自报的Origin或CredentialID仅作为提示。
9. 每次重定向后重新计算最终top-level Origin并重新执行RouteMap、VDNS和OriginBinding检查。重定向前授权/secret handle不得跨Origin复用。
10. HTTP到HTTPS、HTTPS到HTTP、跨子域和跨端口重定向均视为Origin变化。HTTPS到HTTP永不自动携带秘密。

OriginBinding仍绑定`CanonicalOrigin + AccountID`。一个Origin的多账号由本地账号选择完成，账号标识不得进入公开日志。

## 后果

- 当前实现大部分规则已有测试，重定向重新授权需要第二阶段补充。
- 公共后缀共享、通配符和站点组授权若未来需要，必须新增ADR。

