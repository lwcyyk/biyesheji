"""Offline evidence meaning and non-promotion regressions."""
from copy import deepcopy
import unittest
from auth_lifecycle.online_state.evidence_semantics import (
    normalize_material, normalize_query, rt_inactive_or_refresh_response_rejected)


class EvidenceSemanticsTests(unittest.TestCase):
    def test_legacy_introspection_does_not_become_refresh_attempt(self):
        row={"refresh_rejected":True,"refresh_check_kind":"READ_ONLY_INTROSPECTION","refresh_introspection_active":False}
        value=normalize_material(row)
        self.assertFalse(value['refresh_attempt']['performed'])
        self.assertIsNone(value['refresh_attempt']['creation_effect_excluded'])
        self.assertFalse(value['refresh_token_introspection']['active'])
        self.assertTrue(rt_inactive_or_refresh_response_rejected(row))

    def test_untyped_legacy_boolean_stays_ambiguous(self):
        value=normalize_material({'refresh_rejected':True})
        self.assertTrue(value['legacy_ambiguous_boolean'])
        self.assertFalse(rt_inactive_or_refresh_response_rejected({'refresh_rejected':True}))

    def test_actual_refresh_response_scope(self):
        row={'refresh_request_performed':True,'refresh_request_http':400,'refresh_response_has_new_material':False}
        value=normalize_material(row)
        self.assertTrue(value['refresh_attempt']['response_rejects_request'])
        self.assertIsNone(value['refresh_attempt']['creation_effect_excluded'])

    def test_response_with_material_or_parse_error_is_not_clean_rejection(self):
        for update in [{'refresh_response_has_new_material':True},{'refresh_transport_error_type':'ResponseParseFailure'}]:
            row={'refresh_request_performed':True,'refresh_request_http':400,'refresh_response_has_new_material':False,**update}
            self.assertFalse(rt_inactive_or_refresh_response_rejected(row))

    def test_http_error_does_not_become_inactive(self):
        row={'rt_introspection_performed':True,'rt_introspection_http':500,'rt_introspection_active':False}
        value=normalize_material(row)
        self.assertIsNone(value['refresh_token_introspection']['active'])
        self.assertTrue(value['refresh_token_introspection']['inconsistent_http_active'])
        self.assertFalse(rt_inactive_or_refresh_response_rejected(row))
        at=normalize_material({'at_introspection_http':500,'at_introspection_active':False})
        self.assertIsNone(at['access_token_introspection']['active'])

    def test_nonboolean_active_is_unknown(self):
        row={'rt_introspection_performed':True,'rt_introspection_http':200,'rt_introspection_active':'false'}
        self.assertIsNone(normalize_material(row)['refresh_token_introspection']['active'])

    def test_resource_and_token_statement_are_separate(self):
        row={'accepted':True,'userinfo_http':200,'rt_introspection_performed':True,'rt_introspection_active':False}
        value=normalize_material(row)
        self.assertTrue(value['userinfo']['accepted'])
        self.assertFalse(value['refresh_token_introspection']['active'])

    def test_count_is_not_page_count_or_completeness(self):
        q={'reported_pages':4,'returned_records':[{},{}],'page_capacity':100,'page_number':1,'collection_complete':False}
        value=normalize_query(q)
        self.assertEqual(value['native_reported_count'],4)
        self.assertEqual(value['returned_record_count'],2)
        self.assertIsNone(value['native_reported_page_count'])
        self.assertFalse(value['complete_at_find_snapshot'])
        self.assertFalse(value['future_creation_cutoff_established_by_count'])

    def test_conflicting_aliases_visible_and_input_unchanged(self):
        q={'reported_pages':4,'native_reported_count':5,'returned_records':[]}
        before=deepcopy(q);value=normalize_query(q)
        self.assertTrue(value['conflicting_count_fields'])
        self.assertEqual(q,before)


if __name__=='__main__':unittest.main()
