"use strict";

const pptxgen = require("pptxgenjs");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "VPass Graduate Design";
pptx.subject = "VPass：可验证密码生命周期管理系统的设计与实现";
pptx.title = "VPass 研究生毕业设计答辩";
pptx.company = "Graduate Design";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Noto Sans CJK SC",
  bodyFontFace: "Noto Sans CJK SC",
  lang: "zh-CN",
};
pptx.defineSlideMaster({
  title: "VPass",
  background: { color: "07111F" },
  objects: [
    {
      line: {
        x: 0.55,
        y: 7.12,
        w: 12.23,
        h: 0,
        line: { color: "263A52", width: 0.7 },
      },
    },
    {
      text: {
        text: "VPass · AEAD保护密码内容，可验证状态控制层保证生命周期状态可信",
        options: {
          x: 0.58,
          y: 7.17,
          w: 10.5,
          h: 0.18,
          fontFace: "Noto Sans CJK SC",
          fontSize: 7.5,
          color: "7F93AA",
          margin: 0,
        },
      },
    },
  ],
  slideNumber: {
    x: 12.2,
    y: 7.14,
    w: 0.5,
    h: 0.2,
    color: "7F93AA",
    fontFace: "Noto Sans CJK SC",
    fontSize: 8,
    align: "right",
    margin: 0,
  },
});

const C = {
  bg: "07111F",
  panel: "0D1B2B",
  panel2: "10243A",
  line: "29425E",
  text: "F3F7FB",
  muted: "A9B8C8",
  cyan: "35D0BA",
  blue: "4AA8FF",
  amber: "FFB84D",
  red: "FF6B73",
  purple: "A68BFF",
  green: "62D68B",
};

function addSlide(title, section) {
  const slide = pptx.addSlide("VPass");
  slide.background = { color: C.bg };
  slide.addText(section.toUpperCase(), {
    x: 0.62,
    y: 0.38,
    w: 2.8,
    h: 0.22,
    fontFace: "Noto Sans CJK SC",
    fontSize: 8.5,
    bold: true,
    charSpacing: 2.2,
    color: C.cyan,
    margin: 0,
  });
  slide.addText(title, {
    x: 0.6,
    y: 0.66,
    w: 12.05,
    h: 0.55,
    fontFace: "Noto Sans CJK SC",
    fontSize: 25,
    bold: true,
    color: C.text,
    margin: 0,
    breakLine: false,
  });
  return slide;
}

function addCard(slide, x, y, w, h, title, body, accent = C.cyan, options = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: options.fill || C.panel },
    line: { color: options.line || C.line, width: 0.8 },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x,
    y,
    w: 0.055,
    h,
    fill: { color: accent },
    line: { color: accent, transparency: 100 },
  });
  slide.addText(title, {
    x: x + 0.2,
    y: y + 0.15,
    w: w - 0.36,
    h: 0.32,
    fontFace: "Noto Sans CJK SC",
    fontSize: options.titleSize || 13.5,
    bold: true,
    color: options.titleColor || C.text,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.2,
    y: y + 0.55,
    w: w - 0.36,
    h: h - 0.68,
    fontFace: "Noto Sans CJK SC",
    fontSize: options.bodySize || 10.5,
    color: options.bodyColor || C.muted,
    breakLine: false,
    valign: "top",
    margin: 0,
    paraSpaceAfterPt: 3,
  });
}

function addBulletList(slide, items, x, y, w, h, options = {}) {
  const lineHeight = h / items.length;
  items.forEach((item, index) => {
    slide.addText(item, {
      x,
      y: y + index * lineHeight,
      w,
      h: Math.min(0.5, lineHeight),
      fontFace: "Noto Sans CJK SC",
      fontSize: options.fontSize || 13,
      color: options.color || C.text,
      bullet: { type: "bullet", indent: options.indent || 14 },
      hanging: 3,
      margin: 0,
      breakLine: false,
    });
  });
}

function addPill(slide, text, x, y, w, color) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.38,
    rectRadius: 0.08,
    fill: { color, transparency: 82 },
    line: { color, width: 0.8 },
  });
  slide.addText(text, {
    x,
    y: y + 0.065,
    w,
    h: 0.2,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 8.5,
    bold: true,
    color,
    margin: 0,
  });
}

