from pathlib import Path
import json
OUT=Path(__file__).resolve().parents[1]
p=OUT/'00_完整技术调研报告.md'
t=p.read_text(encoding='utf-8')
key='在源模型包含真实执行的前提下，'
assert t.count(key)==1
t=t.replace(key,'若 F 为空，系统返回证据冲突，后续判据要求 F 非空。在源模型包含真实执行的前提下，')
p.write_text(t,encoding='utf-8')
q=OUT/'11_调研质量审查与执行记录.md'
t=q.read_text(encoding='utf-8')
t+='''

## 最终检查结果与统计

14 项文档、来源和路径一致性检查通过，失败 0 项，详见 [quality_audit.json](data/quality_audit.json)。该检查的范围是文件结构、来源编号、链接、引用、输入哈希和表述边界。

内容核读登记为 72 项，其中本轮读取 70 项，同会话前轮复用 2 项。核心论文 45 篇，14 篇定点深析，31 篇首页或摘要级；8 份本地草案按标题、版本与摘要范围读取。新增独立登记来源 3 项，其中前作 2 篇、RFC 1 份。来源总体状态为已核验 25、部分核验 68、待核验 1；每项的实际范围见 09。

主报告保留 9 章、核心文献地图和 94 项来源题录。08 另保留最新探索的 25 项方向索引，05 保留资源谱、固定标签结构、授权询问和 FI 分析的关键条件及负例。容量模型补充 F 为空时的证据冲突分支，避免以空世界集给出关闭。

实际使用的写作规范副本：[zh-tech-writing](working/skill_refs/SKILL.md) 与 [typography](working/skill_refs/typography.md)。三个同名缺失技能按用户给定功能步骤执行，保持缺失登记；第三方依赖安装为 0。文件清点、文本提取及文档检查程序位于 working，均服务于本次调研取证。
'''
q.write_text(t,encoding='utf-8')
