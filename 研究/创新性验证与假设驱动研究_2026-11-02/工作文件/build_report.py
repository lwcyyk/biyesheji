from pathlib import Path
import json,re,hashlib
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(r'D:\毕业设计')
TASK=ROOT/'研究'/'创新性验证与假设驱动研究_2026-11-02'
WORK=TASK/'工作文件'
BASE=ROOT/'硕士研究深化增补_AI数字主体与密码管理器_v2.15_研究空白与创新融合版.docx'
OUT=ROOT/'硕士研究_v2.15_创新性验证与假设驱动研究报告.docx'
source_hash=hashlib.sha256(BASE.read_bytes()).hexdigest()
doc=Document(BASE)
for el in list(doc.element.body):
    if el.tag!=qn('w:sectPr'):doc.element.body.remove(el)
sources=json.loads((WORK/'sources.json').read_text(encoding='utf-8'))
for s in doc.styles:
    if s.name in ['Research Body','Research H1','Research H2','Research Small','Research Table','Research Note']:
        if s.name=='Research H1':s.paragraph_format.page_break_before=False
        if s.name=='Research Small':s.font.size=Pt(9)

def p(text='',style='Research Body'):
    return doc.add_paragraph(text,style)
def hyperlink(par,label,url):
    rid=par.part.relate_to(url,RT.HYPERLINK,is_external=True);h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid)
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'245B78');pr.append(c);u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u);r.append(pr)
    t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);par._p.append(h)

p('当前研究的创新性验证与假设设计','Title')
p('针对 v2.15 的审查报告与待冻结实验规约','Research H2')
p('2026年11月2日　Asia/Shanghai　审查状态 REVISE　实验状态 NOT_TESTED','Research Small')
p('核心结论：A1、B1、AB1尚未确立独立机制创新。部分核心规则已有直接先例；本版将可保留的领域增量改写为条件正确性命题和可证伪的成本、配置及反馈假设，并给出强基线、反证与统计判定。')
p('本报告是v2.15的验证增补，原研究文档保持不变。第2节核验创新边界，第3节给出必须修正的问题，第5节列研究假设，第6至8节规定实验与判定。阈值和样本设计均为待研究者确认的建议，不代表已预注册或已完成实验。')

def table(rows):
    t=doc.add_table(rows=1,cols=len(rows[0]));t.autofit=False
    widths={3:[4.2,6.4,6.4],4:[3.1,4.2,4.8,4.9]}[len(rows[0])]
    for i,w in enumerate(widths):t.columns[i].width=Cm(w)
    for i,v in enumerate(rows[0]):t.rows[0].cells[i].text=v
    for vals in rows[1:]:
        for c,v in zip(t.add_row().cells,vals):c.text=v
    for j,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        if j==0:row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for i,c in enumerate(row.cells):
            c.width=Cm(widths[i]);pr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DDE7ED' if j==0 else ('F5F7F8' if j%2==0 else 'FFFFFF'));pr.append(sh)
            mar=OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),'80');e.set(qn('w:type'),'dxa');mar.append(e)
            pr.append(mar)
            for par in c.paragraphs:
                par.style=doc.styles['Research Table']
                if j==0:
                    par.paragraph_format.keep_with_next=True
                    for r in par.runs:r.bold=True
    p('')

def mr(text):
    r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);return r
def sub(a,b):
    out=OxmlElement('m:sSub');base=OxmlElement('m:e');base.append(mr(a));sc=OxmlElement('m:sub');sc.append(mr(b));out.extend([base,sc]);return out
def eq(parts):
    par=p();par.alignment=WD_ALIGN_PARAGRAPH.CENTER;par.paragraph_format.keep_with_next=True;op=OxmlElement('m:oMathPara');o=OxmlElement('m:oMath')
    for v in parts:o.append(mr(v) if isinstance(v,str) else v)
    op.append(o);par._p.append(op)
def equation(name):
    if name=='horizon':
        eq([sub('W','0'),' = Goal ∩ Safe ,     ',sub('W','r+1'),' = ',sub('W','0'),' ∪ Pre(',sub('W','r'),')'])
        p('其中Pre要求动作获准、满足硬约束且具有至少一个可能结果，并使全部可达观察后继进入参数所给的区域；尚未到达Goal时每次选择均减少剩余步数。','Research Small')
    elif name=='core':
        eq([sub('P','1'),' ∩ ',sub('P','2'),' ≠ ∅ ,   ',sub('P','1'),' ∩ ',sub('P','3'),' ≠ ∅ ,   ',sub('P','2'),' ∩ ',sub('P','3'),' ≠ ∅'])
        eq([sub('P','1'),' ∩ ',sub('P','2'),' ∩ ',sub('P','3'),' = ∅'])
    elif name=='cost':
        eq(['U(e) = 1 ⇒ ',sub('C','Q'),'(e) = ',sub('Q','total'),'(e)'])
        eq(['U(e) = 0 ⇒ ',sub('C','Q'),'(e) = ',sub('Q','cap'),'(e) + 1'])