function addFlowArrow(slide, x, y, w, color = C.blue) {
  slide.addShape(pptx.ShapeType.chevron, {
    x,
    y,
    w,
    h: 0.34,
    fill: { color, transparency: 20 },
    line: { color, transparency: 100 },
  });
}

function addMetric(slide, x, y, w, value, label, accent = C.cyan) {
  slide.addText(value, {
    x,
    y,
    w,
    h: 0.52,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 25,
    bold: true,
    color: accent,
    margin: 0,
  });
  slide.addText(label, {
    x,
    y: y + 0.58,
    w,
    h: 0.42,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 10.5,
    color: C.muted,
    margin: 0,
  });
}

function addSpeakerNotes(slide, lines) {
  if (typeof slide.addNotes === "function") {
    slide.addNotes(lines);
  }
}

// 1. Title
{
  const slide = pptx.addSlide();
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 11.74,
    y: 0.52,
    w: 0.92,
    h: 0.92,
    fill: { color: C.blue, transparency: 82 },
    line: { color: C.blue, width: 1.2 },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 12.08,
    y: 6.38,
    w: 0.45,
    h: 0.45,
    fill: { color: C.cyan, transparency: 82 },
    line: { color: C.cyan, width: 1.2 },
  });
  addPill(slide, "研究生毕业设计答辩", 0.75, 0.72, 2.2, C.cyan);
  slide.addText("VPass：可验证密码生命周期管理系统\n的设计与实现", {
    x: 0.74,
    y: 1.45,
    w: 10.55,
    h: 1.65,
    fontFace: "Noto Sans CJK SC",
    fontSize: 31,
    bold: true,
    color: C.text,
    margin: 0,
    breakLine: false,
    valign: "mid",
  });
  slide.addText("VPass: Verifiable Password Lifecycle Management System", {
    x: 0.78,
    y: 3.4,
    w: 9.7,
    h: 0.42,
    fontFace: "Aptos",
    fontSize: 14,
    color: C.blue,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.78,
    y: 4.15,
    w: 6.0,
    h: 0,
    line: { color: C.line, width: 1 },
  });
  slide.addText("答辩人：__________    导师：__________\n2026 年 7 月", {
    x: 0.78,
    y: 4.45,
    w: 5.9,
    h: 0.85,
    fontFace: "Noto Sans CJK SC",
    fontSize: 13,
    color: C.muted,
    margin: 0,
    breakLine: false,
  });
  slide.addText("核心命题", {
    x: 8.2,
    y: 4.55,
    w: 1.2,
    h: 0.28,
    fontFace: "Noto Sans CJK SC",
    fontSize: 9,
    bold: true,
    color: C.cyan,
    margin: 0,
  });
  slide.addText("AEAD保护密码内容\n可验证状态控制层保证生命周期状态可信", {
    x: 8.18,
    y: 4.94,
    w: 4.25,
    h: 1.05,
    fontFace: "Noto Sans CJK SC",
    fontSize: 20,
    bold: true,
    color: C.text,
    margin: 0,
    breakLine: false,
  });
  addSpeakerNotes(slide, ["开场只说明系统定位：完整密码管理器，不是泄露响应系统。"]);
}

// 2. Positioning
{
  const slide = addSlide("问题不是“能否解密”，还包括“为何相信它是当前密码”", "01 研究定位");
  addCard(slide, 0.65, 1.55, 3.72, 3.45, "普通密码库保护", "主密码 → KDF → 密文库\n\n关注：服务器是否看见密码\n不足：合法旧密文仍可能通过认证", C.blue);
  addCard(slide, 4.8, 1.55, 3.72, 3.45, "不可信同步控制", "存储层可回滚、替换、重放、制造冲突\n\n设备还需确认版本、主体、授权、撤销与历史", C.amber);
  addCard(slide, 8.95, 1.55, 3.72, 3.45, "VPass", "完整密码管理主线\n+\n可验证生命周期控制\n+\n隐私审计与可选事故响应", C.cyan);
  addFlowArrow(slide, 4.42, 3.02, 0.32);
  addFlowArrow(slide, 8.57, 3.02, 0.32);
  addPill(slide, "主线：生成 · 保存 · 填充 · 同步 · 更新 · 撤销 · 恢复", 2.0, 5.55, 9.3, C.cyan);
}

