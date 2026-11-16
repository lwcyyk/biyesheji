# 来源、命令及资源的冻结程度

R42_SOURCE_LOCK固定实际Runner、五函数和helper摘要、现有解释器、原55项源码/测试/fixture pin、28项manifest及历史锁引用。可取得的输入pin均匹配；driver不存在且完整传递运行时来源闭包未形成，因此可执行来源集合尚未闭合。

当前驱动状态：DRIVER_IMPLEMENTED=false，DRIVER_SOURCE_HASH=null。R42_TEST_COMMAND_LOCK严格保持 `argv=null`、command_executable=false、execution_authorized=false、executed=false。没有生成不存在的CLI参数。

## 未来提议上限

继承R41的是待批准请求：一次suite、自动重跑0、120秒、2MiB；额外线程/测试子进程/SQLite/SQL/网络/密钥TLS均0；9个提议对象cap合计999424B，其中包含可选65536B native Journal，额外temp/rename副本0。它们未被登记为本轮执行权限。

拟输出根选择 `D:\毕业设计\research_g2_dsat_implementation\2026-11-15_r42\verification_runs\poison28_001`，依据R42当轮目录命名建议。R41的date14路径继续作为非可执行旧提议引用。该选择也仍是提议；两个旧目录都没有被用作fallback，本轮verification_runs创建0。

## RESOURCE_BUDGET_UNRESOLVED

以下R41缺失项原样保留未知：故障arm总次数；metadata/read/write/flush/fsync/open/close累计调用上限；锁和fixture/虚拟流数量；新目录总上限；整个解释器RSS及监督机制；累计实际payload写入量；正常/异常完整证据需求；120秒外部监督与收尾机制。

54个内部变体规格不能单独推出故障arm上限，因为准备和收尾还可能触发拒绝。32MiB只代表测试自有数据请求，整进程内存没有被设成同一个数。

999424B是9个对象cap之和。若实际驱动证明独占、单次创建/单调追加、无退款和额外scratch，并将全部partial/native输出计入，才可推导相应累计payload上界。缺少实际写入器源码时，sum(st_size)与累计write量分别保持。

## 输出与所有权

日志及receipt只能写新独占根；存在目标即停，运行中不自动改名或重用。stdout/stderr必须各有唯一capture owner，避免driver与launcher竞争同一文件。一次invocation claim拟复用已有artifact角色，不能添加第10个运行文件。

源模型13文件的虚拟账本验证原2MiB合同，主要占RAM；真正驱动的结果/日志及可选native文件另按同一提议物理预算完整计量。模型字节、native syscall及宿主取证写入分列，避免漏账或重复叠加。

清理只关闭当前invocation能确认拥有的句柄，保留失败证据。未知关闭、超时或目录所有权不明必须如实失败；历史删除、回滚Runner、重开已消费输出或释放原费用都不在规格中。

资源锁当前为RESOURCE_BUDGET_UNRESOLVED，命令就绪false。下一阶段只申请单文件实施及静态资源推导，动态额度请求仍为0。
