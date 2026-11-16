# 复现命令、数据与诊断

## 运行

PowerShell，工作目录`D:\毕业设计\research_main_innovation\ci01_policy_regression`：

```powershell
.\run_pair.ps1 -RunId pair_replay_new
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
$auditPython='C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $auditPython -B .\analyze_pair.py --run-id pair_replay_new --out PAIRED_REPLAY_NEW.json
```

RunId应为新名称。原始目录排他创建，历史输出保持。脚本显式设置本地Go1.26.10的GOROOT、隔离缓存/临时路径、GOPROXY/GOSUMDB=off。依赖已经取得；缺少缓存时需按公开资料获取范围补齐，并更新相应依赖记录。

实际测试命令为`go test -p=4 -tags=ci01audit -run '^TestCI01FullPermissionChain$' -count=1 -timeout=180s -json ./routers`，分别在baseline和fixed执行。测试仅通过进程内ServeHTTP进入真实框架；默认出站HTTP传输被阻断。新源代码或配置不能无记录地混入现有run目录。

## 证据层级和出口码

基准Go测试保留违例为观察结果，框架控制及运行完整性通过时退出0；`analyze_pair.py`对3项基准合同违反及修复版合同逐项判断。不能用基准Go退出0声称契约全部通过。最终配对分析34项工件/契约核对通过；60项未决仍未作通过判定。

`raw/baseline01`为修复门证据；`raw/fixed01`为首次修复验证。最终`raw/paired02_baseline`、`raw/paired02_fixed`含前置源码快照和后置会话存储读回。原两批的测试源码另存executed_chain_test.go；最终测试源码在每批source_snapshot下。

## 失败与环境修正

1. build01的Go依赖获取未继承Windows代理，下载停滞后中断。Python使用的既有系统代理随后只在依赖获取进程中传给Go；目标均为公开模块。
2. build02使用了新的go.exe，但继承GOROOT仍指向Go1.20，引起crypto/pbkdf2等标准包缺失。后续显式绑定匹配标准库，完整选定调用链成功构建。
3. `go list -m all`在离线模式下缺少未使用模块的元数据，原始失败保留。针对实际编译import闭包的模块清单成功，273个模块记录于raw/dependencies/compiled_modules.json；`go mod verify`返回all modules verified。
4. 初始diff采用Windows换行，Git apply检查失败；保留raw/initial_format_*，改为LF后检查通过。已测试Go源文件内容保持原样，补丁生成脚本同步使用LF。
5. 工具链备用下载在官方首份校验成功后中断，备用部分文件未安装或使用。BOOTSTRAP.json记录实际采用的官方校验结果。

以上是构建/工件诊断，未被填入认证服务失败或方法效果数据。

## 版本与哈希

DEPENDENCY_AND_TOOLCHAIN.json保存源码归档、官方Go归档/可执行文件、go.mod/go.sum、关键依赖与校验状态。原依赖文件与固定提交归档一致。OBSERVABILITY.diff和MINIMAL_PATCH.diff分别描述观测插桩及产品修复；PATCH_GATE.json与PATCH_HASHES.json绑定修复前证据和源码。

PAIRED_RESULTS.json区分层级未到达（null）、已通过、实际拒绝和合成效果；后置会话字段只保存存在性，不保存真实材料。SQL计数为目标请求窗口内观察，源查询和clear计数单列，异步审计I/O不用于性能优越性声明。

129项前阶段登记文件哈希核对一致。native服务、真实账户、生产配置、并发安全、浏览器与网络传输验证均未执行。当前测试工件和持久数据全部属于本审计目录中的合成资源，未向上游发送消息或发布披露。