// 3. Research questions and contributions
{
  const slide = addSlide("五个研究问题，对应六项可验证贡献", "01 研究定位");
  addBulletList(
    slide,
    [
      "RQ1：根、设备秘密、字段 key 和恢复材料如何组织？",
      "RQ2：如何拒绝合法旧密文、替换对象和同版本冲突？",
      "RQ3：如何验证创建、更新、确认、撤销和恢复？",
      "RQ4：如何不公开稳定关系地完成密码使用审计？",
      "RQ5：如何用固定数据、故障和消融形成可复现证据？",
    ],
    0.78,
    1.55,
    6.05,
    4.5,
    { fontSize: 13 }
  );
  addCard(slide, 7.25, 1.45, 2.55, 1.28, "贡献 1–2", "五层可信状态解析\n名称空间授权主体", C.cyan, { bodySize: 10 });
  addCard(slide, 10.05, 1.45, 2.55, 1.28, "贡献 3–4", "接收方验证同步\n网站确认绑定生命周期", C.blue, { bodySize: 10 });
  addCard(slide, 7.25, 3.05, 2.55, 1.28, "贡献 5", "Epoch 隔离的\n隐私使用审计", C.purple, { bodySize: 10 });
  addCard(slide, 10.05, 3.05, 2.55, 1.28, "贡献 6", "可选泄露—修复\n一致性边界", C.amber, { bodySize: 10 });
  addCard(slide, 7.25, 4.65, 5.35, 1.3, "论文主次", "生命周期与可验证状态是核心创新；SCOPE-ZK 是事故时增强，不参与日常路径。", C.red, { bodySize: 10.5 });
}

// 4. Architecture
{
  const slide = addSlide("六个逻辑平面：前五层承担日常密码管理", "02 总体架构");
  const labels = [
    ["交互平面", "扩展 / 桌面 / 移动", C.blue],
    ["本地密码学与数据", "解锁 / 字段加密 / RouteMap", C.cyan],
    ["生命周期与同步", "创建 / 版本 / 确认 / 撤销", C.green],
    ["可验证状态控制层", "身份 / 权限 / 状态 / 证明", C.amber],
    ["存储与检查点", "密文对象 / 日志 / 周期根", C.purple],
    ["隐私审计与响应", "安全检查 / 可选 SCOPE-ZK", C.red],
  ];
  labels.forEach((entry, index) => {
    const y = 1.38 + index * 0.83;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 1.15,
      y,
      w: 11.0,
      h: 0.62,
      rectRadius: 0.06,
      fill: { color: entry[2], transparency: 88 },
      line: { color: entry[2], width: 0.9 },
    });
    slide.addText(`${index + 1}`, {
      x: 1.38,
      y: y + 0.12,
      w: 0.4,
      h: 0.25,
      fontFace: "Aptos Display",
      fontSize: 12,
      bold: true,
      color: entry[2],
      align: "center",
      margin: 0,
    });
    slide.addText(entry[0], {
      x: 2.0,
      y: y + 0.11,
      w: 3.0,
      h: 0.28,
      fontFace: "Noto Sans CJK SC",
      fontSize: 13,
      bold: true,
      color: C.text,
      margin: 0,
    });
    slide.addText(entry[1], {
      x: 5.25,
      y: y + 0.12,
      w: 5.9,
      h: 0.27,
      fontFace: "Noto Sans CJK SC",
      fontSize: 11,
      color: C.muted,
      margin: 0,
    });
  });
  addPill(slide, "链、VRF、SCOPE-ZK 均不在普通登录关键路径", 3.3, 6.48, 6.7, C.amber);
}

