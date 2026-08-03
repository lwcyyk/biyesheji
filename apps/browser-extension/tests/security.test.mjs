import test from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

async function sourceFiles(directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === "tests") continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) result.push(...await sourceFiles(path));
    else if (/\.(js|html|css|json)$/.test(entry.name)) result.push(path);
  }
  return result;
}

test("Manifest V3 uses minimal permissions and self-only CSP", async () => {
  const manifest = JSON.parse(await readFile(join(root, "manifest.json"), "utf8"));
  assert.equal(manifest.manifest_version, 3);
  assert.deepEqual(
    [...manifest.permissions].sort(),
    ["activeTab", "nativeMessaging", "scripting"].sort()
  );
  assert.deepEqual(manifest.host_permissions, ["http://127.0.0.1/*"]);
  const csp = manifest.content_security_policy.extension_pages;
  assert.match(csp, /script-src 'self'/);
  assert.match(csp, /object-src 'none'/);
  assert.doesNotMatch(csp, /unsafe-|https?:\/\//);
  assert.equal(manifest.content_scripts, undefined);
});

test("extension sources contain no remote scripts, dynamic code, storage, or secret logs", async () => {
  for (const file of await sourceFiles(root)) {
    const source = await readFile(file, "utf8");
    assert.doesNotMatch(source, /<script[^>]+src=["']https?:\/\//i, file);
    assert.doesNotMatch(source, /\beval\s*\(|new\s+Function\s*\(/, file);
    assert.doesNotMatch(source, /\b(?:localStorage|sessionStorage|chrome\.storage)\b/, file);
    assert.doesNotMatch(source, /\bconsole\.(?:log|debug|info|warn|error)\s*\(/, file);
    assert.doesNotMatch(source, /\.innerHTML\s*=/, file);
  }
});

test("autofill content gate binds top frame and exact Origin", async () => {
  const source = await readFile(join(root, "content", "autofill.js"), "utf8");
  assert.match(source, /window\.top !== window/);
  assert.match(source, /message\.origin !== location\.origin/);
  assert.match(source, /EMPTY_SECRET_REJECTED/);
  assert.match(source, /frameId: 0|globalThis/);
});

test("HTTP client sends handles and security headers but exposes no secret-value route", async () => {
  const source = await readFile(join(root, "lib", "api.js"), "utf8");
  assert.match(source, /X-VPass-Request-Nonce/);
  assert.match(source, /Idempotency-Key/);
  assert.match(source, /X-VPass-Vault-Session/);
  assert.match(source, /credentials: "omit"/);
  assert.doesNotMatch(source, /masterPassword\s*:/);
  assert.doesNotMatch(source, /secretValue\s*:/);
});
