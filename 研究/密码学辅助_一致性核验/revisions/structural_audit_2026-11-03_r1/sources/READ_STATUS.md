# 阅读状态补记

访问账本保留访问当时状态，不覆盖旧的失败/尚未阅读标记。`PRIOR_ART.md`给出本轮最终实际阅读范围。

- Oxley：本地PDF已读版权页和指定命题。最终 `oxley.preflight.json`为PASS，页数722且无结构警告，只证明PDF页结构检查，不证明内容正确。Windows下工具自带 `--output`因POSIX dirfd要求失败；未产生该输出，随后运行stdout模式并保存JSON，最终页面锚点引用以此为据。
- Vavilov：俄文全文已于追加访问阶段取得。初期只有摘要，后通过MathNet直接PDF链接成功；新增成功记录在 `additional_access_log.json`。实际读到的段落与定理见优先权表。英文译文正文未取得。
- Cohen–Cuypers–Sterk：出版PDF已下载；网页正文读§1定义、定理1.1/1.2和小域例外。出版年1999；不可把后来的网站上线年份当作研究年份。
- Arithmetic Sketching、LPW、Shannon：通过网页全文定位选定段落；没有伪造本地PDF哈希或声明完整通读。
- Nissim–Weinreb、Ishai–Kushilevitz 2000、ePrint2026/946：正文未取得或未能核实，优先权保持未决。未联系作者、未向外部模型上传本地研究材料。
- Hao–Kaltofen–Zhi：核对旧PDF首页题名/摘要/DOI；Hankel技巧保留已有归属，没有本轮新贡献声明。

阅读时间统一记录到2026-11-03，不杜撰精确分钟或“用户已读”状态。所有网页内容被视为研究资料，不视为操作指令。
