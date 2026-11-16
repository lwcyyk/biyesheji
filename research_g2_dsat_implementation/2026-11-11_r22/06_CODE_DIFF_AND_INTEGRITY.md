# 五文件差异与历史完整性

执行日期按原始UTC记录及本地时间核对；目录名沿用研究者冻结的2026-11-11。过程：本对话内知情模型辅助工程实现、真实离线运行及源码复核；外部核验待取得。

本轮保护清单1199个唯一文件，其中5个获准修改单列，其余1194个保持。


允许修改的五文件原字节在sources/original；old/new SHA和实际diff见R22_CODE_DIFF.json、sources/CODE.diff。原fixture四文件保持，仅追加R22_SUPPLEMENTAL_CASES.json。services/storage/launcher和旧回归测试/runner、R20/R21资料及SOURCE_LOCK保持。

首轮54的8份源码快照保留；PIPE_CLOSE_FIX.diff单列实际修复。后续run以其各自RESULTS.code绑定真实版本，不能把旧版本见证直接改名为当前版本全量验收。

源码定位在sources/SOURCE_LOCATIONS.json。R22_FILE_LOCK当前源码须与最终所选结果逐一比较；是否完全一致在R22_ACTUAL_RESULTS.same_final_code_version表达。

秘密扫描覆盖公开报告、JSON、日志、code_snapshot和diff；专用test key和DB是受限测试资源。值不进入公开证据，key hash省略。历史失败和包装错误均保留。

哈希固定版本，不提供数学独立性。当前实现和复核均为知情模型辅助过程，外部独立审查待取得。