// 5. Cryptographic storage
{
  const slide = addSlide("随机高熵根 + 设备绑定解锁 + 字段级信封加密", "03 密码学存储");
  addCard(slide, 0.68, 1.45, 3.55, 2.0, "设备专属解锁", "Kpwd = Argon2id(Pm, salt)\nKunlock = HKDF(Kpwd ∥ Di, DeviceID)\nRootCapsule = AEAD(Kunlock, RootBundle)", C.cyan, { bodySize: 10 });
  addCard(slide, 4.88, 1.45, 3.55, 2.0, "严格域分离", "Kwrap · Kname · Kaudit\nKrelation · Krotation\n认证 key 与解密 key 不混用", C.purple, { bodySize: 10.5 });
  addCard(slide, 9.08, 1.45, 3.55, 2.0, "私有路由", "Origin + Account\n→ HMAC 索引\n→ 随机 32 B CredentialID", C.blue, { bodySize: 10.5 });
  addFlowArrow(slide, 4.34, 2.25, 0.42);
  addFlowArrow(slide, 8.54, 2.25, 0.42);
  addCard(slide, 0.68, 4.0, 11.95, 1.75, "字段级 CredentialEnvelope", "Origin · Username · Password · TOTP · Recovery Codes · Notes\n每字段独立随机 DEK；AAD 绑定 Namespace、CredentialID、版本、字段、策略摘要和 OriginBinding。\n只改 password 时，其他 ciphertext / wrapped key / digest 逐字节不变。", C.green, { bodySize: 11 });
  addPill(slide, "主密码不上传；只凭主密码 + 存储层数据不能恢复根", 3.35, 6.1, 6.6, C.cyan);
}

// 6. Autofill
{
  const slide = addSlide("日常自动填充：先验证控制面，再解密当前字段", "04 日常主流程");
  const steps = [
    ["1", "识别 Origin", C.blue],
    ["2", "本地 RouteMap", C.cyan],
    ["3", "可信状态解析", C.amber],
    ["4", "L1–L5 验证", C.purple],
    ["5", "获取当前密文", C.green],
    ["6", "版本/hash/AAD", C.red],
    ["7", "一次性句柄填充", C.blue],
  ];
  steps.forEach((step, index) => {
    const x = 0.62 + index * 1.82;
    slide.addShape(pptx.ShapeType.ellipse, {
      x,
      y: 2.05,
      w: 0.72,
      h: 0.72,
      fill: { color: step[2], transparency: 76 },
      line: { color: step[2], width: 1 },
    });
    slide.addText(step[0], {
      x,
      y: 2.22,
      w: 0.72,
      h: 0.24,
      align: "center",
      fontFace: "Aptos Display",
      fontSize: 12,
      bold: true,
      color: step[2],
      margin: 0,
    });
    slide.addText(step[1], {
      x: x - 0.34,
      y: 3.03,
      w: 1.4,
      h: 0.52,
      align: "center",
      fontFace: "Noto Sans CJK SC",
      fontSize: 9.5,
      bold: true,
      color: C.text,
      margin: 0,
      breakLine: false,
    });
    if (index < steps.length - 1) addFlowArrow(slide, x + 0.92, 2.23, 0.55, C.line);
  });
  addCard(slide, 1.0, 4.25, 3.35, 1.45, "不发送", "主密码 · 网站密码 · Origin 明文\n到存储层、状态节点或公告层", C.red, { bodySize: 10.5 });
  addCard(slide, 4.98, 4.25, 3.35, 1.45, "不等待", "区块链确认 · VRF\nSCOPE-ZK / 通用 zkVM", C.amber, { bodySize: 10.5 });
  addCard(slide, 8.96, 4.25, 3.35, 1.45, "不夸大", "AUTOFILL ≠ LOGIN\nSUBMIT ≠ SITE_CONFIRMED", C.cyan, { bodySize: 10.5 });
}

// 7. Lifecycle
{
  const slide = addSlide("耐久候选消除“本地值与网站值失配”窗口", "05 生命周期协议");
  const states = [
    ["ACTIVE(v)", C.green],
    ["UPDATE_PENDING", C.blue],
    ["SITE_CONFIRM_PENDING", C.amber],
    ["ACTIVE(v+1)", C.cyan],
  ];
  states.forEach((state, index) => {
    const x = 0.8 + index * 3.15;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.0,
      w: 2.1,
      h: 0.82,
      rectRadius: 0.08,
      fill: { color: state[1], transparency: 82 },
      line: { color: state[1], width: 1.1 },
    });
    slide.addText(state[0], {
      x,
      y: 2.25,
      w: 2.1,
      h: 0.26,
      align: "center",
      fontFace: "Aptos",
      fontSize: 12,
      bold: true,
      color: state[1],
      margin: 0,
    });
    if (index < states.length - 1) addFlowArrow(slide, x + 2.25, 2.25, 0.65, C.line);
  });
  addCard(slide, 1.2, 3.55, 4.65, 1.75, "强确认路径", "候选先在本地加密耐久\n网站强确认或用户明确确认\n→ 激活 v+1，旧版本失效", C.green, { bodySize: 11 });
  addCard(slide, 7.45, 3.55, 4.65, 1.75, "模糊/失败路径", "响应丢失 → UNKNOWN / REVIEW_REQUIRED\n显式失败 → 保留 ACTIVE(v)\n系统不猜测远端状态", C.red, { bodySize: 11 });
  addPill(slide, "填充、提交、页面跳转只能产生观察事件", 3.38, 5.9, 6.55, C.amber);
}

