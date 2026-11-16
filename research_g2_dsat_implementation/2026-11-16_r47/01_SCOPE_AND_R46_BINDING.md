# G2-R47：单文件修复范围与版本绑定

本轮完成成熟工程计量与证据修复，以及当前对话内知情模型辅助静态审查。唯一修改的工程文件为 `D:\毕业设计\auth-lifecycle\scripts\run_dsat_poison28_supervisor.py`。没有执行或导入该文件，没有运行测试及Windows原生资源API。局部补丁静态义务已逐项核对；整体执行准入继续 `R47_STATIC_PREFLIGHT_BLOCKED`。

正式授权原文：`C:\Users\a1887\.codex\attachments\fdcb8edf-ea6c-4c5c-a2d8-2dee510279b3\Pasted text.txt`。此前R46申请中的approved=false保持历史原样，R47的新授权独立绑定本轮修改。

## 冻结依据

完整读取R46目录25份材料并校验其全局来源锁及全部交付指纹。R46 SOURCE_LOCK SHA为 `bf5eb932d07e5215391fbb95353dbd8b16e4916477df2ac008f866b3066f052d`。实际读取记录见sources/R46_COMPLETE_READ_AND_BINDING.json。

| 对象 | SHA-256 |
|---|---|
| R41 Runner，保持原字节 | `245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f` |
| R43 Driver，保持原字节 | `28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd` |
| R45/R46 Supervisor原始版本 | `953d15d7b000b02014062924f80a40d537cba214e17e3459070000f70b8f16d1` |
| R47 Supervisor新版本 | `2bb2c5daeca2b668f756978aa93f1d1cccad909a40c79e3836677a266bbc2777` |

实施前完整原字节保存为sources/SUPERVISOR_BEFORE.py.txt；实施后副本、完整unified diff及函数级变化见sources/SUPERVISOR_AFTER.py.txt、sources/SUPERVISOR.patch、R47_CODE_DIFF.json。源文件从53418B变为74737B。

## 函数范围

R46申请以PolicyValidator、OutputController和receipt三项责任描述范围，没有穷举函数名。本轮在R47_PATCH_SCOPE_LOCK.json预先列出11个允许改动的既有函数。checked_path承担R47第四节明确列举的路径/元数据检查计费；supervise仅增加锚点API快照和ADMITTED/receipt字段。新增定义全部位于同一文件：ExplicitIO helper、来源读取/PE helper和前缀属性/快照方法。没有第二个工程文件依赖或函数锁冲突。

WindowsApi、DeadlineController、JobController、ChildProcessController、ResourceObserver、process_times、main、canonical及所有11个ABI结构均与修改前AST相同。把supervise中的三个纯证据变化移除后，剩余生命周期AST与原版完全相同。原清理顺序、创建时JOB_LIST、HANDLE_LIST、PID/creation time绑定和异常处理保持。审查定位见sources/ABI_AND_LIFECYCLE_STATIC_AUDIT.json。

## 历史保护口径

继承2591项记录，再加入R46的25份交付，共2616项。唯一允许变化的活路径为Supervisor；R45/R46的源码快照、报告与47份既有SOURCE_LOCK全部保留原字节。最终期望为2615项未变、1项授权替换，5个既有缺失路径保持缺失。详细比较写入sources/HISTORY_AFTER.json；原42份工程源码、fixture、原28项身份及断言通过继承指纹继续保护。

本轮属于已有工程的计量修复，原创算法贡献登记为0。T3、其他数学结论、机制实现分离门、COL2026主动检索暂停及FS23延期均保持原状态。
