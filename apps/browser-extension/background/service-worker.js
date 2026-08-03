import { LocalSecureClient, LocalClientError } from "../lib/api.js";
import { canonicalOrigin, isTopFrame } from "../lib/origin.js";
import {
  authorizeCandidateField,
  closeNativeChannel,
  connectionInfo,
  consumeSecretHandle,
  readSecurityAnalysisResult,
  stageAuditAnalysisSecret,
  stageCredentialField,
  stageMasterPassword
} from "../lib/native.js";

let client = null;
let vaultSession = null;

async function ensureClient() {
  if (!client) client = new LocalSecureClient(await connectionInfo());
  if (vaultSession) client.setVaultSession(vaultSession.sessionId);
  return client;
}

async function activeTopFrame() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id || !tab.url) throw new Error("ACTIVE_TAB_UNAVAILABLE");
  const origin = canonicalOrigin(new URL(tab.url).origin, { allowLoopbackHttp: true });
  await chrome.scripting.executeScript({
    target: { tabId: tab.id, frameIds: [0] },
    files: ["content/autofill.js"]
  });
  return { tab, origin };
}

async function fillOneField(api, tab, origin, route, fieldType) {
  const authorization = await api.authorizeAutofill(
    route.credentialId, origin, fieldType, route.activeVersion
  );
  if (authorization.verdict !== "ACCEPT" &&
      !authorization.verdict.startsWith("DEGRADED_")) {
    throw new Error("STATE_VERDICT_REJECTED");
  }
  if (!authorization.originVerified || authorization.credentialId !== route.credentialId) {
    throw new Error("AUTOFILL_BINDING_REJECTED");
  }
  const native = await consumeSecretHandle(
    vaultSession.sessionId, authorization.secretHandle, origin, fieldType
  );
  try {
    const response = await chrome.tabs.sendMessage(tab.id, {
      type: "VPASS_FILL", origin, fieldType, secretValue: native.secretValue
    }, { frameId: 0 });
    if (!response?.ok) throw new Error(response?.code || "FILL_REJECTED");
  } finally {
    native.secretValue = "";
  }
}

