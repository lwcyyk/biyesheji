import {
  credentialViewModel, securityFindingViewModel, versionViewModel
} from "../lib/view-models.js";

async function command(command, payload = {}) {
  const response = await chrome.runtime.sendMessage({ command, ...payload });
  if (!response?.ok) throw new Error(response?.code || "OPERATION_FAILED");
  return response.result;
}

const node = (tag, className, text) => {
  const value = document.createElement(tag);
  if (className) value.className = className;
  if (text) value.textContent = text;
  return value;
};

async function showVersions(credentialId) {
  const page = await command("versions", { credentialId, limit: 50 });
  const target = document.getElementById("versions");
  target.className = "timeline";
  target.replaceChildren(...page.items.map((item) => {
    const view = versionViewModel(item);
    const card = node("article", `version ${view.completed ? "active" : ""}`);
    card.append(node("strong", "", `${view.version} · ${view.stateText}`));
    card.append(node("span", "", `证据：${view.evidence}`));
    if (view.warning) card.append(node("p", "warning", view.warning));
    return card;
  }));
}

async function refresh() {
  const page = await command("credentials", { limit: 50 });
  const target = document.getElementById("credentials");
  target.replaceChildren(...page.items.map((item) => {
    const view = credentialViewModel(item);
    const card = node("button", `credential ${view.needsReview ? "review" : ""}`);
    card.append(node("strong", "", view.account));
    card.append(node("span", "version-label", `${view.currentVersion} · ${view.lifecycle}`));
    card.append(node("span", "verdict", `${view.verdict}: ${view.verdictText}`));
    card.append(node("small", "", view.sourceText));
    if (view.needsReview) {
      card.append(node("small", "warning", `恢复动作：${view.recoveryActions.join("；")}`));
    }
    card.addEventListener("click", () => showVersions(view.id).catch(showError));
    return card;
  }));
  document.getElementById("status").textContent = `已验证 ${page.items.length} 条凭据。`;
}

function showError(error) {
  const status = document.getElementById("status");
  status.textContent = `读取失败：${error.message}`;
  status.className = "danger";
}

let securityResultReference = "";
let securityCursor = "";

function findingCard(item) {
  const view = securityFindingViewModel(item);
  const card = node("article", "credential finding");
  card.append(node("strong", "", view.riskText));
  card.append(node("span", "", `${view.subject} · ${view.version} · ${view.confidenceText}`));
  const details = node("details");
  details.append(node("summary", "", "查看支持证明"));
  const list = node("ol");
  for (const digest of view.evidence) list.append(node("li", "", digest));
  details.append(list);
  card.append(details);
  return card;
}

function appendFindings(page, replace = false) {
  const target = document.getElementById("security-findings");
  const cards = page.items.map(findingCard);
  if (replace) target.replaceChildren(...cards);
  else target.append(...cards);
  securityCursor = page.nextCursor || "";
  document.getElementById("security-more").hidden = !securityCursor;
  if (replace && page.items.length === 0) {
    target.replaceChildren(node("p", "info-card", "本次检查未发现所选风险。"));
  }
}

async function runSecurityCheck() {
  const input = document.getElementById("audit-secret");
  const candidatePassword = input.value;
  input.value = "";
  if (!candidatePassword) throw new Error("请输入要检查的密码。");
  const result = await command("securityCheck", { candidatePassword });
  securityResultReference = result.operation.resultReference || "";
  appendFindings(result.page, true);
  document.getElementById("status").textContent =
    `安全检查完成：${result.page.items.length} 条结果（可分页查看证明）。`;
}

document.getElementById("refresh").addEventListener("click", () => refresh().catch(showError));
document.getElementById("device-help").addEventListener("click", () => {
  document.getElementById("recovery-actions").hidden =
    !document.getElementById("recovery-actions").hidden;
});
document.getElementById("run-security-check").addEventListener(
  "click", () => runSecurityCheck().catch(showError)
);
document.getElementById("security-more").addEventListener("click", async () => {
  try {
    const page = await command("securityFindings", {
      resultReference: securityResultReference, cursor: securityCursor
    });
    appendFindings(page);
  } catch (error) {
    showError(error);
  }
});
refresh().catch(showError);
