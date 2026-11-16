# 离线复核与复现

本轮只新增研究报告、来源副本、公式图像和离线校验工具。`mathematical_audit.py` 计算树前沿集合、相同节点关系、前缀和有限域标量分布；`verify_artifacts.py` 只读核对工件/来源哈希及结果字段。两者均未实现候选加密协议，也未调用原生 AS/RP。

## 复现命令

在 PowerShell 中运行：

```powershell
$pythonExe = 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $pythonExe 'D:\毕业设计\crypto_expiring_ue_proof_r2\mathematical_audit.py'
& $pythonExe 'D:\毕业设计\crypto_expiring_ue_proof_r2\verify_artifacts.py'
```

这两个命令只向标准输出报告，不修改历史输入或既有结果。原始运行结果保存于 `MATHEMATICAL_CHECKS.json`、`VALIDATION_RESULT.json`。数学工具仅依赖 Python 标准库；本轮来源元数据提取另使用 pypdf，文本和图像使用已安装的 pdftotext/pdftoppm。

## 证据级别

- 手工数学证明：R2-LOCAL、正文相同引理、R2-EXP 的合法性和优势界。
- 有限复核：8 项组合/标量检查，结果属于具体小实例与公式复核。
- 文件完整性：`STARTING_POINT_LOCK.json` 的 12 个历史输入；`ARTIFACT_MANIFEST.json` 的新工件；来源登记引用的实际文件。校验数量以原始 JSON 分项计数。
- 来源对应关系：出版稿原图与提取文本相互核对；作者完整版、历史全文与勘误未核准。
- 外部安全证明复核、作者确认、证明助手与优先权审查：本轮尚未完成。

文件完整性通过只表明登记工件与冻结值对应，不能提升数学结论等级。有限计算通过同样不能替代自适应安全归约。

`ARTIFACT_MANIFEST.json` 排除自身和 `VALIDATION_RESULT.json` 以避免循环哈希；其余当前新增工件逐项登记。`render\gamma.png`、`gamma_crop.png` 为保留的取错页中间件，明确排除为 Γ 定义证据，正确页是 `gamma_correct.png`。ePrint HTML 响应只作为访问失败证据，未计入取得的全文。
