const HOST_NAME = "org.vpass.local_client";
let nativePort = null;
let requestCounter = 0;
const pending = new Map();

function port() {
  if (nativePort) return nativePort;
  nativePort = chrome.runtime.connectNative(HOST_NAME);
  nativePort.onMessage.addListener((response) => {
    const waiter = pending.get(response?.requestId);
    if (!waiter) return;
    pending.delete(response.requestId);
    if (response.ok === true) waiter.resolve(response);
    else waiter.reject(new Error(response?.code || "NATIVE_HOST_UNAVAILABLE"));
  });
  nativePort.onDisconnect.addListener(() => {
    const error = new Error("NATIVE_HOST_DISCONNECTED");
    for (const waiter of pending.values()) waiter.reject(error);
    pending.clear();
    nativePort = null;
  });
  return nativePort;
}

export function nativeCommand(command, payload = {}) {
  const requestId = `native-${Date.now()}-${++requestCounter}`;
  return new Promise((resolve, reject) => {
    pending.set(requestId, { resolve, reject });
    try {
      port().postMessage({ requestId, command, ...payload });
    } catch {
      pending.delete(requestId);
      reject(new Error("NATIVE_HOST_UNAVAILABLE"));
    }
  }).then((response) => {
    if (!response || response.ok !== true) {
      throw new Error(response?.code || "NATIVE_HOST_UNAVAILABLE");
    }
    return response;
  });
}

export function closeNativeChannel() {
  if (nativePort) {
    nativePort.disconnect();
    nativePort = null;
  }
}

export async function connectionInfo() {
  const response = await nativeCommand("connectionInfo");
  return { baseURL: response.baseURL, installToken: response.installToken };
}

export async function stageMasterPassword(deviceId, masterPassword) {
  return nativeCommand("stageMasterPassword", { deviceId, secretValue: masterPassword });
}

export async function stageCredentialField(sessionId, origin, accountId, fieldType, secretValue) {
  return nativeCommand("stageCredentialField", {
    sessionId, origin, accountId, fieldType, secretValue
  });
}

export async function stageAuditAnalysisSecret(sessionId, secretValue) {
  return nativeCommand("stageAuditAnalysisSecret", { sessionId, secretValue });
}

export async function readSecurityAnalysisResult(
  sessionId, resultReference, cursor = undefined, limit = 50
) {
  const response = await nativeCommand("readSecurityAnalysisResult", {
    sessionId, resultReference, ...(cursor ? { cursor } : {}), limit
  });
  return response.result;
}

export async function consumeSecretHandle(sessionId, secretHandle, origin, fieldType) {
  return nativeCommand("consumeSecretHandle", { sessionId, secretHandle, origin, fieldType });
}

export async function authorizeCandidateField(
  sessionId, credentialId, candidateVersion, origin, fieldType
) {
  return nativeCommand("authorizeCandidateField", {
    sessionId, credentialId, candidateVersion, origin, fieldType
  });
}
