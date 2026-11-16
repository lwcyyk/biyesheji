# 静态检查与动态缺口

Material Passport：ManagerRecovery-static-1/r5；HOST_STATIC_ONLY。

|检查|结果|范围|
|---|---|---|
|Python语法/3.12文法/内存compile|PASS_STATIC|31程序；目标导入与执行0|
|调用图/前言及普通返回覆盖|PASS_STATIC|原前言外层、父wait返回、外部停止构造/循环均有失败出口|
|管理器事件与恢复守卫|PASS_STATIC，原生条件待验|实例捕获/保护结果/完整C09链/当前Owner/两侧快照；其他失败拒绝|
|幂等及终态|PASS_STATIC|唯一事件证书、首错exclusive、重复close观察、CLOSED优先及dispatch=false事实|
|停止/封存安全|PASS_STATIC，原生条件待验|STOP先于快照；pidfd身份；未发布/未回收UNKNOWN；单sealer；caller退出待外部确认|
|预算/deadline保持|PASS_STATIC|原核心不改，新前置预付；64,082≤100,000；无新T0/重置代码|
|受保护代码|PASS_STATIC|11程序字节、29函数AST、RootIPC既有权限/发布/等待方法保持|
|原C/S/门18兼容|PASS_STATIC|C00Ready/C09/probe/S驱动字节一致；原18门4个关键函数AST一致|
|输入/oracle|PASS_STATIC|64唯一ID、8mutant、每项≤2帧；oracle无生产/subject导入|
|原件与历史|PASS_ADMIN_ONLY|CalDiag1,398成员逐流SHA核对；所有旧预算/源码最终再核|
|性能/平台/故障行为|UNRUN|新systemd属性、I/O、停止响应及完整300秒仍需动态证据|

验收Gate MR-1=PASS_STATIC，MR-2=CONDITIONAL_PASS，MR-3=CONDITIONAL_PASS，MR-4=CONDITIONAL_PASS。新增夹具完整和静态控制流检查通过；新路径的真实恢复、回收/封存及边界故障模型继续保留动态责任。完整条件批次的独立身份/最终摘要还需阶段A证据后形成。

[调用图/语法](evidence/SYNTAX_CALL_GRAPH.json) · [保护语义](evidence/PROTECTED_SEMANTICS_CHECK.json) · [关闭覆盖](evidence/STATIC_CLOSURE_COVERAGE.json) · [夹具一致性](evidence/FIXTURE_ORACLE_CONSISTENCY.json)。
