# 离线复现与结果解释

## 命令

PowerShell，工作目录`D:\毕业设计\research_main_innovation\ci01_policy_consistency_review`：

```powershell
.\run_offline.ps1 -RunId offline_new
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
$reviewPython='C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $reviewPython -B .\audit_offline.py --run offline_new --out TEST_RESULTS_NEW.json
```

使用未存在的RunId。运行器调用本机`C:\Program Files\Go\bin\go.exe`，先`go run ./tools/extract.go`，再`go test -json -count=1 ./routers`。GOPROXY/GOSUMDB=off，GOTOOLCHAIN=local，缓存和临时目录位于本审计目录。测试无外部模块、HTTP客户端调用、数据库或真实服务依赖。

**预期测试退出码为1。** 这是M081/B02/B04的现有契约不一致被断言捕获；当前版本保留三条失败。审核器独立核对输入/结果对应、Go失败名单、原样声明及历史哈希，审核成功返回0。60项SPEC_UNRESOLVED只作观测，不能按Go子测试的pass事件提升为产品契约通过。

## 实际运行

|目录|结果|解释|
|---|---|---|
|raw/offline01|编译失败，测试未运行|提取器的标准库导入头漏列errors；原函数体未变。stderr、初始提取器和生成片段已保留|
|raw/offline02|113个状态输出；50已知契约符合、3不一致、60未决；2个转换控制通过|正式离线核对输入；Go退出1|
|raw/offline_replay|同一输入和结果确定性重放|比较cases/results字节；时间戳、Go测试耗时另看原始JSONL|

未执行完整Casdoor仓库编译。冻结项目声明Go1.26.0/toolchain1.26.10，本机Go1.20可编译本次选定的语法子集；编译依赖使用mock。跨版本编译子集的一致性不等于完整产品运行环境一致性。[环境](ENVIRONMENT.json)

## 源码、输入和证据

- `SOURCE_EXTRACTS.json`：30项原样声明，包括函数、常量/变量；源文件摘要、原行号、提取字节摘要和目标偏移。
- `raw/offline02/source_hashes.json`及`source_snapshot_final/`：离线包、提取器、审核器、范围和运行脚本快照。
- `OFFLINE_CASES.json`：96格主矩阵与17个边界例，合成对象、预期及规范规则ID。
- `TEST_RESULTS.json`：完整实际决策、原因、已知契约不一致、未决状态及37项工件核对。
- `INPUT_HASHES.json`：30项历史输入；`SUPPLEMENTAL_INPUTS.json`：1项停用语义补充源码；本轮核对均保持一致。
- `HISTORICAL_C11_INDEX.json`：63条历史脱敏事件的只读索引；保持HISTORICAL标记，不计入本轮测试数据或新采样。
- `PUBLIC_*`：公开资料的URL、取得时间、状态及摘要。搜索/GitHub连接器传输失败；三项GitHub提交详情API返回403。官方文档和两项公开patch经允许的官方HTTPS资料入口取得，其他未取得细节继续未决。

允许/拒绝结果来自原生客户端门槛、原生主体读取与声明的下游mock。不存在显示名资源写入。`SessionData`过期使用合成期限1；活跃源token以当前时间前一分钟及3600秒期限构造，结果中只保存逻辑状态。数据来源缺失使用显式内存故障注入；实际可达性单独登记。

## 许可与审查边界

提取声明来自Casdoor的Apache-2.0源码，原始文件的许可头在`sources/frozen/`中保留，生成文件注明来源。当前辅助流程执行了一次反例与规范复核，没有外部审阅者独立确认。没有修改原生实现或原项目；没有新增防护算法。测试通过项、已知失败、未决和未运行项目分别保留。
