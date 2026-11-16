"""整理输出与档案完整性检查。此工具不执行协议、攻防、模型或性能实验。"""
from pathlib import Path
import csv, hashlib, json, re, zipfile
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "证据"
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat()
def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def sha(data):
    return hashlib.sha256(data).hexdigest()
def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})

sources = read_json(EVIDENCE / "文献登记表.json")["sources"]
claims = read_json(EVIDENCE / "主张核验表.json")["claims"]
traces = read_json(EVIDENCE / "增补轨迹设计.json")["traces"]
cards = read_json(EVIDENCE / "研究点注册表_r2.json")["cards"]
write_csv(EVIDENCE / "文献矩阵.csv", sources, list(sources[0]))
write_csv(EVIDENCE / "主张核验表.csv", claims, list(claims[0]))
write_csv(EVIDENCE / "增补实验矩阵.csv", traces, ["id", "extends", "rp", "claims", "title", "baselines", "expected_policy_outcome", "metrics", "falsification", "execution_status"])

mapping = {
"L04":"S02","L05":"S03","L06":"S04","L08":"S28","L09":"S27",
"L11":"S08","L12":"S09","L13":"S10","L16":"S22","L17":"S13",
"L19":"S21","L20":"S26","L21":"S24","L22":"S25","L23":"S20"
}
reasons = {
"L01":"CoSi作历史机制；本轮交集推导不声称是新共签方法，未重读原文",
"L02":"CONIKS作既有背景；本轮直接核验EthIKS/Parakeet，不替CONIKS标本轮已读",
"L03":"SEEMless作历史背景，暂未重读",
"L07":"CertLedger未重读；由直接核验的EthIKS/Catena支持有界先例结论",
"L10":"HotStuff未重读；B5仍为待选具体实现，未声称已部署或验证",
"L14":"ERC-4337为执行基础设施，非本轮核心验证问题，未重读",
"L15":"ERC-6492为未部署账户适配，暂不扩张主线，未重读",
"L18":"zkLogin不承担状态恢复或撤销核心结论，未重读",
"L24":"Google KT设计未重读，不声称已验证该代码",
"L25":"WhatsApp工程报告未重读；不使用其部署性能",
"L26":"witness开源程序未作本轮代码审计，不声称原子性实现已通过",
"L27":"CAIP-122未重读；本轮限EVM/SIWE与合作RP",
"L28":"泛Bitcoin匿名化以历史背景保留；本轮改用S17/S18直接钱包/RPC来源",
"L29":"一般PoS文件未重读；本轮以S08分析引导信任，不发布最终性性能"
}
inherited_path = ROOT / "来源展开" / "V2-第二阶段完整材料包" / "扩展研究V2_第二阶段_文献矩阵_2026-10-15.csv"
with inherited_path.open(encoding="utf-8-sig", newline="") as fh:
    inherited = list(csv.DictReader(fh))
audit=[]
source_index={s["id"]:s for s in sources}
for row in inherited:
    old=row["ref_id"]
    target=mapping.get(old)
    item=source_index.get(target)
    audit.append({
        "old_id":old,"title":row["title"],"old_url":row["primary_url"],
        "current_id":target or "",
        "current_treatment":("REVERIFIED_BOUNDED" if item["included_core"] else "LIMITED_CANDIDATE") if item else "HISTORICAL_NOT_RECHECKED",
        "reason":item["inheritance"]+"；"+item["read_scope"] if item else reasons[old],
        "core_conclusion_allowed":bool(item and item["included_core"])
    })
write_csv(EVIDENCE / "V2原29条文献继承审查.csv", audit, list(audit[0]))

# Original files remain read-only to this tool.
input_files=[p for p in ROOT.parent.iterdir() if p.is_file() and not p.name.startswith("ARS_V2")]
outer_zip=ROOT.parent.parent / "研究.zip"
if outer_zip.exists():
    input_files.append(outer_zip)
