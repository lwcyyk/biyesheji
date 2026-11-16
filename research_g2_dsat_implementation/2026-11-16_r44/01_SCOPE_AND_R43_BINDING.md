# R44范围与R43绑定

本轮完成八类资源及T20外部可观察性静态审定。预算结构完整，局部非null候选有依据，完整八类数值仍不足；资源未批准、监督器未实现、动态执行关闭。

授权附件：`C:\Users\a1887\.codex\attachments\04d1fcb0-6a08-410e-a687-b67ac09b3a52\Pasted text.txt`。本轮只新增R44报告、JSON和来源定位。

## 输入核验

R43全部25份交付完整读取，Driver原源码完整读入并解析AST；六份报告及原资源/测试/来源结构核对。R43 SOURCE_LOCK为 `6ea224b398b0b39b39a00881e21d70bf480f10034200771761a42b43b918a2a2`。

驱动59239字节，SHA：

`28e9ccf96f20a634b274f5350e8044da87b33f0c73905448664a68a3c41c67fd`

R41 Runner继续为：

`245a35d4786fdf4e43b532d11a70a9db1b9be1d5d81d1f6a3f78e1ecfd96646f`

原五函数与helper、28个ID/预期、54个内部变体、旧fixture及历史结果保持。R43的2507项保护基线，另加R43的25份交付及新Driver，共2533项纳入R44保全；旧44份SOURCE_LOCK保持原字节。

## 方法和证据

使用源码、AST、哈希、局部整数/控制流计算，以及Microsoft Learn官方API文档。23份官方来源的URL、读取位置、版本说明及获取时间见WINDOWS_SOURCE_MAP。原网页HTML未归档，其hash保留null；来源定位没有冒充安装系统/二进制身份。

项目scripts/src/tests内对Job/进程I/O监督API名称作只读检索，未发现所需外部监督组合入口。该结论只覆盖此项目范围；系统工具是否安装未探测。没有把公开API存在写成项目实现已就绪。

## 实际边界

SOURCE_MODIFICATIONS=0，DRIVER_MODIFICATIONS=0，DYNAMIC_TEST_RUNS=0，EXECUTION_AUTHORIZED=false，REAL_RESOURCE_ACCESS=0。

最后一项指测试/受监督进程、进程计数/内存采样、Job/ETW/系统追踪及真实业务资源访问均0；本轮允许的静态材料读取和公开文档获取另记。没有创建额外Python代码、测试日志、SQLite、密钥、监督进程、Job或追踪会话，也没有--help或导入目标预检。

当前对话内知情模型辅助静态审查，外部独立核验待取得。G2完整L0、G3、G4和D1-B1继续分别管理。