// 8. Trusted state verification
{
  const slide = addSlide("五层可信状态验证：签名有效只是第一层", "05 生命周期协议");
  const layers = [
    ["L1", "主体真实性", "设备签名 · 根凭证链", C.blue],
    ["L2", "操作资格", "Capability · Scope · 有效期", C.cyan],
    ["L3", "动态状态", "撤销序 · 版本 · counter · 前序", C.amber],
    ["L4", "透明历史", "包含/一致性 · 树头 · 检查点", C.purple],
    ["L5", "本地采信", "风险 · 缓存年龄 · 用户策略", C.green],
  ];
  layers.forEach((entry, index) => {
    const y = 1.42 + index * 0.9;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 0.82,
      y,
      w: 8.2,
      h: 0.67,
      fill: { color: entry[3], transparency: 86 },
      line: { color: entry[3], width: 0.9 },
    });
    slide.addText(entry[0], {
      x: 1.03,
      y: y + 0.16,
      w: 0.6,
      h: 0.24,
      fontFace: "Aptos Display",
      fontSize: 11,
      bold: true,
      color: entry[3],
      margin: 0,
    });
    slide.addText(entry[1], {
      x: 1.75,
      y: y + 0.15,
      w: 1.65,
      h: 0.26,
      fontFace: "Noto Sans CJK SC",
      fontSize: 12,
      bold: true,
      color: C.text,
      margin: 0,
    });
    slide.addText(entry[2], {
      x: 3.55,
      y: y + 0.16,
      w: 4.85,
      h: 0.25,
      fontFace: "Noto Sans CJK SC",
      fontSize: 10.5,
      color: C.muted,
      margin: 0,
    });
  });
  addCard(slide, 9.52, 1.42, 2.85, 2.05, "联合不变量", "IdentityValid\n∧ AuthorizationValid\n∧ NotRevoked\n∧ CausallyFresh\n∧ LogIncluded\n∧ PolicyAccepted", C.cyan, { bodySize: 10 });
  addCard(slide, 9.52, 3.82, 2.85, 1.82, "最终 Verdict", "ACCEPT\nDEGRADED\nREVIEW_REQUIRED\nREJECT", C.amber, { bodySize: 11 });
  addPill(slide, "current state 由接收设备验证，不由同步存储层宣告", 3.2, 6.2, 6.95, C.cyan);
}

// 9. Sync
{
  const slide = addSlide("多设备同步：存储层保存对象，设备验证当前状态", "05 生命周期协议");
  addCard(slide, 0.75, 1.55, 2.65, 3.65, "设备 A", "生成候选\n→ 网站确认\n→ 签名事件\n→ 对象/manifest\n→ ACTIVE(v+1)", C.blue, { bodySize: 12 });
  addCard(slide, 5.34, 1.55, 2.65, 3.65, "不可信存储", "可删除\n可回滚\n可替换\n可重放\n可制造缺失", C.red, { bodySize: 12 });
  addCard(slide, 9.93, 1.55, 2.65, 3.65, "设备 B", "解析可信状态\n→ 验证 L1–L5\n→ 下载当前 hash\n→ 原子接受\n→ ACTIVE(v+1)", C.cyan, { bodySize: 12 });
  addFlowArrow(slide, 3.62, 2.8, 1.4, C.blue);
  addFlowArrow(slide, 8.21, 2.8, 1.4, C.cyan);
  addPill(slide, "returnedVersion < trustedVersion  ⇒  REJECT", 3.17, 5.72, 7.0, C.red);
  slide.addText("同版本异摘要 → CONFLICTED；两个分支均保留，等待显式裁决", {
    x: 2.25,
    y: 6.34,
    w: 8.9,
    h: 0.35,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 11,
    color: C.muted,
    margin: 0,
  });
}

