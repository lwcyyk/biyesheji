from pathlib import Path
import json
root=Path(r'D:\毕业设计')
dest=root/'研究'/'创新性验证与假设驱动研究_2026-11-02'/'工作文件'
dest.mkdir(parents=True,exist_ok=True)
g=json.loads((root/'研究'/'研究空白与创新融合_2026-11-02'/'研究空白与来源核验台账.json').read_text(encoding='utf-8'))['new_sources']
n=json.loads((root/'研究'/'深化调研_2026-11-02'/'文献核验台账.json').read_text(encoding='utf-8'))['new_sources']
index={s['id']:s for s in g+n}
keys=['G04','G03','G05','G06','G16','G01','G09','G10','N04','G13','G14','G12','G11','G02']
sources=[]
for i,k in enumerate(keys,1):
 s=dict(index[k]);s['previous_id']=k;s['id']=f'V{i:02d}';s['read']=s.get('read','');s['boundary']=s.get('boundary',s.get('use',''));sources.append(s)
sources[0]['url']='https://arxiv.org/pdf/2204.00755'
sources[0]['read']='本轮原文§2、§3.1至§3.3：belief support、Definition 2、Theorems 2至5及公平性条件；不是完整全文独立证明复核'
sources[1]['url']='https://arxiv.org/html/2212.01838'
sources[1]['read']='本轮原文§1至§3.3，区分采样学习与依赖模型的安全保证'
sources[7]['url']='https://www.macs.hw.ac.uk/~sr338/publications/'
sources[7]['read']='本轮作者出版列表核对题名、作者及EuroS&P 2026；此前会议列表与机构报告摘要；仍未取得全文'
sources += [
{'id':'V15','title':'Enforcing Almost-Sure Reachability in POMDPs','authors':'Sebastian Junges; Nils Jansen; Sanjit A. Seshia','year':'2021','venue':'CAV 2021，602–625','doi':'10.1007/978-3-030-81688-9_28','url':'https://link.springer.com/chapter/10.1007/978-3-030-81688-9_28','read':'本轮出版社摘要、方法入口与正式出版信息；官方工件仓库说明','boundary':'SAT与决策图的winning-region综合已有先例；未运行工件，不将almost-sure语义外推为有限时限内所有轨迹保证。','code':'https://github.com/sjunges/shielding-POMDPs'},
{'id':'V16','title':'A research agenda for active automata learning','authors':'Sophie Fortz et al.','year':'2026','venue':'International Journal on Software Tools for Technology Transfer，2026-02-19','doi':'10.1007/s10009-026-00839-z','url':'https://link.springer.com/article/10.1007/s10009-026-00839-z','read':'本轮原文摘要及Concurrency、Unobservability、Resets段落与Challenges 17、18、20','boundary':'确认resetless、并发及不可观测学习已形成研究脉络；开放挑战不等于本课题已解决。'},
{'id':'V17','title':'Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution','authors':'Genliang Zhu; Chu Wang','year':'2026','venue':'arXiv:2609.21284v1，预印本','doi':'10.48550/arXiv.2609.21284','url':'https://arxiv.org/abs/2609.21284v1','read':'本轮HTML §4.1至§4.2；延续此前§3至§5指定段落核对','boundary':'最小支持、实际选定见证及独立重绑已有先例；未复现其工件，不把静止等同业务完成。'}
]
(dest/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print('sources',len(sources))
