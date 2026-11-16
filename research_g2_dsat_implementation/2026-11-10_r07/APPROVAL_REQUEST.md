# 一次性具体授权申请（当前PENDING）

申请批准以下全部固定范围；当前尚未执行下载/安装/依赖代码。

## 1. 唯一软件分发

- 包：networkx==3.7；无extras，无其他新依赖。
- 文件：networkx-3.7-py3-none-any.whl；2,142,205bytes。
- SHA-256：`e3fd2c13a7814cee3746340d8d7f8598a67f16a58bf47fb7f8793fab6efca1b0`。
- 唯一下载URL：https://files.pythonhosted.org/packages/7e/cd/fe58041e9011f307c490e3e17dd48cc516448f7c698a3f2d9d9d65d7e6a8/networkx-3.7-py3-none-any.whl
- 本地存放：D:/毕业设计/research_g2_dsat_implementation/2026-11-10_r07/wheelhouse/networkx-3.7-py3-none-any.whl。

下载后先核SHA/大小及Wheel元数据/许可证，哈希或身份不符即停止。该步骤包含固定URL的一次软件包下载授权，区别于已允许的元数据读取。

## 2. 唯一隔离安装位置

`D:/毕业设计/auth-lifecycle/.venv-dsat-r07-networkx-3.7`

使用现有CPython3.12.14创建without-pip环境；用已安装pip26.2.2的--python管理此环境，安装仅从上述本地Wheel目录读取。共用Python和全局site-packages保持原样。

以下命令是待批准计划，当前未执行：

```powershell
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7' --without-pip
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip --isolated --disable-pip-version-check --no-cache-dir --python 'D:\毕业设计\auth-lifecycle\.venv-dsat-r07-networkx-3.7\Scripts\python.exe' install --no-index --no-deps --require-hashes --only-binary=:all: --find-links 'D:\毕业设计\research_g2_dsat_implementation\2026-11-10_r07\wheelhouse' -r 'D:\毕业设计\research_g2_dsat_implementation\2026-11-10_r07\requirements-dsat.lock'
```

## 3. 依赖执行、接线和指定测试

允许在该环境导入并核验NetworkX3.7版本/路径，只接入dsat_flow的整数m/d优化、残量势和不足割；最小修改现有两个DSAT测试及必要的离线runner审计/日志，明确登记新增纯S2专项。保持S1/类型/独立检查器标准和所有旧运行协议。

执行原两个指定模块的全部77项并保留/替换原SKIP为真实求解验证；增加本轮列明的有限反例；独立检查自动生成的合成证书CLI。采用隔离环境绝对Python路径及-I，runner只加载批准模块。资源界沿R06（尝试/见证各256、来源边16384、整数128bits、有限JSON），不做大规模压力或优化竞赛。

真实认证API、账号/Token/密码、运行AuthorityStore/Provider、S3写回、S5原生、整仓测试、新协议/算法和额外依赖均超此申请。出现环境/哈希/资源/独立证书问题时停止对应功能，保留O和历史结果。

本申请须获得研究者明确答复，静默/经过时间均不视为批准。
