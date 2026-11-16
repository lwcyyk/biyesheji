import json
from pathlib import Path
import tempfile
import unittest
from auth_lifecycle.experiment.journal import Journal,Gate,read_verified,ResponseLost,ApprovalDenied,BudgetDenied,fingerprint,canonical
from auth_lifecycle.experiment.scoring import score
from auth_lifecycle.experiment.statistics import analyze,bootstrap,estimate,family_table,icc,pair_runs,sample_size_sensitivity,confirmation_gate
from auth_lifecycle.experiment.planning import plan

ROOT=Path(__file__).resolve().parents[1]


def rows():
    result=[]
    for implementation in ['keycloak','casdoor']:
        for f,cost in [('f1',2),('f2',10)]:
            for method,multiplier in [('A1',1),('B-A',2)]:
                result.append({'metadata':{'pair_id':implementation+f,'hypothesis':'H-A','implementation':implementation,'family_id':f,
                    'method':method,'goal':'remote','fault':'none','repeat':0,'Q_cap':64,'G_cap':8,'approval_cap':8,'source_sha256':'same',
                    'environment_digest':'same','lineage':'one-template','independence_attested':False},
                    'metrics':{'C_Q':cost*multiplier,'C_G':1,'U':1}})
    return result


class ExperimentTests(unittest.TestCase):
    def test_journal_redacts_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'});j.emit('data',access_token='private',password='password');j.close()
            self.assertNotIn('"private"',path.read_text());self.assertEqual(1,len(read_verified(path)))
            text=path.read_text().replace('"event":"data"','"event":"changed"');path.write_text(text)
            with self.assertRaises(ValueError):read_verified(path)

    def test_boolean_sequence_rejected_even_with_recomputed_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'});j.emit('x');j.close()
            row=json.loads(path.read_text());row.pop('sha256');row['seq']=False;row['sha256']=fingerprint(canonical(row));path.write_text(json.dumps(row))
            with self.assertRaises(ValueError):read_verified(path)

    def test_loss_charged_after_actual_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp)/'e.jsonl',{'run_id':'r'});g=Gate(j,fault='response_loss');called=[]
            with self.assertRaises(ResponseLost):g.transport('configure',lambda:(called.append(1) or {'http':200,'body':{'access_token':'secret'}}))
            self.assertEqual(1,len(called));self.assertEqual(1,g.sent);self.assertEqual(1,len(g.private_effects));j.close()

    def test_approval_rechecked_before_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp)/'e.jsonl',{'run_id':'r'});g=Gate(j,fault='approval_withdrawal')
            with self.assertRaises(ApprovalDenied):g.call('stop',lambda:self.fail('must not dispatch'))
            self.assertEqual(0,g.sent);j.close()

    def test_budget_shared_across_operation_kinds(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp)/'e.jsonl',{'run_id':'r'});g=Gate(j,cap=2)
            for kind in ['configure','probe']:g.call(kind,lambda:{'http':200,'body':{}})
            with self.assertRaises(BudgetDenied):g.call('cleanup',lambda:self.fail('over budget'))
            j.close()

    def test_scorer_rejects_false_completion_and_penalizes_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'})
            j.emit('request_sent',operation='configure',counted=True,approval_charge=1);j.emit('credential_created','witness',credential_ref='t',native_unit_ref='native-root');j.close()
            meta={'Q_cap':8,'G_cap':4,'approval_cap':2}
            bad=score(path,meta,'COMPLETED',[True],[True],[True],[],1)
            self.assertEqual(0,bad['U']);self.assertEqual(1,bad['FA']);self.assertEqual(9,bad['C_Q'])
            good=score(path,meta,'COMPLETED',[True],[False],[True],[],1)
            self.assertEqual(1,good['U']);self.assertEqual(1,good['G'])

    def test_unknown_measurement_is_not_denial(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'});j.close()
            value=score(path,{'Q_cap':8,'G_cap':4,'approval_cap':2},'COMPLETED',[True],[None],[True],[],0)
            self.assertEqual(0,value['U'])
            self.assertEqual(0,value['FA']);self.assertEqual('INCONCLUSIVE',value['status'])

    def test_witness_failure_does_not_change_method_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'});g=Gate(j)
            def unavailable(body):raise RuntimeError('observer unavailable')
            g.on_credential=unavailable
            result=g.call('configure',lambda:{'http':200,'body':{'access_token':'private'}})
            self.assertEqual('private',result['body']['access_token']);j.close()
            value=score(path,{'Q_cap':8,'G_cap':4,'approval_cap':2},'COMPLETED',[True],[False],[True],[],1)
            self.assertEqual('INCONCLUSIVE',value['status']);self.assertEqual(0,value['FA'])

    def test_unknown_inflight_creation_retains_obligation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'});g=Gate(j)
            def lost():raise TimeoutError()
            with self.assertRaises(TimeoutError):g.call('configure',lost)
            j.close();self.assertEqual(1,g.uncertain_creation_requests)
            value=score(path,{'Q_cap':8,'G_cap':4,'approval_cap':2},'UNKNOWN',[],[],[],[],0,1)
            self.assertEqual(1,value['O_material']);self.assertIsNone(value['G'])

    def test_scorer_independently_detects_unauthorized_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'})
            j.emit('fault_triggered','fault',fault='approval_withdrawal');j.emit('request_sent',operation='stop',counted=True,approval_charge=0);j.close()
            value=score(path,{'Q_cap':8,'G_cap':4,'approval_cap':2},'COMPLETED',[True],[False],[True],[],0)
            self.assertEqual(1,value['E']);self.assertEqual(0,value['U'])

    def test_G_counts_native_units_not_material_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'e.jsonl';j=Journal(path,{'run_id':'r'})
            for ref in ['token1','token2']:j.emit('credential_created','witness',credential_ref=ref,native_unit_ref='one-native-grant')
            j.close();value=score(path,{'Q_cap':8,'G_cap':4,'approval_cap':2},'COMPLETED',[True],[False],[True],[],1)
            self.assertEqual(1,value['G']);self.assertEqual(1,value['U'])

    def test_family_equal_weighting_not_run_weighting(self):
        r=rows();r.extend([dict(x,metadata=dict(x['metadata'],pair_id=x['metadata']['pair_id']+'extra')) for x in rows() if x['metadata']['family_id']=='f1'])
        t=family_table(pair_runs(r,'H-A','A1','B-A'),'C_Q');e=estimate(t)
        self.assertEqual(6,e['candidate_mean_cost']);self.assertEqual(.5,e['ratio'])

    def test_pair_conditions_and_missing_arm(self):
        r=rows();r[0]['metadata']['Q_cap']=7
        with self.assertRaises(ValueError):pair_runs(r,'H-A','A1','B-A')
        with self.assertRaises(ValueError):pair_runs(rows()[:-1],'H-A','A1','B-A')

    def test_cost_ratio_is_ratio_of_means(self):
        s={'keycloak':[{'candidate_cost':2,'baseline_cost':1,'candidate_U':1,'baseline_U':1},
                       {'candidate_cost':4,'baseline_cost':9,'candidate_U':1,'baseline_U':1}]}
        self.assertEqual(.6,estimate(s)['ratio'])

    def test_bootstrap_reproducible_with_paired_clusters(self):
        t=family_table(pair_runs(rows(),'H-A','A1','B-A'),'C_Q')
        a=bootstrap(t,100,7);self.assertEqual(a,bootstrap(t,100,7));self.assertEqual(.5,a['ratio_upper'])
        self.assertAlmostEqual(1-.05/3,a['one_sided_confidence'])

    def test_small_cluster_analysis_never_supports_hypothesis(self):
        registry=json.loads((ROOT/'experiments/registry.json').read_text())
        a=analyze(rows(),registry,50)['hypotheses']['H-A']
        self.assertFalse(a['formal_inference_allowed']);self.assertEqual('NOT_TESTED',a['formal_status'])
        self.assertEqual(1,a['adequacy']['keycloak']['lineage_groups'])

    def test_degenerate_variance_not_zero_required_sample(self):
        self.assertIsNone(icc([[0,0],[0,0]])['estimate'])
        self.assertIsNone(sample_size_sensitivity(.8,.8,.2)['families_per_implementation'])
        self.assertIsNone(sample_size_sensitivity(.8,.7,0)['families_per_implementation'])
        assumptions=sample_size_sensitivity(.8,.7,.4)
        self.assertEqual(.9,assumptions['marginal_power_used'])
        self.assertEqual(.8,assumptions['target_joint_IUT_power'])

    def test_confirmatory_gate_stays_closed(self):
        registry=json.loads((ROOT/'experiments/registry.json').read_text())
        self.assertFalse(confirmation_gate(registry,None)['allowed'])
        approval={k:'provided' for k in registry['required_researcher_freeze']};approval.update(decision='APPROVED_BY_RESEARCHER',native_binding_profile='known-contract-single-path/v1')
        registry['confirmatory_execution_enabled']=True
        self.assertFalse(confirmation_gate(registry,approval)['allowed'])

    def test_fixed_methods_native_nominal_projection(self):
        for method in ['A1','B-A','AB1','B-AB']:
            p=plan('keycloak','online',0,'remote_or_mixed','H-A',method)
            self.assertEqual('FEASIBLE',p['status']);self.assertFalse(p['formal_H_A_H_AB_eligible'])
        self.assertEqual('IMPOSSIBLE',plan('keycloak','offline',0,'remote_or_mixed','H-A','A1')['status'])
        self.assertEqual('IMPOSSIBLE',plan('keycloak','online',1,'local','H-A','A1')['status'])
        self.assertEqual('FEASIBLE',plan('casdoor','online',1,'local','H-A','A1')['status'])


if __name__=='__main__':unittest.main()
