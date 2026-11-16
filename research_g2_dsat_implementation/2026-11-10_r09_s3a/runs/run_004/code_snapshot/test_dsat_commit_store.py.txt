"""Real isolated SQLite version/CAS/idempotence and ordered connection cases."""
from test_dsat_commit_contract import *


class StoreCases(Harness):
    def test_T001_first_and_bounds(self):
        s=self.new()
        def plain():
            self.accepted(self.submit(s));v=s.recover();self.assertEqual((v["a"],v["world"]["dsat"]["obligation_revision"]),(121,0))
        self.sub(1,plain)
        def A08():
            other=self.new("A08");p=self.prepare(other);before=other.read()["world"]
            self.assertEqual(len(before["dsat"]["O"]),5);self.assertEqual(len(p["proof"]["bindings"]["O_before"]),6)
            self.accepted(self.submit(other,p));after=other.recover()
            self.assertEqual((after["a"],after["world"]["dsat"]["obligation_revision"]),(121,1))
            self.assertEqual(len(after["world"]["dsat"]["O"]),6)
            self.assertTrue(risks(before)<=risks(after["world"]))
        self.sub(2,A08)
        def boundaries():
            for limits in (Limits(O_items=5),Limits(risk_components=5)):
                other=self.new("A08",limits);self.rejected_unchanged(other,self.prepare(other),"UNKNOWN_RESOURCE_LIMIT")
            p=self.prepare(s);size=len(canonical(p["proof"]))
            Proposal.parse(p,Limits(proof_bytes=size))
            with self.assertRaises(CommitError):Proposal.parse(p,Limits(proof_bytes=size-1))
            w=s.read()["world"];size=len(canonical(w));validate_world(w,Limits(world_bytes=size))
            with self.assertRaises(CommitError):validate_world(w,Limits(world_bytes=size-1))
        self.sub(3,boundaries)

    def test_T002_same_body(self):
        s=self.new();p=self.prepare(s);r=self.submit(s,p)
        s.domain_event(self.event("O_only",[self.raw("close:later")]))
        before=audit(s);replay=self.submit(s,p)
        self.assertEqual(replay["status"],"REPLAY_HISTORICAL_RECEIPT")
        self.assertEqual(replay["receipt"],r["receipt"]);self.assertEqual(before,audit(s))

    def test_T003_independent_ids(self):
        s=self.new();r1=self.submit(s);r2=self.submit(s)
        self.accepted(r1);self.accepted(r2);v=s.recover();self.assertEqual(v["a"],122)
        self.assertEqual(len(v["world"]["dsat"]["work_index"]),1)
        p=self.prepare(s);p["cost_delta"][0]["id"]="work:distinct"
        self.accepted(self.submit(s,seal(p)))
        self.assertEqual(len(s.recover()["world"]["dsat"]["work_index"]),2)

    def test_T006_same_base(self):
        s=self.new();p1=self.prepare(s);p2=self.prepare(s)
        p1["obligations_delta"]["add"].append(obligation(self.raw("close:c2"),digest("scope",s.read()["world"]["scope"])))
        r1,r2=self.pair(s,{"body":seal(p1)},{"body":p2})
        self.accepted(r1);self.assertEqual(r2["status"],"REJECTED_REVISION")
        v=s.recover();self.assertEqual((v["a"],v["world"]["dsat"]["obligation_revision"]),(121,1))
        self.assertIn("close:c2",{x["id"] for x in v["world"]["dsat"]["O"]})

    def test_T007_revoke_order(self):
        s=self.new();p=self.prepare(s)
        _,r=self.pair(s,{"action":"event","event":self.event("revoke",target_active=False)}, {"body":p})
        self.assertEqual(r["status"],"REJECTED_REVISION");self.assertFalse(s.recover()["world"]["simulation"]["target_active"])
        s2=self.new();p2=self.prepare(s2)
        r,_=self.pair(s2,{"body":p2},{"action":"event","event":self.event("revoke",target_active=False)})
        self.accepted(r);self.assertEqual(s2.recover()["a"],122)
        self.assertEqual(len(audit(s2)["s3a_proposals"]),1)

    def test_T008_late_and_A08(self):
        s=self.new("A02");p=self.prepare(s);old=risks(s.read()["world"])
        _,r=self.pair(s,{"action":"event","event":self.event("late",[self.raw("close:c2")])},{"body":p})
        self.assertEqual(r["status"],"REJECTED_REVISION")
        def late():
            v=s.recover()["world"];self.assertTrue(old<=risks(v));self.assertIn("close:c2",{x["id"] for x in v["dsat"]["O"]})
            self.assertEqual(v["source"]["bundle"]["authority"]["requests"],self.registry.sources["AUTO_A02_A"]["bundle"]["authority"]["requests"])
        self.sub(1,late)
        def binding():
            other=self.new("A08");p=self.prepare(other);self.assertEqual(len(other.read()["world"]["dsat"]["O"]),5)
            self.assertEqual(len(p["proof"]["bindings"]["O_before"]),6);self.accepted(self.submit(other,p))
            self.assertEqual(len(other.recover()["world"]["dsat"]["O"]),6)
        self.sub(2,binding)

    def test_T009_third_grant(self):
        s=self.new();p=self.prepare(s)
        _,r=self.pair(s,{"action":"event","event":self.event("third_grant",[self.raw("frontier:V")])},{"body":p})
        self.assertEqual(r["status"],"REJECTED_REVISION")
        self.assertIn("frontier:V",{x["id"] for x in s.recover()["world"]["dsat"]["O"]})

    def test_T011_O_dependency_version(self):
        s=self.new();p=self.prepare(s)
        _,r=self.pair(s,{"action":"event","event":self.event("O_only",[self.raw("close:new")])},{"body":p})
        self.assertEqual(r["status"],"REJECTED_REVISION");self.assertEqual(s.recover()["world"]["dsat"]["obligation_revision"],1)
        # Deliberate corruption in another owned test DB challenges recovery hashes.
        other=self.new();self.accepted(self.submit(other));c=other._connect()
        w=other.read()["world"];w["dsat"]["obligation_revision"]+=1
        c.execute("UPDATE s3a_state SET payload=?",(canonical(w),));c.close()
        with self.assertRaises(CommitError):other.recover()

    def test_T013_rejected_identity(self):
        s=self.new();p=self.prepare(s);s.domain_event(self.event());rejection=self.submit(s,p)
        self.assertEqual(rejection["status"],"REJECTED_REVISION")
        changed=clone(p);changed["base_authority_revision"]+=1
        first,second=self.pair(s,{"body":p},{"body":seal(changed)})
        self.assertEqual(first["receipt"],rejection["receipt"])
        self.assertEqual(second["status"],"CONFLICT_PROPOSAL_BODY")

    def test_T015_owner_and_capacity(self):
        s=self.new();p=self.prepare(s);self.accepted(self.submit(s,p))
        q=clone(p);q["actor"]="syn:other"
        _,r=self.pair(s,{"body":p},{"body":seal(q),"actor":"syn:other"})
        self.sub(1,lambda:self.assertEqual(r["status"],"REJECT_UNAUTHORIZED"))
        def history():
            s.domain_event(self.event("permission",manager_read=False,source_changed=False))
            self.rejected_unchanged(s,p,"REJECT_UNAUTHORIZED")
        self.sub(2,history)
        def capacity():
            other=self.new();first=None;receipt=None
            for i in range(256):
                body=self.prepare(other,"cap:"+str(i));body["base_authority_revision"]=119;body=seal(body)
                r=self.submit(other,body);self.assertEqual(r["status"],"REJECTED_REVISION")
                if i==0:first,receipt=body,r["receipt"]
            before=audit(other);self.assertEqual(len(before["s3a_proposals"]),256)
            self.assertEqual(self.submit(other,first)["receipt"],receipt)
            self.assertEqual(audit(other),before)
            self.rejected_unchanged(other,self.prepare(other),"UNKNOWN_RESOURCE_LIMIT")
        self.sub(3,capacity)

    def test_T021_B_independent(self):
        s=self.new("A09");old=risks(s.read()["world"]);self.accepted(self.submit(s))
        s.domain_event(self.event("B_release",[self.raw("exec:rB")]))
        new=s.recover()["world"];self.assertTrue(old<=risks(new));self.assertTrue(new["simulation"]["B_active"])
        self.assertIn("exec:rB",{x["id"] for x in new["dsat"]["O"]})

    def test_T023_work_and_revision(self):
        s=self.new();p=self.prepare(s);self.accepted(self.submit(s,p));self.accepted(self.submit(s))
        self.sub(1,lambda:self.assertEqual(len(s.recover()["world"]["dsat"]["work_index"]),1))
        def conflict():
            q=self.prepare(s);q["cost_delta"][0]["body"]["amount"]+=1
            self.rejected_unchanged(s,seal(q),"CONFLICT_WORK_BODY")
        self.sub(2,conflict)
        def bad_cost():
            for value in (-1,True,1<<128):
                q=self.prepare(s);q["cost_delta"][0]["body"]["amount"]=value
                if value==1<<128:
                    with self.assertRaises(CommitError):seal(q)
                else:self.rejected_unchanged(s,seal(q),"INVALID_INPUT")
        self.sub(3,bad_cost)
        def exhausted():
            for seed,a,o in [("A01",MAX_REVISION,0),("A08",120,MAX_REVISION)]:
                other=self.new(seed,a=a,o=o);self.rejected_unchanged(other,self.prepare(other),"REVISION_EXHAUSTED")
                self.assertEqual((other.recover()["a"],other.read()["world"]["dsat"]["obligation_revision"]),(a,o))
        self.sub(4,exhausted)

    def test_T039_stale_digests(self):
        s=self.new();p=self.prepare(s);s.domain_event(self.event());self.rejected_unchanged(s,p,"REJECTED_REVISION")
        for field in ("base_O_digest","source_snapshot_digest","request_scope_digest","current_grant_digest"):
            q=self.prepare(s);q[field]="0"*64;self.rejected_unchanged(s,seal(q),"REJECTED_BASE_DIGEST")
        q=self.prepare(s);q["base_obligation_revision"]+=1;self.rejected_unchanged(s,seal(q),"REJECTED_REVISION")
