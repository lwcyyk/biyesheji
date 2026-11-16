from pathlib import Path
import json,re
root=Path(r"D:\毕业设计\研究\ARS_V2深化研究_2026-10-16")
for name in ["web_retrievals.json","增补核验记录.json"]:
    p=root/"检索记录"/name
    data=json.loads(p.read_text(encoding="utf-8"))
    if data.get("scope")=="SEARCH_RETURN_METADATA_NOT_FULLTEXT_ARCHIVE":
        continue
    cleaned={}
    for key,result in data["retrievals"].items():
        text="\n".join(c.get("text","") for c in result.get("content",[]) if c.get("type")=="text")
        records=[]
        for part in re.split(r"\n-{10,}\n",text):
            m=re.match(r"([^\n]*?) \((https?://[^\n]+?)\)\n",part)
            if not m:
                continue
            records.append({
                "title":m[1],
                "url":m[2],
                "access_date":"2026-10-16",
                "availability":"FETCH_LIMITED" if re.search(r"Failed to fetch|not accessible|403|JavaScript is disabled|not a robot",part,re.I) else "SOURCE_RETURNED",
                "screening_note":"Returned candidate metadata only; inclusion and permitted support are recorded separately in the source registry."
            })
        cleaned[key]={"tool_is_error":result.get("isError",False),"returned_source_metadata":records}
    out={"date":"2026-10-16","provider":"Codex web search connector","scope":"SEARCH_RETURN_METADATA_NOT_FULLTEXT_ARCHIVE","note":"保留工具返回来源的题名、URL与取得状态，不转存全文或长段摘录。文献用途及阅读范围见证据登记表。","retrievals":cleaned}
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Retrieval metadata saved; no fulltext snapshots included.")

