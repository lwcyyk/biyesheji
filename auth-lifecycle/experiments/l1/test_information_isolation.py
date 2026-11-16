"""Synthetic regression: scorer-private rejection must not steer the method."""
import json
from pathlib import Path
import sys
import tempfile
import shutil
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"));sys.path.insert(0,str(ROOT/"scripts"))
import l1_pilot
import analyze_pilot
from auth_lifecycle.experiment.journal import read_verified


class FakeProvider:
    name="casdoor";version="SYNTHETIC_UNIT_ONLY";transport=None
    http=SimpleNamespace(count=0);admin_http=SimpleNamespace(count=0)
    def admin_login(self):pass
    def create_actor(self,name):return {"id":"unit-subject","name":name}
    def issue(self,actor):return self.transport("configure",lambda:{"http":200,"body":{"access_token":"unit-access","refresh_token":"unit-refresh"}})
    def root_stop(self,actor):return {"http":200,"body":{}}
    def remove_actor(self,actor):pass


class FakeWitness:
    http=SimpleNamespace(count=0)
    def __init__(self,*args):pass
    def signed_access(self,*args,**kwargs):return True
    def native_unit(self,*args):return "unit-native-record"


class FakeResource:
    dispatched=False
    def __init__(self,*args):pass
    def bind(self,mapping):pass
    def evaluate(self,*args):return False  # privileged adverse observation
    def close_task(self,task):
        FakeResource.dispatched=True;return {"http":200,"body":{}}
    def shutdown(self):pass


def main():
    result={"status":"PASS_SYNTHETIC_ISOLATION_TEST","native_used":False}
    with tempfile.TemporaryDirectory() as folder:
        out=Path(folder);(out/"models").mkdir();(out/"events").mkdir()
        meta={"run_id":"information-isolation-unit","phase":"SYNTHETIC_UNIT_ONLY","native_used":False,"Q_cap":64,"G_cap":8,"approval_cap":8,
              "fault":"none","goal":"local","hypothesis":"H-A","method":"A1","timeout_seconds":30}
        with patch.object(l1_pilot,"Witness",FakeWitness),patch.object(l1_pilot,"Resource",FakeResource):
            row=l1_pilot.execute(FakeProvider(),meta,{"mode":"online","query_client":0},out)
        events=read_verified(out/row["event_file"])
        end=next(e["payload"]["status"] for e in events if e["event"]=="method_end")
        assert FakeResource.dispatched and end=="COMPLETED","method improperly used scorer-private initial result"
        assert row["metrics"]["U"]==0 and row["metrics"]["FA"]==1,"independent scorer failed to reject false completion"
        result.update(method_dispatched_despite_private_adverse_observation=True,method_end=end,independent_U=0,independent_FA=1)
    source=ROOT/"results/experiments/pilot02"
    if source.exists():
        schedule=json.loads((source/"scheduled_pairs.json").read_text());first=schedule[0]
        records=[json.loads(x) for x in (source/"runs.jsonl").read_text(encoding="utf-8").splitlines()]
        retained=next(x for x in records if x["metadata"]["pair_id"]==first["pair_id"])
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);(target/"events").mkdir()
            (target/"scheduled_pairs.json").write_text(json.dumps([first]),encoding="utf-8")
            shutil.copyfile(source/"plan.json",target/"plan.json")
            shutil.copyfile(source/retained["event_file"],target/retained["event_file"])
            (target/"runs.jsonl").write_text(json.dumps(retained)+"\n",encoding="utf-8")
            rebuilt,missing=analyze_pilot.load(target)
            assert len(rebuilt)==2 and len(missing)==1
            placeholder=next(x for x in rebuilt if x.get("analysis_placeholder_not_execution"))
            assert placeholder["metrics"]["U"]==0 and placeholder["metrics"]["C_Q"]==65
        result["missing_arm_retained_with_labeled_penalty"]=True
    print(json.dumps(result))


if __name__=="__main__":main()
