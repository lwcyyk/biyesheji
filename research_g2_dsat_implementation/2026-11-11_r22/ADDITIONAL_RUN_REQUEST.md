# 追加一次54项重跑申请

首轮54项实际为53 PASS、1 ERROR。F24竞争失败子进程已经退出，BufferedWriter.close再次flush时出现OSError22；其余跨进程见证及F23/F26/T45通过。完整原日志保留。

修复仅在确认拥有子进程已经退出时接纳stdin关闭的BrokenPipe/OSError，存活进程错误继续拒绝。原授权两组回归将继续运行。请求总suite上限3→4，新增第4次仅new54，自动重跑仍0。

新54使用独立run，单次资源上限保持；两轮累计上限为：子进程16（并发2）、文件SQLite208、state测试key4、TLS材料4、SSLContext4、私有目录128、路径1024、输出128MiB、测试线程创建32（峰值4）、子进程窗口总120s。每个case连接仍至多2。实际部署、网络、P1/P2、S3-B2/S5继续关闭。

准确命令、修复和预算见ADDITIONAL_RUN_REQUEST.json。当前approved=false。R22第1/13节规定原总额3次，第14节要求资源上限固定，因此追加run及其新资源需独立批准。
