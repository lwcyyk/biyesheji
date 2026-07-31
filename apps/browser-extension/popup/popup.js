const element = (id) => document.getElementById(id);

async function command(command, payload = {}) {
  const response = await chrome.runtime.sendMessage({ command, ...payload });
  if (!response?.ok) {
    const error = new Error(response?.message || "操作未完成");
    error.code = response?.code || "OPERATION_FAILED";
    error.details = response?.details;
    throw error;
  }
  return response.result;
}

function status(message, tone = "") {
  const target = element("status");
  target.textContent = message;
  target.className = tone;
}

function setUnlocked(unlocked) {
  element("unlock-panel").hidden = unlocked;
  element("daily-panel").hidden = !unlocked;
  element("vault-state").textContent = unlocked ? "已解锁" : "未解锁";
  element("vault-state").className = `badge ${unlocked ? "success" : "pending"}`;
}

let pendingChange = null;

async function refresh() {
  const state = await command("status");
  setUnlocked(state.unlocked);
  if (state.unlocked) {
    try {
      const discovered = await command("discover");
      element("current-origin").textContent = discovered.origin;
    } catch {
      element("current-origin").textContent = "当前页面不支持填充";
    }
  }
}

element("unlock").addEventListener("click", async () => {
  const deviceId = element("device-id").value.trim();
  const input = element("master-password");
  const masterPassword = input.value;
  input.value = "";
  try {
    await command("unlock", { deviceId, masterPassword });
    status("密码库已解锁。", "success");
    setUnlocked(true);
    await refresh();
  } catch (error) {
    status(`解锁失败：${error.code}`, "danger");
  }
});

element("generate").addEventListener("click", async () => {
  const accountId = element("account-id").value.trim();
  if (!accountId) return status("请先输入账号。", "warning");
  try {
    const result = await command("generate", {
      accountId, policyVersion: 1, length: 20
    });
    element("password-handle").value = result.generated.secretHandle;
    element("create-panel").hidden = false;
    element("save-retry").hidden = true;
    status("已生成一次性密码句柄；明文未进入扩展页面。", "success");
  } catch (error) {
    status(`生成失败：${error.code}`, "danger");
  }
});

element("save-credential").addEventListener("click", async () => {
  const accountId = element("account-id").value.trim();
  const username = element("username").value;
  const passwordHandle = element("password-handle").value;
  try {
    const staged = await command("stageField", {
      accountId, fieldType: "USERNAME", secretValue: username
    });
    element("username").value = "";
    await command("createCredential", {
      body: {
        accountId,
        usernameHandle: staged.secretHandle,
        passwordHandle,
        cryptoPolicyHash: "CQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJyg"
      }
    });
    element("password-handle").value = "";
    element("create-panel").hidden = true;
    status("凭据已加密保存并进入可验证生命周期。", "success");
  } catch (error) {
    element("save-retry").hidden = false;
    status(`保存未完成：${error.code}`, "danger");
  }
});

element("autofill").addEventListener("click", async () => {
  try {
    const result = await command("autofill", {
      accountId: element("account-id").value.trim() || undefined
    });
    element("account-choice").hidden = true;
    status(`已验证并填充 v${result.credential.activeVersion}。`, "success");
  } catch (error) {
    if (error.code === "ACCOUNT_SELECTION_REQUIRED" && error.details?.accountLabels) {
      const options = element("account-options");
      options.replaceChildren(...error.details.accountLabels.map((account) => {
        const button = document.createElement("button");
        button.textContent = account;
        button.addEventListener("click", () => {
          element("account-id").value = account;
          element("autofill").click();
        });
        return button;
      }));
      element("account-choice").hidden = false;
    }
    status(`未填充任何字段：${error.code}`, "danger");
  }
});

element("prepare-change").addEventListener("click", async () => {
  const accountId = element("account-id").value.trim();
  if (!accountId) return status("请先选择要改密的账号。", "warning");
  try {
    pendingChange = await command("prepareChange", { accountId });
    element("change-panel").hidden = false;
    element("change-summary").textContent =
      `候选 v${pendingChange.candidate.version} 已保存并填入网站的新密码框。请在网站提交后选择真实结果。`;
    status("候选版本尚未激活。", "warning");
  } catch (error) {
    status(`改密准备失败：${error.code}`, "danger");
  }
});

for (const button of document.querySelectorAll("[data-outcome]")) {
  button.addEventListener("click", async () => {
    if (!pendingChange) return;
    const outcome = button.dataset.outcome;
    try {
      const result = await command("confirmSite", {
        credentialId: pendingChange.credentialId,
        body: {
          expectedVersion: pendingChange.expectedVersion,
          candidateVersion: pendingChange.candidate.version,
          outcome,
          evidenceLevel: outcome === "SUCCEEDED" ? "USER_SIGNED_CONFIRMATION" : "SUBMIT_OBSERVED"
        }
      });
      if (result.state === "ACTIVE") {
        status(`v${result.version} 已激活。`, "success");
      } else if (result.state === "UNKNOWN") {
        status("网站结果未知：旧版本继续生效。", "warning");
      } else {
        status(`改密状态：${result.state}。`, result.state === "FAILED" ? "danger" : "warning");
      }
      pendingChange = null;
      element("change-panel").hidden = true;
    } catch (error) {
      status(`确认未记录：${error.code}`, "danger");
    }
  });
}

element("open-dashboard").addEventListener("click", () => {
  chrome.tabs.create({ url: chrome.runtime.getURL("dashboard/dashboard.html") });
});

element("lock").addEventListener("click", async () => {
  try {
    await command("lock");
  } finally {
    setUnlocked(false);
    status("密码库已锁定。");
  }
});

refresh().catch(() => setUnlocked(false));
