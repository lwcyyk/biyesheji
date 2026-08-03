import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import {
  canonicalOrigin,
  explicitOriginPolicy,
  isTopFrame,
  redirectDecision
} from "../lib/origin.js";
import {
  confirmationViewModel,
  credentialViewModel,
  securityFindingViewModel,
  versionViewModel
} from "../lib/view-models.js";

test("canonical Origin normalizes IDN, case, and default ports", () => {
  assert.equal(
    canonicalOrigin("https://BÜCHER.example:443"),
    "https://xn--bcher-kva.example"
  );
  assert.equal(
    canonicalOrigin("https://EXAMPLE.com:8443"),
    "https://example.com:8443"
  );
});

test("Origin rejects paths, credentials, remote HTTP, and whitespace", () => {
  for (const value of [
    "https://example.com/login",
    "https://alice@example.com",
    "http://example.com",
    "https://example.com.",
    "https://example.com:0",
    "chrome-extension://abcdefghijklmnop/popup.html",
    " https://example.com",
    "javascript:alert(1)"
  ]) {
    assert.throws(() => canonicalOrigin(value));
  }
  assert.equal(
    canonicalOrigin("http://127.0.0.1:8080", { allowLoopbackHttp: true }),
    "http://127.0.0.1:8080"
  );
});

test("shared canonical Origin vectors match the browser boundary", () => {
  const vectors = JSON.parse(readFileSync(
    new URL("../../../specs/001-vdns-audit-rotation/canonical-origin-vectors.json", import.meta.url),
    "utf8"
  ));
  for (const vector of vectors.valid) {
    assert.equal(canonicalOrigin(vector.input, {
      allowLoopbackHttp: vector.allowLoopbackHttp
    }), vector.canonical);
  }
  for (const input of vectors.invalid) {
    assert.throws(() => canonicalOrigin(input));
  }
});

test("redirects force rerouting and cross-Origin handle invalidation", () => {
  assert.deepEqual(
    redirectDecision("https://example.com", "https://example.com:443"),
    {
      targetOrigin: "https://example.com",
      sameOrigin: true,
      requiresRouteRevalidation: true,
      invalidatePreviousHandle: false
    }
  );
  const cross = redirectDecision("https://example.com", "https://login.example.com");
  assert.equal(cross.requiresRouteRevalidation, true);
  assert.equal(cross.invalidatePreviousHandle, true);
  assert.throws(() => redirectDecision("https://example.com", "http://example.com"));
});

test("multi-Origin accounts require an explicit exact policy", () => {
  const policy = explicitOriginPolicy([
    "https://example.com",
    "https://login.example.com"
  ]);
  assert.equal(policy.allows("https://example.com:443"), true);
  assert.equal(policy.allows("https://other.example.com"), false);
  assert.throws(() => explicitOriginPolicy([
    "https://example.com",
    "https://EXAMPLE.com:443"
  ]));
});

test("trusted sender must be the top frame", () => {
  assert.equal(isTopFrame({ frameId: 0 }), true);
  assert.equal(isTopFrame({ frameId: 2 }), false);
  assert.equal(isTopFrame(null), null);
});

test("view models never map UNKNOWN to completed", () => {
  const unknown = versionViewModel({
    version: 2, state: "UNKNOWN", evidenceLevel: "SUBMIT_OBSERVED"
  });
  assert.equal(unknown.completed, false);
  assert.match(unknown.warning, /旧版本继续生效/);
  assert.equal(confirmationViewModel({
    version: 2, state: "UNKNOWN", evidenceLevel: "SUBMIT_OBSERVED"
  }).tone, "warning");
});

test("credential view explains source, verdict, and conflict recovery", () => {
  const view = credentialViewModel({
    credentialId: "id", accountLabel: "alice", activeVersion: 4,
    lifecycleStatus: "CONFLICTED", verdict: "REVIEW_REQUIRED"
  });
  assert.equal(view.needsReview, true);
  assert.match(view.sourceText, /可验证状态/);
  assert.match(view.verdictText, /人工复核/);
  assert.ok(view.recoveryActions.some((value) => value.includes("descriptor")));
});

test("security finding view exposes only pseudonym, confidence, and proof references", () => {
  const view = securityFindingViewModel({
    kind: "PASSWORD_REUSE",
    credentialPseudonym: "abcdefghijklmnopqrstuvwxyz",
    confidence: "STRONG",
    evidenceObjectDigests: ["proof-a", "proof-b"],
    currentVersion: 3,
    observedTimeBucket: 42
  });
  assert.equal(view.riskText, "当前密码重复使用");
  assert.equal(view.subject, "abcdefghijkl");
  assert.equal(view.confidenceText, "强证据");
  assert.deepEqual(view.evidence, ["proof-a", "proof-b"]);
  assert.equal("password" in view, false);
  assert.equal("credentialId" in view, false);
  assert.equal("deviceId" in view, false);
});
