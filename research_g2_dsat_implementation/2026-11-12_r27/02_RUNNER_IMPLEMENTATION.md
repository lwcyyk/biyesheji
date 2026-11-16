# 单文件Runner实现

日期：2026-11-12（Asia/Shanghai）。过程：当前对话内知情模型辅助单文件测试基础设施实现与静态审查；本轮未导入或执行新Runner，未运行--help、测试、SQLite或测试子进程。外部独立复核待取得。

**R27_MINIMAL_RUNNER_IMPLEMENTED / R27_68_TEST_MANIFEST_VERIFIED。** 本轮只登记实现和静态条件，实际68项仍NOT_RUN。

## 受控执行流程

1. 严格解析suite/output-root/approval-ref，固定唯一regression68、R26根与run ID。
2. 只读独立批准receipt，核对最终命令锁、Runner SHA、构建摘要、资源锁、真实研究者回复hash、单次额度和全部真实操作关闭位。
3. 验证根只能预有这一份receipt；独占创建SUITE_INVOCATION_01及新run，旧结果或既有槽位拒绝。
4. 安装只读/写入/SQL/网络/进程/模块执行审计，核验当前源、依赖、测试和历史。
5. 按A1→H1→D1A逐组懒加载；按manifest中每组原顺序构造原TestCase实例。
6. 组间关闭自有memory连接、记录实际module来源；D24单独进入投影上下文。
7. 再次核验源和历史，恢复线程启动hook、D24上下文并关闭自有连接，统一保存结果/费用/来源/索引。

其中“一个suite”是一次直接Runner调用包含三组原身份；没有拆成三个外部调用，没有测试子进程，也没有额外54项。

## 测试身份与结果

R27_68_TEST_MANIFEST保存68个原ID/callable/expected/spec/源hash/fixture。原20A、24H、24D全部保留，执行顺序为原组内顺序。Runner只从固定原文件读取已校验字节，创建新且不存在的case模块alias，用compile执行该固定源；没有宽泛发现，没有历史bytecode替代，没有删缓存或生产模块stub。

unittest原setUp/body/tearDown实际执行条件保持；Results按原ID记录PASS/FAIL/ERROR/SKIP。failfast或框架异常后的剩余身份仍以NOT_RUN保留完整68分母；SKIP无法被当作全部成功。最终成功要求68PASS且其余0、无harness/cleanup/边界错误、memory连接已关闭。

## 生命周期与异常

只在合法执行参数和新批准后才创建State、运行槽、日志、timer或内存连接。导入时仅有标准库导入、纯常量、类/函数定义；标准库加载可能分配内存或加载其DLL，未发生项目测试、文件/服务初始化。

超时与异常保留原测试结果、脱敏traceback和后续cleanup信息，预算/源/投影失败均为非零或不完整运行。顶层收尾/存储故障会尝试在同一新run写EARLY_FAILURE；存储本身不可写或额度耗尽时，保留已有文件和内存错误并exit1，无历史fallback，不伪造完整结果。

上述是限定本机可信OS/文件系统/固定源输入的静态控制流结论。尚无运行记录证明这份新Runner已经通过68项或所有故障分支。
