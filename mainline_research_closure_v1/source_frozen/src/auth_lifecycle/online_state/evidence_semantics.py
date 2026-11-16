"""Pure, versioned evidence views. No network, state changes, or token inputs.

Legacy booleans remain observations with their original scope. Introspection
never implies that a refresh was sent or that future creation is impossible.
"""
from copy import deepcopy

MATERIAL_SCHEMA = "native-material-observation/2"
QUERY_SCHEMA = "native-enumeration-observation/2"


def boolean(value):
    return value if type(value) is bool else None


def normalize_material(row, provenance=None):
    """Normalize a secret-free measurement row, preserving missing evidence."""
    mode = row.get("refresh_check_kind")
    rt_active = row.get("rt_introspection_active", row.get("refresh_introspection_active"))
    rt_performed = row.get("rt_introspection_performed") is True or mode == "READ_ONLY_INTROSPECTION"
    rt_http = row.get("rt_introspection_http")
    rt_http_valid = rt_http is None or rt_http == 200
    at_http = row.get("at_introspection_http", row.get("introspection_http"))
    at_http_valid = at_http is None or at_http == 200
    refresh_performed = row.get("refresh_request_performed") is True or (
        mode != "READ_ONLY_INTROSPECTION" and "refresh_http" in row)
    refresh_http = row.get("refresh_request_http", row.get("refresh_http")) if refresh_performed else None
    material = boolean(row.get("refresh_response_has_new_material"))
    # Old active-probe producer set refresh_rejected only after a 4xx response
    # with no access token. It did not record all returned material fields.
    legacy_rejected = row.get("refresh_rejected") is True
    old_active_rejection = refresh_performed and refresh_http in {400, 401, 403} and legacy_rejected and material is None
    response_rejected = refresh_performed and refresh_http in {400, 401, 403} and (
        material is False or old_active_rejection) and not row.get("refresh_transport_error_type")
    ambiguous = "refresh_rejected" in row and not rt_performed and not refresh_performed
    return {"schema": MATERIAL_SCHEMA, "rid": row.get("rid"),
        "userinfo": {"http": row.get("userinfo_http"), "accepted": boolean(row.get("accepted")),
                     "scope": "configured cookie-free UserInfo and expected account"},
        "access_token_introspection": {"performed": "at_introspection_active" in row or "introspection_active" in row,
            "http": at_http,
            "active": boolean(row.get("at_introspection_active", row.get("introspection_active"))) if at_http_valid else None},
        "refresh_token_introspection": {"performed": rt_performed,
            "http": rt_http, "active": boolean(rt_active) if rt_performed and rt_http_valid else None,
            "inconsistent_http_active": rt_performed and not rt_http_valid and type(rt_active) is bool,
            "native_sequence": row.get("rt_introspection_native_sequence"),
            "http_not_explicitly_recorded": rt_performed and "rt_introspection_http" not in row},
        "refresh_attempt": {"performed": refresh_performed, "http": refresh_http,
            "response_rejects_request": bool(response_rejected), "new_material_in_response": material,
            "legacy_only_no_access_token": old_active_rejection,
            "response_error_present": boolean(row.get("refresh_response_error_present")),
            "transport_error_type": row.get("refresh_transport_error_type"),
            "native_sequence": row.get("refresh_native_sequence"),
            "creation_effect_excluded": None},
        "legacy_ambiguous_boolean": ambiguous, "provenance": deepcopy(provenance or {}),
        "does_not_establish": ["arbitrary RP rejection", "future creation cutoff", "all descendants closed"]}


def rt_inactive_or_refresh_response_rejected(row):
    view = normalize_material(row)
    intro = view["refresh_token_introspection"]
    return ((intro["performed"] and intro["active"] is False)
            or view["refresh_attempt"]["response_rejects_request"])


def normalize_query(query, provenance=None):
    records = query.get("returned_records")
    new_count = query.get("native_reported_count")
    old_count = query.get("reported_pages")
    count = new_count if "native_reported_count" in query else old_count
    return {"schema": QUERY_SCHEMA, "native_reported_count": count if type(count) is int else None,
        "returned_record_count": len(records) if isinstance(records, list) else query.get("returned_record_count"),
        "requested_page_capacity": query.get("page_capacity"), "requested_page_number": query.get("page_number"),
        "native_reported_page_count": None,
        "count_and_rows_share_snapshot": False,
        "complete_at_find_snapshot": boolean(query.get("collection_complete")),
        "completeness_basis": {"snapshot_scope": query.get("snapshot_scope"),
                               "lifetime_record_upper_bound": query.get("record_upper_bound")},
        "future_creation_cutoff_established_by_count": False,
        "legacy_field_mapping": "reported_pages -> native_reported_count (Casdoor data2)",
        "conflicting_count_fields": "native_reported_count" in query and "reported_pages" in query and new_count != old_count,
        "provenance": deepcopy(provenance or {})}
