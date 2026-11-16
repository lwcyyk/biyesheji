# 只读复核与本轮文件

## 运行校验

在PowerShell中设置以下变量并执行：

    $r = 'D:\毕业设计\mainline_research_closure_v1'
    $py = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    & $py -B -X utf8 "$r\verify_evidence.py" --out "$r\audit_REPLAY_NEW_ID" --claims "$r\CLAIMS.json"

输出须位于本closure目录内，建议新目录。读取历史工件、源码归档和密文，SQLite只打开输出目录中的复制品；无NativeHTTP对象构造，无原生HTTP。缺失或无法解密将显式登记。公开规范化视图不含原文秘密。

已有结果为audit01、audit02、audit_final、audit_final_v2及audit_final_v3。最终采用audit_final_v3/VALIDATION_RESULT.json和NORMALIZED_EVIDENCE.json；早期错误读形状的结果保留。CLAIMS为27项机器登记，字段与条件由build_claims.py创建，该程序只改本closure生成文件。

## 当前代码与回归

证据读取器位于auth-lifecycle/src/auth_lifecycle/online_state/evidence_semantics.py，没有网络或持久状态修改接口。生产者与四个评分消费者支持v2明确字段及已知legacy模式；单独无类型布尔保持歧义。

从auth-lifecycle运行unittest discover -s tests -v。将ONLINE_STATE_TEST_ROOT、NATIVE_TEST_ROOT、RECONCILIATION_TEST_ROOT、UNIDENTIFIED_TEST_ROOT、M5_TEST_ROOT、M6_TEST_ROOT、AUTH_L0_RESULT_DIR、TEMP、TMP设为新建的closure开发目录，PYTHONPATH指向src，避免写历史路径。当前最终回归157/157，FULL_REGRESSION_V2.log及SOURCE_LOCK记录实际版本。

## 交付结构

- EVIDENCE_SEMANTICS：状态、字段和单位映射。
- ALGORITHM_RUNTIME_MAP：实际调用图、版本消歧及缺口规格。
- CLAIMS及CLAIM_EVIDENCE_MATRIX：类别、量词、来源、分母、失效条件和论文措辞。
- THESIS_CORE_DRAFT、THESIS_UPDATE_MAP：新核心段落与旧稿组装位置。
- ADVERSARIAL_REVIEW、VERDICT：内部反方审查和阶段裁决。
- prechange、source_frozen、IMPLEMENTATION.patch：本轮修改前后代码与补丁。
- audit_final_v3：只读校验原始输出、副本及规范视图。

本轮不运行历史原生采样器或评分器的原位写入模式。历史预算账本的读取量和SHA由校验记录；原始结果、冻结源码和成本函数保持原状态。
