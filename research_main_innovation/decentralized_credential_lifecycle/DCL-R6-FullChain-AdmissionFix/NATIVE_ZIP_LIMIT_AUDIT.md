# Native ZIP上限及相关检查器

Material Passport：DCL-R6-FullChain-AdmissionFix；FullChainAdmission-static-1/review-1；2026-11-13；HOST_STATIC_REVIEW_ONLY。


257来自terminal_contract.native_archive_members及terminal_evidence._native_artifact的len(names)>257分支。guard.seal逐件记录ROOT原件并增加out/EVIDENCE_MANIFEST.json，形成一件原件对应一ZIP成员的实际格式。重复/缺失/多余成员、原件摘要和总解压32MiB构成原证明责任。

相关依赖还包括startup_lifecycle.post_exit_export中的原生包审查、host行政finalizer、终态_reader5秒界、manifest4MiB、journal32MiB与32768字节行界。旧post-exit包审查只按declared逐件比hash，完整成员集合/类型检查责任主要位于终态_reader；新维护组件尚未接入，弱项未登记成已修复。

新增常规archive_check在ZipFile创建索引前读取固定EOCD并限制中央目录大小，随后拒绝目录穿越、反斜杠/drive路径、Unicode规范化冲突、重复manifest键/路径、重复成员、symlink/FIFO、加密/不支持方法、缺/多成员、字节/摘要/权限不匹配及部分归档。流式读取保持32MiB总界，无文件解压写入。archive_oracle使用独立代码重算这些义务。

该组件支持原native dict manifest与行政list manifest，原manifest字节逐件验证。真实TR-A2的234成员native与250成员行政包均通过新组件及独立oracle的主机只读复核。Zip/文件来源与Linux实际权限仍依赖原Root绑定/metadata守卫，当前原生行为未运行。

[旧格式兼容与最终组件检查](evidence/FINAL_COMPONENT_CHECKS.json) · [维护检查器](maintenance/archive_check.py) · [独立oracle](maintenance/archive_oracle.py)。

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。全部原生动态测试UNRUN。
