# 自动行政入口导入根因

Material Passport：PTA-PhaseFinalizer-static-1/r3；DCL-R6-PTA-PhaseFinalizer-Fix；2026-11-12；HOST_STATIC_ONLY。

**历史异常为ModuleNotFoundError: No module named 'boot_continuity'。旧锁直接以-I脚本运行startup_lifecycle.py，其第11行在设置同目录模块路径前执行绝对导入。**

历史精确argv：`C:\Windows\System32\wsl.exe --distribution Ubuntu-24.04 --user root --exec /usr/bin/python3.12 -I -S -B /var/lib/dcl-r6/pt01/src/startup_lifecycle.py --post-exit-export`。入口文件和boot_continuity.py均在49文件部署快照中，解释器为合同绑定的CPython3.12.3，调用身份由--user root指定。traceback没有权限错误；post执行前的实际cwd和sys.path完整快照均UNKNOWN。

CPython隔离参数-I排除脚本目录/当前目录及用户环境路径。旧脚本在绝对import boot_continuity时尚无对应sys.path插入，导致源文件存在仍无法解析。boot_continuity自身虽然有固定SOURCE引导，导入解析失败使其代码尚未执行；host正常入口先放入src路径的方式没有覆盖该直接Native脚本路径。旧compile只验证文法，无法检出这一导入阶段错误。

该布局原本由平铺src模块组成，没有包__init__.py。改为-m需要稳定可发现包或额外路径配置；本轮采用独立stdlib引导文件admin_postexit.py，保持-I -S -B与平铺部署结构，校验固定Root源目录/文件及摘要后加载兄弟模块，并检查真实模块origin。生产入口不依赖PYTHONPATH、cwd或systemd WorkingDirectory；Native post是host发起的独立WSL调用，未使用业务服务的Environment。

最终r3主机受控探针5项：两种cwd的惰性入口装载、固定可信兄弟stub优先于cwd诱饵、主机身份拒绝、缺模块错误传播。三个候选累计15项受控探针，均未调用入口main或真实生命周期模块。它们仅是主机环境证据；原生3.12装载、Root元数据和实际post调用仍UNRUN。

[历史stderr原件](evidence/PTA_ORIGINALS/host/STARTUP_POSTEXIT.stderr.raw) · [382项导入关系清单](evidence/IMPORT_GRAPH.json) · [最终受控导入结果](evidence/CONTROLLED_IMPORT_RESULTS.json)

RESOURCE_GATE_PASS=NOT_OBTAINED；F1/F4=UNRUN_RESOURCE_GATE；PASS_BOUNDED=[]；STRICT_SEPARATION_INSTANCES=0；IMPLEMENTATION_GATE=CLOSED。D1/D2原安全、条件结论及强G覆盖裁决保持。