// 10. Audit
{
  const slide = addSlide("隐私审计持续运行；泄露响应只在显式事故中启动", "06 隐私审计");
  addCard(slide, 0.7, 1.5, 3.7, 4.2, "日常隐私审计", "Epoch audit key\n+ ExactEncode(password)\n→ 加密隐藏见证\n\n检测：复用 / 历史 / 陈旧\n异常设备 / 回滚 / 冲突", C.purple, { bodySize: 11 });
  addCard(slide, 4.82, 1.5, 3.7, 4.2, "最小公开叶", "namespace commitment\nsubject pseudonym\nobject type / digest\noperation / final sequence / epoch\n\n不含密码、Origin、账号\nCredentialID、DeviceID、稳定 tag", C.cyan, { bodySize: 10.5 });
  addCard(slide, 8.94, 1.5, 3.7, 4.2, "可选事故响应", "固定 IncidentSnapshot\nAffectedRoot 绑定集合\n最小成本动作规划\nCompleted / Pending / Failed / Unknown\n\nSCOPE-ZK：UNAVAILABLE", C.amber, { bodySize: 10.5 });
  addPill(slide, "ChangedSet = Completed；未完成项和无关字段不变", 3.05, 6.15, 7.25, C.green);
}

// 11. Implementation
{
  const slide = addSlide("参考实现：模块化单体 + 端口/适配器", "07 系统实现");
  addCard(slide, 0.68, 1.45, 3.55, 2.02, "交互与入口", "Browser Extension\nNative Messaging\nLocal Secure Client / HTTP / Mock Site", C.blue, { bodySize: 11 });
  addCard(slide, 4.88, 1.45, 3.55, 2.02, "领域核心", "cryptokit · credential · device\nsync · resolver · transparency\nmonitoring · audit · remediation", C.cyan, { bodySize: 10.5 });
  addCard(slide, 9.08, 1.45, 3.55, 2.02, "外部适配器", "SQLite WAL/FULL\n内容寻址对象库\n模拟日志 / Anvil research adapter", C.purple, { bodySize: 10.5 });
  addFlowArrow(slide, 4.34, 2.28, 0.42);
  addFlowArrow(slide, 8.54, 2.28, 0.42);
  addMetric(slide, 1.05, 4.3, 2.25, "43", "功能需求 FR");
  addMetric(slide, 3.95, 4.3, 2.25, "21", "验收条件 AC", C.blue);
  addMetric(slide, 6.85, 4.3, 2.25, "22", "/api/v2 操作", C.amber);
  addMetric(slide, 9.75, 4.3, 2.25, "33", "SBOM 组件", C.purple);
  addPill(slide, "领域核心不依赖 HTTP、SQLite、浏览器或链 SDK", 3.13, 6.1, 7.1, C.cyan);
}

// 12. Experiment methodology
{
  const slide = addSlide("实验设计：固定数据、真实边界、失败结果保留", "08 实验评估");
  addCard(slide, 0.72, 1.45, 3.65, 2.0, "可复现输入", "dataset v1\nseed = 20260723\nTEST_ONLY，无真实密码\n数据摘要固定", C.cyan, { bodySize: 11 });
  addCard(slide, 4.83, 1.45, 3.65, 2.0, "统计口径", "10 次预热 + 30 次测量\nP50 / P95 / P99\n标准差 + bootstrap 95%\nCPU / 分配 / max RSS", C.blue, { bodySize: 10.5 });
  addCard(slide, 8.94, 1.45, 3.65, 2.0, "Provider 分类", "真实本地密码学 / SQLite\nMock Site / 模拟日志\nAnvil optional\nZK provider unavailable", C.amber, { bodySize: 10.5 });
  addCard(slide, 0.72, 3.95, 5.75, 1.75, "环境", "Go 1.25.12 · Linux amd64 · Ryzen 9 8945HX · 16 逻辑核 · 8.28 GB\n工作区无 Git：证据记录 WORKTREE_NO_GIT", C.green, { bodySize: 10.5 });
  addCard(slide, 6.88, 3.95, 5.71, 1.75, "声明边界", "浏览器未安装：扩展为合同/TAP/e2e\n无真实公网、生产链或硬件 key\n历史 G5/G6 数据不与 G7 合并统计", C.red, { bodySize: 10.5 });
}

