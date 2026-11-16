# PSCD复现与证据入口

所有命令在PowerShell中执行，WSL发行版为Ubuntu-24.04。Python命令使用-B以避免向历史依赖写入字节码。源码与现存原始结果属于本修订目录。分离门为NOT_PASSED，下列命令用于现存原型核验。

## 1. 设置当前修订路径

```powershell
$pscdRoot = '/mnt/d/毕业设计/研究/密码学辅助_一致性核验/revisions/pscd_protocol_2026-11-04'
```

依赖版本和哈希记录在validation/ENVIRONMENT.json。底座沿用已存在的MP-SPDZ0.4.4、MASCOT二方二进制及其Compiler。AES公共模型、实际运行fixtures和全部随机材料已经留档。该目录是包含合成秘密输入的特权实验资料集，公开验证者接口的作用域见PROTOCOL_SPEC。

## 2. 公共模型与单元核验

```powershell
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/check_models.py"
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/test_protocol.py"
```

本次结果为5个模型检查通过、34项单元测试通过。以上两个入口会刷新各自在当前修订目录内的汇总文件。收尾时的结果另存validation/MODELS_FINAL.json和UNIT_RESULTS_FINAL.json。独立证书检查器调用历史verify_dual的独立计数接口，求解器引用只存在于公开模型生成过程。

## 3. 从原始尝试重新汇总主结果

```powershell
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/collect_results.py" --directory evaluation_final
```

预期输出为planned_cells=135、statuses.PASS=135、attempts_recorded=136、all_terminal=true。该命令读取逐次result.json，刷新RESULTS.json、MEASUREMENTS.csv和RECOVERED_ATTEMPTS.jsonl。失败尝试保存在P1_n256_private_zero_rep1/attempt01，成功重试位于attempt02。

## 4. 独立接收方解码

```powershell
$pscdRun = "$pscdRoot/evaluation_final/runs/P0_n8_pscd_rep1/attempt01"
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/receive_private.py" decode "$pscdRun/recipient_package"
```

解码入口读取三项交付文件，输出获准支持和幅值。接收材料export入口只供特权实验管理者使用。decode逻辑取得的三个字典对象分别为公开回复、私密恢复材料及公开模型，计算结果之后才与oracle比较。本次验证详见validation/RECIPIENT_RESULTS.json。

## 5. 新鲜随机复测

单元复测应使用尚未存在的本修订子目录。以下为已有协议入口的复测命令。

```powershell
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/run_protocol.py" --out reproduction/p0_n8 --profile P0 --n 8 --method pscd --repeat 1 --timeout 600
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/run_protocol.py" --out reproduction/p1_dense --profile P1 --n 8 --method pscd --case dense --timeout 600
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/run_protocol.py" --out reproduction/t2_r3 --profile P1 --n 5 --variant t2_r3 --method pscd --case boundary --timeout 600
```

预期依次为PASS、EXPECTED_REJECT、PASS，privileged result.json保存内部判定。CLI只输出公开接口。P0的公开接口保留隐藏状态，内部PASS状态和支持留在实验审计文件。

完整新鲜主矩阵可用已有sweep入口执行，输出目录需与历史测量分开。

```powershell
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/sweep.py" --out reproduction_main --workers 4 --timeout 600
wsl -d Ubuntu-24.04 -- python3 -B "$pscdRoot/collect_results.py" --directory reproduction_main
```

本次最终补充验证使用既有supplemental/PLAN.json中的20格，逐格调用已有run_cell(cell, 新目录, 600)，输出到supplemental_final。计划、实际命令、字节码、两方日志、私密输入及结果均保存。固定材料适合功能回放，隐私评价使用分布论证和新鲜随机材料的正常运行。

## 6. 版本和证据目录

- evaluation保存初版135格及进度报告器失败，evaluation/source_snapshot为相应源码。
- evaluation_final保存最终135格、136次尝试及完整汇总，source_snapshot保存重跑时源码。端口修复后的runner与最终报告快照见FINAL_SOURCE_SNAPSHOT。
- supplemental保留旧20格，supplemental_final保留最终20格。
- validation保留最终单元、模型、矩阵一致性、接收接口和历史哈希检查。
- dev保留编译失败及后续smoke。
- public保留五个公开模型、精确分数及T2原始/对偶证书。
- FINAL_SOURCE_SNAPSHOT冻结本轮源码、规格、报告和模型。MANIFEST.json登记适用范围内文件SHA-256及排除项。

MPC输入、SSL材料和oracle均为实验资料。真实服务身份、批准和安全传输的验收有独立前置条件。源代码功能复现、一般证明、首次性和部署安全分别验收。
