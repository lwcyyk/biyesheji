# 静态验证结果
Material Passport：BF-static-1 / STATIC_SYNTAX_PASS；SOURCE_REVIEW_CONDITIONAL；DYNAMIC_UNVERIFIED。

## 实际命令
完整预登记argv见evidence/COMMAND_PLAN.json，原始字节流与退出见evidence/commands/。使用已有/usr/bin/python3.12，Python3.12.3，SHA-256=e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。
- order01：只读sha进程已发起，输出捕获目录错误，退出未知；事件保留。
- order02、03：前置结果检查在启动前拒绝，执行次数0。
- order04、05：摘要/版本成功退出0。
- order06：八源码py_compile退出0，编译目标正文执行次数0。
- order07：内部工厂/父身份修订后的guard编译退出0。
- order08：授权文件名host修订后首次UNC复制失败，实际编译Linux此前稿，退出0；该条只作为旧稿证据。
- order09：正确UNC复制并核对host/Linux最终guard SHA之后，最终guard编译退出0。
- order10：stat只读核对lc03目录、关键记录与三个既有单位，退出0。
- order11：31个既有运行时关键文件原生sha256sum，退出0。

已有WSL代理配置提示原文保留；本轮网络请求与配置修改均0。py_compile显式生成pyc，-B用于抑制普通import缓存写入；语法编译不调用目标模块正文及其业务import。

## 证据等级
|检查|状态|
|---|---|
|最终八源语法（order06+最终guard order09）|PASS_STATIC|
|预算接口、调用点、N公式、顺序及异常分支|PASS_STATIC/CONDITIONAL_PASS，详见安全审查|
|五业务原hash+run_batch字节相同|PASS_STATIC|
|八源/缓存两端冻结、最终源码diff|PASS_STATIC|
|授权/输入/未来argv锁链|PASS_STATIC|
|历史/运行时关键文件/原单位只读复核|见evidence/HISTORY_AND_ENVIRONMENT_CHECK.json|
|真实速度、fsync分布、C02实际启动、运行API兼容|UNRESOLVED|
|范围租约S1–S9动态故障/并发|UNRESOLVED|
|C00–C12新资源资格|UNRESOLVED，实际新运行0|
|F1/F4|UNRUN_RESOURCE_GATE，实际新运行0|

本报告通过范围限于静态检查。人工控制流推导、文本核对及编译各自登记，未使用动态import或把source中的PASS分支当作实际运行结果。标准库完整树锁按旧1224项冻结记录原样复制；本轮31关键文件重新核验，完整树每项运行前重核义务保持，避免把旧记录写成新实测。

记录器两次行政失误只影响保存/复制/静态工件生成，相关过程没有启动目标程序；具体见CAPTURE_ERROR_EVENT与COPY_COMPILE_EVENT。纠正后原记录继续保留，顺序与失败事实保持可审。
