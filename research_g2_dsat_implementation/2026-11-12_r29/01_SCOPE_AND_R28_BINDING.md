# R29范围与R28绑定

日期：2026-11-12（Asia/Shanghai）。过程：本对话内知情模型辅助单文件修复、AST/源码/元数据/哈希审查。本轮Runner与测试模块未导入，--help和所有测试未执行，SQL/key/测试进程资源0；外部独立核验待取得。

## 唯一代码变更

获准文件：`D:\毕业设计\auth-lifecycle\scripts\run_dsat_current_build_regressions.py`。实施前核对a9版本与R27/R28完全相同，并把原字节保存于`D:\毕业设计\research_g2_dsat_implementation\2026-11-12_r29\sources\original\run_dsat_current_build_regressions.py.txt`。

- 修改前SHA：`a9cb35bcce7d1439f45b2593a16c7fb2884117dd63d515eac7cf40e5d75eda70`。
- 修改后SHA：`27c29f6e8b346799b9ac0492d2e7377326113dbe3a44c53dd33207fec8dd9514`。
- 当前774行，AST解析通过。

只修改该Runner，新增工程代码文件0；原42工程源码、3测试、10fixture、生产读取白名单和所有旧Runner保持。差异全文及定义位置见R29_CODE_DIFF和sources/R29_PATCH.diff。

## 保持的真实事实

R28一次直接调用、native退出1、用例执行0、68NOT_RUN及原11个输出文件保持，剩余额度0。原A17与D24没有被实际执行，静态状态不提升为动态验证。

R25相关42源与24runtime保持，54实际PASS继续有效。当前工程摘要仍为`621f69552f8fcb20aa0db142c5d3b7783e5bd9a641a03559a25b1247099cffb9`。本轮修复不自动关闭D1B1合同，也不重用R28运行许可。

## 旧材料保护

重新核验原2120份历史保护文件，并核对本轮新增的修改前源码快照。R27/R28 SOURCE_LOCK与原始RESULTS/日志等保持原字节。历史清单排除唯一获准修改的当前Runner本体，其a9原字节在新快照单独保留。

4份历史T33链接继续只读hash核验，未改属性、内容或身份；既有例外范围保持。原私有合成DB/key仍按元数据范围处理，不输出秘密摘要。

本轮仅建立R29报告/锁目录，未来verification_runs、run目录、receipt、投影副本和RESULTS均未创建。
