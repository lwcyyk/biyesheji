# 修复实现与差异范围

Material Passport：PreT0Recovery-static-1/r3；独立pt01工作区；动态0。

新增startup_lifecycle.py提供活体预窗上下文、临时认证查询scope、单调初始化intent/phase、运行checkpoint、工作前置条件、startup期限与封存适用性；新增startup_regression.py、独立startup_oracle.py及startup_contract.json；新增host/startup_finalize.py作为自动退出后行政收尾与host前端异常归档。

manager_recovery.query仅改为通过生命周期接口选择检查点/截断查询期限；正常运行态审查/classify/实例/ACK/Receiver/waitpid/恢复规则保持AST。abort只补启动上下文期限选择，seal增加适用性分派。guard在initial health外建立pre-scope，在真实state/counter前后加初始化标记/guard/ready/armed及work gate；新增PT最小诊断scope及Formal前PT资格。原预算核心、C00Ready、C09、原C/S/门18保持。

host入口在原active退出记录写完后自动finalize，异常前端另做host-only归档，原退出码保留。新增post调用是只读行政导出，源/输入/角色及原件SHA可核，绝不建立T0/账或启动测试。

相对r5：51项文件、35程序/16输入；20份同路径修改、25份字节保持、6个新增路径（4程序、1输入及slice新名），原slice只在新工作区更名。13份关键程序字节与40个既有预算/Boot/门18/MR函数AST一致。RootIPC原权限/发布/等待方法及slice资源字节保持，新增两个固定Root公共checkpoint/资格对象按原0640合同注册。

原mr01/r5、MRA、CalDiag及全部历史文件保持。r1/r2候选源/锁保留，最终r3权威。静态迭代纠正了合法work前必须ARMED的独立reference、缺checkpoint变异的作用阶段、实际archive核验及process/application分类，未运行夹具或程序正文。

[最终源码](evidence/SOURCE_FINAL_R3/inputs/static_manifest.json) · [完整diff](evidence/FULL_DIFF.patch) · [逐文件SHA](evidence/FILE_DIFF_INDEX.json) · [保护检查](evidence/PROTECTED_SEMANTICS_CHECK.json)。
