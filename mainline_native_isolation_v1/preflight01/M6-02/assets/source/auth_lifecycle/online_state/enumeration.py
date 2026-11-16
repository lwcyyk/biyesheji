"""Authorized-scope snapshot and conservative difference attribution."""


class ScopeViolation(ValueError):
    pass


def analyze(rows, organization, application, target_user, allowed_users, known_ids,
            page_capacity, record_bound, unique_unknown, manifest_ok, actual_sends):
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("INVALID_COLLECTION")
    if any(row.get("organization") != organization for row in rows):
        raise ScopeViolation("UNAUTHORIZED_ORGANIZATION_RETURNED")
    projections = [{"unit_id": row.get("owner", "") + "/" + row.get("name", ""),
                    "user": row.get("user"), "application": row.get("application"),
                    "organization": row.get("organization")} for row in rows]
    ids = [row["unit_id"] for row in projections]
    universe_ok = all(row["user"] in allowed_users and row["application"] == application for row in projections)
    complete = (type(page_capacity) is int and type(record_bound) is int
                and 0 < record_bound <= page_capacity and len(rows) <= record_bound
                and len(ids) == len(set(ids)) and universe_ok and manifest_ok)
    target = [row["unit_id"] for row in projections if row["user"] == target_user and row["application"] == application]
    candidates = sorted(set(target) - set(known_ids))
    bound = complete and unique_unknown and actual_sends == 1 and len(candidates) == 1
    return {"evidence_origin": "AUTHORIZED_SCOPE_ENUMERATION", "query_kind": "organization_equal_single_page",
            "exact_authorized_read": True, "record_found": len(candidates) == 1, "origin_bound": bound,
            "actual_sends": actual_sends, "observed_distinct_effects": 1 if bound else 0,
            "organization": organization, "application": application, "target_user": target_user,
            "all_returned_rows_authorized": True, "registered_universe_complete": universe_ok,
            "collection_complete": complete, "page_capacity": page_capacity, "record_upper_bound": record_bound,
            "page_number": 1, "snapshot_scope": "single_find_statement", "organization_equal_filter": True,
            "returned_records": projections, "target_unit_ids": sorted(set(target)),
            "known_input_ids": sorted(set(known_ids)), "candidate_unit_ids": candidates,
            "selected_unit_id": candidates[0] if bound else None}
