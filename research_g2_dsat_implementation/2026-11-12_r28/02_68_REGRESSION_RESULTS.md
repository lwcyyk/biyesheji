# 68项逐项结果与入口错误

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助实际离线调用与只读证据审查；独立外部核验待取得。本轮源码、Runner、测试及fixture修改均为0。

| TOTAL | PASS | FAIL | ERROR | SKIP | BLOCKED | NOT_RUN |
|---:|---:|---:|---:|---:|---:|---:|
| 68 | 0 | 0 | 0 | 0 | 0 | 68 |

另列 **harness装配错误1**：Refusal: READ_SCOPE_REFUSED。native退出1，runner.passed=false。错误发生在load_group编译A1模块后，该模块第19行导入auth_lifecycle核心包期间，尚未创建或执行任何TestCase。逐项ERROR=0不能解释为入口成功；全部68为真实NOT_RUN，避免把装配异常登记成某个原用例失败。

| 分组 | 计划数 | 实际用例执行 | PASS | NOT_RUN |
|---|---:|---:|---:|---:|
| A1 | 20 | 0 | 0 | 20 |
| H1 | 24 | 0 | 0 | 24 |
| D1-A | 24 | 0 | 0 | 24 |

| ID | 组 | 实际状态 | executed |
|---|---|---|---|
| D01 | D1A | NOT_RUN | false |
| D02 | D1A | NOT_RUN | false |
| D03 | D1A | NOT_RUN | false |
| D04 | D1A | NOT_RUN | false |
| D05 | D1A | NOT_RUN | false |
| D06 | D1A | NOT_RUN | false |
| D07 | D1A | NOT_RUN | false |
| D08 | D1A | NOT_RUN | false |
| D09 | D1A | NOT_RUN | false |
| D10 | D1A | NOT_RUN | false |
| D11 | D1A | NOT_RUN | false |
| D12 | D1A | NOT_RUN | false |
| D13 | D1A | NOT_RUN | false |
| D14 | D1A | NOT_RUN | false |
| D15 | D1A | NOT_RUN | false |
| D16 | D1A | NOT_RUN | false |
| D17 | D1A | NOT_RUN | false |
| D18 | D1A | NOT_RUN | false |
| D19 | D1A | NOT_RUN | false |
| D20 | D1A | NOT_RUN | false |
| D21 | D1A | NOT_RUN | false |
| D22 | D1A | NOT_RUN | false |
| D23 | D1A | NOT_RUN | false |
| D24 | D1A | NOT_RUN | false |
| A01 | A1 | NOT_RUN | false |
| A02 | A1 | NOT_RUN | false |
| A03 | A1 | NOT_RUN | false |
| A04 | A1 | NOT_RUN | false |
| A05 | A1 | NOT_RUN | false |
| A06 | A1 | NOT_RUN | false |
| A07 | A1 | NOT_RUN | false |
| A08 | A1 | NOT_RUN | false |
| A09 | A1 | NOT_RUN | false |
| A10 | A1 | NOT_RUN | false |
| A11 | A1 | NOT_RUN | false |
| A12 | A1 | NOT_RUN | false |
| A13 | A1 | NOT_RUN | false |
| A14 | A1 | NOT_RUN | false |
| A15 | A1 | NOT_RUN | false |
| A16 | A1 | NOT_RUN | false |
| A17 | A1 | NOT_RUN | false |
| A18 | A1 | NOT_RUN | false |
| A19 | A1 | NOT_RUN | false |
| A20 | A1 | NOT_RUN | false |
| H01 | H1 | NOT_RUN | false |
| H02 | H1 | NOT_RUN | false |
| H03 | H1 | NOT_RUN | false |
| H04 | H1 | NOT_RUN | false |
| H05 | H1 | NOT_RUN | false |
| H06 | H1 | NOT_RUN | false |
| H07 | H1 | NOT_RUN | false |
| H08 | H1 | NOT_RUN | false |
| H09 | H1 | NOT_RUN | false |
| H10 | H1 | NOT_RUN | false |
| H11 | H1 | NOT_RUN | false |
| H12 | H1 | NOT_RUN | false |
| H13 | H1 | NOT_RUN | false |
| H14 | H1 | NOT_RUN | false |
| H15 | H1 | NOT_RUN | false |
| H16 | H1 | NOT_RUN | false |
| H17 | H1 | NOT_RUN | false |
| H18 | H1 | NOT_RUN | false |
| H19 | H1 | NOT_RUN | false |
| H20 | H1 | NOT_RUN | false |
| H21 | H1 | NOT_RUN | false |
| H22 | H1 | NOT_RUN | false |
| H23 | H1 | NOT_RUN | false |
| H24 | H1 | NOT_RUN | false |

每项原callable、expected、源hash和状态在R28_68_TEST_RESULTS保留。unit stdout文件0B，RESULTS.executed_order为空，MODULE_ORIGINS仅记录部分A1模块和stdlib；这些数据与原堆栈共同支持“用例尚未开始”。

## 最小原因

原冻结堆栈在CPython frozen importlib._bootstrap_external.get_code第1091行进入get_data；同版本配套源该行是`self.get_data(bytecode_path)`，随后只有OSError会被作为缓存不可读而转读源码。当前Runner的READ_SCOPE_REFUSED继承RuntimeError，因而直接中止导入。

R27静态审查漏查标准导入器仍尝试读取.pyc。-B关闭缓存写入，保留缓存读取/探测；源码白名单没有涵盖该探测，导致框架装配失败。R27的历史静态结果和源码锁保持，当前缺陷另外登记。

具体被拒绝绝对路径未在原audit中输出。本轮按首个包加载、未观察到auth_lifecycle包代码exec及标准缓存规则，重建候选为src/auth_lifecycle/__pycache__/__init__.cpython-312.pyc；只读目录核对见该文件270B。该路径属于控制流重建，不能冒充原运行日志直接记录。其内容本轮没有为分析而读取或执行。

详细堆栈及版本/位置在sources/FAILURE_CAUSE_ANALYSIS.json和CPYTHON_IMPORT_CACHE_REFERENCE.txt。后续分析只读文件/JSON/元数据，没有重复import探测或任何测试。
