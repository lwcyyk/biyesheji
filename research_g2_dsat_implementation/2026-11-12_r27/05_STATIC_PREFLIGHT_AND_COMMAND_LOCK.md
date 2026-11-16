# 静态预检与真实命令锁

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

**34项静态检查通过；command_executable=true。execution_authorized=false、executed=false、actual_suite_runs=0。** 这里的命令可执行性仅表示入口实际存在、参数及静态合同完整。

检查覆盖单文件范围、42源/24runtime/3test/10fixture、原68、顶层import与main guard、懒加载及缓存策略、两个D24源与静态字节代入、上下文恢复、文件/SQL/线程/时限、无进程网络调用、准确参数、控制锁和历史路径。初次检查发现4个合法T33硬链接，修订后仅保留其只读核验例外；历史原文保持，来源记录保留。

准确argv：

```text
["C:\\Users\\a1887\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe", "-I", "-B", "-X", "utf8", "D:\\毕业设计\\auth-lifecycle\\scripts\\run_dsat_current_build_regressions.py", "--suite", "regression68", "--output-root", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r26\\verification_runs", "--approval-ref", "D:\\毕业设计\\research_g2_dsat_implementation\\2026-11-12_r26\\verification_runs\\RUN_APPROVAL_RECEIPT.json"]
```

PowerShell复制形式（本轮未执行）：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py' --suite regression68 --output-root 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs' --approval-ref 'D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r26\verification_runs\RUN_APPROVAL_RECEIPT.json'
```

工作目录必须为`D:\毕业设计\auth-lifecycle`。-I屏蔽用户site与Python环境注入，-B关闭bytecode写入，-X utf8固定默认文本解码；解释器和关键依赖仍为R25原二进制/版本。测试原文件及合法辅助CLI的当前project/src插入有来源校验。

## 后续授权准备

未来研究者明确批准后，受信准备步骤创建冻结验证根并放入唯一的实际receipt；其内容参考sources/RUN_APPROVAL_RECEIPT.template.json，绑定最终命令锁和资源锁SHA、构建摘要、真实回复摘要、max_suite_runs=1、automatic_reruns=0及全部真实权限false。

当前只有approved=false模板，实际receipt不存在。模板中未来回复字段占位不属于命令argv；argv各项均为真实确定值。准备后目录若已有其他文件/run/槽位就停止，不覆盖日志，不更换root/run ID或自动重试。

动态执行后才可能取得68项结果。任何source/依赖/fixture/投影/预算/cleanup变化或FAIL/ERROR/SKIP/部分完成均保留证据并停止，剩余身份按NOT_RUN保持68分母。R25的54项额度0不参与此新许可。