async function handleMessage(message, sender) {
  if (!message || typeof message.command !== "string") throw new Error("MESSAGE_REJECTED");
  if (sender.tab && !isTopFrame(sender)) throw new Error("IFRAME_REJECTED");
  const api = await ensureClient();
  switch (message.command) {
  case "status":
    return { unlocked: Boolean(vaultSession), session: vaultSession };
  case "unlock": {
    if (!message.deviceId || typeof message.masterPassword !== "string") {
      throw new Error("UNLOCK_INPUT_INVALID");
    }
    const staged = await stageMasterPassword(message.deviceId, message.masterPassword);
    message.masterPassword = "";
    vaultSession = await api.unlock(message.deviceId, staged.secretHandle);
    api.setVaultSession(vaultSession.sessionId);
    return { unlocked: true, session: vaultSession };
  }
  case "lock":
    if (vaultSession) await api.lock(vaultSession.sessionId);
    vaultSession = null;
    api.setVaultSession(null);
    return { unlocked: false };
  case "discover": {
    const { tab, origin } = await activeTopFrame();
    return chrome.tabs.sendMessage(tab.id, { type: "VPASS_DISCOVER", origin }, { frameId: 0 });
  }
  case "generate": {
    const { origin } = await activeTopFrame();
    const generated = await api.generatePassword(
      origin, message.accountId, message.policyVersion, message.length
    );
    return { origin, generated };
  }
  case "stageField": {
    const { origin } = await activeTopFrame();
    return stageCredentialField(
      vaultSession.sessionId, origin, message.accountId,
      message.fieldType, message.secretValue
    );
  }
  case "createCredential": {
    const { origin } = await activeTopFrame();
    return api.createCredential({ ...message.body, origin });
  }
  case "autofill": {
    const { tab, origin } = await activeTopFrame();
    const resolved = await api.resolveRoute(origin, message.accountId);
    const credential = await api.credential(resolved.credentialId);
    const route = { ...resolved, activeVersion: credential.activeVersion };
    const discovered = await chrome.tabs.sendMessage(
      tab.id, { type: "VPASS_DISCOVER", origin }, { frameId: 0 }
    );
    // Resolve + trusted-state verdict/object hash in the Local Secure Client + exact Origin are
    // all complete before the first field is sent to the page.
    if (discovered.hasUsername) await fillOneField(api, tab, origin, route, "USERNAME");
    if (discovered.hasPassword) await fillOneField(api, tab, origin, route, "PASSWORD");
    return { credential, filled: true };
  }
  case "credentials":
    return api.credentials(message.cursor, message.limit);
  case "versions":
    return api.versions(message.credentialId, message.cursor, message.limit);
  case "createVersion":
    return api.createVersion(message.credentialId, message.body);
  case "prepareChange": {
    const { tab, origin } = await activeTopFrame();
    const route = await api.resolveRoute(origin, message.accountId);
    const credential = await api.credential(route.credentialId);
    const generated = await api.generatePassword(origin, message.accountId, 1, 20);
    const candidate = await api.createVersion(route.credentialId, {
      expectedVersion: credential.activeVersion,
      previousDescriptorHash: credential.descriptorHash,
      fieldUpdates: [{ fieldType: "PASSWORD", secretHandle: generated.secretHandle }]
    });
    const staged = await authorizeCandidateField(
      vaultSession.sessionId, route.credentialId, candidate.version, origin, "PASSWORD"
    );
    const native = await consumeSecretHandle(
      vaultSession.sessionId, staged.secretHandle, origin, "PASSWORD"
    );
    try {
      const response = await chrome.tabs.sendMessage(tab.id, {
        type: "VPASS_FILL_NEW_PASSWORD", origin, secretValue: native.secretValue
      }, { frameId: 0 });
      if (!response?.ok) throw new Error(response?.code || "CHANGE_FILL_REJECTED");
    } finally {
      native.secretValue = "";
    }
    return {
      credentialId: route.credentialId,
      expectedVersion: credential.activeVersion,
      candidate
    };
  }
  case "confirmSite":
    return api.confirmSite(message.credentialId, message.body);
  case "securityCheck": {
    if (!vaultSession || typeof message.candidatePassword !== "string" ||
        message.candidatePassword.length === 0) {
      throw new Error("SECURITY_CHECK_INPUT_INVALID");
    }
    const credentials = await api.credentials(undefined, 1);
    if (!credentials.items.length) throw new Error("SECURITY_CHECK_EMPTY_VAULT");
    await stageAuditAnalysisSecret(vaultSession.sessionId, message.candidatePassword);
    message.candidatePassword = "";
    const operation = await api.securityAnalysis({
      analysisTypes: [
        "PASSWORD_REUSE", "HISTORICAL_USE", "STALE_CREDENTIAL",
        "ANOMALOUS_DEVICE", "ROLLBACK", "CONFLICT"
      ],
      sourceCheckpointHash: credentials.items[0].descriptorHash
    });
    if (operation.state !== "COMPLETED" || !operation.resultReference) {
      return { operation, page: { items: [] } };
    }
    const page = await readSecurityAnalysisResult(
      vaultSession.sessionId, operation.resultReference, undefined, 20
    );
    return { operation, page };
  }
  case "securityFindings":
    return readSecurityAnalysisResult(
      vaultSession.sessionId, message.resultReference, message.cursor, 20
    );
  default:
    throw new Error("MESSAGE_REJECTED");
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender)
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({
      ok: false,
      code: error instanceof LocalClientError ? error.code : error.message,
      message: error instanceof LocalClientError ? error.message : "操作未完成",
      details: error instanceof LocalClientError ? error.details : undefined
    }));
  return true;
});

chrome.runtime.onSuspend.addListener(() => {
	vaultSession = null;
	client?.clear();
	client = null;
	closeNativeChannel();
});
