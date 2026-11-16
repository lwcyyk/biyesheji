# 本轮读取、定位与证据台账

日期2026-11-06。原文获取与数学分析分开；同一模型/上下文内的本轮核查按知情文献审查登记，未新增外部数学读者或证明助手。

## 1. 新原文与绑定

|ID|本地文件/来源|取得范围、版本和关联|
|---|---|---|
|KU-A12|KU2012_author.pdf；https://fpt.akt.tu-berlin.de/publications/ce-bounded-degree.pdf|28页；2012-05-23，作者公开的Preprint submitted to Discrete Applied Mathematics。题名、作者、刊物与DOI题录对应；期刊排版版逐字一致性未核|
|D13-P|DAM2013_preview.pdf；https://page-one.springer.com/pdf/preview/10.1007/978-3-642-45278-9_38|正式章节前两页433–434，完整章433–437。出版页直接预览链接绑定DOI；后3页未取得|
|D13-M|DAM2013_publisher.html、DAM2013_chalmers_record.html|出版方摘要与Chalmers187873题录；后者没有本轮可见全文链接|
|D16-R|frozen_inputs/ae_priority_audit/sources/damaschke_edopt2016.pdf|复用9页作者稿及旧PASS；首页声明只扩展2013的一节，使用范围不扩张|

KU-A12和D13-P的精确SHA256、页数与结构预检见相应sidecar及SOURCE_MANIFEST.json。完整来源身份见主稿SOURCE_AND_VERSION.md。

## 2. 实读定位

KU-A12：

- pp1–6：版本、摘要、Definition1、参数及Table1。
- pp7–12：Lemma1、3-SAT构造、Th1及证明、Cor1和Th2；对其量词和参数与T2比较。pp13–14读取Deletion入口、Th3/4及Cor2，未外查所调用RPIT来源的全部证明。
- pp19–25：§4全部模型框、参数关系、Rules3–8、Lemma5/6/7、Th6/7及其全部核化证明。该范围承担主要覆盖判断。
- §3低度数Deletion算法已定位Th5并读取主要说明，未独立重证其匹配黑箱；本文没有用它承担T2覆盖。
- pp26–28参考文献：同工作版本及相关引文。

D13-P：两页全部文字及公式，含p433参数定义、新旧核大小和时间、p434 Definitions1/2、Lemma1及其证明首段；余文中断处明确保留。

D16-R：复读首页版本脚注、团/编辑定义与Theorem5，继承前轮更广阅读记录；本轮没有把后续充分条件改写为2013核化算法。

## 3. 关键公式目视核对

|图像|核对内容|
|---|---|
|KU2012_author_page01.png|题名、两作者、日期与submitted版本声明|
|KU2012_author_page03.png|Definition1所有顶点局部预算|
|KU2012_author_page05.png|Table1中的4dt/2dt核和局部/全局参数|
|KU2012_author_page12.png|Cor1“每个YES实例存在局部4解”、Th2 ETH界|
|KU2012_author_page19.png|输入框τ:V→{0,…,t}、d/K及所有顶点限制|
|KU2012_author_page21.png|Rules3/4阈值>2t、扣K与两端τ、O(N³)|
|KU2012_author_page22.png|Rule6大小>2t、d减1、Lemma6末句2k文字疑点|
|KU2012_author_page23.png|Th6的4dt、O(N³)、大团矛盾证明|
|KU2012_author_page24.png|Deletion Rule7阈值t、Th7的2dt|
|DAM2013_preview_page1.png|印刷433，新核5dt+d、O((M+dt²)logN)，随机接近4dt/期望时间|
|DAM2013_preview_page02.png|印刷434，Lemma1假设/时间、开邻域及x/y首段|

渲染返回码与字体警告见RENDER_LOG.json。没有将渲染成功升级为数学证明验证。

## 4. PDF读取完整性

KU结构PASS，28页计数一致；D13预览结构UNAVAILABLE，2页计数一致，xref对象866警告保持。D13第一次CLI指定sidecar输出遇Windows缺少POSIX dirfd支持，随后保存stdout真实JSON，仍为UNAVAILABLE。

第二解析pdfplumber/pdfminer分别得到28/2页，无空白文本页、捕获警告为空，见SECOND_READER.json。原PDF没有修复或改写；一项解析器没有警告也不覆盖原预检警告。

## 5. 本文数学工作的归属

- 已有原文：局部度模型、团目标、4dt/2dt核、邻域差/公共邻点强制规则、D13可见新核声明。
- 标准补全：核后d标签枚举、显式费用和解日志恢复。
- 本文纸面分析：P₄、K₁,₄、孤立对象、私有复制反例；图模型到带相等约束矩阵的全称等价；精确T2桥接责任。
- 尚缺：D13后3页、KU正式版差异、COL2026全文，以及任何声称完成任意模板/单侧预算归约者的完整证明。

原来源里的文字疑点与本轮构造正确性分别管理。本文没有由某源中的排版/自点疑点宣布其整项定理无效；相应原文和证明上下文等待完整核对。

## 6. 验证边界

INPUT_MANIFEST.json绑定历史输入；SOURCE_MANIFEST.json绑定新增来源；DELIVERY_CHECK.json仅检查文件、哈希、链接和JSON，不承担数学验证。网络动作仅正常只读；无外部消息、购买、账户、挑战绕过或候选机制实现。