input_inventory=[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())} for p in sorted(input_files)]
write_json(EVIDENCE / "输入清单与哈希.json", {"created_at":STAMP,"scope":"original_input_snapshot_only","files":input_inventory})
archive_checks=[]
for p in input_files:
    if p.suffix.lower() != ".zip" or p.name=="研究.zip":
        continue
    with zipfile.ZipFile(p) as archive:
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            dst=ROOT / "来源展开" / p.stem / entry.filename
            if not dst.exists():
                raise AssertionError("Missing extracted entry: "+str(dst))
            original=archive.read(entry)
            actual=dst.read_bytes()
            assert original==actual, "Extraction mismatch: "+str(dst)
            archive_checks.append({"archive":p.name,"entry":entry.filename,"sha256":sha(actual)})
write_json(EVIDENCE / "展开来源完整性.json", {"status":"BYTE_MATCH","entry_count":len(archive_checks),"entries":archive_checks})

# Static validation only. No expected result is converted to an observed result.
for p in ROOT.rglob("*.json"):
    read_json(p)
assert len(sources)==28 and sum(s["included_core"] for s in sources)==26
assert len(inherited)==29 and len(audit)==29
assert len(claims)==16 and len({c["claim_id"] for c in claims})==16
assert len(traces)==13 and all(t["execution_status"]=="NOT_RUN" for t in traces)
assert len(cards)==4 and all(not t["frozen"] and not t["author_confirmed"] for t in cards)
assert {t["id"] for t in cards}=={"RP-2026-005","RP-2026-006","RP-2026-007","RP-2026-008"}
assert {c["claim_id"] for c in claims}.issuperset({cid for t in traces for cid in t["claims"]})
report=(ROOT / "03_综合研究报告.md").read_text(encoding="utf-8")
refs=list(re.finditer(r"<!--ref:([^>]+)-->",report))
known={s["citation_key"] for s in sources if s["included_core"]}
for match in refs:
    assert match[1] in known, "Unknown or limited core reference"
    assert re.match(r"\s*<!--anchor:(quote|page|section|paragraph):[^>]+-->",report[match.end():]), "Missing locator"
assert "<!--anchor:none:" not in report
assert "\ufffd" not in report
for cid in ["005","006","007","008"]:
    assert "RP-2026-"+cid in (ROOT / "06_研究点修订_r2.md").read_text(encoding="utf-8")
for p in ROOT.glob("*.md"):
    assert "\ufffd" not in p.read_text(encoding="utf-8"), "Encoding replacement in "+p.name
validation={
    "checked_at":STAMP,"scope":"DOCUMENT_AND_DATA_STRUCTURE_ONLY",
    "protocol_experiment_execution":"NOT_RUN",
    "core_sources":26,"limited_sources":2,"inherited_rows_accounted_for":29,
    "atomic_claims":16,"symbolic_trace_designs":13,"proposed_cards":4,
    "frozen_count":0,"report_characters_including_references":len(report),
    "report_ref_occurrences":len(refs),"report_unique_cited_sources":len({m[1] for m in refs}),
    "adjacent_locators":"PRESENT","json_parse":"PASS",
    "source_archive_byte_match_count":len(archive_checks),
    "canonical_ars_schema_validation":"NOT_RUN",
    "citation_semantic_validation":"MANUAL_BOUNDED_READING_NOT_THIS_SCRIPT",
    "independent_review":"NOT_PERFORMED",
    "status":"PASS"
}
write_json(EVIDENCE / "文档交付校验.json",validation)
files=[]
manifest=EVIDENCE / "交付文件清单.json"
for p in sorted(ROOT.rglob("*")):
    if p.is_file() and p!=manifest and "__pycache__" not in p.parts:
        files.append({"path":p.relative_to(ROOT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p.read_bytes())})
write_json(manifest,{"created_at":STAMP,"manifest_self_excluded":True,"files":files})
print(json.dumps(validation,ensure_ascii=False,indent=2))

