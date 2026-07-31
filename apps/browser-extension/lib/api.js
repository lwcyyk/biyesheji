import { canonicalOrigin } from "./origin.js";

const API_PREFIX = "/api/v2";
const LOOPBACK_PATTERN = /^http:\/\/127\.0\.0\.1:(\d{1,5})$/;

function base64url(bytes) {
  let binary = "";
  for (const value of bytes) binary += String.fromCharCode(value);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

function nonce() {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return base64url(bytes);
}

function idempotencyKey() {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return `vdns-${base64url(bytes)}`;
}

export class LocalAgentError extends Error {
  constructor(code, message, requestId, details = undefined, status = 0) {
    super(message || code || "LOCAL_AGENT_ERROR");
    this.name = "LocalAgentError";
    this.code = code || "LOCAL_AGENT_ERROR";
    this.requestId = requestId;
    this.details = details;
    this.status = status;
  }
}

export class LocalAgentClient {
  #baseURL;
  #installToken;
  #vaultSession;

  constructor(connection) {
    if (!connection || typeof connection.baseURL !== "string" ||
        typeof connection.installToken !== "string" || connection.installToken.length < 32) {
      throw new Error("LOCAL_CONNECTION_INVALID");
    }
    const match = LOOPBACK_PATTERN.exec(connection.baseURL);
    if (!match || Number(match[1]) < 1 || Number(match[1]) > 65535) {
      throw new Error("LOCAL_CONNECTION_INVALID");
    }
    this.#baseURL = connection.baseURL;
    this.#installToken = connection.installToken;
    this.#vaultSession = null;
  }

  setVaultSession(sessionId) {
    if (sessionId !== null && !/^[0-9a-f-]{36}$/.test(sessionId)) {
      throw new Error("VAULT_SESSION_INVALID");
    }
    this.#vaultSession = sessionId;
  }

  clear() {
    this.#installToken = "";
    this.#vaultSession = null;
  }

  async request(path, {
    method = "GET",
    body,
    mutation = false,
    nonceRequired = false,
    sessionRequired = true,
    idempotency = undefined
  } = {}) {
    if (!path.startsWith("/") || path.includes("..") || path.includes("://")) {
      throw new Error("API_PATH_INVALID");
    }
    const headers = {
      "Authorization": `Bearer ${this.#installToken}`,
      "Accept": "application/json"
    };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    if (sessionRequired) {
      if (!this.#vaultSession) throw new Error("VAULT_SESSION_REQUIRED");
      headers["X-VDNS-Vault-Session"] = this.#vaultSession;
    }
    if (nonceRequired) headers["X-VDNS-Request-Nonce"] = nonce();
    if (mutation) headers["Idempotency-Key"] = idempotency || idempotencyKey();
    const response = await fetch(`${this.#baseURL}${API_PREFIX}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
      credentials: "omit",
      redirect: "error",
      referrerPolicy: "no-referrer"
    });
    if (response.status === 204) return null;
    const value = await response.json().catch(() => ({
      code: "MALFORMED_LOCAL_RESPONSE",
      message: "本地代理返回了无法解析的响应。"
    }));
    if (!response.ok) {
      throw new LocalAgentError(value.code, value.message, value.requestId, value.details, response.status);
    }
    return value;
  }

  unlock(deviceId, masterPasswordHandle) {
    return this.request("/vault-sessions", {
      method: "POST", mutation: true, nonceRequired: true, sessionRequired: false,
      body: { deviceId, masterPasswordHandle }
    });
  }

  lock(sessionId) {
    return this.request(`/vault-sessions/${encodeURIComponent(sessionId)}`, {
      method: "DELETE", nonceRequired: true
    });
  }

  generatePassword(origin, accountId, policyVersion, length) {
    return this.request("/password-generations", {
      method: "POST", mutation: true, nonceRequired: true,
      body: { origin: canonicalOrigin(origin, { allowLoopbackHttp: true }), accountId, policyVersion, length }
    });
  }

  resolveRoute(origin, accountId = undefined) {
    return this.request("/credential-route-resolutions", {
      method: "POST", nonceRequired: true,
      body: {
        origin: canonicalOrigin(origin, { allowLoopbackHttp: true }),
        ...(accountId ? { accountId } : {}),
        topFrame: true
      }
    });
  }

  createCredential(body, idempotency) {
    return this.request("/credentials", {
      method: "POST", mutation: true, nonceRequired: true, idempotency, body
    });
  }

  credentials(cursor = undefined, limit = 50) {
    const query = new URLSearchParams({ limit: String(limit) });
    if (cursor) query.set("cursor", cursor);
    return this.request(`/credentials?${query}`);
  }

  credential(credentialId) {
    return this.request(`/credentials/${encodeURIComponent(credentialId)}`);
  }

  authorizeAutofill(credentialId, origin, fieldType, expectedVersion) {
    return this.request(`/credentials/${encodeURIComponent(credentialId)}/autofill-authorizations`, {
      method: "POST", mutation: true, nonceRequired: true,
      body: {
        origin: canonicalOrigin(origin, { allowLoopbackHttp: true }),
        fieldType, expectedVersion
      }
    });
  }

  createVersion(credentialId, body, idempotency) {
    return this.request(`/credentials/${encodeURIComponent(credentialId)}/versions`, {
      method: "POST", mutation: true, nonceRequired: true, idempotency, body
    });
  }

  confirmSite(credentialId, body, idempotency) {
    return this.request(`/credentials/${encodeURIComponent(credentialId)}/site-confirmations`, {
      method: "POST", mutation: true, nonceRequired: true, idempotency, body
    });
  }

  versions(credentialId, cursor = undefined, limit = 50) {
    const query = new URLSearchParams({ limit: String(limit) });
    if (cursor) query.set("cursor", cursor);
    return this.request(`/credentials/${encodeURIComponent(credentialId)}/versions?${query}`);
  }

  securityAnalysis(body, idempotency) {
    return this.request("/security-analyses", {
      method: "POST", mutation: true, idempotency, body
    });
  }

  operation(operationId) {
    return this.request(`/operations/${encodeURIComponent(operationId)}`);
  }
}