def refs():
    for s in sources:
        par=p(f"[{s['id']}] {s['authors']}. {s['title']}. {s['year']}. {s['venue']}.",'Research Small');par.paragraph_format.keep_with_next=True
        par=p('','Research Small');par.paragraph_format.keep_with_next=True;hyperlink(par,'原文或官方入口',s['url'])
        if s.get('doi'):par.add_run('　DOI: '+s['doi'])
        if s.get('code'):par.add_run('　');hyperlink(par,'工件或实现入口',s['code'])
        par=p('读取范围：'+s['read']+'。','Research Small');par.paragraph_format.keep_with_next=True
        par=p('边界：'+s['boundary']+'　访问/核验截止：2026-11-02。','Research Small');par.paragraph_format.space_after=Pt(8)

lines=(WORK/'report.txt').read_text(encoding='utf-8').splitlines();i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
        table(rows);continue
    if line.startswith('# '):p(line[2:],'Research H1')
    elif line.startswith('## '):p(line[3:],'Research H2')
    elif line.startswith('{EQ '):equation(line[4:-1])
    elif line=='{REFERENCES}':refs()
    else:p(line)
    i+=1

for sec in doc.sections:
    for par in sec.header.paragraphs:
        par.text='v2.15 创新性验证与假设设计';par.style=doc.styles['Research Small']
    for par in sec.footer.paragraphs:
        for r in par.runs:r.text=r.text.replace('研究增补','研究验证')
doc.core_properties.title='当前研究的创新性验证与假设设计'
doc.core_properties.subject='针对v2.15的创新性审查与待冻结实验规约'
doc.core_properties.comments='所有经验假设NOT_TESTED；数值阈值为建议；未登记外部预注册。'
doc.save(OUT)
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==source_hash

