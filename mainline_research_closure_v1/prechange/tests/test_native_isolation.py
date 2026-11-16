"""M6 regression uses signed synthetic responses and real restricted processes."""
import importlib.util
import json
import os
from pathlib import Path
import secrets
import unittest

from auth_lifecycle.online_state.native_http import budget_path
from auth_lifecycle.online_state.native_isolation import run_preflight,run_native
from auth_lifecycle.online_state.protocol import InvalidInput

spec=importlib.util.spec_from_file_location('m6_independent_rules',Path(__file__).resolve().parents[1]/'scripts/score_native_isolation.py')
rules=importlib.util.module_from_spec(spec);spec.loader.exec_module(rules)


class M6ConfigurationTests(unittest.TestCase):
    def test_budget_writable_subdirectory_and_legacy_compatibility(self):
        root=Path(__file__).resolve().parent
        self.assertEqual(budget_path(root,{}),root/'native_budget.db')
        self.assertEqual(budget_path(root,{'budget_subdirectory':'http_budget'}),root/'http_budget/native_budget.db')
        with self.assertRaises(InvalidInput):budget_path(root,{'budget_subdirectory':'../escape'})

    def test_native_execution_requires_explicit_gate(self):
        with self.assertRaisesRegex(ValueError,'EXPLICIT_NATIVE_ENABLE_REQUIRED'):
            run_native('unused','unauthorized',None,False)


@unittest.skipUnless(os.name=='nt','Windows primary-token integration')
class M6ZeroNativeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent=Path(os.environ.get('M6_TEST_ROOT',r'D:\毕业设计\mainline_native_isolation_v1\dev_work'))
        parent.mkdir(parents=True,exist_ok=True)
        cls.root=parent/('preflight_'+secrets.token_hex(5))
        cls.preflight=run_preflight(cls.root,'M6-DEVELOPMENT-ZERO-NATIVE')
        if not cls.preflight['gate_pass']:
            raise AssertionError(json.dumps(cls.preflight['records']))

    def test_two_native_modules_flows_under_real_tokens(self):
        self.assertTrue(self.preflight['gate_pass'])
        self.assertEqual(self.preflight['native_requests'],0)
        for scenario in ('M6-01','M6-02'):
            scored=rules.score(self.root/scenario,True)
            self.assertTrue(scored['status'].startswith('PASS_'),scored)

    def score_mutation(self,scenario,relative,mutate):
        case=self.root/scenario;path=case/relative;before=path.read_bytes()
        try:
            value=json.loads(before);mutate(value);path.write_text(json.dumps(value))
            return rules.score(case,True)
        finally:
            path.write_bytes(before);rules.score(case,True)

    def test_checker_rejects_actual_file_access_grant(self):
        def change(v):v['file_reads'][0].update(allowed=True,winerror=0)
        r=self.score_mutation('M6-01','trusted/runner/outcome.json',change)
        self.assertEqual(r['status'],'SAFETY_FAILURE')

    def test_checker_rejects_wrong_effective_token(self):
        def change(v):v['identities']['A']['token']['restricting_sids']=[]
        r=self.score_mutation('M6-01','SETUP_CONTROLS.json',change)
        self.assertEqual(r['status'],'SAFETY_FAILURE')

    def test_checker_finds_material_in_agent_readable_file(self):
        case=self.root/'M6-01'
        private=json.loads((case/'scorer_private/actual_responses.json').read_text())
        token=next(r['response']['body']['refresh_token'] for r in private if r['operation']=='issue')
        path=case/'agents/A/deliberately_bad_material.txt'
        try:
            path.write_text(token)
            self.assertEqual(rules.score(case,True)['status'],'SAFETY_FAILURE')
        finally:path.unlink();rules.score(case,True)

    def test_checker_rejects_unsupported_closed_receipt(self):
        def change(v):v['closure']['receipt']['remaining_creation_bound']=1
        r=self.score_mutation('M6-02','trusted/runner/outcome.json',change)
        self.assertEqual(r['status'],'SAFETY_FAILURE')


if __name__=='__main__':unittest.main()
