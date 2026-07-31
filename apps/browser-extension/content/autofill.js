(() => {
  if (window.top !== window || globalThis.__VDNS_PM_CONTENT_READY__) return;
  globalThis.__VDNS_PM_CONTENT_READY__ = true;

  function visible(input) {
    const style = getComputedStyle(input);
    const rect = input.getBoundingClientRect();
    return !input.disabled && !input.readOnly && style.display !== "none" &&
      style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
  }

  function discover() {
    const inputs = [...document.querySelectorAll("input")].filter(visible);
    const password = inputs.find((input) =>
      input.type === "password" && input.autocomplete !== "new-password");
    const username = inputs.find((input) =>
      input !== password &&
      (input.autocomplete === "username" || input.type === "email" ||
       /user|email|account|login/i.test(`${input.name} ${input.id}`)));
    return {
      origin: location.origin,
      hasUsername: Boolean(username),
      hasPassword: Boolean(password)
    };
  }

  function fillField(fieldType, secretValue) {
    if (typeof secretValue !== "string" || secretValue.length === 0) {
      throw new Error("EMPTY_SECRET_REJECTED");
    }
    const inputs = [...document.querySelectorAll("input")].filter(visible);
    const target = fieldType === "PASSWORD"
      ? inputs.find((input) => input.type === "password" && input.autocomplete !== "new-password")
      : inputs.find((input) =>
        input.autocomplete === "username" || input.type === "email" ||
        /user|email|account|login/i.test(`${input.name} ${input.id}`));
    if (!target) throw new Error("TARGET_FIELD_NOT_FOUND");
    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    descriptor.set.call(target, secretValue);
    target.dispatchEvent(new Event("input", { bubbles: true }));
    target.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function fillNewPassword(secretValue) {
    if (typeof secretValue !== "string" || secretValue.length === 0) {
      throw new Error("EMPTY_SECRET_REJECTED");
    }
    const targets = [...document.querySelectorAll("input[type='password']")]
      .filter(visible)
      .filter((input) => input.autocomplete === "new-password")
      .slice(0, 2);
    if (targets.length === 0) throw new Error("NEW_PASSWORD_FIELD_NOT_FOUND");
    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    for (const target of targets) {
      descriptor.set.call(target, secretValue);
      target.dispatchEvent(new Event("input", { bubbles: true }));
      target.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (!message || message.origin !== location.origin) {
      sendResponse({ ok: false, code: "ORIGIN_REJECTED" });
      return false;
    }
    try {
      if (message.type === "VDNS_DISCOVER") {
        sendResponse({ ok: true, ...discover() });
      } else if (message.type === "VDNS_FILL") {
        fillField(message.fieldType, message.secretValue);
        sendResponse({ ok: true });
      } else if (message.type === "VDNS_FILL_NEW_PASSWORD") {
        fillNewPassword(message.secretValue);
        sendResponse({ ok: true });
      } else {
        sendResponse({ ok: false, code: "MESSAGE_REJECTED" });
      }
    } catch (error) {
      sendResponse({ ok: false, code: error.message || "FILL_REJECTED" });
    }
    return false;
  });
})();
