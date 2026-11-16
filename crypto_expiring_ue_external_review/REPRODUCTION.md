# 材料包复核

本轮仅新增外审草稿、来源快照及离线元数据工具。历史输入以 `INPUT_LOCK.json` 绑定；公开出版 PDF 另保留字节一致的核对副本 `sources\tcc_published_reference.pdf`。新幻灯片和原始 HTML/失败响应均保留实际类型。

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\毕业设计\crypto_expiring_ue_external_review\verify_package.py'
```

命令只读本地工件、输出 JSON，结果保存于 `VALIDATION_RESULT.json`。它核对文件哈希、P1–P7 的前后状态、288 词正文与其独立副本和审批用哈希、实际 PDF/HTML 类型，以及未发送状态。工件完整性通过不提升条件定理、正确性或具体构造安全性的结论等级。

`ARTIFACT_MANIFEST.json` 排除自身及校验结果以避免循环哈希。四份主交付为 `EXTERNAL_REVIEW_PACKAGE.md`、`SOURCE_AND_RESPONSE_REGISTER.json`、`PREMISE_UPDATE.json`、`DECISION.md`。可复制正文为 `INQUIRY_BODY.txt`；研究者审批时还需核对收件人及公式附件版本。

候选协议实现为 0，原生 AS/RP 请求为 0，外部消息为 0。文献检索的 7 次 curl 尝试与原生请求分别登记；其中 6 次取得 HTTP 响应，1 次默认 TLS 检查在 HTTP 前失败。
