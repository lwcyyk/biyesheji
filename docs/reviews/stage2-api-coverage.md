# Stage 2 `/api/v2`覆盖审计

合同：OpenAPI 2.1.0  
机器报告：`test-results/stage2/api-coverage.json`  
生成器：`scripts/generate_api_coverage.py`

## 结论

OpenAPI包含22个唯一operationId，handler清单逐项匹配。机器核对结果为13个`COMPLETE`、7个`PARTIAL`、2个`NOT_IMPLEMENTED`。因此“22项API全部实现一致”不再是`UNVERIFIED`泛化声明，准确结论是“22项均已核对，完成边界各不相同”。

| API | OpenAPI | Handler | 领域逻辑 | 测试 | 状态 |
|---|---:|---:|---:|---:|---|
| createVaultSession | 是 | 是 | 是 | 是 | COMPLETE |
| deleteVaultSession | 是 | 是 | 是 | 是 | COMPLETE |
| createPasswordGeneration | 是 | 是 | 是 | 是 | COMPLETE |
| createCredentialRouteResolution | 是 | 是 | 是 | 是 | COMPLETE |
| listCredentials | 是 | 是 | 是 | 是 | COMPLETE |
| createCredential | 是 | 是 | 是 | 是 | COMPLETE |
| getCredential | 是 | 是 | 是 | 是 | COMPLETE |
| createAutofillAuthorization | 是 | 是 | 是 | 是 | COMPLETE |
| listCredentialVersions | 是 | 是 | 是 | 是 | COMPLETE |
| createCredentialVersion | 是 | 是 | 是 | 是 | COMPLETE |
| createSiteConfirmation | 是 | 是 | 是 | 是 | COMPLETE |
| createSyncPublication | 是 | 是 | 排队边界 | 是 | PARTIAL |
| createSyncPull | 是 | 是 | 排队边界 | 是 | PARTIAL |
| createDeviceEnrollment | 是 | 是 | 本地研究投影/排队 | 是 | PARTIAL |
| createDeviceRevocation | 是 | 是 | 本地研究投影/排队 | 是 | PARTIAL |
| createRecoverySession | 是 | 是 | 本地验证/排队 | 是 | PARTIAL |
| createVdnsResolution | 是 | 是 | 需注入完整Verifier | 是 | PARTIAL |
| createAuditEvent | 是 | 是 | 排队边界 | 是 | PARTIAL |
| createSecurityAnalysis | 是 | 是 | 是 | 是 | COMPLETE |
| createExposureAnalysis | 是 | 是（501） | 无 | 是 | NOT_IMPLEMENTED |
| createRemediationCampaign | 是 | 是（501） | 无 | 是 | NOT_IMPLEMENTED |
| getOperation | 是 | 是 | 是 | 是 | COMPLETE |

## 合同规则

- OpenAPI版本和合同测试统一为2.1.0；
- 状态写端点要求`Idempotency-Key`，只读型POST解析与VDNS解析按冻结合同例外；
- 版本候选、自动填充和网站确认携带`expectedVersion`，候选写还绑定`previousDescriptorHash`；
- 列表使用认证cursor并限制limit；
- 普通JSON不出现主密码、网站密码、RecoverySecret或根秘密；
- 未配置完整L1～L5 Verifier时`/vdns-resolutions`返回501，不返回合成成功；
- exposure/remediation关闭时返回稳定`OPTIONAL_FEATURE_UNAVAILABLE`；
- 7个PARTIAL端点返回的202/201只表示本地研究状态或排队，不表示生产同步、全局最终性或外部操作完成。

## 工具说明

仓库合同测试会解析所有`$ref`、路径参数、统一错误、分页和secret handle。外部通用linter未解析parameter `$ref`时会把引用参数误报为“缺少name”，该工具输出不作为本项目合同失败依据；本报告使用仓库内可解析引用的合同测试与机器覆盖清单。
