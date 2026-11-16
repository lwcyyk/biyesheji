"""从原研究包转换为简体中文，保留原有链接、编号、数值及文件路径。
依赖 opencc-python-reimplemented==0.1.7。此工具不运行研究实验。
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone, timedelta
import hashlib, json, re, sys, tempfile, zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE_ZIP=ROOT.parent / "ARS_V2深化研究_2026-10-16_材料包.zip"
sys.path.insert(0,str(Path(tempfile.gettempdir())/"codex-v2-chinese-converter-20261016"))
from opencc import OpenCC
converter=OpenCC("t2s")
protected=re.compile(r"<!--[\s\S]*?-->|https?://[^\s<>\)\]]+|(?<=\]\()[^\)\r\n]+(?=\))|[^\s\"'<>]{1,180}\.(?:md|json|csv|py|zip)\b")
terms=[("资讯","信息"),("程式码","代码"),("程式","程序"),("软体","软件"),("硬体","硬件"),
       ("伺服器","服务器"),("资料库","数据库"),("位元组","字节"),("杂凑","哈希"),
       ("伫列","队列"),("网际网络","互联网"),("连线","连接"),("讯号","信号"),
       ("栏位","字段"),("预设","默认"),("唯读","只读"),("实作","实现"),
       ("金钥","密钥"),("登入","登录"),("介面","接口"),("专案","项目"),
       ("记忆体","内存"),("帐户","账户"),("帐号","账号"),("透过","通过"),("纪录","记录"),("模组","模块")]
def convert(value):
    saved=[]
    def protect(match):
        saved.append(match.group(0))
        return "\x00"+str(len(saved)-1)+"\x00"
    value=protected.sub(protect,value)
    value=converter.convert(value)
    for old,new in terms:
        value=value.replace(old,new)
    value=value.replace("「","“").replace("」","”").replace("『","‘").replace("』","’")
    return re.sub(r"\x00(\d+)\x00",lambda m:saved[int(m[1])],value)
def shape(value):
    if isinstance(value,dict):
        return {k:shape(v) for k,v in value.items()}
    if isinstance(value,list):
        return [shape(v) for v in value]
    return {"string":True} if isinstance(value,str) else value
numbers=re.compile(r"\d+(?:[.-]\d+)*")
skip={"交付文件清单.json","文档交付校验.json","输入清单与哈希.json","展开来源完整性.json","转换为简体.py"}
changes=[]
with zipfile.ZipFile(SOURCE_ZIP) as z:
    for entry in z.infolist():
        parts=PurePosixPath(entry.filename).parts
        if entry.is_dir() or not parts or parts[0]!=ROOT.name:
            continue
        relative=Path(*parts[1:])
        if "来源展开" in relative.parts or relative.suffix.lower() not in {".md",".json",".csv",".py"} or relative.name in skip:
            continue
        path=(ROOT/relative).resolve()
        assert ROOT in path.parents, "Output path outside the research folder"
        raw=z.read(entry)
        before=raw.decode("utf-8-sig")
        after=convert(before)
        assert numbers.findall(before)==numbers.findall(after), str(path)+": number changed"
        assert protected.findall(before)==protected.findall(after), str(path)+": link, citation or path changed"
        if path.suffix==".json":
            assert shape(json.loads(before))==shape(json.loads(after)),str(path)+": JSON structure changed"
        if path.suffix==".md":
            plain=protected.sub("",after)
            assert converter.convert(plain)==plain,str(path)+": traditional characters remain"
            assert len(before.splitlines())==len(after.splitlines()),str(path)+": lines changed"
            assert "内核" not in after,str(path)+": avoid incorrect regional term conversion"
        result=(b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"")+after.encode("utf-8")
        path.write_bytes(result)
        if before!=after:
            changes.append({"path":relative.as_posix(),"before_sha256":hashlib.sha256(raw).hexdigest(),"after_sha256":hashlib.sha256(result).hexdigest()})
report={"converted_at":datetime.now(timezone(timedelta(hours=8))).isoformat(),"language":"zh-CN",
        "scope":"本轮生成的7份报告、研究卡及配套中文说明；历史来源原件不变",
        "converter":"OpenCC t2s 0.1.7 with explicitly reviewed mainland terminology",
        "markdown_reports":len(list(ROOT.glob("*.md"))),"changed_files":changes,
        "protected_elements":["URLs","Markdown link targets","citation comments","numeric tokens","file paths","JSON keys and non-string values"],
        "research_claim_strength_changed":False,"experiment_execution":"NOT_RUN"}
(ROOT/"证据"/"简体转换记录.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"language":"zh-CN","markdown_reports":7,"changed_files":len(changes),"protected_elements":"PASS"},ensure_ascii=False))

