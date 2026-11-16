# 54项结果与实际费用

执行与审查日期：2026-11-12（Asia/Shanghai）。证据类型：本对话内知情模型辅助实际离线运行、源码/日志核对；外部独立核验待取得。

**TOTAL=54；PASS54 / FAIL0 / ERROR0 / SKIP0 / BLOCKED0 / NOT_RUN0。** 解释器退出0、runner.passed=true、8条worker额外完整性检查全部通过。业务REPLAY、UNKNOWN或RECOVERY_REQUIRED仍按原测试预期判断，没有改动断言。

调用数1、自动重跑0、剩余0。主源码计量38.4438399s，unittest计量36.727s；外层从02:51:40.9079378Z到02:52:19.8846827Z。三者测量边界不同。

| 测试ID | 实际结果 | case耗时ms |
|---|---|---:|
| X01 | PASS | 2658.966 |
| X02 | PASS | 1303.432 |
| F01 | PASS | 8.287 |
| F02 | PASS | 8.263 |
| F03 | PASS | 10.439 |
| F04 | PASS | 6.754 |
| F05 | PASS | 62.003 |
| F06 | PASS | 307.513 |
| F07 | PASS | 307.715 |
| F08 | PASS | 320.389 |
| F09 | PASS | 336.547 |
| F10 | PASS | 326.107 |
| F11 | PASS | 331.724 |
| F12 | PASS | 294.732 |
| F13 | PASS | 879.467 |
| F14 | PASS | 641.536 |
| F15 | PASS | 571.563 |
| F16 | PASS | 690.079 |
| F17 | PASS | 712.327 |
| F18 | PASS | 741.851 |
| F19 | PASS | 1746.917 |
| F20 | PASS | 876.859 |
| F21 | PASS | 872.760 |
| F22 | PASS | 917.192 |
| F23 | PASS | 23.697 |
| F24 | PASS | 1416.249 |
| F25 | PASS | 85.570 |
| F26 | PASS | 980.634 |
| F27 | PASS | 936.911 |
| F28 | PASS | 1242.493 |
| T29 | PASS | 8.354 |
| T30 | PASS | 1.199 |
| T31 | PASS | 1010.989 |
| T32 | PASS | 16.547 |
| T33 | PASS | 29.429 |
| T34 | PASS | 82.714 |
| T35 | PASS | 1038.758 |
| T36 | PASS | 1425.578 |
| T37 | PASS | 1.317 |
| T38 | PASS | 1041.907 |
| T39 | PASS | 383.184 |
| T40 | PASS | 2753.421 |
| T41 | PASS | 1550.369 |
| T42 | PASS | 936.386 |
| T43 | PASS | 956.055 |
| T44 | PASS | 9.369 |
| T45 | PASS | 625.609 |
| T46 | PASS | 1472.884 |
| T47 | PASS | 1323.406 |
| T48 | PASS | 7.930 |
| T49 | PASS | 807.672 |
| T50 | PASS | 31.999 |
| T51 | PASS | 1.534 |
| T52 | PASS | 1590.096 |

## 冻结资源对照

| 资源/计量 | 本轮实际 | 上限 | 判定 |
|---|---:|---:|---|
| suite_runs | 1 | 1 | 满足 |
| owned_children | 8 | 8 | 满足 |
| concurrent_children | 2 | 2 | 满足 |
| max_child_observation_seconds | 1.844 | 10 | 满足 |
| sum_child_observation_seconds | 7.611 | 60 | 满足 |
| file_SQLite_connections | 12 | 104 | 满足 |
| per_case_connections | 2 | 2 | 满足 |
| state_test_keys | 2 | 2 | 满足 |
| TLS_test_materials | 1 | 2 | 满足 |
| SSLContext_loads | 2 | 2 | 满足 |
| all_output_directories_including_root | 59 | 64 | 满足 |
| all_output_file_paths | 382 | 512 | 满足 |
| all_output_logical_bytes | 1013728 | 67108864 | 满足 |
| python_threads_peak | 2 | 4 | 满足 |
| observed_additional_threads_plus_watchdog | 1 | 16 | 满足 |
| source_scope_lock_acquisitions | 64 | 128 | 满足 |
| suite_elapsed_seconds | 38.44384 | 300 | 满足 |
| child_stdout_bytes_max | 66 | 4096 | 满足 |
| child_stderr_bytes_max | 0 | 4096 | 满足 |
| child_cleanup_bytes_max | 4024 | 2097152 | 满足 |
| memory_SQLite_connections | 0 | 16 | 满足 |
| source_closure_files | 42 | 64 | 满足 |

主进程峰值working set **55,656,448B（约53.08MiB）**；子进程RAM峰值、原生OS线程峰值、VFS/物理磁盘峰值未测。SQL execute调用90，其中返回88、预期失败2，另有rollback调用1；包括1次被authorizer拒绝的ATTACH故障验证。没有把拒绝调用当作零费用。原申请未单列聚合SQL/RAM字节上限，本轮记录实测并核对既有逐操作/冻结测试范围。

文件SQLite计数12，各case最多2；具体连接及SQL ledger在原RESULTS.details保留。后处理没有连接任何数据库。新鲜state测试key2、TLS材料1、SSLContext加载2；测试公开AES向量复用与新生成秘密key分别管理。

## 清理与计量边界

8个worker均有CREATED和EXITED，精确身份对应；并发峰值2，窗口总7.611s、最大1.844s；该窗口为亲本创建至回收观察，包含子进程真实生命，未声称精确内核退出FILETIME。scope累计7607ms是逐项取整后的原计数，保留差异。所有pipe/process handle关闭，强制终止0、主/清理错误0；原预期故障进程按73/74退出。

原始`unique_created_paths`最终为1：T52新scope的局部created_paths覆盖共享计数字段；T51前值344。本轮未修改该计量代码，改用完整文件目录清点 **382文件、59目录（含输出根）、1,013,728B逻辑内容** 判预算。目录数包含run和snapshot，属于保守计数。最终清点覆盖RESULTS、FAULT_COVERAGE、索引和外层日志。

thread计数器记录后续创建0、Python峰值2；计数挂钩前的1个watchdog Timer另列，仍在冻结额度内。原生库线程数不由该计数器推出。

原失败new54与本轮两次合计worker16/16、文件SQLite24/208、state key4/4、TLS材料2/4、SSLContext4/4、目录117/128、文件752/1024、逻辑字节1,929,696/134,217,728、窗口总31.189/120秒。历史失败轮败者17.953秒仍为推迟回收观察窗口，其内核寿命未独立测量的缺项保持。

临时合成DB/key/TLS和证据按原合同保留于私有run目录，关闭句柄与保留文件分别登记；自动清理删除0。SQLite内部VFS/checkpoint/write-amplification仍NOT_MEASURED。
