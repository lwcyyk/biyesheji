# ADR-014：网站确认证据等级

- 状态：Accepted
- 日期：2026-07-31
- 追踪：FR-017、FR-023～026；AC-005、AC-014

## 背景

浏览器填充、表单提交和页面提示只能说明本地观察到某个动作。它们不能证明网站已经保存新密码。旧枚举把`LOGIN_INFERRED`、用户确认和站点确认混合，容易把页面启发式结果写成真实证明。

## 决策

证据等级冻结为：

| 编码 | 名称 | 语义 | 默认状态 | 能否激活 |
|---:|---|---|---|---|
| E0 | `AUTOFILL_OBSERVED` | 扩展执行过填充 | `UNKNOWN` | 否 |
| E1 | `SUBMIT_OBSERVED` | 观察到表单提交 | `UNKNOWN` | 否 |
| E2 | `PAGE_SUCCESS_INDICATED` | 页面文本、导航或DOM显示成功 | `REVIEW_REQUIRED` | 否 |
| E3 | `NEW_PASSWORD_RELOGIN_CONFIRMED` | 独立新会话用新密码重新登录成功 | `REVIEW_REQUIRED`或策略激活 | 条件允许 |
| E4 | `SITE_SIGNED_RECEIPT` | 受信站点/connector签署绑定变更的回执 | 可激活 | 是 |
| E5 | `USER_SIGNED_CONFIRMATION` | 用户对具体凭据、版本和结果显式签名确认 | 可激活，但只表示用户声明 | 是 |

E3只有同时满足以下条件才可由L5策略激活：新会话、精确CanonicalOrigin、候选版本绑定、凭据未在页面脚本中暴露、无跨Origin重定向、重登录成功证据新鲜；实现还应尽可能验证旧密码不再可用。缺任一条件进入`REVIEW_REQUIRED`。

E4回执必须绑定Namespace承诺、Credential承诺、旧/新版本、nonce、结果、签发者、有效期和签名。签发者必须在站点信任注册表内。Mock Site签名只能标记`MOCK_SITE_E4`，不能外推为真实网站。

E5必须由具有确认能力的用户设备签署，明确显示站点、账号提示、候选版本和“这是用户确认，不是网站证明”。E5可以驱动产品状态，但论文不得称为站点密码学证明。

旧数值1～5不能原地解释为新E0～E5。代码、数据库、OpenAPI和事件编码需要显式版本迁移。

## 后果

- 页面成功提示永远不能单独激活新版本。
- 现有代码仍使用旧枚举，因此在第二阶段迁移前只可按legacy研究实现描述。
- UNKNOWN不能直接进入ACTIVE，必须附加满足策略的新证据。

