# 静态检查结果

Material Passport：BF-static-2/r4；STATIC_SYNTAX_PASS；动态UNRUN。

## 编译与实际命令

当前/usr/bin/python3.12=Python3.12.3，SHA-256=e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f。COMMAND_PLAN预登记全部WSL argv，commands保存原始字节流及退出。

17条已捕获WSL命令均exit0：01为原生存在性find、02为项目单位只读列表、03/04为编译器hash/version；05–15为获准py_compile。16为现有journalctl二进制只读hash核验，尚未读取运行日志。17为最终静态目录/关键source与输入权限只读核验：所查目录root:root0755，所查文件root:root0644。源码覆盖为：

- 05：全部11份源码初始语法检查。

- 11：最终guard.py与range_fixtures.py。

- 15：最终range_core.py与range_evidence.py。

- 其余7份源码保持05检查时字节。
目标模块正文、S1–S9、C00–C12和F1/F4执行次数均0；没有动态import或故障注入。

行政记录中包含命令长度拒绝、一次PowerShell复制脚本解析错误、一次safe job空mutant字段的清单生成错误；均为静态工件处理，详见ADMIN_ERROR_EVENT。07编译的是复制失败前的Linux稿，最终证据按11/15归属，不把旧稿检查代替最终文件。WSL原始代理提示保留，配置及依赖未改。

## 静态核查

STATIC_CONTROL_FLOW_CHECK：PASS_STATIC。34个唯一job、9项性质、11类变异、17个门负向检查、统一oracle断言、调用接口、真实计费前置、并发请求屏障与意外失败拒绝均有源码/输入对应。
ARGV_STATIC_CHECK：15组payload、每组36项属性、34条worker模板与源码字面合同一致；驱动实际会为6类崩溃场景和并发场景的正反版本顺序启动14个worker，其余模板不由本驱动调用。
五业务、runner和原探针共7份文件逐字节一致。30项静态工作区文件在host/Linux两端摘要匹配，包含11源、11缓存、8输入。

## 历史与未决项

144项BF/batch03研究工件、BF外部24项、batch02原件51项和误路径47项hash复核通过。batch03预检包76项逐流核对；原1266项运行时核验的机器证据保持。本轮重核编译器，完整运行时树与manager/kernel身份锁继承原记录，下一动态准入仍须重新核验。

01/02原生查询确认batch03/batch04运行根/单位/cgroup及项目运行实体没有匹配项。实际batch03停于预检，无T0、counter或运行CLOSED文件；当前同样没有新运行账/窗口。没有把“研究预检停止”写成一次已运行批次的关闭。

语法/文本核对与人工控制流审查各有范围。fsync设备合同、进程调度/终止延迟、同UID任意恶意代码和实际测试命中仍为条件/未决；当前不授予任何动态PASS或RESOURCE_GATE_PASS。
