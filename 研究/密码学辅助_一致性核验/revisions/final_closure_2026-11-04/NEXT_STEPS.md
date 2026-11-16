# 外部输入触发的维护事项

本线已进入MAINTENANCE。以下事项仅在对应外部输入到达时处理。

| 外部输入 | 响应范围 | 关联归档文件 |
|---|---|---|
| 审稿人对核分类、交比计数或压缩等价性提出具体疑问 | 核对指定计数、证明和证书，必要时修正文稿或降低结论等级 | MODEL_REDUCTION、INSTANCE_EXACT、CLOSED_FORM_PROOF |
| 审稿人提供覆盖r5或五列四维闭式的原始文献 | 逐命题映射，更新优先权并明确归属 | FINAL_VERDICT、SUICIDE_REVIEW_UPDATE |
| PI取得Yamamoto日文原版或英文翻译正文 | 核对定义、参数、份额规模和强ramp条件，再更新引用等级 | PI_HANDOFF、CLASSICS_LINKED |
| 主线提出具体诊断接口或数据契约需求 | 核对来源、作用域、批准、预算、允许泄漏与强基线，按需要给出适用性意见 | CONTRIBUTION_MAPPING、CRYPTO_CHAPTER_DRAFT |
| 外部提交可复现的求解或验算失败 | 重放指定命令，比较源码哈希和输入，记录修复与影响范围 | DUAL_CERTIFICATES、verify_dual.py、VERIFICATION_RESULTS |

实例求解、独立验算及符号核对的命令已经列于INSTANCE_EXACT。主文献和来源获取记录保存在CLASSICS_LINKED及HTTP_REQUESTS.jsonl。

一般n与一般维数、最优分布唯一性、联合熵预算、实际采样成本和部署问题维持归档未决状态。维护工作由上述外部事件触发。