// 13. Performance
{
  const slide = addSlide("冻结性能目标全部满足", "08 实验评估");
  slide.addChart(
    pptx.ChartType.bar,
    [
      {
        name: "P95 / 目标（%）",
        labels: ["解锁", "字段解密", "Route 10k", "Route 100k", "同步 10k", "1m 证明"],
        values: [26.19, 3.31, 8.04, 1.2, 30.74, 0.067],
      },
    ],
    {
      x: 0.72,
      y: 1.45,
      w: 7.55,
      h: 4.85,
      catAxisLabelFontFace: "Noto Sans CJK SC",
      catAxisLabelFontSize: 10,
      valAxisLabelFontFace: "Aptos",
      valAxisLabelFontSize: 9,
      valAxisMinVal: 0,
      valAxisMaxVal: 100,
      valAxisMajorUnit: 20,
      showLegend: false,
      showTitle: false,
      showValue: true,
      dataLabelPosition: "outEnd",
      dataLabelColor: C.text,
      dataLabelFormatCode: "0.0",
      chartColors: [C.cyan],
      showCatName: false,
      showValAxisTitle: true,
      valAxisTitle: "目标消耗比例（越低越好）",
      valAxisTitleFontFace: "Noto Sans CJK SC",
      valAxisTitleFontSize: 9,
      showCatName: false,
      showValue: true,
      showValAxis: true,
      showCatAxisTitle: false,
      showValGridLine: true,
      valGridLine: { color: C.line, width: 0.5 },
      chartLineColor: C.line,
      showBorder: false,
      layout: { x: 0.18, y: 0.08, w: 0.74, h: 0.82 },
    }
  );
  addMetric(slide, 8.7, 1.65, 3.35, "392.85 ms", "Argon2id 解锁 P95", C.cyan);
  addMetric(slide, 8.7, 3.0, 3.35, "614.70 ms", "10k 对象分批同步 P95", C.blue);
  addMetric(slide, 8.7, 4.35, 3.35, "16.79 μs", "1m 叶证明验证 P95", C.purple);
  addPill(slide, "100k 审计扫描：563.62 ms（目标 < 5 s）", 8.53, 5.8, 3.8, C.green);
}

// 14. Correctness
{
  const slide = addSlide("故障注入与 H1–H6：验证“机制移除会发生什么”", "08 实验评估");
  addMetric(slide, 0.75, 1.45, 2.2, "8 / 8", "全栈故障场景通过", C.green);
  addMetric(slide, 3.15, 1.45, 2.2, "7 / 7", "恢复演练通过", C.cyan);
  addMetric(slide, 5.55, 1.45, 2.2, "6", "消融假设 H1–H6", C.blue);
  addMetric(slide, 7.95, 1.45, 2.2, "0", "完整方案预置攻击接受", C.green);
  addMetric(slide, 10.35, 1.45, 2.2, "0 B", "无关字段变化", C.purple);
  addCard(slide, 0.72, 3.05, 3.7, 2.45, "H1–H2：控制面", "移除 trusted current state → 旧对象可被当成当前\n移除 capability/final sequence → 撤销后签名仍可能被接受", C.red, { bodySize: 10.5 });
  addCard(slide, 4.82, 3.05, 3.7, 2.45, "H3–H4：生命周期", "直接覆盖/候选不耐久 → 密码失配或丢失窗口\n整包重加密 → 无关字段变化", C.amber, { bodySize: 10.5 });
  addCard(slide, 8.92, 3.05, 3.7, 2.45, "H5–H6：隐私与响应", "稳定公开 tag → 跨 Epoch 关联\n无界批量修复 → 越界变化；完整方案只改 Completed", C.purple, { bodySize: 10.5 });
  addPill(slide, "弱化变体 = TEST_ONLY_DECISION_MODEL，不是生产隐藏开关", 3.05, 6.05, 7.3, C.amber);
}

