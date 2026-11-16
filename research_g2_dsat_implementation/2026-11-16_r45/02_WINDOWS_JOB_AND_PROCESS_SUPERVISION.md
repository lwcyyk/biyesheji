# Windows Job和Child生命周期

PolicyValidator先读取策略、原8类批准值、源码、Driver执行packet、完整来源和产物证明。任何必需值为null时，在WindowsApi构造之前抛出RESOURCE_LIMIT_NOT_APPROVED。标准库导入、字面Path及ctypes类型定义允许出现在模块顶层，显式DLL加载、文件读取和资源操作均位于受控函数。

## 创建与归属

选择R44已规定的创建时JOB_LIST，再配合CREATE_SUSPENDED。先创建私有unnamed Job，设置KILL_ON_JOB_CLOSE和活动进程1，读取配置确认。提交内存Quota仅在独立批准的数值和enable标记都存在时设置。

Child使用准确ApplicationName和可写Unicode命令缓冲，flags包括CREATE_SUSPENDED、EXTENDED_STARTUPINFO_PRESENT和CREATE_NO_WINDOW。JOB_LIST把私有Job在原生创建时关联。恢复前两次IsProcessInJob、创建时间和实际镜像路径检查成立后，仅调用一次ResumeThread，预期原挂起计数1。

AssignProcessToJobObject保留类型化封装，当前编排走JOB_LIST。版本/宿主嵌套不支持会停止创建或恢复。父Job环境记录在ADMITTED，选定Windows build与已批准runtime锁一致。创建时归属加强了创建后到显式分配之间的控制范围。

## 继承范围

STARTUPINFOEX的HANDLE_LIST恰好包含NUL stdin、stdout写端、stderr写端。两pipe读端先清除HANDLE_FLAG_INHERIT，Job、process/thread和witness都位于继承清单外。bInheritHandles=true与这个显式清单共同使用。

Child创建成功后父进程关闭本地三个child端，留下两读端交替Peek/Read。每次读取至多当前可用字节和批准chunk值，并检查时限/字节配额。成功路径必须确认stdout、stderr均到EOF，余留输出会阻断成功。

CreatePipe的nSize是OS缓冲提示，实际内核分配峰值仍UNKNOWN。同步pipe调用、磁盘write/fsync可能迟返，其平台延迟责任保留。

## 所有权与异常

父进程保存CreateProcess返回的真实process/thread句柄和PID/TID，创建FILETIME与固定镜像路径绑定其身份。操作基于持有句柄和私有Job，源调用图没有PID扫描或打开其他进程。

关闭操作设置一次性attempt标记，成功后才清空句柄。失败时身份和错误记录保留，后续清理按既有attempt状态处理。GetCurrentProcess伪句柄仅作借用查询，关闭函数不会接收它。

部分初始化、membership失败和Resume异常都进入owned cleanup。已取得但归属未确认的process可通过其创建句柄请求终止。Kill-on-close是最后私有Job句柄关闭后的后备控制，未继承Job句柄的条件由创建路径保障。

原生函数成功到Python状态登记间的异步中断、OOM及实际OS资源行为仍需要单独故障验证。本轮未执行这些路径。
