# 初始假设失败记录

2026-11-03。第一次`classify_gf7.py --out results/classify01`完成几何枚举后，断言“r3两个实例覆盖全部共点结构类别”失败。该断言没有证明基础，失败揭示抽样不能代替分类。随后依赖该输出的`compressed_lp.py --out results/compressed01`因不存在summary.json而失败，未产生数学结果。

修改为如实输出全部类别及覆盖标志，使用新的classify02/compressed02目录重跑；原空目录保留。这个失败不否定r3两个已核验的最优值，而是否定它们已经穷尽GF7全部表示类别的额外猜测。
