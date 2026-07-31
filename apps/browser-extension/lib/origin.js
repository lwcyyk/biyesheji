const LOOPBACK_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]"]);

export function canonicalOrigin(raw, { allowLoopbackHttp = false } = {}) {
  if (typeof raw !== "string" || raw.length === 0 || raw.length > 2048 || raw.trim() !== raw) {
    throw new Error("ORIGIN_INVALID");
  }
  let parsed;
  try {
    parsed = new URL(raw);
  } catch {
    throw new Error("ORIGIN_INVALID");
  }
  if (parsed.username || parsed.password || parsed.search || parsed.hash ||
      (parsed.pathname !== "" && parsed.pathname !== "/")) {
    throw new Error("ORIGIN_INVALID");
  }
  if (parsed.hostname.endsWith(".") || parsed.port === "0") {
    throw new Error("ORIGIN_INVALID");
  }
  if (!parsed.hostname.startsWith("[")) {
    const labels = parsed.hostname.split(".");
    if (parsed.hostname.length > 253 || labels.some((label) =>
      label.length === 0 || label.length > 63 ||
      label.startsWith("-") || label.endsWith("-"))) {
      throw new Error("ORIGIN_INVALID");
    }
  }
  const authority = raw.match(/^[a-z][a-z0-9+.-]*:\/\/([^/?#]+)/i)?.[1] ?? "";
  const rawHost = authority.replace(/:\d+$/, "");
  if (/^[0-9.]+$/.test(rawHost) && rawHost !== parsed.hostname) {
    throw new Error("ORIGIN_INVALID");
  }
  if (parsed.protocol !== "https:" &&
      !(allowLoopbackHttp && parsed.protocol === "http:" && LOOPBACK_HOSTS.has(parsed.hostname))) {
    throw new Error("ORIGIN_TRANSPORT_REJECTED");
  }
  const port = parsed.port;
  const defaultPort = (parsed.protocol === "https:" && port === "443") ||
    (parsed.protocol === "http:" && port === "80");
  return `${parsed.protocol}//${parsed.hostname.toLowerCase()}${port && !defaultPort ? `:${port}` : ""}`;
}

export function topFrameOrigin(tabURL) {
  return canonicalOrigin(tabURL, { allowLoopbackHttp: true });
}

export function isTopFrame(sender) {
  return sender && sender.frameId === 0;
}

export function redirectDecision(previous, current, options = {}) {
  const previousOrigin = canonicalOrigin(previous, options);
  const currentOrigin = canonicalOrigin(current, options);
  const sameOrigin = previousOrigin === currentOrigin;
  return Object.freeze({
    targetOrigin: currentOrigin,
    sameOrigin,
    requiresRouteRevalidation: true,
    invalidatePreviousHandle: !sameOrigin
  });
}

export function explicitOriginPolicy(origins, options = {}) {
  if (!Array.isArray(origins) || origins.length === 0 || origins.length > 16) {
    throw new Error("ORIGIN_POLICY_INVALID");
  }
  const canonical = origins.map((value) => canonicalOrigin(value, options));
  if (new Set(canonical).size !== canonical.length) {
    throw new Error("ORIGIN_POLICY_INVALID");
  }
  const allowed = new Set(canonical);
  return Object.freeze({
    allows(raw) {
      return allowed.has(canonicalOrigin(raw, options));
    }
  });
}
