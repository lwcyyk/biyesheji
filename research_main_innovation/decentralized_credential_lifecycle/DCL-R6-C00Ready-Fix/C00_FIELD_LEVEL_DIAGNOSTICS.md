# 逐字段诊断结构、来源与失败发布

Material Passport：C00Ready-static-1/r2；host有限静态修复；2026-11-11；新增WSL/服务/目标测试0。

[service_readiness.py:145 collect_native](<../../../DCL-R6-isolated-verification/cr01/src/service_readiness.py>)只调用真实systemd、/proc、cgroup与当前boot/授权接口，生产路径没有fixture backend或从JSON读取observed入口。原生origin=NATIVE_OS/1，合成记录另为SIMULATION_ONLY/1且不能mintlease。

顶层字段包含batch/boot、service_unit、case、process_pid/starttime、样本序号、开始/完成BOOTTIME、check_phase、checks[8]、aux_checks、first_failed_check/all_failed_checks、raw_error、overall_result。每项包括expected、双侧observed、来源、read_time、process_identity、state_phase、status_version、read_success、MATCH/MISMATCH/NOT_READY/READ_ERROR及原始错误。

systemd argv/exit/原始双流hex、前后完整属性；/proc status/limits/cgroup原文与采样时间；parent kernel值/device/inode均保存。分项结果独立计算，不靠OR短路。转化/读取中断保留partial_raw；未读字段用null与错误说明，绝不填期望值。STARTING的凭据字段为明确deferred的NOT_READY，不声称已观察正确或错误。

每个采样在进一步判断/等待/放票据前写入Root私有`ready_C00_####.json`或C10对应文件。写入失败输出必要错误并fail-closed；不会以日志失败作为继续理由。稳定READY再完整重采样，发布Root:989/0640的C00_READINESS/C10_READINESS；Root原始行置于既有0700私有目录。无sealed nonce复制到诊断。

辅助门使用独立CR-A-*编号，明确区分原8项；PID/version/boot/stop/deadline及parent/proc错误不再混入未知总拒绝。状态转变/退出后最后合法快照保留其时刻，不用服务退出后的默认配置补现场。
