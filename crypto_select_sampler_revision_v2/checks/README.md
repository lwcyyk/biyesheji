# SPEC2有限数学核对

复现（PowerShell）：

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\毕业设计\crypto_select_sampler_revision_v2\checks\verify_math.py'
```

Python仅使用标准库、Fraction精确有理数、整数及有限词串。INPUTS.json是实际输入，RAW_RESULTS.json包含全部180个检查项目及中间值。类别和数量另见RUN_SUMMARY.json。首次运行171项通过；补入域映射、调用内部尾界位置、直接控制位及规范采样三查询后重跑180项通过。两个运行版本哈希见RUN_HISTORY.json。

覆盖n=1、2的幂、略高于半幂的域，F_q/F_q*不同词宽，B=1和其他B，三角/矩形秩，带编码及拒绝词，适应性域选择的逐条件尾界及union bound。小n所有B词预抽样串显式枚举，接受后尚未消费的词仅作为等量补全，不进入返回带。

提交失败核对采用抽象状态账本：Setup、普通Enc/Upd、Challenge两个分支、挑战前/后的Next在每个采样位置注入失败，检查未提交临时字段与旧状态的分离。它验证本稿声明的原子规则在这些有限位置的具体含义；没有运行密码协议，也没有验证生产实现的事务性。

评分范围核对包括C0单失败质量系数1、FAIR系数1/2，以及判定器两个世界累计2和1。R1采用旧guarded-uniform的精确概率，另外计算SPEC2三查询偏差及其误差界。此处数值只是算术核对；DDH困难性与无限族安全性依据正文归约。

180是检查项目数，包含70个规范概率输入、若干有限枚举和状态位置；它不代表180个安全场景、原生请求或独立复审。完整一般定理未交给证明助手验证。
