"""M4 scope, completeness, exclusion, and sealed-audit regressions."""

import copy
import io
import json
import os
from pathlib import Path
import secrets
import unittest
from unittest.mock import Mock

from auth_lifecycle.online_state.enumeration import analyze, ScopeViolation
from auth_lifecycle.online_state.lab import initialize
from auth_lifecycle.online_state.native_http import create_budget, NativeHTTP, private_http_records
from auth_lifecycle.online_state.protocol import digest
from auth_lifecycle.online_state.reconciliation import make_receipt
import test_reconciliation as base_receipts


def row(name,user='target',organization='org4',application='app4'):
    return {'owner':'admin','name':name,'organization':organization,'application':application,'user':user}


def analyzed(rows=None,**changes):
    values={'organization':'org4','application':'app4','target_user':'target','allowed_users':['target','target-extra','peer'],
            'known_ids':['admin/A0','admin/B0'],'page_capacity':100,'record_bound':50,'unique_unknown':True,'manifest_ok':True,'actual_sends':1}
    values.update(changes)
    return analyze(rows if rows is not None else [row('B0'),row('A1'),row('I0','target-extra')],**values)


def receipt_for(query):
    target,facts,evidence=base_receipts.fixture()
    known={'known_unit_ids':query['known_input_ids'],'unknown_creators':['A1'],'account_grant_count':2,'account_budget_total':20}
    query.update(input_context=known,input_context_ref=digest(known))
    evidence['origin']='AUTHORIZED_SCOPE_ENUMERATION'
    evidence['identifier_receipt_ref']=None
    evidence['enumeration_ref']='synthetic-native-snapshot'
    evidence['authorized_scope_ref']='synthetic-authorized-org'
    evidence['packet']['query']=query
    evidence['packet']['model'].update(organization='org4',application_name='app4',client_id=target['audience'],
        account_names=['target','target-extra','peer'],account_id_by_name={'target':target['account'],'target-extra':'I','peer':'P'},approved_scope_budgets=[10,10,10,10,10])
    evidence['packet_ref']=digest(evidence['packet'])
    for key in ['exact_authorized_read','record_found','origin_bound','actual_sends','observed_distinct_effects']:facts[key]=query[key]
    return make_receipt(target,facts,evidence)


class EnumerationTests(unittest.TestCase):
    def test_single_unknown_positive_and_substring_interferer_excluded(self):
        query=analyzed()
        self.assertEqual(query['candidate_unit_ids'],['admin/A1'])
        self.assertNotIn('admin/I0',query['target_unit_ids'])
        receipt=receipt_for(query)
        self.assertEqual(receipt['claim'],'CLOSED')
        self.assertEqual(base_receipts.CHECKER.check(receipt)['status'],'VALID_CONDITIONAL_CLOSED')

    def test_unsafe_models_cannot_force_closed(self):
        cases={
            'two_unknown_creators':analyzed(unique_unknown=False),
            'extra_approval':analyzed(manifest_ok=False),
            'other_account_only':analyzed([row('B0'),row('I0','target-extra')]),
            'wrong_application':analyzed([row('B0'),row('A1',application='other')]),
            'page_below_bound':analyzed(page_capacity=2),
            'insert_delete_pagination':analyzed(page_capacity=2),
            'same_lists_then_late_create':analyzed([row('A0'),row('B0')],actual_sends=0),
            'zero_candidate_future_send':analyzed([row('A0'),row('B0')],actual_sends=0)}
        for name,query in cases.items():
            with self.subTest(name=name):
                receipt=receipt_for(query)
                self.assertEqual(receipt['claim'],'UNKNOWN')
                receipt.update(claim='CLOSED',remaining_creation_bound=0,remaining_obligations=[])
                self.assertEqual(base_receipts.CHECKER.check(receipt)['status'],'INVALID')

    def test_wrong_organization_is_scope_violation(self):
        with self.assertRaises(ScopeViolation):analyzed([row('A1',organization='shared')])

    def test_count_timing_metadata_is_not_completeness_basis(self):
        query=analyzed()
        query['reported_pages']=0
        self.assertEqual(receipt_for(query)['claim'],'CLOSED')
        query['page_capacity']=1
        query['collection_complete']=False
        self.assertEqual(receipt_for(query)['claim'],'UNKNOWN')

    def test_disposal_unknown_and_B_failure_refuse_closed(self):
        for key in ['known_A_units_inactive','B_preserved_after_disposal']:
            receipt=receipt_for(analyzed());receipt['facts'][key]=False
            self.assertEqual(base_receipts.CHECKER.check(receipt)['status'],'INVALID')

    def test_candidate_selection_tampering_rejected(self):
        receipt=receipt_for(analyzed())
        receipt['evidence']['packet']['query']['selected_unit_id']='admin/I0'
        receipt['evidence']['packet_ref']=digest(receipt['evidence']['packet'])
        self.assertEqual(base_receipts.CHECKER.check(receipt)['status'],'INVALID')


class AuditScopeTests(unittest.TestCase):
    def test_runtime_has_only_audit_public_key_and_fixed_org_query(self):
        parent=Path(os.environ.get('UNIDENTIFIED_TEST_ROOT',Path(__file__).resolve().parents[2]/'mainline_native_unidentified_v1/dev_work'))
        parent.mkdir(parents=True,exist_ok=True)
        root=initialize(parent/secrets.token_hex(8))
        scope={'organization':'org4','application_name':'app4','client_id':'client4','dedicated_scope':True,
               'organization_scope_read_enabled':True,'page_size':100,'record_upper_bound':50,'audit_mode':'sealed_to_scorer'}
        create_budget(root,'synthetic-only',['target','target-extra','peer'],scope=scope)
        client=NativeHTTP(root,'method',enabled=True)
        self.assertIsNone(client.key)
        self.assertIsNotNone(client.audit_public)
        self.assertFalse((root/'secure/http.key').exists())
        response=io.BytesIO(b'{"status":"ok","data":[]}');response.status=200
        client.opener.open=Mock(return_value=response)
        client.call('get_tokens',actor='target')
        url=client.opener.open.call_args.args[0].full_url
        self.assertIn('organization=org4',url)
        self.assertIn('pageSize=100',url)
        self.assertNotIn('value=target',url)
        self.assertEqual(private_http_records(root)[0]['response']['body']['data'],[])
        self.assertTrue((root/'secure/http/1.aes').read_bytes().startswith(b'M4AE'))

    def test_application_delete_requires_original_organization(self):
        from auth_lifecycle.online_state.protocol import InvalidInput
        parent=Path(os.environ.get('UNIDENTIFIED_TEST_ROOT',Path(__file__).resolve().parents[2]/'mainline_native_unidentified_v1/dev_work'))
        parent.mkdir(parents=True,exist_ok=True)
        root=initialize(parent/secrets.token_hex(8))
        scope={'organization':'org4','application_name':'app4','client_id':'client4','dedicated_scope':True}
        create_budget(root,'synthetic-only',['target'],scope=scope)
        client=NativeHTTP(root,'cleanup',enabled=True)
        client.opener.open=Mock(side_effect=AssertionError('no native network'))
        with self.assertRaises(InvalidInput):
            client.call('delete_application',payload={'owner':'admin','name':'app4'})
        with self.assertRaises(InvalidInput):
            client.call('delete_application',payload={'owner':'admin','name':'app4','organization':'shared'})
        self.assertFalse(client.opener.open.called)