shared={'state':'DRAFT_FOR_REVIEW','thresholds_are_proposals':True,'registered_externally':False,'formal_test_data_collected':False,'primary_family_alpha':0.05,'primary_hypotheses':['H-A','H-B','H-AB'],'decision_method':'Bonferroni alpha/3; within each claim all cost and utility conditions must hold','experimental_unit':'run','cluster_unit':'configuration_family','fixed_strata':'authentication_implementation','planned_power':0.8,'confirmatory_sample_size':None,'sample_size_reason':'requires independent pilot variance, cluster dependence and utility rate estimates','failure_costs':{'C_Q':'Q_total if lawful completion else Q_cap+1','C_G':'G if lawful completion else G_cap+1'},'baseline_information':'identical approval, native capabilities, observation rights and fixture initialization; scorer truth hidden'}
hypotheses=[
{'id':'H-S','kind':'conditional_deductive_claim','target':'sound bounded policies and certificates','null':'an in-scope counterexample exists','alternative':'all checker-accepted policies/certificates satisfy the stated guarantees within the defined model class','prerequisites':['closed finite semantic class','faithful observation and action mapping','trusted approval store and execution boundary','strictly decreasing remaining horizon','multi-world conflict certificate support'],'falsifier':'one reproducible in-scope accepted unsafe/nonterminating/wrongly classified trace','validation':['proof obligations','exhaustive schedules within each declared finite fixture','independent replay'],'status':'NOT_TESTED_THIS_ROUND','proof_status':'NOT_COMPLETED','new_experiment_results':None},
{'id':'H-A','kind':'primary_empirical','population':'pre-fixed D_A; independently certified feasible goals requiring at least one request','iv':'candidate authentication abstraction and evidence selection','baseline':'B-A mature property-directed learning/test selection with identical safety and obligation constraints','outcomes':['mean_C_Q_ratio','lawful_completion_rate_difference','unsafe_executions','false_assurances'],'null':'R_A >= 0.80 OR delta_U_A <= -0.05','alternative':'R_A < 0.80 AND delta_U_A > -0.05','support':'adjusted one-sided upper bound R_A < 0.80; adjusted lower bound delta_U_A > -0.05; no in-scope safety counterexample','controls':['B module','executor','observations','budgets','side-effect accounting'],'falsifiers':['valid safety counterexample','adequate evidence excludes material advantage','advantage explained by extra information or omitted cleanup'],'status':'NOT_TESTED','results':None},
{'id':'H-B','kind':'primary_empirical','population':'pre-fixed D_B; common verified contract; feasible mixed-control goals with 4 or 8 tasks plus simple negative strata','iv':'credential configuration algorithm','baseline':'B-B fixed portfolio of shared broker, fully independent grants, valid signature grouping, privilege greedy; choose best valid candidate via same checker','outcomes':['mean_C_G_ratio','lawful_configuration_and_control_completion_difference','approval_count','isolation_count','solver_time'],'null':'R_B >= 0.80 OR delta_U_B <= -0.05','alternative':'R_B < 0.80 AND delta_U_B > -0.05','support':'adjusted cost and utility limits passed with identical capability and approval caps','controls':['verified contract input','native capabilities','hard budgets','checker'],'falsifiers':['valid safety counterexample','equivalence to simple portfolio within pre-fixed practical margin','benefit only with extra provider capability'],'status':'NOT_TESTED','results':None},
{'id':'H-AB','kind':'primary_empirical','population':'all pre-fixed D_AB cases, not post-selected feedback-active survivors','iv':'B-to-A decision-relevant feedback enabled','baseline':'same A/B with feedback disabled; retain task guidance, safety, cache and stopping rules','outcomes':['mean_C_Q_ratio','lawful_completion_rate_difference','approval_count'],'null':'R_AB >= 0.85 OR delta_U_AB <= -0.05','alternative':'R_AB < 0.85 AND delta_U_AB > -0.05','support':'adjusted cost and utility limits passed without relaxed obligations','additional_reference':'R-J same-objective joint belief planning; small exact optimum is not to be beaten','falsifiers':['valid safety counterexample','no material marginal benefit','benefit explained by extra permissions or weaker legitimate functionality'],'status':'NOT_TESTED','results':None},
{'id':'H-M','kind':'secondary_mechanism','population':'pre-labelled synthetic side-effect fixtures only','design':'2x2 feedback on/off by obligation tracking on/off; same instantaneous approval checks','null':'obligation tracking does not reduce strict unresolved obligations','alternative':'obligation tracking reduces the unresolved obligation rate','outcomes':['paired_unresolved_obligation_rate_difference','interaction','lawful_completion'],'baseline_role':'negative control only; not a paper reproduction or product-vulnerability claim','status':'NOT_TESTED','results':None},
{'id':'H-D','kind':'optional_exploratory','population':'observable drift; identical notification and polling rights','null':'no unaffected-task continuity gain or stale assurance used after valid conflict observation','alternative':'localized withdrawal lowers unaffected-task interruption without stale-authority acceptance after observation','outcomes':['unaffected_task_interruption_difference','post-observation_stale_acceptance','change_to_observation_latency'],'exclusion':'unobservable latent drift is outside detection guarantee, not silently excluded from latency reporting','status':'NOT_TESTED','results':None}
]
registry={'date':'2026-11-02','timezone':'Asia/Shanghai','base_document':str(BASE),'base_sha256':source_hash,'report':str(OUT),'design':shared,'novelty_verdict':{'general_new_mechanism':'NOT_SUPPORTED','A1':'ALGORITHM_LEVEL_NOVELTY_NOT_ESTABLISHED','B1':'ALGORITHM_LEVEL_NOVELTY_NOT_ESTABLISHED','AB1':'CONDITIONAL_COMPOSITION_CANDIDATE','unresolved_prior':'RAG full text not obtained'},'required_specification_repairs':['winning-region membership does not force progress','pairwise counterexamples are not complete for multi-world unsatisfiability','OOD marker does not certify unseen behavior'],'hypotheses':hypotheses,'sources':sources}
(TASK/'研究假设与创新性核验登记表.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
bib=[]
for s in sources:
 a=s['authors'].replace('; ',' and ').replace(', ',' and ').replace(' et al.',' and others')
 f={'author':a,'title':s['title'],'year':re.search(r'\d{4}',s['year']).group(),'url':s['url'],'note':s['venue']+'; accessed 2026-11-02; '+s['read']}
 if s.get('doi'):f['doi']=s['doi']
 bib.append('@misc{'+s['id']+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in f.items())+'\n}')
(TASK/'核验参考文献.bib').write_text('\n\n'.join(bib),encoding='utf-8')
print(json.dumps({'output':str(OUT),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'sources':len(sources),'equations':len(doc.element.xpath('.//m:oMath')),'base_unchanged':True},ensure_ascii=False))
