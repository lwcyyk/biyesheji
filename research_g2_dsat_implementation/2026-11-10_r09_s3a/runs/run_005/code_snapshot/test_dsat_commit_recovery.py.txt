"""Owned child process crashes and independently inspected SQLite recovery."""
from unittest import mock
from test_dsat_commit_contract import *


class RecoveryCases(Harness):
    def handoff(self, stage):
        s=self.new();before,after,_=self.crash(s,self.prepare(s),stage,action="handoff")
        self.assertEqual(before,after)

    def test_T024_read_handoff(self):self.handoff("trusted_read")
    def test_T025_partial_evidence(self):self.handoff("partial_evidence")
    def test_T026_S1_handoff(self):self.handoff("S1_frozen_output")
    def test_T027_S2_not_delivered(self):self.handoff("S2_output_not_delivered")
    def test_T028_proof_handoff(self):self.handoff("frozen_proof")
    def test_T029_checked_handoff(self):self.handoff("trusted_checker_record")

    def test_T030_before_begin(self):
        s=self.new();before,after,_=self.crash(s,self.prepare(s),"before_begin")
        self.assertEqual(before,after)

    def test_T031_partial_SQL(self):
        for index,stage in enumerate(("after_objects","after_state","after_event_receipt"),1):
            def rollback(stage=stage):
                s=self.new();before,after,_=self.crash(s,self.prepare(s),stage)
                self.assertEqual(before,after)
            self.sub(index,rollback)
        self.sub(4,lambda:self.assertTrue(all(s.recover()["a"]==120 and not audit(s)["s3a_proposals"] for s in self.stores)))

    def committed_crash(self):
        s=self.new();p=self.prepare(s);before,after,snap=self.crash(s,p,"after_commit")
        self.assertEqual(snap["a"],121);self.assertEqual(len(after["s3a_proposals"]),1)
        self.assertGreater(len(after["s3a_objects"]),0)
        receipt=strict_load(bytes(after["s3a_proposals"][0][5]))
        return s,p,receipt

    def test_T032_ACK_loss(self):
        s,p,receipt=self.committed_crash()
        def handshake():
            ev=next(x for x in reversed(self.evidence) if x.get("killed"))
            self.assertEqual(ev["hook.json"]["stage"],"after_commit")
            self.assertFalse(ev["hook.json"]["in_transaction"])
            self.assertNotEqual(ev["exit_code"],0)
        self.sub(1,handshake)
        def complete():
            v=s.recover();self.assertEqual(v["a"],121);self.assertEqual(len(v["world"]["dsat"]["work_index"]),1)
            self.assertEqual(len(audit(s)["s3a_events"]),1)
        self.sub(2,complete)
        def replay():
            s.domain_event(self.event());before=audit(s);self.assertEqual(self.submit(s,p)["receipt"],receipt)
            self.assertEqual(before,audit(s))
        self.sub(3,replay)

    def test_T033_reopen_same_body(self):
        s,p,r=self.committed_crash();before=audit(s)
        self.assertEqual(self.submit(s,p)["receipt"],r);self.assertEqual(before,audit(s))

    def test_T034_reopen_changed_body(self):
        s,p,_=self.committed_crash();p["base_authority_revision"]+=1
        self.rejected_unchanged(s,seal(p),"CONFLICT_PROPOSAL_BODY")

    def test_T035_reopen_stale(self):
        s,p,r=self.committed_crash();self.assertEqual(self.submit(s,p,now=101)["receipt"],r)
        q=self.prepare(s);q["dependency_policy"]["require_current"]=True
        self.rejected_unchanged(s,seal(q),"STALE_EVIDENCE",now=101)

    def test_T036_reopen_late(self):
        s=self.new("A02");p=self.prepare(s);old=risks(s.read()["world"])
        self.crash(s,p,"before_begin")
        s.domain_event(self.event("late",[self.raw("close:c2")]))
        self.rejected_unchanged(s,p,"REJECTED_REVISION")
        self.assertTrue(old<=risks(s.recover()["world"]))

    def test_T037_recovery_revoke(self):
        s=self.new();p=self.prepare(s);self.crash(s,p,"before_begin")
        _,result=self.pair(s,{"action":"event","event":self.event("revoke",target_active=False)},{"body":p})
        self.assertEqual(result["status"],"REJECTED_REVISION")
        self.assertFalse(s.recover()["world"]["simulation"]["target_active"])

    def test_T046_safety_boundaries(self):
        def paths():
            for path in (RUN_ROOT/"authority.db",DB_ROOT/"authority.db",PROJECT/"fake.sqlite3",DB_ROOT/".."/"dsat_s3a_wrong.sqlite3"):
                with self.assertRaises(CommitError):SyntheticStore(path)
        self.sub(1,paths)
        def unknown():
            path=DB_ROOT/("dsat_s3a_unknown_"+uuid.uuid4().hex+".sqlite3");path.write_bytes(b"owned unknown bytes")
            before=path.read_bytes()
            with mock.patch("auth_lifecycle.online_state.dsat_synthetic_store.sqlite3.connect",side_effect=AssertionError("must not connect")):
                with self.assertRaises(CommitError):SyntheticStore(path).read()
            self.assertEqual(before,path.read_bytes())
        self.sub(2,unknown)
        def junction():
            import _winapi
            link=RUN_ROOT/("owned_junction_"+uuid.uuid4().hex)
            _winapi.CreateJunction(str(DB_ROOT),str(link))
            try:
                self.assertTrue(link.lstat().st_file_attributes & 0x400)
                with self.assertRaises(CommitError):SyntheticStore(link/"dsat_s3a_link.sqlite3")
            finally:
                self.assertEqual(link.parent,RUN_ROOT)
                self.assertTrue(link.lstat().st_file_attributes & 0x400)
                os.rmdir(link)  # Remove only this owned junction entry; do not recurse.
        self.sub(3,junction)
        def markers():
            for field,value in (("application_id",0),("user_version",2)):
                s=self.new();conn=s._connect();conn.execute("PRAGMA "+field+"="+str(value));conn.close()
                with self.assertRaises(CommitError):s.recover()
            s=self.new();conn=s._connect();world=s.read()["world"];world["authority_instance"]="syn:different"
            conn.execute("UPDATE s3a_state SET payload=?",(canonical(world),));conn.close()
            with self.assertRaises(CommitError):s.recover()
        self.sub(4,markers)
        def init_interruption():
            from auth_lifecycle.online_state import dsat_synthetic_store as module
            s=SyntheticStore(DB_ROOT/("dsat_s3a_brokeninit_"+uuid.uuid4().hex+".sqlite3"));self.stores.append(s)
            with mock.patch.object(module,"DDL",module.DDL+("INVALID SYNTHETIC SQL",)):
                with self.assertRaises(sqlite3.DatabaseError):s.create(self.registry.seed("AUTO_A01_A","syn:brokeninit"))
            self.assertTrue(s.path.exists())
            with self.assertRaises(CommitError):s.recover()
        self.sub(5,init_interruption)
        def codecs():
            for field in ("codec","O"):
                s=self.new();conn=s._connect();world=s.read()["world"]
                if field=="O":del world["dsat"]["O"]
                else:world["codec"]="legacy-AES-format"
                conn.execute("UPDATE s3a_state SET payload=?",(canonical(world),));conn.close()
                with self.assertRaises(CommitError):s.recover()
        self.sub(6,codecs)
        def imports():
            forbidden={"storage","services","native_provider","socket","requests","networkx","urllib"}
            for filename in ("dsat_commit_types.py","dsat_commit.py","dsat_synthetic_store.py"):
                tree=ast.parse((PROJECT/"src/auth_lifecycle/online_state"/filename).read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node,ast.Import):names=[x.name for x in node.names]
                    elif isinstance(node,ast.ImportFrom):names=[node.module or ""]
                    else:continue
                    self.assertFalse(any(set(name.split(".")) & forbidden for name in names))
                self.assertFalse(any(isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) for x in tree.body))
            self.assertFalse(any("native_provider" in key or key=="networkx" for key in sys.modules))
        self.sub(7,imports)
        def storage_limits():
            s=self.new();p=self.prepare(s);lock=s._connect();lock.execute("BEGIN IMMEDIATE")
            try:self.assertEqual(self.submit(s,p)["status"],"UNKNOWN_STORAGE_BUSY")
            finally:lock.rollback();lock.close()
            s2=self.new();c=s2._connect();pages=c.execute("PRAGMA page_count").fetchone()[0];c.close()
            s2.limits=Limits(db_pages=pages+1)
            self.rejected_unchanged(s2,self.prepare(s2),"REJECTION_NOT_PERSISTED")
            s3=self.new();c=s3._connect();c.execute("PRAGMA wal_autocheckpoint=0")
            self.accepted(self.submit(s3))
            self.assertGreater(Path(str(s3.path)+"-wal").stat().st_size,1)
            s3.limits=Limits(wal_bytes=1)
            try:self.rejected_unchanged(s3,self.prepare(s3),"UNKNOWN_RESOURCE_LIMIT")
            finally:c.close();s3.limits=Limits()
            s4=self.new();s4.limits=Limits(run_bytes=1)
            self.rejected_unchanged(s4,self.prepare(s4),"UNKNOWN_RESOURCE_LIMIT");s4.limits=Limits()
        self.sub(8,storage_limits)
        def uncertain_and_refusal():
            s=self.new();p=self.prepare(s)
            def uncertain(stage,connection):
                if stage=="after_commit":raise sqlite3.OperationalError("synthetic lost COMMIT acknowledgement")
            r=self.submit(s,p,hook=uncertain);self.assertEqual(r["status"],"UNKNOWN_COMMIT_OUTCOME")
            self.assertEqual(self.submit(s,p)["receipt"]["status"],"ACCEPTED")
            s2=self.new();q=self.prepare(s2);q["base_authority_revision"]=119;q=seal(q)
            with mock.patch.object(s2,"_insert_receipt",side_effect=sqlite3.OperationalError("synthetic disk full")):
                self.rejected_unchanged(s2,q,"REJECTION_NOT_PERSISTED")
            self.assertEqual(audit(s2)["s3a_proposals"],[])
        self.sub(9,uncertain_and_refusal)
        def integrity():
            lock=strict_load((SCOPE_PATH.parent/"SOURCE_LOCK.json").read_bytes())
            for item in lock["checks"]:
                self.assertEqual(hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest(),item["expected_sha256"])
            self.assertFalse(any("services" in key and key.startswith("auth_lifecycle.online_state") for key in sys.modules))
        # SCOPE_PATH is imported explicitly to keep the helper's public surface small.
        from auth_lifecycle.online_state.dsat_commit_types import SCOPE_PATH
        self.sub(10,integrity)
