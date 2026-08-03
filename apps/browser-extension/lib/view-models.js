const VERDICT_TEXT = {
  ACCEPT: "五层验证通过",
  DEGRADED_OFFLINE: "离线缓存读取（降级）",
  DEGRADED_PENDING_LOG: "等待透明日志包含（降级）",
  REVIEW_REQUIRED: "需要人工复核",
  REJECT_IDENTITY: "设备身份验证失败",
  REJECT_CAPABILITY: "设备无此操作权限",
  REJECT_REVOKED: "设备已撤销",
  REJECT_CAUSAL: "版本或因果顺序异常",
  REJECT_PROOF: "透明证明验证失败",
  REJECT_ORIGIN: "网站来源不匹配",
  REJECT_POLICY: "本地策略拒绝",
  REJECT_OBJECT: "密文对象不匹配"
};

const VERSION_TEXT = {
  CANDIDATE_LOCAL: "候选已在本地保存",
  SITE_CHANGE_IN_PROGRESS: "网站正在处理改密",
  SITE_CHANGED_LOCAL_COMMIT_PENDING: "网站已改，等待本地提交",
  SITE_CONFIRM_PENDING: "等待网站或用户确认",
  ACTIVE: "当前生效版本",
  SUPERSEDED: "已被新版本替代",
  FAILED: "修改失败，旧版本仍生效",
  UNKNOWN: "网站结果未知，禁止激活",
  ABORTED: "已中止"
};

export function credentialViewModel(credential) {
  return {
    id: credential.credentialId,
    account: credential.accountLabel || "未命名账号",
    currentVersion: `v${credential.activeVersion}`,
    lifecycle: credential.lifecycleStatus,
    verdict: credential.verdict,
    verdictText: VERDICT_TEXT[credential.verdict] || credential.verdict,
    sourceText: "当前版本来源：可验证状态描述与已验证对象哈希",
    needsReview: credential.lifecycleStatus === "CONFLICTED" ||
      credential.verdict.startsWith("REJECT_") ||
      credential.verdict === "REVIEW_REQUIRED",
    recoveryActions: credential.lifecycleStatus === "CONFLICTED"
      ? ["查看冲突 descriptor", "保留双分支证据", "选择已确认版本"]
      : ["查看版本历史", "重新解析可信状态"]
  };
}

export function versionViewModel(version) {
  return {
    version: `v${version.version}`,
    state: version.state,
    stateText: VERSION_TEXT[version.state] || version.state,
    evidence: version.evidenceLevel || "尚无强确认",
    completed: version.state === "ACTIVE",
    warning: version.state === "UNKNOWN"
      ? "网站状态未知：旧版本继续生效，不得显示完成。"
      : ""
  };
}

export function confirmationViewModel(result) {
  const model = versionViewModel(result);
  return {
    ...model,
    tone: model.completed ? "success" :
      model.state === "FAILED" ? "danger" :
      model.state === "UNKNOWN" ? "warning" : "pending"
  };
}

const RISK_TEXT = {
  PASSWORD_REUSE: "当前密码重复使用",
  HISTORICAL_USE: "历史中出现待检查密码",
  STALE_CREDENTIAL: "长期未更新",
  ANOMALOUS_DEVICE: "异常设备操作",
  ROLLBACK: "版本回滚",
  CONFLICT: "同版本冲突"
};

const CONFIDENCE_TEXT = {
  STRONG: "强证据",
  MEDIUM: "中等证据",
  WEAK: "弱证据"
};

export function securityFindingViewModel(finding) {
  const evidence = Array.isArray(finding.evidenceObjectDigests)
    ? finding.evidenceObjectDigests : [];
  return {
    kind: finding.kind,
    riskText: RISK_TEXT[finding.kind] || finding.kind,
    subject: String(finding.credentialPseudonym || "").slice(0, 12),
    confidenceText: CONFIDENCE_TEXT[finding.confidence] || finding.confidence,
    evidence,
    version: `v${finding.currentVersion}`,
    observedBucket: finding.observedTimeBucket
  };
}
