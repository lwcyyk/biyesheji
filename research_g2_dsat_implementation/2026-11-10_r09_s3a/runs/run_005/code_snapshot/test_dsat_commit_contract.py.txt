"""R09 contract cases and independent SQL/risk test harness. Offline only."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import unittest
import uuid

from auth_lifecycle.online_state.dsat_commit_types import (
    Actor, CommitError, DB_ROOT, Limits, MAX_REVISION, PROJECT, RUN_ROOT,
    canonical, clone, digest, legacy_digest, obligation, O_digest, packet_digest,
    pending_source, Proposal, seal, strict_load, validate_world,
)
from auth_lifecycle.online_state.dsat_commit import FrozenRegistry, PrepareDSatCommit, artifact_path
from auth_lifecycle.online_state.dsat_synthetic_store import SyntheticStore


CONFIG = {}
RESULTS = []


def configure(registry, run_dir, ready_path, matrix):
    CONFIG.update(registry=registry, run_dir=run_dir, ready=ready_path, matrix=matrix)


def audit(store):
    """Read actual tables independently of the production transition/coverage code."""
    store._ticket()
    conn = sqlite3.connect(store.path.as_uri() + "?mode=rw", uri=True)
    try:
        return {name: [list(row) for row in conn.execute("SELECT * FROM " + name + " ORDER BY 1,2")]
                for name in ("s3a_state", "s3a_events", "s3a_proposals", "s3a_objects")}
    finally:
        conn.close()


def audit_hash(tables):
    return hashlib.sha256(repr(tables).encode("utf-8")).hexdigest()


def risks(world):
    # The oracle expands retained old descriptors itself, without coverage helpers.
    result = set()
    for item in world["dsat"]["O"]:
        descriptor = item["descriptor"]
        result.add(json.dumps(descriptor, sort_keys=True))
        retained = item["retained"]
        while retained is not None:
            result.add(json.dumps(retained["descriptor"], sort_keys=True))
            retained = retained["retained"]
    return result


class Harness(unittest.TestCase):
    def setUp(self):
        self.case_id = self._testMethodName.split("_")[1]
        self.info = next(x for x in CONFIG["matrix"]["cases"] if x["id"] == self.case_id)
        self.registry = CONFIG["registry"]
        self.started = time.perf_counter_ns()
        self.subresults = []
        self.stores = []
        self.workers = []
        self.evidence = []
        self.prepare_ns = []

    def tearDown(self):
        for worker in self.workers:
            if worker["process"].poll() is None:
                worker["process"].kill()
                self.finish(worker, killed=True)
        dbs = []
        for store in self.stores:
            try:
                snapshot = store.recover()
                self.assertFalse(snapshot["world"].get("global_complete", False))
                tables = audit(store)
                dbs.append({"path": str(store.path), "a": snapshot["a"],
                            "o": snapshot["world"]["dsat"]["obligation_revision"],
                            "O": snapshot["world"]["dsat"]["O"], "O_digest": O_digest(snapshot["world"]["dsat"]["O"]),
                            "four_table_digest": audit_hash(tables),
                            "receipts": [strict_load(bytes(x[5])) for x in tables["s3a_proposals"]],
                            "objects": len(tables["s3a_objects"]), "events": len(tables["s3a_events"])})
            except (CommitError, sqlite3.DatabaseError) as exc:
                dbs.append({"path": str(store.path), "intentional_recovery_refusal": str(exc)})
        RESULTS.append({"id": self.case_id, "elapsed_ns": time.perf_counter_ns()-self.started,
                        "subassertions": self.subresults, "evidence": self.evidence, "databases": dbs,
                        "metrics": [x for store in self.stores for x in store.metrics], "prepare_ns": self.prepare_ns})

    def new(self, seed="A01", limits=Limits(), a=120, o=0):
        name = seed if seed.startswith("VAR_") else "AUTO_" + seed + "_A"
        token = uuid.uuid4().hex
        store = SyntheticStore(DB_ROOT / ("dsat_s3a_"+self.case_id+"_"+token+".sqlite3"), limits)
        store.create(self.registry.seed(name, "syn:"+self.case_id+":"+token, a, o))
        self.stores.append(store)
        return store

    def prepare(self, store, label=None, level="MATH_ARCHIVE"):
        start = time.perf_counter_ns()
        body = PrepareDSatCommit(store.read(), self.registry, label or "p:"+uuid.uuid4().hex, level=level)
        self.prepare_ns.append(time.perf_counter_ns()-start)
        return body

    def submit(self, store, body=None, actor=Actor("syn:manager"), now=100, hook=None):
        result = store.commit(body or self.prepare(store), actor, self.registry, now, hook)
        self.evidence.append({"operation": "submit", "database": str(store.path), "result": result})
        if result["receipt"] is not None:
            self.assertEqual(result["receipt"]["native_admission"], "SOURCE_OR_REFINEMENT_GAP")
            self.assertIs(result["receipt"]["global_complete"], False)
        return result

    def accepted(self, result):
        self.assertTrue(result["status"].startswith("COMMITTED_"), result)

    def rejected_unchanged(self, store, body, reason, actor=Actor("syn:manager"), **kwargs):
        before = audit(store)
        result = self.submit(store, body, actor, **kwargs)
        self.assertEqual(result["status"], reason)
        after = audit(store)
        for table in ("s3a_state", "s3a_events", "s3a_objects"):
            self.assertEqual(before[table], after[table], table)
        self.assertEqual(len(after["s3a_proposals"]), len(before["s3a_proposals"]) + (1 if result["receipt"] else 0))
        return result

    def sub(self, index, action):
        description = self.info["mandatory_subcases"][index-1]
        result = {"index": index, "description": description, "status": "FAIL"}
        self.subresults.append(result)
        action()
        result["status"] = "PASS"

    def spawn(self, store, action="submit", body=None, stage=None, event=None, actor="syn:manager", now=100):
        self.assertLess(sum(x["process"].poll() is None for x in self.workers), 2)
        folder = artifact_path(CONFIG["run_dir"] / ("worker_"+uuid.uuid4().hex)); folder.mkdir()
        conf = {"folder": str(folder), "database": str(store.path), "action": action,
                "body": body, "stage": stage, "event": event, "actor": actor, "now": now,
                "ready_registry": str(CONFIG["ready"])}
        path = folder / "config.json"; path.write_bytes(canonical(conf))
        cmd = [sys.executable, "-B", str(PROJECT/"scripts/run_dsat_s3a_tests.py"), "--worker", str(path)]
        process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        worker = {"process": process, "folder": folder, "command": cmd, "pid": process.pid,
                  "creation_ns": time.perf_counter_ns(), "token": folder.name, "config": conf}
        self.workers.append(worker)
        self.wait(worker, "prepared.json")
        return worker

    def wait(self, worker, name):
        path = worker["folder"]/name; deadline = time.monotonic()+10
        while not path.exists():
            if worker["process"].poll() is not None:
                stdout, stderr = worker["process"].communicate()
                self.fail("worker exited before " + name + ": " + stderr.decode("utf-8", "replace"))
            if time.monotonic() > deadline:
                worker["process"].kill()
                self.fail("owned worker deadline: " + name)
            time.sleep(.01)
        return strict_load(path.read_bytes())

    def release(self, worker, name="go"):
        (worker["folder"]/name).write_bytes(b"go")

    def finish(self, worker, killed=False):
        stdout, stderr = worker["process"].communicate(timeout=10)
        evidence = {k: worker[k] for k in ("command", "pid", "creation_ns", "token")}
        evidence.update(killed=killed, exit_code=worker["process"].returncode,
                        stdout=stdout.decode("utf-8", "replace"), stderr=stderr.decode("utf-8", "replace"))
        for marker in ("prepared.json", "hook.json", "output.json"):
            path = worker["folder"]/marker
            if path.exists():
                evidence[marker] = strict_load(path.read_bytes())
        self.evidence.append(evidence)
        if not killed:
            self.assertEqual(worker["process"].returncode, 0, evidence)
            return evidence["output.json"]["result"]
        return evidence

    def pair(self, store, first, second):
        w1 = self.spawn(store, **first); w2 = self.spawn(store, **second)
        self.assertEqual(self.wait(w1, "prepared.json")["a"], self.wait(w2, "prepared.json")["a"])
        self.release(w1); r1 = self.finish(w1)
        self.release(w2); r2 = self.finish(w2)
        return r1, r2

    def crash(self, store, body, stage, action="submit"):
        before = audit(store)
        worker = self.spawn(store, action=action, body=body, stage=stage)
        self.release(worker); self.wait(worker, "hook.json")
        worker["process"].kill()  # Held Popen handle; never terminate by a reused PID.
        self.finish(worker, killed=True)
        snapshot = store.recover()
        return before, audit(store), snapshot

    def event(self, kind="O_only", add=None, **kwargs):
        return {"id": "ev:"+uuid.uuid4().hex, "kind": kind, "add": add or [], **kwargs}

    def raw(self, ident, kind=None):
        return {"id": ident, "kind": kind or ident.split(":")[0], "refs": [ident.split(":",1)[1]], "strict": True}


class ContractCases(Harness):
    def test_T004_math_archive(self):
        s = self.new(); before = s.read(); result = self.submit(s)
        self.accepted(result)
        after = s.recover(); self.assertEqual(after["a"], 121)
        self.assertEqual(after["world"]["dsat"]["obligation_revision"], 0)
        self.assertEqual(risks(before["world"]), risks(after["world"]))

    def test_T005_conditional(self):
        s = self.new(); result = self.submit(s, self.prepare(s, level="CONDITIONAL_ARCHIVE"))
        self.assertEqual(result["status"], "COMMITTED_CONDITIONAL_RECORD")
        self.assertEqual(len(s.recover()["world"]["dsat"]["O"]), 5)

    def test_T010_external_async(self):
        s = self.new(); p = self.prepare(s)
        _, r = self.pair(s, {"action":"external", "event":{"AS_insert":True}}, {"body":p})
        self.accepted(r); self.assertFalse(r["receipt"]["global_complete"])
        self.assertEqual(s.read()["a"], 121)

    def test_T012_permission_expiry(self):
        s = self.new(); p = self.prepare(s)
        _, r = self.pair(s, {"action":"event", "event":self.event("permission", manager_write=False, source_changed=False)}, {"body":p})
        self.assertEqual(r["status"], "REJECT_UNAUTHORIZED")
        s2 = self.new(); original = self.prepare(s2); accepted = self.submit(s2, original)
        s2.domain_event(self.event("permission", manager_write=False, source_changed=False))
        self.assertEqual(self.submit(s2, original)["receipt"], accepted["receipt"])
        s3 = self.new(); p3 = self.prepare(s3); p3["dependency_policy"]["require_current"] = True
        self.rejected_unchanged(s3, seal(p3), "STALE_EVIDENCE", now=101)
        self.accepted(self.submit(s3, now=101))

    def test_T014_guard_to_commit(self):
        s = self.new(); p = self.prepare(s)
        w1 = self.spawn(s, body=p, stage="before_commit"); w2 = self.spawn(s, action="external", event={"clock":101})
        self.release(w1); self.wait(w1, "hook.json")
        self.release(w2); self.finish(w2)
        self.release(w1, "go_hook"); result = self.finish(w1)
        self.accepted(result); self.assertEqual(result["receipt"]["current_use"], "INPUT_TIME_HISTORY_ONLY")

    def test_T016_unknown(self):
        s = self.new("A02"); before = s.read()["world"]
        self.accepted(self.submit(s)); after = s.recover()["world"]
        self.assertTrue(risks(before) <= risks(after))
        self.assertTrue({"settle:i1","settle:i2","settle:j"} <= {x["id"] for x in after["dsat"]["O"]})

    def test_T017_preserving_transform(self):
        s = self.new(); before = s.read()["world"]; old = next(x for x in before["dsat"]["O"] if x["id"]=="settle:i1")
        p = self.prepare(s, level="COVER_PRESERVING_MODEL_TRANSFORM")
        p["obligations_delta"]["replace"] = [{"old_id":old["id"],"pending":pending_source(old)}]
        p["obligations_delta"]["add"].append(obligation(self.raw("close:u"), digest("scope",before["scope"])))
        result = self.submit(s, seal(p)); self.accepted(result)
        after = s.recover()["world"]; self.assertTrue(risks(before) <= risks(after))
        item = next(x for x in after["dsat"]["O"] if x["kind"]=="pending_source")
        self.assertEqual(item["retained"], old); self.assertEqual(item["origin"], old["origin"])

    def test_T018_false_cover(self):
        for fake in (False, True):
            s=self.new(); p=self.prepare(s); old=s.read()["world"]["dsat"]["O"][1]; pending=pending_source(old)
            pending["holds"]=[] if not fake else pending["holds"]; pending["retained"]=None
            p["obligations_delta"]["replace"]=[{"old_id":old["id"],"pending":pending}]
            self.rejected_unchanged(s,seal(p),"REJECTED_COVERAGE")

    def test_T019_saturated_not_closed(self):
        s=self.new("VAR_MISSING_D_A"); p=self.prepare(s,level="CONDITIONAL_ARCHIVE")
        self.sub(1,lambda:self.assertEqual((p["proof"]["claims"]["R_T"],p["proof"]["claims"]["H_T"]),(0,1)))
        old=risks(s.read()["world"]);self.accepted(self.submit(s,p))
        self.sub(2,lambda:self.assertTrue(old <= risks(s.recover()["world"])))

    def test_T020_A24(self):
        s=self.new("A24"); p=self.prepare(s,level="CONDITIONAL_ARCHIVE"); before=s.read()["world"]
        self.accepted(self.submit(s,p));after=s.recover()["world"]
        def four():
            self.assertEqual((len(before["dsat"]["O"]),len(p["proof"]["bindings"]["O_before"]),len(after["dsat"]["O"])),(5,6,6))
            self.assertNotEqual(p["base_O_digest"],p["proof_context_O_digest"])
            self.assertEqual(p["projection_O_digest"],p["proof_context_O_digest"])
        self.sub(1,four)
        self.sub(2,lambda:self.assertTrue({"await_terminal:i1","window:account-paper"} <= {x["id"] for x in after["dsat"]["O"]}))
        old=next(x for x in after["dsat"]["O"] if x["id"]=="settle:i1");p2=self.prepare(s,level="COVER_PRESERVING_MODEL_TRANSFORM")
        p2["obligations_delta"]["replace"]=[{"old_id":old["id"],"pending":pending_source(old)}]
        def retained():
            self.accepted(self.submit(s,seal(p2))); self.assertTrue(risks(after)<=risks(s.recover()["world"]))
        self.sub(3,retained)

    def test_T022_new_frontier(self):
        s=self.new("A22");p=self.prepare(s);self.accepted(self.submit(s,p));old=self.prepare(s)
        s.domain_event(self.event("third_grant",[self.raw("frontier:new")]))
        self.rejected_unchanged(s,old,"REJECTED_REVISION")
        self.assertIn("frontier:new",{x["id"] for x in s.recover()["world"]["dsat"]["O"]})

    def test_T038_bad_packet_and_parser(self):
        s=self.new();p=self.prepare(s);bad=clone(p["proof"]);first=next(iter(bad["math_input"]["c"]))
        bad["math_input"]["c"][first]+=1;bad["packet_digest"]=packet_digest(bad)
        def mathematical():
            rec=self.registry.check_untrusted(bad);self.assertFalse(rec["accepted"])
            q=clone(p);q["proof"]=bad;self.rejected_unchanged(s,seal(q),"REJECTED_PROOF_BINDING")
            for variant in ("flow","digest"):
                q=self.prepare(s);tampered=clone(q["proof"])
                if variant=="flow":tampered["proof"]["m"]["flow"][0][2]+=1
                else:tampered["digests"]["math_input_digest"]="0"*64
                tampered["packet_digest"]=packet_digest(tampered)
                self.assertFalse(self.registry.check_untrusted(tampered)["accepted"])
                q["proof"]=tampered;self.rejected_unchanged(s,seal(q),"REJECTED_PROOF_BINDING")
            q=self.prepare(s);q["proof"]={}
            self.rejected_unchanged(s,seal(q),"REJECTED_PROOF_BINDING")
        self.sub(1,mathematical)
        def invalid_json():
            for data in [b'{"a":1,"a":2}',b'{"a":1.5}',b'{"a":NaN}',b'{"a":"\\ud800"}']:
                with self.assertRaises(CommitError):strict_load(data)
            with self.assertRaises(CommitError):canonical(self._deep())
            q=clone(p);q["unknown"]=True;self.rejected_unchanged(s,seal(q),"INVALID_INPUT")
        self.sub(2,invalid_json)
        def sizes():
            q=clone(p);q["proof"]["padding"]="x"*4194304;self.rejected_unchanged(s,seal(q),"UNKNOWN_RESOURCE_LIMIT")
            self.rejected_unchanged(s,b"x"*8388609,"UNKNOWN_RESOURCE_LIMIT")
        self.sub(3,sizes)
        def forged():
            q=clone(p);q["math_accepted"]=True;self.rejected_unchanged(s,seal(q),"INVALID_INPUT")
            q=self.prepare(s);q["checker_source_digest"]="0"*64;self.rejected_unchanged(s,seal(q),"REJECTED_PROOF_BINDING")
        self.sub(4,forged)
        self.sub(5,lambda:self.assertEqual(self.registry.check_untrusted(p["proof"],timeout=.00001)["result"]["status"],"UNKNOWN_RESOURCE_LIMIT"))

    def _deep(self):
        value=0
        for _ in range(34):value=[value]
        return value

    def test_T040_forged_identity(self):
        s=self.new();p=self.prepare(s);p["actor"]="syn:forged"
        self.rejected_unchanged(s,seal(p),"REJECT_UNAUTHORIZED")
        p=self.prepare(s);p["projection_digest"]="0"*64
        self.rejected_unchanged(s,seal(p),"REJECTED_PROOF_BINDING")

    def test_T041_cross_origin(self):
        s=self.new("A08");p=self.prepare(s);p["obligations_delta"]["add"][0]["origin"]={"refs":["V"]}
        self.rejected_unchanged(s,seal(p),"REJECTED_ORIGIN_SCOPE")

    def test_T042_empty_F(self):
        s=self.new("A19");p=self.prepare(s);old=risks(s.read()["world"])
        p["obligations_delta"]["add"].append(obligation({"id":"investigate:conflict","kind":"investigate","refs":[],"strict":True},digest("scope",s.read()["world"]["scope"])))
        result=self.submit(s,seal(p));self.assertEqual(result["status"],"COMMITTED_CONFLICT_RECORD")
        self.assertTrue(old <= risks(s.recover()["world"]))

    def test_T043_point_false(self):
        s=self.new("A16");p=self.prepare(s);p["requested_level"]="NATIVE_CLOSED"
        self.rejected_unchanged(s,seal(p),"INVALID_INPUT")
        result=self.submit(s);self.accepted(result);self.assertFalse(result["receipt"]["global_complete"])

    def test_T044_external_no_fence(self):
        s=self.new();before=risks(s.read()["world"]);self.accepted(self.submit(s))
        p=self.prepare(s);p["requested_level"]="CURRENT_NATIVE_ELIGIBLE"
        self.rejected_unchanged(s,seal(p),"INVALID_INPUT")
        self.assertTrue(before <= risks(s.recover()["world"]))

    def test_T045_forbidden_fields(self):
        s=self.new("A18")
        for field in ("CLOSED","global_complete","grants","phase","spent","window"):
            p=self.prepare(s);p[field]=True;self.rejected_unchanged(s,seal(p),"INVALID_INPUT")


if __name__ == "__main__":
    raise SystemExit("Use the scoped run_dsat_s3a_tests.py runner")
