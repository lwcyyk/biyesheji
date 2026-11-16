# 检查点保全与失败收尾

逐项断言保全已经动态验证：68项结果和关键断言在来源失败后仍可读取。609条JSONL记录全部校验成功，journal为2,056,226字节。测试完成与最终合同完成有明确区分：TESTS_FINISHED为第553行，最终第609行为RECOVERY_REQUIRED。

原执行异常保存在第598行，POST_TEST_PROVENANCE异常在第604行。失败最终receipt的errors同时包含这两条异常和RESOURCE_AUDIT检查点、三个最终JSON的RESOURCE_OUTPUT_BYTES异常。错误类型、阶段、堆栈及错误码保留，未转成成功。

完整持久化验收继续为false：原运行路径中的RESULTS.json、MODULE_ORIGINS.json、RESOURCE_LEDGER.json三份文件均缺失。各自独立写入尝试确实执行，均在创建前由2MiB总字节守卫拒绝；RESOURCE_AUDIT检查点也被该守卫拒绝。

最终TEST_RUNS.json实际存在，status=FAILED、FULL_CONTRACT_ACCEPTED=false、RESULTS摘要=UNKNOWN、native_exit_required=1。它绑定的现存文件摘要及609事件链头全部匹配。本轮没有向旧路径补写成功JSON。

| journal中的主要内容 | 实际字节 |
|---|---:|
| PHASE_ASSERTIONS_FINISHED | 640738 |
| TESTS_FINISHED | 486619 |
| ORIGIN_CLASSIFIED | 374149 |
| ORIGIN_OBSERVED | 283485 |
| PROVENANCE_SNAPSHOT_FINISHED | 171040 |

阶段details/meter和TESTS_FINISHED重复内容占用较大空间，完整最终输出的容量预留仍有缺口。实际10个运行文件合计2,075,679字节，小于2,097,152上限；拒绝写入保护了物理上限，最终三件套仍未形成。

已触发的来源失败、字节额度拒绝和非零失败receipt路径得到实际证据。操作系统崩溃、半行写入、fsync/磁盘权限故障等本轮未发生，继续登记静态范围。所有恢复操作均为只读解析、校验和R32新审计稿生成；原运行文件保持。