// 15. Engineering gates
{
  const slide = addSlide("安全、API 与供应链门禁", "08 实验评估");
  addCard(slide, 0.7, 1.45, 3.75, 3.85, "安全工程", "初始：30 个可达漏洞\n升级后：0 个可达漏洞\n\n秘密扫描：通过\n扩展 CSP：通过\n密码学具名测试：385", C.green, { bodySize: 11 });
  addCard(slide, 4.8, 1.45, 3.75, 3.85, "API 复审", "22 个 /api/v2 操作\n合同 / 幂等 / 分页 / 错误通过\n\n评分：86.35 / 100（B+）\n结论：PASS_WITH_DOCUMENTATION_DEBT", C.blue, { bodySize: 10.5 });
  addCard(slide, 8.9, 1.45, 3.75, 3.85, "供应链", "CycloneDX 1.5\n33 个组件\n\n未知许可证：0\n拒绝许可证：0\nmodule-only advisory：1（不可达）", C.purple, { bodySize: 10.5 });
  addPill(slide, "升级前失败证据保留；不通过删除测试 fixture“修复”扫描", 2.9, 5.85, 7.55, C.amber);
}

// 16. Limitations
{
  const slide = addSlide("准确性边界与后续工作", "09 局限与展望");
  addCard(slide, 0.72, 1.45, 5.75, 4.65, "当前边界", "已解锁端点完全失陷不在防御范围\n撤销不能擦除历史秘密\nEpoch 伪名不提供网络匿名\nMock Site / 模拟日志 / Anvil ≠ 生产\nSCOPE-ZK / 通用 zkVM 未配置\n浏览器与移动端矩阵未实测\n单份 10k manifest 超 64 KiB", C.red, { bodySize: 12 });
  addCard(slide, 6.88, 1.45, 5.73, 4.65, "后续工作", "冻结批次与 collection root 协议\n移动端 Argon2id 能耗评估\n硬件保护根控制 key\n真实浏览器和站点 connector 矩阵\n多观察者 gossip / 生产日志\n第三方密码学与渗透审计\n经伦理审查的用户研究", C.cyan, { bodySize: 12 });
  addPill(slide, "不夸大模拟、链、撤销或零知识能力", 3.72, 6.35, 5.88, C.amber);
}

// 17. Conclusion
{
  const slide = addSlide("结论：把“当前密码的裁判权”从存储层交回验证设备", "10 总结");
  addCard(slide, 0.72, 1.48, 3.72, 2.18, "内容安全", "随机高熵根\n设备绑定 RootCapsule\n字段级 AEAD\n私有 RouteMap", C.blue, { bodySize: 11.5 });
  addCard(slide, 4.81, 1.48, 3.72, 2.18, "控制安全", "名称空间 capability\n可信状态 L1–L5\n透明历史与最终序\n网站确认生命周期", C.cyan, { bodySize: 11.5 });
  addCard(slide, 8.9, 1.48, 3.72, 2.18, "增强能力", "Epoch 隐私审计\n固定事故快照\n最小影响修复\n可选证明 provider", C.purple, { bodySize: 11.5 });
  slide.addText("AEAD 保护密码内容", {
    x: 1.2,
    y: 4.35,
    w: 4.8,
    h: 0.65,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 25,
    bold: true,
    color: C.blue,
    margin: 0,
  });
  slide.addText("+", {
    x: 6.16,
    y: 4.32,
    w: 0.8,
    h: 0.7,
    align: "center",
    fontFace: "Aptos Display",
    fontSize: 28,
    bold: true,
    color: C.muted,
    margin: 0,
  });
  slide.addText("可验证状态控制层保护控制过程", {
    x: 7.1,
    y: 4.35,
    w: 4.95,
    h: 0.65,
    align: "center",
    fontFace: "Noto Sans CJK SC",
    fontSize: 25,
    bold: true,
    color: C.cyan,
    margin: 0,
  });
  addPill(slide, "谢谢 · 欢迎提问", 4.75, 5.82, 3.83, C.cyan);
  addSpeakerNotes(slide, ["收束到核心命题，并主动提示可选 ZK 尚未实现。"]);
}

for (const slide of pptx._slides) {
  // Full-slide backgrounds and text placed inside cards are intentional containment.
  warnIfSlideHasOverlaps(slide, pptx, {
    muteContainment: true,
    ignoreLines: true,
    ignoreDecorativeShapes: true,
  });
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

pptx
  .writeFile({ fileName: "VPass答辩演示.pptx" })
  .then(() => console.log("vpass-defense-pptx-ok"))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
