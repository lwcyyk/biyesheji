#!/usr/bin/env python3
"""Generate evidence-backed /api/v2 coverage without inferring implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "specs/001-vdns-audit-rotation/contracts/openapi.json"
HANDLER = ROOT / "internal/adapters/inbound/httpapi/handler.go"
AGENT = ROOT / "internal/localapi/application/agent.go"
HANDLER_TEST = ROOT / "internal/adapters/inbound/httpapi/handler_test.go"
AGENT_TEST = ROOT / "internal/localapi/application/agent_test.go"
CONTRACT_TEST = ROOT / "tests/contract/openapi_local_api_test.go"


# A capability is COMPLETE only when the handler delegates to concrete domain
# logic and an endpoint-level or domain-level regression test marker exists.
# Queue-only research stubs remain PARTIAL; explicit optional 501 routes remain
# NOT_IMPLEMENTED.
REGISTRY = {
    "createVaultSession": ("CreateVaultSession(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "deleteVaultSession": ("DeleteVaultSession(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "createPasswordGeneration": ("GeneratePassword(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "createCredentialRouteResolution": ("ResolveRoute(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "listCredentials": ("ListCredentials(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "createCredential": ("CreateCredential(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "getCredential": ("GetCredential(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "createAutofillAuthorization": ("AuthorizeAutofill(", "TestHTTPDailyCredentialContract", "COMPLETE"),
    "listCredentialVersions": ("ListVersions(", "TestHTTPVersionUnknownDoesNotActivate", "COMPLETE"),
    "createCredentialVersion": ("CreateVersion(", "TestHTTPVersionUnknownDoesNotActivate", "COMPLETE"),
    "createSiteConfirmation": ("ConfirmSite(", "TestHTTPVersionUnknownDoesNotActivate", "COMPLETE"),
    "createSyncPublication": ("QueueOperation(sessionID, \"SYNC_PUBLICATION\")", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createSyncPull": ("QueueOperation(sessionID, \"SYNC_PULL\")", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createDeviceEnrollment": ("EnrollDevice(", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createDeviceRevocation": ("RevokeDevice(", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createRecoverySession": ("Recover(", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createVdnsResolution": ("ResolveVDNS(", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createAuditEvent": ("QueueOperation(sessionID, \"AUDIT_EVENT\")", "TestHTTPStage2CapabilityBoundaries", "PARTIAL"),
    "createSecurityAnalysis": ("CreateSecurityAnalysis(", "TestHTTPStage2CapabilityBoundaries", "COMPLETE"),
    "createExposureAnalysis": ("OPTIONAL_FEATURE_UNAVAILABLE", "TestHTTPStage2CapabilityBoundaries", "NOT_IMPLEMENTED"),
    "createRemediationCampaign": ("OPTIONAL_FEATURE_UNAVAILABLE", "TestHTTPStage2CapabilityBoundaries", "NOT_IMPLEMENTED"),
    "getOperation": ("GetOperation(", "TestHTTPDurableIdempotencySurvivesHandlerRestart", "COMPLETE"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def generate() -> dict:
    document = json.loads(read(OPENAPI))
    handler = read(HANDLER)
    domain = read(AGENT)
    tests = "\n".join((read(HANDLER_TEST), read(AGENT_TEST), read(CONTRACT_TEST)))
    operations = []
    unknown = []
    seen = set()
    for path, methods in document["paths"].items():
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation_id = operation.get("operationId", "")
            if operation_id in seen:
                raise ValueError(f"duplicate operationId: {operation_id}")
            seen.add(operation_id)
            rule = REGISTRY.get(operation_id)
            if rule is None:
                unknown.append(operation_id)
                continue
            domain_marker, test_marker, declared_status = rule
            handler_present = operation_id in handler
            domain_present = domain_marker in domain or domain_marker in handler
            test_present = test_marker in tests
            effective = declared_status
            if not handler_present:
                effective = "NOT_IMPLEMENTED"
            elif declared_status == "COMPLETE" and (not domain_present or not test_present):
                effective = "UNVERIFIED"
            operations.append({
                "operationId": operation_id,
                "method": method.upper(),
                "path": path,
                "openapi": True,
                "handler": handler_present,
                "domainLogic": domain_present,
                "test": test_present,
                "status": effective,
                "declaredBoundary": (
                    "explicit optional capability"
                    if declared_status == "NOT_IMPLEMENTED"
                    else "queue/research composition boundary"
                    if declared_status == "PARTIAL"
                    else "local research implementation"
                ),
            })
    missing_from_openapi = sorted(set(REGISTRY) - seen)
    counts = {}
    for operation in operations:
        counts[operation["status"]] = counts.get(operation["status"], 0) + 1
    return {
        "schemaVersion": "vdns-pm-stage2-api-coverage/1",
        "contractVersion": document["info"]["version"],
        "sourceFiles": [
            str(OPENAPI.relative_to(ROOT)),
            str(HANDLER.relative_to(ROOT)),
            str(AGENT.relative_to(ROOT)),
            str(HANDLER_TEST.relative_to(ROOT)),
            str(AGENT_TEST.relative_to(ROOT)),
            str(CONTRACT_TEST.relative_to(ROOT)),
        ],
        "operationCount": len(operations),
        "counts": counts,
        "unknownOperations": sorted(unknown),
        "registryMissingFromOpenAPI": missing_from_openapi,
        "allOperationsAccountedFor": (
            not unknown and not missing_from_openapi and len(operations) == len(REGISTRY)
        ),
        "operations": operations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    report = generate()
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    if not report["allOperationsAccountedFor"]:
        return 1
    if any(
        operation["status"] == "UNVERIFIED"
        for operation in report["operations"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
