# 静态审查中的两项证据建模修正

本轮静态取证脚本曾在两个假设检查处停止，均未启动Runner或测试。

1. 原2146文件清单包含获准修改的Runner。先前2177项快照中该项在补丁后自然变化。现将其独立列为before/after源锁，初始快照保存在INITIAL_PREPATCH_BASELINE.json；其余2176项按历史SHA保持。
2. 原68项manifest物理行顺序为D/A/H；实际执行由原PHASES分组过滤为A1/H1/D1A。静态比较改用原分组规则，manifest及测试内容保持原字节。

这两处属于静态检查输入模型的修正。最终STATIC_AUDIT.py.txt完成38组检查；动态suite计数始终为0。补丁后内存观测可能触发的ctypes.wintypes导入也已移到最后来源快照前，最终源锁覆盖该改动。
